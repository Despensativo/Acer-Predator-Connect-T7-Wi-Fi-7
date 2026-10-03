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

print("=== SEARCHING 1.01.000024 IN FILES ===")
print(exec_cmd("grep -rn '000024' /etc /tmp /var /rom/etc 2>/dev/null"))

print("=== NVRAM SHOW ===")
print(exec_cmd("nvram show | grep -iE 'ver|sku|model'"))

print("=== /etc/openwrt_version, /etc/version ===")
print(exec_cmd("cat /etc/version /etc/openwrt_version /etc/banner /etc/device_info 2>/dev/null"))

tn.close()
