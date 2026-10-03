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

print("=== LOGS IN /var/log /tmp ===")
print(exec_cmd("ls -la /var/log /tmp/*.log /tmp/sysupgrade* 2>/dev/null"))

print("=== LOGREAD GREP ===")
print(exec_cmd("logread | grep -iE 'fota|upgrade|ota|update|version|download' | tail -n 40"))

print("=== NVRAM SHOW ALL VARIABLES WITH VERSION/OTA ===")
print(exec_cmd("nvram show | grep -iE 'ver|update|ota|build|old|sw_'"))

print("=== CHECK UCI SYSTEM / UCI ACER_OTA ===")
print(exec_cmd("uci show system; uci show acer_ota"))

print("=== CHECK /proc/upgrade_info and /proc/boot_info ===")
print(exec_cmd("ls -la /proc/upgrade_info/ /proc/boot_info/ 2>/dev/null"))
print(exec_cmd("cat /proc/boot_info/bootconfig0/rootfs/upgradepartition 2>/dev/null"))

print("=== SEARCH FOR STRINGS IN /overlay OR PERSISTENT STORAGE ===")
print(exec_cmd("find /overlay -name '*version*' -o -name '*ota*' -o -name '*fota*' 2>/dev/null"))

tn.close()
