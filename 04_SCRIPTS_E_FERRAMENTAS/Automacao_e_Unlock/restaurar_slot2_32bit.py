#!/usr/bin/env python3
"""
Restaurador Seguro do Slot 2 (mtd20 / rootfs_1) em 32-bit (ARMv7l)
Acer Predator Connect T7 (Qualcomm IPQ5322 / IPQ5332)
"""

import telnetlib
import time

ROUTER_IP = "192.168.73.2"

RESTORE_SCRIPT = r"""cat << 'EOF' > /tmp/do_restore.sh
#!/bin/sh
set -e
echo "=========================================================="
echo "=== ETAPA 1: Anexando Slot 2 e criando nos UBI ==="
echo "=========================================================="
ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true

for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] || continue
    name=$(cat $v/name 2>/dev/null)
    dev=$(cat $v/dev 2>/dev/null)
    maj=$(echo $dev | cut -d: -f1)
    min=$(echo $dev | cut -d: -f2)
    bname=$(basename $v)
    mknod /dev/$bname c $maj $min 2>/dev/null || true
    echo "Node /dev/$bname ($name) -> $maj:$min"
done

echo ""
echo "=========================================================="
echo "=== ETAPA 2: Clonando Kernel FIT 32-bit ==="
echo "=========================================================="
k_sz=$(cat /sys/class/ubi/ubi0_1/data_bytes)
echo "Tamanho exato do Kernel: $k_sz bytes"
dd if=/dev/ubi0_1 of=/tmp/k32.fit bs=64k count=70 2>/dev/null
md5sum /tmp/k32.fit
ubiupdatevol /dev/ubi1_1 -s $k_sz /tmp/k32.fit
rm -f /tmp/k32.fit
echo "[OK] Kernel gravado no Slot 2 com sucesso!"

echo ""
echo "=========================================================="
echo "=== ETAPA 3: Clonando RootFS SquashFS ==="
echo "=========================================================="
r_sz=$(cat /sys/class/ubi/ubi0_2/data_bytes)
echo "Tamanho exato do RootFS: $r_sz bytes"
dd if=/dev/ubi0_2 of=/tmp/r32.squashfs bs=1M 2>/dev/null
md5sum /tmp/r32.squashfs
ubiupdatevol /dev/ubi1_2 -s $r_sz /tmp/r32.squashfs
rm -f /tmp/r32.squashfs
echo "[OK] RootFS gravado no Slot 2 com sucesso!"

echo ""
echo "=========================================================="
echo "=== ETAPA 4: Formatando Overlay do Slot 2 ==="
echo "=========================================================="
ubiupdatevol /dev/ubi1_3 -t
echo "[OK] Overlay do Slot 2 formatado limpo!"

echo ""
echo "=========================================================="
echo "=== ETAPA 5: Validando Volumes Finais ==="
echo "=========================================================="
for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] || continue
    echo "$(cat $v/name): $(cat $v/data_bytes) bytes"
done
sync
rm -f /tmp/do_restore.sh
echo ""
echo "=========================================================="
echo "=== [SUCESSO TOTAL] O SLOT 2 FOI RESTAURADO EM 32-BIT! ==="
echo "=========================================================="
EOF
chmod +x /tmp/do_restore.sh
/tmp/do_restore.sh
"""

def main():
    print("=" * 70)
    print("INICIANDO RESTAURAÇÃO DO SLOT 2 (mtd20) EM 32-BIT NATIVO")
    print("Acer Predator Connect T7 (IPQ5322)")
    print("=" * 70)

    print(f"[*] Conectando ao roteador em {ROUTER_IP} via Telnet...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
    tn.read_until(b"/ # ", timeout=5)

    print("[*] Enviando e executando script de restauração atômico...")
    tn.write(RESTORE_SCRIPT.encode("ascii") + b"\n")

    start_time = time.time()
    while True:
        line = tn.read_until(b"\n", timeout=120).decode("utf-8", errors="replace")
        if not line:
            break
        print(line, end="")
        if "=== [SUCESSO TOTAL]" in line or "/ # " in line and time.time() - start_time > 10:
            break

    tn.close()

if __name__ == "__main__":
    main()
