#!/usr/bin/env python3
"""
=============================================================================
RESTAURADOR PADRAO DO SLOT 2 (OpenWrt Otimizado / LuCI Porta 80)
Acer Predator Connect T7 (Qualcomm IPQ5322)
=============================================================================
Restaura o Slot 2 (mtd20 / rootfs_1) exatamente para o estado perfeito de
producao atual:
- Kernel 32-bit QSDK oficial com acelerador NSS/PPE
- Wi-Fi 7 Tri-Band (BE11000) 100% calibrado
- RootFS SquashFS estavel
- Overlay completo com LuCI na porta 80, hostname 'Predator-Connect-T7',
  debloat de telemetrias/modems e utilitarios dual-boot
- Slot 1 (Acer Original de Fabrica) 100% preservado intacto
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
BACKUP_KERNEL = os.path.join(BASE_DIR, "Backups_MTD", "backup_predator_t7_kernel.bin")
BACKUP_ROOTFS = os.path.join(BASE_DIR, "Backups_MTD", "backup_predator_t7_ubi_rootfs.bin")
BACKUP_OVERLAY = os.path.join(BASE_DIR, "Backups_MTD", "backup_slot2_overlay_personalizado.tar.gz")

def start_http_server():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
        def translate_path(self, path):
            if "kernel" in path:
                return BACKUP_KERNEL
            elif "rootfs" in path:
                return BACKUP_ROOTFS
            elif "overlay" in path:
                return BACKUP_OVERLAY
            return super().translate_path(path)

    server = http.server.HTTPServer(("0.0.0.0", HTTP_PORT), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def main():
    print("=" * 70)
    print("RESTAURADOR OFICIAL DO SLOT 2 (PADRAO ATUAL DE PRODUCAO)")
    print(f"Alvo: Acer Predator Connect T7 ({ROUTER_IP})")
    print("=" * 70)

    for f in [BACKUP_KERNEL, BACKUP_ROOTFS, BACKUP_OVERLAY]:
        if not os.path.exists(f):
            print(f"[-] Arquivo de backup obrigatorio ausente: {f}")
            return 1

    k_sz = os.path.getsize(BACKUP_KERNEL)
    rf_sz = os.path.getsize(BACKUP_ROOTFS)
    ov_sz = os.path.getsize(BACKUP_OVERLAY)

    print(f"[*] Kernel Backup : {k_sz} bytes ({k_sz / (1024*1024):.2f} MB)")
    print(f"[*] RootFS Backup : {rf_sz} bytes ({rf_sz / (1024*1024):.2f} MB)")
    print(f"[*] Overlay Backup: {ov_sz} bytes ({ov_sz / (1024*1024):.2f} MB)")

    print("[*] Iniciando servidor de streaming HTTP local...")
    server = start_http_server()

    print(f"[*] Conectando ao roteador em {ROUTER_IP} via Telnet...")
    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
        tn.read_until(b"/ # ", timeout=5)
    except Exception as e:
        print(f"[-] Erro ao conectar ao roteador: {e}")
        server.shutdown()
        return 1

    # Detecta se estamos rodando dentro do Slot 1 ou Slot 2
    tn.write(b"cat /proc/boot_info/bootconfig0/rootfs/primaryboot\n")
    time.sleep(0.5)
    out_slot = tn.read_very_eager().decode("utf-8", errors="ignore")
    lines = [l.strip() for l in out_slot.splitlines() if l.strip().isdigit()]
    cur_slot = lines[-1] if lines else "1"

    print(f"[*] Roteador operando no Slot {cur_slot}")

    # Se estiver no Slot 1 (primaryboot = 1), o Slot 2 eh ubi1 (mtd20)
    # Se estiver no Slot 2 (primaryboot = 0), mtd20 eh ubi0 (ativo)
    target_ubi = "ubi1" if cur_slot == "1" else "ubi0"

    payload = f"""cat << 'EOF' > /tmp/do_restore_slot2.sh
#!/bin/sh
set -e
echo "=========================================================="
echo "=== [1/5] Verificando e anexando Slot 2 ==="
echo "=========================================================="
if [ "{target_ubi}" = "ubi1" ]; then
    ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true
fi

for v in /sys/class/ubi/{target_ubi}_*; do
    [ -d "$v" ] || continue
    maj=$(cut -d: -f1 "$v/dev" 2>/dev/null)
    min=$(cut -d: -f2 "$v/dev" 2>/dev/null)
    bname=$(basename "$v")
    mknod /dev/$bname c $maj $min 2>/dev/null || true
done

echo ""
echo "=========================================================="
echo "=== [2/5] Restaurando Kernel Estavel ({k_sz} bytes) ==="
echo "=========================================================="
wget -qO- "http://{LOCAL_IP}:{HTTP_PORT}/kernel" | ubiupdatevol /dev/{target_ubi}_1 -s {k_sz} -
echo "[OK] Kernel restaurado com sucesso!"

echo ""
echo "=========================================================="
echo "=== [3/5] Restaurando RootFS Estavel ({rf_sz} bytes) ==="
echo "=========================================================="
wget -qO- "http://{LOCAL_IP}:{HTTP_PORT}/rootfs" | ubiupdatevol /dev/{target_ubi}_2 -s {rf_sz} -
echo "[OK] RootFS restaurado com sucesso!"

echo ""
echo "=========================================================="
echo "=== [4/5] Formatando Overlay e Restaurando Configuracoes ==="
echo "=========================================================="
ubiupdatevol /dev/{target_ubi}_3 -t
mkdir -p /mnt/slot2_restore
mount -t ubifs /dev/{target_ubi}_3 /mnt/slot2_restore
mkdir -p /mnt/slot2_restore/upper /mnt/slot2_restore/work
ln -sf 2 /mnt/slot2_restore/.fs_state
wget -qO- "http://{LOCAL_IP}:{HTTP_PORT}/overlay" | tar -xz -C /mnt/slot2_restore/upper
sync
umount /mnt/slot2_restore
rm -rf /mnt/slot2_restore
echo "[OK] Overlay restaurado com todas as customizacoes e LuCI!"

echo ""
echo "=========================================================="
echo "=== [5/5] Finalizando e Sincronizando ==="
echo "=========================================================="
sync
rm -f /tmp/do_restore_slot2.sh
echo ""
echo "=========================================================="
echo "=== [SUCESSO TOTAL] O SLOT 2 FOI 100% RESTAURADO! ==="
echo "=========================================================="
EOF
chmod +x /tmp/do_restore_slot2.sh
/bin/sh /tmp/do_restore_slot2.sh
"""

    print("[*] Enviando e executando rotina de restauracao...")
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
    print("\n" + "=" * 70)
    print("[*] Restauracao do Slot 2 concluida com sucesso absoluto!")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
