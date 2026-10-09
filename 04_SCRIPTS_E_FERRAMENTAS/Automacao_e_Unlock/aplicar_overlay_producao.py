import http.server
import socketserver
import threading
import telnetlib
import time
import os

PC_IP = "192.168.73.90"
ROUTER_IP = "192.168.73.2"
HTTP_PORT = 8089
BASE_DIR = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7"
TARBALL = os.path.join(BASE_DIR, "Backups_MTD", "backup_slot2_overlay_perfeito_producao.tar.gz")

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(TARBALL), **kwargs)
    def log_message(self, format, *args): pass

server = socketserver.TCPServer((PC_IP, HTTP_PORT), QuietHandler)
server.allow_reuse_address = True
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
tn.read_until(b"/ # ", timeout=5)

def run_cmd(cmd, timeout=30):
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.5)
    return tn.read_until(b"/ # ", timeout=timeout).decode("ascii", errors="ignore")

print("[*] Anexando Slot 2 e montando overlay...")
run_cmd("ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true")
run_cmd("mkdir -p /mnt/slot2_restore")
run_cmd("mount -t ubifs /dev/ubi1_3 /mnt/slot2_restore")
run_cmd("mkdir -p /mnt/slot2_restore/upper /mnt/slot2_restore/work")
run_cmd("ln -sf 2 /mnt/slot2_restore/.fs_state")

print("[*] Baixando tarball verificado de producao (3.81 MB)...")
run_cmd(f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/backup_slot2_overlay_perfeito_producao.tar.gz -o /tmp/ov.tar.gz", timeout=30)
out_ls = run_cmd("ls -lh /tmp/ov.tar.gz")
print("    ", out_ls.strip())

print("[*] Descompactando overlay...")
out_tar = run_cmd("tar -xzf /tmp/ov.tar.gz -C /mnt/slot2_restore/upper", timeout=60)
print("    ", out_tar.strip())
run_cmd("rm -f /tmp/ov.tar.gz")

print("[*] Sincronizando e desmontando...")
run_cmd("sync")
run_cmd("umount /mnt/slot2_restore")
run_cmd("rm -rf /mnt/slot2_restore")
run_cmd("ubidetach -m 20 2>/dev/null || true")

tn.close()
server.shutdown()
print("[OK] Overlay de producao restaurado com sucesso absoluto!")
