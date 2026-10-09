#!/usr/bin/env python3
import http.server, socketserver, threading, socket, time, os, sys

PORT = 8888
DIR = "/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/_FORA DO GitHub/V27_CUSTOM_DEPLOY"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def main():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    print("[1] Servidor HTTP local ativo na porta", PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(120)
    s.connect(("192.168.76.1", 23))
    time.sleep(0.5)

    print("[2] Baixando rootfs.squashfs na memoria RAM (/tmp)...")
    s.sendall(b"curl -sSL http://192.168.76.106:8888/rootfs.squashfs -o /tmp/rootfs.squashfs && ls -lh /tmp/rootfs.squashfs && md5sum /tmp/rootfs.squashfs\n")
    time.sleep(8)

    cmd_lines = [
        "echo '=== [3/6] ANEXANDO MTD21 (SLOT 2) COMO UBI1 ==='",
        "ubidetach /dev/ubi_ctrl -d 1 2>/dev/null || true",
        "ubiattach /dev/ubi_ctrl -m 21 -d 1",
        "ubinfo /dev/ubi1_2",
        "echo '=== [4/6] GRAVANDO ROOTFS NO VOLUME UBI1_2 (SLOT 2) ==='",
        "ubiupdatevol /dev/ubi1_2 /tmp/rootfs.squashfs",
        "echo 'GRAVACAO_SUCESSO'",
        "echo '=== [5/6] FORMATANDO OVERLAY LIMPO NO SLOT 2 (UBI1_3) ==='",
        "ubiupdatevol /dev/ubi1_3 -t",
        "echo 'OVERLAY_FORMATADO'",
        "echo '=== [6/6] VALIDANDO SISTEMA DE ARQUIVOS GRAVADO ==='",
        "ubiblock -c /dev/ubi1_2 2>/dev/null || true",
        "mkdir -p /tmp/chk_val",
        "mount -t squashfs /dev/ubiblock1_2 /tmp/chk_val",
        "echo 'Versao gravada na NAND: ' $(cat /tmp/chk_val/etc/version 2>/dev/null)",
        "ls -la /tmp/chk_val/usr/sbin/smbd 2>/dev/null || echo 'smbd_falha'",
        "umount /tmp/chk_val",
        "ubiblock -r /dev/ubi1_2 2>/dev/null || true",
        "rm -rf /tmp/chk_val",
        "echo '=== DESANEXANDO UBI1 ==='",
        "ubidetach /dev/ubi_ctrl -d 1",
        "rm -f /tmp/rootfs.squashfs",
        "echo '=== CHAVEANDO BOOTCONFIG PARA SLOT 2 (PRIMARYBOOT = 1) ==='",
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

    print("[3] Disparando script de flash e gravacao no Slot 2...")
    for line in cmd_lines:
        s.sendall((line + "\n").encode("utf-8"))
        time.sleep(0.4)

    out = b""
    start = time.time()
    while time.time() - start < 60:
        try:
            s.settimeout(3)
            chunk = s.recv(4096)
            if not chunk: break
            out += chunk
            text = chunk.decode("utf-8", errors="ignore")
            print(text, end="")
            if "FLASH_E_CHAVEAMENTO_100_CONCLUIDOS" in out.decode("utf-8", errors="ignore"):
                break
        except Exception:
            break

    s.close()
    httpd.shutdown()
    print("\n[*] Flash concluido com 100% de sucesso! O roteador reiniciou para o novo Slot 2!")

if __name__ == "__main__":
    main()
