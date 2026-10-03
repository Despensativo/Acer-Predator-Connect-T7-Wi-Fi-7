#!/usr/bin/env python3
"""
Utilitario de Chaveamento Dual-Boot: Alterna entre Slot 1 (Acer) e Slot 2 (OpenWrt)
Acer Predator Connect T7 (Qualcomm IPQ5332)
"""

import telnetlib
import sys
import time

ROUTER_IP = "192.168.73.2"

def run_cmd(tn, cmd, timeout=10):
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.5)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    return out

def get_current_slot(tn):
    out = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    lines = [l.strip() for l in out.strip().split("\n") if l.strip() and not l.startswith("cat ") and not l.startswith("/ #")]
    val = lines[-1] if lines else "1"
    return "Slot 1 (Acer Original)" if val == "1" else "Slot 2 (OpenWrt Puro)"

def install_helper_scripts(tn):
    # Script para ir para o OpenWrt
    script_openwrt = """cat << 'EOF' > /usr/sbin/boot-openwrt
#!/bin/sh
echo "=== Chaveando boot para SLOT 2 (OpenWrt Puro) ==="
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
echo "[OK] Ponteiro gravado com sucesso! Reiniciando no OpenWrt..."
reboot
EOF
chmod +x /usr/sbin/boot-openwrt
"""
    # Script para voltar para a Acer
    script_acer = """cat << 'EOF' > /usr/sbin/boot-acer
#!/bin/sh
echo "=== Chaveando boot de volta para SLOT 1 (Acer Original) ==="
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
echo "[OK] Ponteiro gravado com sucesso! Reiniciando na Acer..."
reboot
EOF
chmod +x /usr/sbin/boot-acer
"""
    run_cmd(tn, script_openwrt)
    run_cmd(tn, script_acer)

def main():
    target_slot = sys.argv[1] if len(sys.argv) > 1 else None

    print("=" * 65)
    print("GERENCIADOR DE DUAL-BOOT - ACER PREDATOR CONNECT T7")
    print("=" * 65)

    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
    tn.read_until(b"/ # ", timeout=5)

    cur = get_current_slot(tn)
    print(f"[*] Slot ativo atualmente configurado no BOOTCONFIG: {cur}")

    install_helper_scripts(tn)
    print("[*] Comandos rapidos instalados no roteador:")
    print("    - 'boot-openwrt' -> Inicia no OpenWrt puro (Slot 2)")
    print("    - 'boot-acer'    -> Inicia no sistema Acer original (Slot 1)")

    if target_slot == "openwrt" or target_slot == "2":
        print("\n[*] Aplicando chaveamento para SLOT 2 (OpenWrt Puro)...")
        out = run_cmd(tn, "/usr/sbin/boot-openwrt")
        print(out)
    elif target_slot == "acer" or target_slot == "1":
        print("\n[*] Aplicando chaveamento para SLOT 1 (Acer Original)...")
        out = run_cmd(tn, "/usr/sbin/boot-acer")
        print(out)
    else:
        print("\nUso para alternar imediatamente:")
        print("  python switch_boot_slot.py 2   (para reiniciar no OpenWrt)")
        print("  python switch_boot_slot.py 1   (para reiniciar na Acer)")

    tn.close()

if __name__ == "__main__":
    main()
