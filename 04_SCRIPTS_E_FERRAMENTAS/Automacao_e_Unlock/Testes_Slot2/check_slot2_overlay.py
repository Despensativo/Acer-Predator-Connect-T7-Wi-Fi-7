import telnetlib
import time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
tn.read_until(b"/ # ", timeout=4)

def run(cmd):
    tn.write(cmd.encode('ascii') + b'\n')
    time.sleep(0.3)
    out = tn.read_until(b"/ # ", timeout=10).decode('utf-8', errors='replace')
    lines = [l.strip() for l in out.strip().split('\n') if l.strip() and not l.startswith(cmd) and not l.startswith('/ #')]
    return '\n'.join(lines)

print("=== CHECKING SLOT 2 OVERLAY ===")
run("mkdir -p /tmp/chk && mount -t ubifs /dev/ubi1_3 /tmp/chk 2>/dev/null || true")
print("Network config in Slot 2:")
print(run("cat /tmp/chk/upper/etc/config/network | grep -E 'switch|eth|192.168'"))
print("\nWifi fw mount in Slot 2:")
print(run("grep -n 'rootfs_1' /tmp/chk/upper/etc/init.d/wifi_fw_mount"))
run("umount /tmp/chk 2>/dev/null || true")

tn.close()
