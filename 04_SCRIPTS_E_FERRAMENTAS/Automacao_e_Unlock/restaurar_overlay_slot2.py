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
TARBALL = os.path.join(BASE_DIR, "Backups_MTD", "backup_slot2_overlay_personalizado.tar.gz")

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

cmd = f"""ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true
ubiupdatevol /dev/ubi1_3 -t
mkdir -p /mnt/slot2_ov
mount -t ubifs /dev/ubi1_3 /mnt/slot2_ov
mkdir -p /mnt/slot2_ov/upper /mnt/slot2_ov/work
ln -sf 2 /mnt/slot2_ov/.fs_state
curl -fsSL http://{PC_IP}:{HTTP_PORT}/backup_slot2_overlay_personalizado.tar.gz -o /tmp/ov.tar.gz
ls -l /tmp/ov.tar.gz
tar -xzf /tmp/ov.tar.gz -C /mnt/slot2_ov/upper
rm -f /tmp/ov.tar.gz
sync
umount /mnt/slot2_ov
rm -rf /mnt/slot2_ov
ubidetach -m 20 2>/dev/null || true
echo "OVERLAY_RESTORED_OK"
"""
for line in cmd.splitlines():
    tn.write(line.encode("ascii") + b"\n")
    time.sleep(0.3)

out = tn.read_until(b"OVERLAY_RESTORED_OK", timeout=30).decode("ascii", errors="ignore")
print(out)
tn.close()
server.shutdown()
