#!/usr/bin/env python3
"""
=============================================================================
CORRETOR DE LAYOUT UBI E RESTAURADOR DEFINITIVO DO SLOT 2
Acer Predator Connect T7 (IPQ5322)
=============================================================================
Corrige o formato de instalacao do Slot 2 (mtd20 / ubi1):
- Volume 1 'kernel' como STATIC (25 LEBs / 6348800 bytes) com data_bytes=4238664
- Volume 2 'ubi_rootfs' como DYNAMIC (157 LEBs / 39870464 bytes)
- Volume 3 'rootfs_data' como DYNAMIC (690 LEBs / resto da memoria)
Exatamente como a Qualcomm e a Acer definiram no Slot 1!
=============================================================================
"""

import telnetlib
import time
import sys

ROUTER_IP = "192.168.73.2"

SCRIPT = r"""cat << 'EOF' > /tmp/fix_slot2.sh
#!/bin/sh
set -e

echo "=== [1/6] Anexando Slot 2 (mtd20) ==="
ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true

echo "=== [2/6] Removendo volumes com formato incorreto (1, 2, 3) ==="
ubirmvol /dev/ubi1 -n 3 2>/dev/null || true
ubirmvol /dev/ubi1 -n 2 2>/dev/null || true
ubirmvol /dev/ubi1 -n 1 2>/dev/null || true

echo "=== [3/6] Recriando volumes com a especificacao exata de fabrica ==="
# Volume 1: KERNEL DEVE SER STATIC para o bootipq do U-Boot!
ubimkvol /dev/ubi1 -n 1 -N kernel -s 6348800 -t static
# Volume 2: ubi_rootfs (SquashFS 38 MB)
ubimkvol /dev/ubi1 -n 2 -N ubi_rootfs -s 39870464
# Volume 3: rootfs_data (Overlay UBIFS restante)
ubimkvol /dev/ubi1 -n 3 -N rootfs_data -m

echo "=== [4/6] Garantindo device nodes ==="
for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] || continue
    maj=$(cut -d: -f1 "$v/dev" 2>/dev/null)
    min=$(cut -d: -f2 "$v/dev" 2>/dev/null)
    bname=$(basename "$v")
    mknod /dev/$bname c $maj $min 2>/dev/null || true
done

echo "=== [5/6] Gravando Kernel FIT no Volume STATIC ==="
k_sz=$(cat /sys/class/ubi/ubi0_1/data_bytes)
dd if=/dev/ubi0_1 of=/tmp/k.fit bs=64k count=70 2>/dev/null
ubiupdatevol /dev/ubi1_1 -s $k_sz /tmp/k.fit
rm -f /tmp/k.fit

echo "=== [6/6] Gravando RootFS e Formatando Overlay ==="
r_sz=$(cat /sys/class/ubi/ubi0_2/data_bytes)
dd if=/dev/ubi0_2 of=/tmp/root.squashfs bs=1M 2>/dev/null
ubiupdatevol /dev/ubi1_2 -s $r_sz /tmp/root.squashfs
rm -f /tmp/root.squashfs
ubiupdatevol /dev/ubi1_3 -t

sync
rm -f /tmp/fix_slot2.sh
echo "=== LAYOUT_SLOT2_CORRIGIDO_COM_SUCESSO ==="
EOF
chmod +x /tmp/fix_slot2.sh
/bin/sh /tmp/fix_slot2.sh
"""

def main():
    print("=" * 70)
    print("APLICANDO CORREÇÃO DO FORMATO DE PARTIÇÃO DO SLOT 2")
    print("Alvo: Acer Predator Connect T7 (192.168.73.2)")
    print("=" * 70)

    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
    tn.read_until(b"/ # ", timeout=5)

    print("[*] Enviando script de reestruturação do UBI...")
    tn.write(SCRIPT.encode("ascii") + b"\n")

    t0 = time.time()
    while time.time() - t0 < 120:
        line = tn.read_until(b"\n", timeout=10).decode("utf-8", errors="replace")
        if not line:
            break
        print(line, end="")
        if "=== LAYOUT_SLOT2_CORRIGIDO_COM_SUCESSO ===" in line:
            print("\n[+] SUCESSO! O layout foi reconstruído exatamente como o de fábrica!")
            break

    tn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
