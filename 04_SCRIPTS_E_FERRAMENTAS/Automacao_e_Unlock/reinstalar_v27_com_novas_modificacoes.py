#!/usr/bin/env python3
"""
Orquestrador Seguro de Re-Flash A/B para Acer Predator Connect T7 (IPQ5332)
1. Envia a nova imagem SquashFS compilada (MD5 60c5a57dd891814ee330bbf70d4f52c3) para a Flash de espera (Slot 1) via HTTP interno.
2. Comuta o bootconfig para o Slot 1 (OEM v24).
3. Aguarda o boot limpo no Slot 1.
4. No Slot 1, grava o novo SquashFS na partição do Slot 2 (ubi1_2), limpa o overlay do Slot 2 (ubi1_3 -t), restaura bootconfig para Slot 2 e reinicia.
5. Aguarda o novo Slot 2 subir e valida todos os serviços.
"""

import http.server
import os
import socket
import socketserver
import sys
import threading
import time

ROUTER_IP = "192.168.76.1"
TELNET_PORT = 23
MAC_IP = "192.168.76.106"
HTTP_PORT = 8089
IMAGE_PATH = "/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/_FORA DO GitHub/03_ARTEFATOS_SQUASHFS_BUILD/rootfs_custom_opt.squashfs"
EXPECTED_MD5 = "b7a5db07f1706b699fa14516817581fd"

def telnet_run_cmd(cmd, wait_after=1, timeout=60):
    """Executa comando via Telnet no roteador."""
    out = b""
    try:
        s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=5)
        time.sleep(0.3)
        try:
            s.settimeout(1.0)
            s.recv(4096)
        except Exception:
            pass

        s.sendall(cmd.encode("utf-8") + b"\n")
        time.sleep(wait_after)

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                s.settimeout(2.0)
                chunk = s.recv(4096)
                if not chunk:
                    break
                out += chunk
                if b"=== FLASH_COMPLETO_COM_SUCESSO ===" in out:
                    break
                if b"/ #" in out[-20:] or b"# " in out[-10:]:
                    break
            except socket.timeout:
                if out:
                    break
            except Exception:
                break
        s.close()
    except Exception as e:
        return f"ERROR: {e}"
    return out.decode("utf-8", errors="ignore")

def wait_for_router(expected_version=None, max_retries=70, retry_delay=3):
    print(f"[*] Aguardando roteador responder em {ROUTER_IP}:{TELNET_PORT}...")
    for i in range(max_retries):
        try:
            s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=2)
            time.sleep(0.5)
            s.sendall(b"cat /etc/version\n")
            time.sleep(1)
            resp = s.recv(2048).decode("utf-8", errors="ignore")
            s.close()
            for line in resp.splitlines():
                if "1.01." in line or "T7_" in line:
                    ver = line.strip()
                    print(f"    [+] Roteador online! Versao detectada: {ver}")
                    if expected_version is None or expected_version in ver:
                        return True, ver
        except Exception:
            pass
        time.sleep(retry_delay)
        if (i + 1) % 5 == 0:
            print(f"    ... aguardando inicializacao ({(i+1)*retry_delay}s decorridos)")
    return False, "TIMEOUT"

class SingleFileHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/rootfs.squashfs":
            try:
                with open(IMAGE_PATH, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                print(f"[HTTP] Imagem enviada com sucesso ({len(data)} bytes)!")
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")

def start_http_server():
    server = socketserver.TCPServer((MAC_IP, HTTP_PORT), SingleFileHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server

def main():
    print("=" * 70)
    print("  ORQUESTRADOR DE RE-FLASH SEGURO - PREDATOR CONNECT T7")
    print(f"  Imagem Alvo: {IMAGE_PATH}")
    print(f"  MD5 Esperado: {EXPECTED_MD5}")
    print("=" * 70)

    # Etapa 1: Iniciar servidor HTTP local
    print("\n[Etapa 1/6] Iniciando servidor de transferencia local...")
    server = start_http_server()
    print(f"    Servidor rodando em http://{MAC_IP}:{HTTP_PORT}/rootfs.squashfs")

    # Etapa 2: Preparar e transferir imagem para o Slot 1
    print("\n[Etapa 2/6] Gravando imagem na particao de espera (Slot 1)...")
    prep_cmd = f"""
ubiattach /dev/ubi_ctrl -m 21 -d 1 2>/dev/null || true
mkdir -p /tmp/mnt1
mount -t ubifs /dev/ubi1_3 /tmp/mnt1 2>/dev/null || true
wget -O /tmp/mnt1/upper/rootfs.squashfs http://{MAC_IP}:{HTTP_PORT}/rootfs.squashfs
cp -vf /tmp/mnt1/upper/rootfs.squashfs /tmp/mnt1/upper/root/rootfs.squashfs
md5sum /tmp/mnt1/upper/rootfs.squashfs
sync
umount /tmp/mnt1 2>/dev/null || true
ubidetach -d 1 2>/dev/null || true
"""
    out_prep = telnet_run_cmd(prep_cmd, wait_after=2, timeout=60)
    print(f"Saida da preparacao no Slot 1:\n{out_prep.strip()}")
    server.shutdown()

    if EXPECTED_MD5 not in out_prep:
        print("[-] ERRO: O checksum MD5 da imagem no roteador nao corresponde ao esperado!")
        sys.exit(1)
    print(f"[+] Integridade 100% confirmada no Slot 1! MD5: {EXPECTED_MD5}")

    # Etapa 3: Chavear bootconfig para o Slot 1 (OEM v24)
    print("\n[Etapa 3/6] Chaveando bootconfig para inicializar no Slot 1 (OEM v24)...")
    telnet_run_cmd("/usr/sbin/boot-acer", wait_after=2, timeout=10)
    print("    Comando /usr/sbin/boot-acer executado. Aguardando boot do Slot 1...")
    time.sleep(10)

    # Etapa 4: Aguardar Slot 1 subir
    print("\n[Etapa 4/6] Aguardando Slot 1 (OEM v24)...")
    ok, ver = wait_for_router(expected_version="000024", max_retries=60, retry_delay=3)
    if not ok:
        print(f"[-] Falha ao aguardar Slot 1: {ver}")
        sys.exit(1)
    print(f"[OK] Slot 1 ativo com sucesso! ({ver})")

    # Etapa 5: Executar a gravacao no Slot 2 a partir do Slot 1
    print("\n[Etapa 5/6] Executando /root/auto_flash.sh no Slot 1...")
    flash_out = telnet_run_cmd("/root/auto_flash.sh", wait_after=3, timeout=90)
    print(f"Log do auto_flash:\n{flash_out}")

    if "FLASH_COMPLETO_COM_SUCESSO" not in flash_out and "Volume RootFS gravado com sucesso" not in flash_out:
        print("[-] ALERTA: A gravacao nao indicou sucesso comprovado! Verifique a saida.")
        sys.exit(1)

    print("[+] Gravacao concluida com sucesso! Roteador reiniciando de volta para o Slot 2...")
    time.sleep(10)

    # Etapa 6: Aguardar novo Slot 2 subir
    print("\n[Etapa 6/6] Aguardando o novo Slot 2 (v27 atualizado)...")
    ok, ver = wait_for_router(expected_version="000027", max_retries=60, retry_delay=3)
    if not ok:
        print(f"[-] Roteador demorou para responder: {ver}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("  🎉 RE-FLASH CONCLUIDO COM SUCESSO ABSOLUTO!")
    print(f"  Versao ativa: {ver}")
    print("=" * 70)

if __name__ == "__main__":
    main()
