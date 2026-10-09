#!/usr/bin/env python3
import http.server
import os
import socket
import socketserver
import sys
import threading
import time

ROUTER_IP = "192.168.76.1"
TELNET_PORT = 23
HTTP_PORT = 8089

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, "_FORA DO GitHub", "V27_CUSTOM_DEPLOY")
IMAGE_FILE = "rootfs.squashfs"
SCRIPT_FILE = "do_flash.sh"
EXPECTED_MD5 = "b7a5db07f1706b699fa14516817581fd"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((ROUTER_IP, 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "192.168.76.106"
    finally:
        s.close()
    return ip

def start_http_server(directory, port):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        def log_message(self, format, *args):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("0.0.0.0", port), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def run_telnet_interactive(cmd_to_send, timeout=180):
    s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=5)
    time.sleep(0.3)
    try:
        s.settimeout(0.5)
        s.recv(4096)
    except Exception:
        pass

    s.sendall(cmd_to_send.encode("utf-8") + b"\n")
    out = b""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            s.settimeout(3.0)
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
            sys.stdout.write(chunk.decode("utf-8", errors="ignore"))
            sys.stdout.flush()
            if b"=== FLASH_E_CONFIGURACAO_CONCLUIDOS_COM_SUCESSO ===" in out:
                time.sleep(2)
                break
        except socket.timeout:
            pass
        except Exception:
            break
    s.close()
    return out.decode("utf-8", errors="ignore")

def simple_telnet_query(cmd, timeout=5):
    try:
        s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=2)
        time.sleep(0.2)
        try:
            s.settimeout(0.5)
            s.recv(4096)
        except Exception:
            pass
        s.sendall(cmd.encode("utf-8") + b"\n")
        time.sleep(0.5)
        resp = s.recv(4096).decode("utf-8", errors="ignore")
        s.close()
        return resp
    except Exception as e:
        return f"ERR: {e}"

def wait_for_slot(expected_primary="0", max_retries=60, retry_delay=3):
    print(f"\n[*] Aguardando roteador reiniciar no Slot {expected_primary}...")
    for i in range(max_retries):
        try:
            resp = simple_telnet_query("cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
            lines = [l.strip() for l in resp.splitlines() if l.strip().isdigit()]
            if lines and lines[-1] == expected_primary:
                print(f"    [+] Roteador online e ativo no Slot {expected_primary}!")
                return True
        except Exception:
            pass
        time.sleep(retry_delay)
        if (i + 1) % 5 == 0:
            print(f"    ... aguardando inicializacao ({(i+1)*retry_delay}s decorridos)")
    return False

def main():
    print("=" * 70)
    print("  GRAVACAO REAL E ATOMICA DO FIRMWARE NO SLOT 2 (NAND MTD20)")
    print("  Acer Predator Connect T7 (IPQ5332)")
    print("=" * 70)

    # 1. Checar imagem local
    full_image_path = os.path.join(IMAGE_DIR, IMAGE_FILE)
    file_sz = os.path.getsize(full_image_path)
    print(f"[*] Imagem local validada: {full_image_path}")
    print(f"    Tamanho: {file_sz:,} bytes ({file_sz/(1024*1024):.2f} MB)")
    print(f"    MD5 Esperado: {EXPECTED_MD5}")

    # 2. Verificar conexão e Slot atual
    slot_resp = simple_telnet_query("cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    lines = [l.strip() for l in slot_resp.splitlines() if l.strip().isdigit()]
    if not lines or lines[-1] != "1":
        print(f"[-] ERRO: Roteador nao esta no Slot 1! Retorno: {slot_resp}")
        sys.exit(1)
    print("    [OK] Confirmado: Roteador esta no Slot 1 (primaryboot = 1).")

    # 3. Subir HTTP local
    local_ip = get_local_ip()
    print(f"\n[*] Subindo servidor HTTP local em {local_ip}:{HTTP_PORT}...")
    httpd = start_http_server(IMAGE_DIR, HTTP_PORT)
    time.sleep(0.5)

    # 4. Baixar imagem e script no /tmp do roteador
    print("\n[*] Baixando imagem e script de gravacao no /tmp do roteador...")
    simple_telnet_query("ubidetach -m 20 2>/dev/null || true")
    simple_telnet_query(f"curl -fsSL http://{local_ip}:{HTTP_PORT}/{SCRIPT_FILE} -o /tmp/{SCRIPT_FILE} && chmod +x /tmp/{SCRIPT_FILE}")
    simple_telnet_query(f"[ -f /tmp/{IMAGE_FILE} ] || curl -fsSL http://{local_ip}:{HTTP_PORT}/{IMAGE_FILE} -o /tmp/{IMAGE_FILE}")

    # 5. Conferir MD5 no roteador
    md5_out = simple_telnet_query(f"md5sum /tmp/{IMAGE_FILE}")
    print(f"    MD5 remoto: {md5_out.strip()}")
    if EXPECTED_MD5 not in md5_out:
        print("[-] MD5 divergente! Baixando novamente...")
        simple_telnet_query(f"curl -fsSL http://{local_ip}:{HTTP_PORT}/{IMAGE_FILE} -o /tmp/{IMAGE_FILE}")
        md5_out = simple_telnet_query(f"md5sum /tmp/{IMAGE_FILE}")
        if EXPECTED_MD5 not in md5_out:
            print("[-] ERRO FATAL: MD5 divergente no roteador!")
            httpd.shutdown()
            sys.exit(1)

    print("    [OK] Hash MD5 confirmado 100%!")
    httpd.shutdown()

    # 6. Executar gravacao completa via /tmp/do_flash.sh
    print("\n[*] Disparando script de gravacao da NAND (/tmp/do_flash.sh)...")
    print("-" * 70)
    out = run_telnet_interactive("sh /tmp/do_flash.sh", timeout=180)
    print("\n" + "-" * 70)

    if "FLASH_E_CONFIGURACAO_CONCLUIDOS_COM_SUCESSO" not in out:
        print("[-] ERRO: A gravacao nao confirmou sucesso!")
        sys.exit(1)

    print("\n[+] Gravacao na NAND concluida com exito!")
    time.sleep(10)

    # 7. Aguardar Slot 2 subir
    ok = wait_for_slot(expected_primary="0", max_retries=60, retry_delay=3)
    if not ok:
        print("[-] Falha ao aguardar o Slot 0.")
        sys.exit(1)

    # 8. Validar Slot 2 vivo
    ver = simple_telnet_query("cat /etc/version").strip()
    ovl = simple_telnet_query("df -h /overlay").strip()

    print("\n" + "=" * 70)
    print("  🎉 FLASH REAL, GRAVACAO NA NAND E BOOT NO SLOT 2 CONCLUIDOS!")
    print(f"  Versao ativa: {ver}")
    print(f"  Status Overlay:\n{ovl}")
    print(f"  IP LuCI: http://{ROUTER_IP}/")
    print("=" * 70)

if __name__ == "__main__":
    main()
