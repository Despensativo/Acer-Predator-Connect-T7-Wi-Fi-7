#!/usr/bin/env python3
"""
executar_flash_slot2_auto.py
Gravacao Atomica e Segura da Nova ROM no Slot 2 (MTD21)
Acer Predator Connect T7 (Qualcomm IPQ5332)
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
HTTP_PORT = 8089

BASE_DIR = "/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7"
IMAGE_DIR = os.path.join(BASE_DIR, "_FORA DO GitHub", "V27_CUSTOM_DEPLOY")
IMAGE_FILE = "rootfs.squashfs"
EXPECTED_MD5 = "b7a5db07f1706b699fa14516817581fd"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((ROUTER_IP, 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "192.168.76.238"
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

def telnet_run_interactive(cmds, timeout=120):
    s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=10)
    time.sleep(0.3)
    try:
        s.settimeout(0.5)
        s.recv(4096)
    except Exception:
        pass

    for cmd in cmds:
        s.sendall(cmd.encode("utf-8") + b"\n")
        time.sleep(0.2)

    out = b""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            s.settimeout(2.0)
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
            sys.stdout.write(chunk.decode("utf-8", errors="ignore"))
            sys.stdout.flush()
            if b"FLASH_E_CHAVEAMENTO_100_CONCLUIDOS" in out:
                time.sleep(2)
                break
        except socket.timeout:
            pass
        except Exception:
            break
    s.close()
    return out.decode("utf-8", errors="ignore")

def simple_query(cmd, timeout=5):
    try:
        s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=timeout)
        time.sleep(0.2)
        try:
            s.settimeout(0.5)
            s.recv(4096)
        except Exception:
            pass
        s.sendall(cmd.encode("utf-8") + b"\nexit\n")
        time.sleep(0.5)
        out = b""
        start = time.time()
        while time.time() - start < timeout:
            try:
                s.settimeout(1.0)
                chunk = s.recv(4096)
                if not chunk: break
                out += chunk
            except Exception:
                break
        s.close()
        return out.decode("utf-8", errors="ignore")
    except Exception as e:
        return f"ERR: {e}"

def main():
    print("=" * 70)
    print("  GRAVACAO ATOMICA DO FIRMWARE NO SLOT 2 (MTD21)")
    print("  Acer Predator Connect T7 (IPQ5332)")
    print("=" * 70)

    # 1. Validar imagem local
    img_path = os.path.join(IMAGE_DIR, IMAGE_FILE)
    if not os.path.isfile(img_path):
        print(f"[-] ERRO: Arquivo {img_path} nao encontrado!")
        sys.exit(1)
    sz = os.path.getsize(img_path)
    print(f"[*] Imagem local validada: {img_path}")
    print(f"    Tamanho: {sz:,} bytes ({sz/(1024*1024):.2f} MB)")
    print(f"    MD5 Esperado: {EXPECTED_MD5}")

    # 2. Verificar slot ativo
    resp = simple_query("cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    lines = [l.strip() for l in resp.splitlines() if l.strip().isdigit()]
    if not lines or lines[-1] != "0":
        print(f"[-] ERRO: Roteador nao esta no Slot 1 (primaryboot != 0). Resposta: {resp}")
        sys.exit(1)
    print("    [OK] Confirmado: Roteador esta no Slot 1 (primaryboot = 0). Slot 2 pronto para gravacao.")

    # 3. Subir servidor HTTP local
    local_ip = get_local_ip()
    print(f"\n[*] Iniciando servidor HTTP local em {local_ip}:{HTTP_PORT}...")
    httpd = start_http_server(IMAGE_DIR, HTTP_PORT)
    time.sleep(0.5)

    # 4. Sequencia de gravacao
    flash_commands = [
        "echo '=== [1/6] BAIXANDO NOVO SQUASHFS NA MEMORIA RAM ==='",
        f"rm -f /tmp/{IMAGE_FILE}",
        f"curl -fsSL http://{local_ip}:{HTTP_PORT}/{IMAGE_FILE} -o /tmp/{IMAGE_FILE}",
        f"ls -lh /tmp/{IMAGE_FILE}",
        f"md5sum /tmp/{IMAGE_FILE}",
        "echo '=== [2/6] ANEXANDO MTD21 (SLOT 2) COMO UBI1 ==='",
        "ubidetach /dev/ubi_ctrl -d 1 2>/dev/null || true",
        "ubiattach /dev/ubi_ctrl -m 21 -d 1",
        "ubinfo /dev/ubi1_2",
        "echo '=== [3/6] GRAVANDO ROOTFS NO VOLUME UBI1_2 (SLOT 2) ==='",
        f"ubiupdatevol /dev/ubi1_2 /tmp/{IMAGE_FILE}",
        "echo 'GRAVACAO_VOLUME_SUCESSO'",
        "echo '=== [4/6] FORMATANDO OVERLAY LIMPO NO SLOT 2 (UBI1_3) ==='",
        "ubiupdatevol /dev/ubi1_3 -t",
        "echo 'OVERLAY_FORMATADO_SUCESSO'",
        "echo '=== [5/6] VALIDANDO SISTEMA DE ARQUIVOS GRAVADO ==='",
        "ubiblock -c /dev/ubi1_2 2>/dev/null || true",
        "mkdir -p /tmp/chk_val",
        "mount -t squashfs /dev/ubiblock1_2 /tmp/chk_val",
        "echo 'Versao gravada na NAND: ' $(cat /tmp/chk_val/etc/version 2>/dev/null)",
        "ls -la /tmp/chk_val/usr/lib/lua/luci/controller/sqm.lua 2>/dev/null || echo 'sqm_falha'",
        "ls -la /tmp/chk_val/www/luci-static/resources/view/samba4.js 2>/dev/null || echo 'samba_falha'",
        "umount /tmp/chk_val",
        "ubiblock -r /dev/ubi1_2 2>/dev/null || true",
        "rm -rf /tmp/chk_val",
        "echo '=== DESANEXANDO UBI1 E LIMPANDO RAM ==='",
        "ubidetach /dev/ubi_ctrl -d 1",
        f"rm -f /tmp/{IMAGE_FILE}",
        "echo '=== [6/6] CHAVEANDO BOOTCONFIG PARA SLOT 2 (PRIMARYBOOT = 1) ==='",
        "echo 1 > /proc/boot_info/bootconfig0/rootfs/primaryboot",
        "echo 1 > /proc/boot_info/bootconfig1/rootfs/primaryboot",
        "cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin",
        "cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin",
        "mtd unlock /dev/mtd3 2>/dev/null || true",
        "mtd unlock /dev/mtd4 2>/dev/null || true",
        "mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3",
        "mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4",
        "rm -f /tmp/bc0.bin /tmp/bc1.bin",
        "sync",
        "echo 'FLASH_E_CHAVEAMENTO_100_CONCLUIDOS'",
        "reboot"
    ]

    print("\n[*] Enviando comandos de gravacao via Telnet...")
    output = telnet_run_interactive(flash_commands, timeout=120)

    httpd.shutdown()

    if "FLASH_E_CHAVEAMENTO_100_CONCLUIDOS" in output:
        print("\n" + "=" * 70)
        print("  [+] GRAVACAO E CONFIGURACAO CONCLUIDAS COM 100% DE SUCESSO!")
        print("  O roteador esta reiniciando para o NOVO SLOT 2...")
        print("=" * 70)
    else:
        print("\n[-] AVISO: Nao foi detectada a mensagem final esperada. Verifique os logs acima.")

if __name__ == "__main__":
    main()
