import telnetlib
import time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
time.sleep(0.5)
data = tn.read_very_eager().decode('ascii', errors='ignore')
if 'login:' in data:
    tn.write(b'root\n')
    time.sleep(0.5)
    data += tn.read_very_eager().decode('ascii', errors='ignore')
    if 'Password:' in data:
        tn.write(b'admin\n')
        time.sleep(0.5)

def exec_cmd(cmd, wait=1.5):
    tn.write(cmd.encode('ascii') + b'\n')
    time.sleep(wait)
    return tn.read_very_eager().decode('ascii', errors='ignore')

print("=== CHECK FIT STRUCTURE OF KERNEL IN SLOT 1 ===")
# Read 4238664 bytes from /dev/ubi0_1 into /tmp/k.fit and check dumpimage -l
print(exec_cmd("dd if=/dev/ubi0_1 of=/tmp/k.fit bs=4096 count=1035 2>&1"))
print(exec_cmd("dumpimage -l /tmp/k.fit"))
print(exec_cmd("rm /tmp/k.fit"))

tn.close()
