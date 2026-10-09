#!/usr/bin/env python3
"""
Orquestrador Seguro de Flash Real A/B para Acer Predator Connect T7 (IPQ5332)
Grava o novo rootfs.squashfs de 36.032.512 bytes no Slot 2 com transição pelo Slot 1 (OEM v24).
"""

import http.server
import hashlib
import os
import socket
import socketserver
import subprocess
import sys
import threading
import time

ROUTER_IP = "192.168.76.1"
TELNET_PORT = 23
HTTP_PORT = 8089
IMAGE_PATH = "/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/_FORA DO GitHub/V27_CUSTOM_DEPLOY/rootfs.squashfs"

def get_mac_ip_for_router():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((ROUTER_IP, 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "192.168.76.106"
    finally:
        s.close()
    return ip

def compute_md5(filepath):
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def telnet_run_cmd(cmd, wait_after=1, timeout=90):
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

def wait_for_router(expected_version=None, max_retries=75, retry_delay=3):
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

class ImageHTTPHandler(http.server.SimpleHTTPRequestHandler):
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

def start_http_server(bind_ip):
    server = socketserver.TCPServer((bind_ip, HTTP_PORT), ImageHTTPHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def main():
    print("=" * 75)
    print("  ORQUESTRADOR DE FLASH REAL A/B - PREDATOR CONNECT T7")
    print(f"  Imagem Alvo: {IMAGE_PATH}")
    
    if not os.path.exists(IMAGE_PATH):
        print(f"[-] ERRO: Imagem {IMAGE_PATH} nao existe!")
        sys.exit(1)
        
    expected_md5 = compute_md5(IMAGE_PATH)
    file_size = os.path.getsize(IMAGE_PATH)
    mac_ip = get_mac_ip_for_router()
    
    print(f"  Tamanho: {file_size:,} bytes ({file_size/(1024*1024):.2f} MiB)")
    print(f"  MD5 Local: {expected_md5}")
    print(f"  IP de Origem (Mac): {mac_ip}")
    print("=" * 75)

    # 1. Iniciar servidor HTTP
    print("\n[Etapa 1/6] Iniciando servidor HTTP local...")
    server = start_http_server(mac_ip)
    print(f"    Servidor ativo em http://{mac_ip}:{HTTP_PORT}/rootfs.squashfs")

    # 2. Gravar imagem e script auto_flash no Slot 1
    print("\n[Etapa 2/6] Gravando imagem e auto_flash na particao de espera (Slot 1)...")
    prep_cmd = f"""
ubiattach /dev/ubi_ctrl -m 21 -d 1 2>/dev/null || true
mkdir -p /tmp/mnt1
mount -t ubifs /dev/ubi1_3 /tmp/mnt1 2>/dev/null || true
mkdir -p /tmp/mnt1/upper/root

echo "Baixando imagem..."
wget -O /tmp/mnt1/upper/rootfs.squashfs http://{mac_ip}:{HTTP_PORT}/rootfs.squashfs
cp -vf /tmp/mnt1/upper/rootfs.squashfs /tmp/mnt1/upper/root/rootfs.squashfs
md5sum /tmp/mnt1/upper/rootfs.squashfs

cat << 'EOF_FLASH' > /tmp/mnt1/upper/root/auto_flash.sh
#!/bin/sh
set -e
echo "=== INICIANDO GRAVACAO OFFLINE NO SLOT 2 ==="
echo "=== 1. Anexando Slot 2 (MTD20) ==="
ubidetach -m 20 2>/dev/null || true
ubiattach /dev/ubi_ctrl -m 20 -d 1

echo "=== 2. Verificando imagem local ==="
ls -lh /rootfs.squashfs
md5sum /rootfs.squashfs

echo "=== 3. Gravando Volume RootFS (ubi1_2) ==="
ubiupdatevol /dev/ubi1_2 /rootfs.squashfs
echo "[OK] Volume RootFS gravado com sucesso!"

echo "=== 4. Limpando Overlay do Slot 2 (ubi1_3) ==="
ubiupdatevol /dev/ubi1_3 -t
echo "[OK] Overlay limpo com padroes de fabrica!"

echo "=== 5. Validando Gravacao na Flash NAND ==="
ubiblock -c /dev/ubi1_2
mkdir -p /tmp/chk
mount -t squashfs /dev/ubiblock1_2 /tmp/chk
echo "Versao gravada:" $(cat /tmp/chk/etc/version 2>/dev/null || echo "ok")
grep "predator0100" /tmp/chk/etc/config/wireless | head -n 1
umount /tmp/chk
ubiblock -r /dev/ubi1_2
rm -rf /tmp/chk

echo "=== 6. Chaveando Boot de Volta para o Slot 2 ==="
echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null || true
mtd unlock /dev/mtd4 2>/dev/null || true
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync

echo "=== FLASH_COMPLETO_COM_SUCESSO ==="
reboot
EOF_FLASH
chmod +x /tmp/mnt1/upper/root/auto_flash.sh

sync
umount /tmp/mnt1 2>/dev/null || true
ubidetach -m 21 2>/dev/null || true
"""
    out_prep = telnet_run_cmd(prep_cmd, wait_after=2, timeout=60)
    print(f"Saida da preparacao no Slot 1:\n{out_prep.strip()}")
    server.shutdown()

    if expected_md5 not in out_prep:
        print("[-] ERRO: O checksum MD5 no roteador nao bate com o esperado!")
        sys.exit(1)
    print(f"[+] Integridade 100% confirmada no Slot 1! MD5: {expected_md5}")

    # 3. Comutar para Slot 1
    print("\n[Etapa 3/6] Comutando boot para o Slot 1 (OEM v24)...")
    telnet_run_cmd("/usr/sbin/boot-acer", wait_after=2, timeout=10)
    print("    Comando /usr/sbin/boot-acer enviado. Roteador reiniciando no Slot 1...")
    time.sleep(10)

    # 4. Aguardar Slot 1 subir
    print("\n[Etapa 4/6] Aguardando Slot 1 (OEM v24)...")
    ok, ver = wait_for_router(expected_version="000024", max_retries=65, retry_delay=3)
    if not ok:
        print(f"[-] Falha ao aguardar Slot 1: {ver}")
        sys.exit(1)
    print(f"[OK] Slot 1 ativo com sucesso! ({ver})")

    # 5. Disparar auto_flash no Slot 1
    print("\n[Etapa 5/6] Executando /root/auto_flash.sh no Slot 1...")
    flash_out = telnet_run_cmd("/root/auto_flash.sh", wait_after=5, timeout=120)
    print(f"Log do auto_flash:\n{flash_out}")

    if "FLASH_COMPLETO_COM_SUCESSO" not in flash_out and "Volume RootFS gravado com sucesso" not in flash_out:
        print("[-] ALERTA: A gravacao nao confirmou conclusao bem-sucedida!")
        sys.exit(1)

    print("[+] Gravacao no Slot 2 concluida com exito! Roteador reiniciando para o novo firmware...")
    time.sleep(10)

    # 6. Aguardar Slot 2 subir
    print("\n[Etapa 6/6] Aguardando o novo Slot 2 com o firmware recem-gravado...")
    ok, ver = wait_for_router(expected_version="000027", max_retries=75, retry_delay=3)
    if not ok:
        print(f"[-] Roteador demorou para responder: {ver}")
        sys.exit(1)

    print("\n" + "=" * 75)
    print("  🎉 FLASH REAL E BOOT LIMPO CONCLUÍDOS COM SUCESSO TOTAL!")
    print(f"  Versao ativa: {ver}")
    print(f"  IP LuCI: http://{ROUTER_IP}/")
    print("=" * 75)

if __name__ == "__main__":
    main()
