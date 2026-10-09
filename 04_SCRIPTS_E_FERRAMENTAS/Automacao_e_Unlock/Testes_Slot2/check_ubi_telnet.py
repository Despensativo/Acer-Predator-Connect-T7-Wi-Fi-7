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

print("=== UBI1 VOLUMES ===")
print(run("""for v in /sys/class/ubi/ubi1_*; do [ -d "$v" ] && echo "$(basename $v): name=$(cat $v/name) bytes=$(cat $v/data_bytes 2>/dev/null || echo N/A)"; done"""))

print("\n=== UBI0 VS UBI1 KERNEL & ROOTFS ===")
print("ubi0_1 (kernel slot 1):", run("cat /sys/class/ubi/ubi0_1/data_bytes 2>/dev/null"))
print("ubi1_1 (kernel slot 2):", run("cat /sys/class/ubi/ubi1_1/data_bytes 2>/dev/null"))
print("ubi0_2 (rootfs slot 1):", run("cat /sys/class/ubi/ubi0_2/data_bytes 2>/dev/null"))
print("ubi1_2 (rootfs slot 2):", run("cat /sys/class/ubi/ubi1_2/data_bytes 2>/dev/null"))

tn.close()
