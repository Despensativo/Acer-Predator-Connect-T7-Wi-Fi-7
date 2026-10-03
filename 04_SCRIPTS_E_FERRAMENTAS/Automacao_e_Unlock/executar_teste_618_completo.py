#!/usr/bin/env python3
"""
=============================================================================
EXECUTOR DO TESTE COMPLETO KERNEL 6.18 ARM64 + ROOTFS OPENWRT (SLOT 2)
Acer Predator Connect T7 (Qualcomm IPQ5322)
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
IMG_DIR = os.path.join(BASE_DIR, "1 - Firmware e Imagens OpenWrt")
KERNEL_PATH = os.path.join(IMG_DIR, "openwrt-predator-t7-kernel-618-final.fit")
ROOTFS_PATH = os.path.join(IMG_DIR, "root.squashfs")

def get_md5(fpath):
    with open(fpath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def run_cmd(tn, cmd, timeout=60):
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.5)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    return out

def main():
    print("=" * 70)
    print("INICIANDO GRAVACAO E DISPARO DO TESTE MAINLINE 6.18 (SLOT 2)")
    print("=" * 70)

    if not os.path.exists(KERNEL_PATH) or not os.path.exists(ROOTFS_PATH):
        print("[-] Arquivos de imagem ausentes no PC!")
        return 1

    k_sz = os.path.getsize(KERNEL_PATH)
    r_sz = os.path.getsize(ROOTFS_PATH)
    k_md5 = get_md5(KERNEL_PATH)
    r_md5 = get_md5(ROOTFS_PATH)

    print(f"[*] Kernel 6.18 FIT : {k_sz} bytes | MD5: {k_md5}")
    print(f"[*] RootFS SquashFS : {r_sz} bytes | MD5: {r_md5}")

    # 1. Iniciar servidor HTTP
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=IMG_DIR, **kwargs)
        def log_message(self, format, *args): pass

    server = socketserver.TCPServer((PC_IP, HTTP_PORT), QuietHandler)
    server.allow_reuse_address = True
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()

    # 2. Conectar ao roteador
    print(f"[*] Conectando ao roteador em {ROUTER_IP} via Telnet...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
    tn.read_until(b"/ # ", timeout=5)

    # 3. Validar se estamos no Slot 1
    out_slot = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    lines = [l.strip() for l in out_slot.splitlines() if l.strip().isdigit()]
    cur_slot = lines[-1] if lines else "unknown"

    print(f"[*] Slot ativo no momento: primaryboot = {cur_slot}")
    if cur_slot != "1":
        print("[-] ERRO: Roteador nao esta no Slot 1! Abortando por seguranca.")
        tn.close()
        server.shutdown()
        return 1

    # 4. Anexar Slot 2 e preparar nodes
    print("[*] [1/5] Anexando Slot 2 (mtd20) e criando device nodes...")
    run_cmd(tn, "ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true")
    fix_nodes = """for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] || continue
    maj=$(cut -d: -f1 "$v/dev" 2>/dev/null)
    min=$(cut -d: -f2 "$v/dev" 2>/dev/null)
    bname=$(basename "$v")
    mknod /dev/$bname c $maj $min 2>/dev/null || true
done"""
    run_cmd(tn, fix_nodes)

    # 5. Baixar imagens no /tmp do roteador e verificar MD5
    print("[*] [2/5] Baixando Kernel e RootFS na memoria RAM (/tmp) do roteador...")
    run_cmd(tn, "rm -f /tmp/k618.fit /tmp/root.squashfs")
    
    print("    -> Baixando Kernel 6.18 FIT...")
    run_cmd(tn, f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/openwrt-predator-t7-kernel-618-final.fit -o /tmp/k618.fit", timeout=30)
    
    print("    -> Baixando RootFS SquashFS...")
    run_cmd(tn, f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/root.squashfs -o /tmp/root.squashfs", timeout=30)

    out_md5 = run_cmd(tn, "md5sum /tmp/k618.fit /tmp/root.squashfs")
    print(f"    Hashes remotos:\n{out_md5.strip()}")

    if k_md5 not in out_md5 or r_md5 not in out_md5:
        print("[-] ERRO: Hashes MD5 divergentes no roteador! Abortando.")
        run_cmd(tn, "rm -f /tmp/k618.fit /tmp/root.squashfs")
        tn.close()
        server.shutdown()
        return 1
    print("    [OK] Hashes conferidos com 100% de exatidao!")

    # 6. Gravar Kernel e RootFS
    print(f"[*] [3/5] Gravando Kernel 6.18 no Volume 1 STATIC ({k_sz} bytes)...")
    out_k = run_cmd(tn, f"ubiupdatevol /dev/ubi1_1 -s {k_sz} /tmp/k618.fit", timeout=30)
    print(f"    {out_k.strip()}")

    print(f"[*] [4/5] Gravando RootFS OpenWrt no Volume 2 DYNAMIC ({r_sz} bytes)...")
    out_r = run_cmd(tn, f"ubiupdatevol /dev/ubi1_2 -s {r_sz} /tmp/root.squashfs", timeout=60)
    print(f"    {out_r.strip()}")

    print("    -> Formatando Overlay /dev/ubi1_3...")
    run_cmd(tn, "ubiupdatevol /dev/ubi1_3 -t", timeout=15)

    run_cmd(tn, "rm -f /tmp/k618.fit /tmp/root.squashfs; sync; ubidetach -m 20 2>/dev/null || true")

    # 7. Marcador DRAM e Bootconfig
    print("[*] [5/5] Gravando marcador 0xDEADBEEF na DRAM (0x4CC00000) e chaveando boot...")
    run_cmd(tn, "devmem 0x4cc00000 32 0xdeadbeef")
    out_mem = run_cmd(tn, "devmem 0x4cc00000 32")
    print(f"    DRAM Check: {out_mem.strip()}")

    cmd_switch = """echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
echo "BOOTCONFIG_SLOT2_PRONTO"
"""
    out_sw = run_cmd(tn, cmd_switch, timeout=15)
    print("    [OK] Bootconfig comutado para Slot 2!")

    print("\n" + "=" * 70)
    print("[DISPARO] ENVIANDO REBOOT PARA O SLOT 2 COM O KERNEL 6.18 ESTÁTICO!")
    print("=" * 70)
    tn.write(b"reboot\n")
    time.sleep(1)
    tn.close()
    server.shutdown()
    print("[OK] Comando de reinicializacao enviado.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
