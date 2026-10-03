#!/usr/bin/env python3
"""
=============================================================================
TESTE DEFINITIVO DO KERNEL 6.18 ARM64 EM VOLUME ESTÁTICO (SLOT 2)
Acer Predator Connect T7 (IPQ5322)
=============================================================================
1. Executado a partir do Slot 1 (Acer Original).
2. Grava openwrt-predator-t7-kernel-618-final.fit no volume estático /dev/ubi1_1
   com o tamanho exato dos bytes para cálculo de CRC32 pelo UBI.
3. Formata /dev/ubi1_3 (overlay).
4. Grava marcador 0xDEADBEEF na RAM física (0x4CC00000).
5. Chaveia o bootconfig para o Slot 2 (primaryboot=0) e reinicia.
=============================================================================
"""

import http.server
import socketserver
import threading
import telnetlib
import time
import os
import hashlib
import sys

ROUTER_IP = "192.168.73.2"
PC_IP = "192.168.73.90"
HTTP_PORT = 8089

BASE_DIR = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7"
IMG_PATH = os.path.join(BASE_DIR, "1 - Firmware e Imagens OpenWrt", "openwrt-predator-t7-kernel-618-final.fit")

def get_md5(fpath):
    with open(fpath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def main():
    print("=" * 70)
    print("GRAVADOR DO KERNEL 6.18 ARM64 EM VOLUME ESTÁTICO")
    print("=" * 70)

    if not os.path.exists(IMG_PATH):
        print(f"[-] Arquivo não encontrado: {IMG_PATH}")
        return 1

    img_sz = os.path.getsize(IMG_PATH)
    img_md5 = get_md5(IMG_PATH)
    print(f"[*] Kernel 6.18 Final: {img_sz} bytes ({img_sz/(1024*1024):.2f} MB) | MD5: {img_md5}")

    # Iniciar servidor HTTP
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=os.path.dirname(IMG_PATH), **kwargs)
        def log_message(self, format, *args): pass

    server = socketserver.TCPServer((PC_IP, HTTP_PORT), Handler)
    server.allow_reuse_address = True
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()

    print(f"[*] Conectando ao roteador em {ROUTER_IP} via Telnet...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
    tn.read_until(b"/ # ", timeout=5)

    # Validar se estamos no Slot 1
    tn.write(b"cat /proc/boot_info/bootconfig0/rootfs/primaryboot\n")
    time.sleep(0.5)
    out_slot = tn.read_very_eager().decode("ascii", errors="ignore")
    lines = [l.strip() for l in out_slot.splitlines() if l.strip().isdigit()]
    cur_slot = lines[-1] if lines else "unknown"

    print(f"[*] Slot ativo no momento: primaryboot = {cur_slot}")
    if cur_slot != "1":
        print("[-] ERRO: O roteador DEVE estar no Slot 1 para gravar com segurança no Slot 2!")
        print("    Execute primeiro: python Scripts_Automacao/switch_boot_slot.py 1")
        tn.close()
        server.shutdown()
        return 1

    cmd_flash = f"""ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true
for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] || continue
    maj=$(cut -d: -f1 "$v/dev" 2>/dev/null)
    min=$(cut -d: -f2 "$v/dev" 2>/dev/null)
    bname=$(basename "$v")
    mknod /dev/$bname c $maj $min 2>/dev/null || true
done

# Baixar imagem
curl -fsSL http://{PC_IP}:{HTTP_PORT}/openwrt-predator-t7-kernel-618-final.fit -o /tmp/k618.fit
md5sum /tmp/k618.fit

# Gravar no volume estático
ubiupdatevol /dev/ubi1_1 -s {img_sz} /tmp/k618.fit
rm -f /tmp/k618.fit

# Formatar overlay
ubiupdatevol /dev/ubi1_3 -t

# Marcador na DRAM
devmem 0x4cc00000 32 0xdeadbeef
devmem 0x4cc00000 32

sync
ubidetach -m 20 2>/dev/null || true

# Chavear para Slot 2
echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync

echo "PRONTO_PARA_REBOOT"
"""

    print("[*] Enviando kernel 6.18 e gravando no volume estático do Slot 2...")
    for line in cmd_flash.strip().splitlines():
        tn.write(line.encode("ascii") + b"\n")
        time.sleep(0.3)

    out = tn.read_until(b"PRONTO_PARA_REBOOT", timeout=40).decode("ascii", errors="ignore")
    print(out)

    print("\n" + "=" * 70)
    print("[DISPARO] ENVIANDO REBOOT PARA O SLOT 2 COM KERNEL 6.18 ESTÁTICO...")
    print("=" * 70)
    tn.write(b"reboot\n")
    time.sleep(1)
    tn.close()
    server.shutdown()
    print("[OK] Roteador reiniciado no Slot 2 com o Kernel 6.18!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
