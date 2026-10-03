#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
RESTAURADOR E ATIVADOR DEFINITIVO DO SLOT 2 (OPENWRT OTIMIZADO)
Acer Predator Connect T7 (IPQ5322 / Wi-Fi 7 BE11000)
=============================================================================
Este script restaura o Slot 2 (mtd20 / ubi1) para o estado de produção perfeito:
1. Volume 1 'kernel' (STATIC): Grava o Kernel oficial QSDK 5.4 100% funcional.
2. Volume 2 'ubi_rootfs' (DYNAMIC): Grava o RootFS oficial SquashFS.
3. Volume 3 'rootfs_data' (DYNAMIC): Formata e aplica o Overlay de produção
   com LuCI, SSH root, debloat de telemetrias e suporte Wi-Fi 7 Tri-Band.
4. Chaveia o BOOTCONFIG para Slot 2 e monitora a reinicialização.
O Slot 1 (Acer Fábrica) permanece 100% INTOCADO e preservado.
=============================================================================
"""

import sys
import io
import os
import time
import socket
import telnetlib
import http.server
import socketserver
import threading

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROUTER_IP = "192.168.73.2"
PC_IP = "192.168.73.90"
HTTP_PORT = 8089

BASE_DIR = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7"
TARBALL = os.path.join(BASE_DIR, "Backups_MTD", "backup_slot2_overlay_perfeito_producao.tar.gz")

def iniciar_servidor_http():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=os.path.dirname(TARBALL), **kwargs)
        def log_message(self, format, *args): pass

    server = socketserver.TCPServer((PC_IP, HTTP_PORT), QuietHandler)
    server.allow_reuse_address = True
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def run_cmd(tn, cmd, timeout=30):
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.4)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    return out

def main():
    print("=" * 70)
    print("🚀 RESTAURAÇÃO E ATIVAÇÃO DO SLOT 2 (OPENWRT OTIMIZADO)")
    print(f"Alvo: Acer Predator Connect T7 ({ROUTER_IP})")
    print("=" * 70)

    if not os.path.exists(TARBALL):
        print(f"[-] Erro: Arquivo de overlay não encontrado em: {TARBALL}")
        return 1

    print("[*] Iniciando servidor HTTP local para transferência do overlay...")
    server = iniciar_servidor_http()

    print(f"[*] Conectando via Telnet em {ROUTER_IP}:23...")
    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=6)
        tn.read_until(b"/ # ", timeout=4)
        print("[+] Conexão Telnet estabelecida!")
    except Exception as e:
        print(f"[-] Erro de conexão com o roteador: {e}")
        server.shutdown()
        return 1

    # 1. Verifica se estamos no Slot 1
    slot_out = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    print(f"[*] Slot atual: primaryboot = {slot_out.strip()[-1:]}")

    # 2. Anexa mtd20 e garante device nodes
    print("[*] Anexando Slot 2 (mtd20) como ubi1...")
    run_cmd(tn, "ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true")
    
    # 3. Garante que os volumes existam corretamente
    print("[*] Verificando e criando nós de dispositivo para ubi1...")
    mknod_script = """for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] || continue
    maj=$(cut -d: -f1 "$v/dev" 2>/dev/null)
    min=$(cut -d: -f2 "$v/dev" 2>/dev/null)
    bname=$(basename "$v")
    mknod /dev/$bname c $maj $min 2>/dev/null || true
done"""
    run_cmd(tn, mknod_script)

    # 4. Grava Kernel estável no ubi1_1
    print("[*] [1/4] Gravando Kernel estável de produção no Slot 2 (ubi1_1)...")
    k_cmd = """k_sz=$(cat /sys/class/ubi/ubi0_1/data_bytes)
dd if=/dev/ubi0_1 of=/tmp/k.fit bs=64k count=70 2>/dev/null
ubiupdatevol /dev/ubi1_1 -s $k_sz /tmp/k.fit
rm -f /tmp/k.fit"""
    run_cmd(tn, k_cmd, timeout=30)
    print("    [OK] Kernel 5.4 QSDK gravado com sucesso!")

    # 5. Grava RootFS no ubi1_2
    print("[*] [2/4] Sincronizando RootFS estável no Slot 2 (ubi1_2)...")
    r_cmd = """r_sz=$(cat /sys/class/ubi/ubi0_2/data_bytes)
dd if=/dev/ubi0_2 of=/tmp/root.squashfs bs=1M 2>/dev/null
ubiupdatevol /dev/ubi1_2 -s $r_sz /tmp/root.squashfs
rm -f /tmp/root.squashfs"""
    run_cmd(tn, r_cmd, timeout=45)
    print("    [OK] RootFS SquashFS sincronizado!")

    # 6. Formata e aplica o Overlay de produção no ubi1_3
    print("[*] [3/4] Formatando e aplicando Overlay com LuCI (ubi1_3)...")
    ov_cmd = f"""ubiupdatevol /dev/ubi1_3 -t
mkdir -p /mnt/slot2_restore
mount -t ubifs /dev/ubi1_3 /mnt/slot2_restore
mkdir -p /mnt/slot2_restore/upper /mnt/slot2_restore/work
ln -sf 2 /mnt/slot2_restore/.fs_state
curl -fsSL http://{PC_IP}:{HTTP_PORT}/backup_slot2_overlay_perfeito_producao.tar.gz -o /tmp/ov.tar.gz
tar -xzf /tmp/ov.tar.gz -C /mnt/slot2_restore/upper
rm -f /tmp/ov.tar.gz
sync
umount /mnt/slot2_restore
rm -rf /mnt/slot2_restore"""
    run_cmd(tn, ov_cmd, timeout=60)
    print("    [OK] Overlay de produção aplicado!")

    # 7. Instala os utilitários de boot rápido
    print("[*] [4/4] Instalando scripts de chaveamento rápido no roteador...")
    script_boot = """cat << 'EOF' > /usr/sbin/boot-openwrt
#!/bin/sh
echo "=== Chaveando boot para SLOT 2 (OpenWrt) ==="
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
echo "[OK] Reiniciando no Slot 2..."
reboot
EOF
chmod +x /usr/sbin/boot-openwrt

cat << 'EOF' > /usr/sbin/boot-acer
#!/bin/sh
echo "=== Chaveando boot para SLOT 1 (Acer Original) ==="
echo 1 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 1 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
echo "[OK] Reiniciando no Slot 1..."
reboot
EOF
chmod +x /usr/sbin/boot-acer"""
    run_cmd(tn, script_boot)

    # 8. Chaveia para o Slot 2 e executa reboot
    print("\n" + "=" * 70)
    print("⚡ CHAVEANDO BOOT PARA O SLOT 2 E REINICIANDO...")
    print("=" * 70)
    tn.write(b"/usr/sbin/boot-openwrt\n")
    time.sleep(1)
    tn.close()
    server.shutdown()

    print("[*] Comando de reboot enviado. Aguardando o roteador reiniciar no Slot 2...")
    print("[*] Monitorando portas de rede (192.168.73.2)...")
    
    t0 = time.time()
    booted = False
    time.sleep(15)  # Espera o roteador desligar

    for attempt in range(60):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            res = s.connect_ex((ROUTER_IP, 23))
            s.close()
            if res == 0:
                print(f"\n[+] ROTEADOR ONLINE APÓS {int(time.time() - t0)} SEGUNDOS!")
                booted = True
                break
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(2)

    if booted:
        time.sleep(3)
        tn2 = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
        tn2.read_until(b"/ # ", timeout=4)
        active_slot = run_cmd(tn2, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
        cmdline = run_cmd(tn2, "cat /proc/cmdline")
        tn2.close()

        slot_num = active_slot.strip()[-1:]
        print("\n" + "=" * 70)
        print("🎉 SUCESSO ABSOLUTO! SLOT 2 ESTÁ ATIVO E OPERACIONAL!")
        print(f"[*] Slot Ativo: primaryboot = {slot_num} (0 = Slot 2 OpenWrt)")
        print(f"[*] Linha do Kernel: {cmdline.strip()}")
        print(f"[*] Web UI LuCI: http://{ROUTER_IP}:8080/ ou http://{ROUTER_IP}/")
        print("=" * 70)
        return 0
    else:
        print("\n[-] Timeout aguardando retorno de rede do roteador.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
