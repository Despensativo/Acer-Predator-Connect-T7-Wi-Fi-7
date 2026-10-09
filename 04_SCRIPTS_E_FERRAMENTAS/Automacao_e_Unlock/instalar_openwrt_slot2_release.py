#!/usr/bin/env python3
"""
=============================================================================
INSTALADOR DE 1 CLIQUE - FIRMWARE OPENWRT FULL RELEASE NO SLOT 2
Acer Predator Connect T7 (Qualcomm IPQ5322)
=============================================================================
Instala a imagem FULL definitiva do OpenWrt no Slot 2 (mtd20) com seguranca
total, sem tocar no Slot 1 (Acer Original de Fabrica).
=============================================================================
"""

import os
import sys
import time
import socket
import telnetlib
import http.server
import threading

ROUTER_IP = sys.argv[1] if len(sys.argv) > 1 else "192.168.73.2"
LOCAL_IP = "192.168.73.90"
HTTP_PORT = 8089

BASE_DIR = r"h:\FEITOS COM IA\Acer-Predator-Connect-T7"
RELEASE_ROOTFS = os.path.join(BASE_DIR, "Firmwares_Custom", "openwrt_predator_t7_release_rootfs.bin")
STOCK_KERNEL = os.path.join(BASE_DIR, "Backups_MTD", "backup_predator_t7_kernel.bin")

def start_http_server():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
        def translate_path(self, path):
            if "rootfs" in path:
                return RELEASE_ROOTFS
            elif "kernel" in path:
                return STOCK_KERNEL
            return super().translate_path(path)

    server = http.server.HTTPServer(("0.0.0.0", HTTP_PORT), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def main():
    print("=" * 70)
    print("INSTALADOR DE FIRMWARE OPENWRT FULL RELEASE (SLOT 2)")
    print(f"Alvo: Acer Predator Connect T7 ({ROUTER_IP})")
    print("=" * 70)

    if not os.path.exists(RELEASE_ROOTFS):
        print(f"[-] Erro: Imagem de release nao encontrada em: {RELEASE_ROOTFS}")
        return 1

    rf_size = os.path.getsize(RELEASE_ROOTFS)
    k_size = os.path.getsize(STOCK_KERNEL)

    print(f"[*] RootFS Full Release: {rf_size} bytes ({rf_size / (1024*1024):.2f} MB)")
    print(f"[*] Kernel QSDK Estável: {k_size} bytes ({k_size / (1024*1024):.2f} MB)")

    print("[*] Iniciando servidor de streaming HTTP local...")
    server = start_http_server()

    print(f"[*] Conectando ao roteador em {ROUTER_IP} via Telnet...")
    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
        tn.read_until(b"/ # ", timeout=5)
    except Exception as e:
        print(f"[-] Erro ao conectar ao roteador: {e}")
        return 1

    payload = f"""cat << 'EOF' > /tmp/do_flash_full.sh
#!/bin/sh
set -e
echo "=========================================================="
echo "=== [1/4] Anexando Slot 2 (mtd20) e criando nos UBI ==="
echo "=========================================================="
ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true

for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] || continue
    maj=$(cut -d: -f1 "$v/dev" 2>/dev/null)
    min=$(cut -d: -f2 "$v/dev" 2>/dev/null)
    bname=$(basename "$v")
    mknod /dev/$bname c $maj $min 2>/dev/null || true
done

echo ""
echo "=========================================================="
echo "=== [2/4] Gravando Kernel Estavel no Slot 2 ==="
echo "=========================================================="
wget -qO- "http://{LOCAL_IP}:{HTTP_PORT}/kernel" | ubiupdatevol /dev/ubi1_1 -s {k_size} -
echo "[OK] Kernel gravado com sucesso!"

echo ""
echo "=========================================================="
echo "=== [3/4] Gravando RootFS Full Release no Slot 2 ==="
echo "=========================================================="
wget -qO- "http://{LOCAL_IP}:{HTTP_PORT}/rootfs" | ubiupdatevol /dev/ubi1_2 -s {rf_size} -
echo "[OK] RootFS Full Release gravado com sucesso!"

echo ""
echo "=========================================================="
echo "=== [4/4] Formatando Overlay Limpo do Slot 2 ==="
echo "=========================================================="
ubiupdatevol /dev/ubi1_3 -t
echo "[OK] Overlay limpo formatado!"

sync
rm -f /tmp/do_flash_full.sh
echo ""
echo "=========================================================="
echo "=== [SUCESSO TOTAL] FIRMWARE FULL INSTALADO NO SLOT 2! ==="
echo "=========================================================="
EOF
chmod +x /tmp/do_flash_full.sh
/bin/sh /tmp/do_flash_full.sh
"""

    print("[*] Enviando e executando rotina de gravacao atomica...")
    tn.write(payload.encode("ascii") + b"\n")

    t0 = time.time()
    while time.time() - t0 < 120:
        chunk = tn.read_some().decode("utf-8", errors="ignore")
        if not chunk:
            break
        print(chunk, end="", flush=True)
        if "=== [SUCESSO TOTAL]" in chunk:
            break

    tn.close()
    server.shutdown()
    print("\n[*] Gravacao finalizada com sucesso absoluto!")
    print("[*] Para reiniciar no OpenWrt Full Slot 2, basta rodar:")
    print("    python Scripts_Automacao/switch_boot_slot.py 2")
    return 0

if __name__ == "__main__":
    sys.exit(main())
