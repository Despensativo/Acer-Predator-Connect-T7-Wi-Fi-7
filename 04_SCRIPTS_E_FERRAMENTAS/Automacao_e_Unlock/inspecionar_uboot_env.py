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

print("=== FW_PRINTENV (U-BOOT ENV) ===")
print(exec_cmd("fw_printenv"))

print("=== UBI0 VOLUMES (SLOT 1) ===")
print(exec_cmd("ubinfo -d 0"))

print("=== DUMPIMAGE ON KERNEL IN /dev/ubi0_1 ===")
print(exec_cmd("dumpimage -l /dev/ubi0_1 2>&1"))

tn.close()
