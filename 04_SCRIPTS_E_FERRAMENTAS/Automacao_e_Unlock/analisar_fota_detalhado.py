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

print("=== ALL URLS & DOMAINS IN /usr/bin/fota ===")
print(exec_cmd("strings /usr/bin/fota | grep -E 'https?://'"))

print("=== OPENSSL COMMANDS / STRINGS IN /usr/bin/fota ===")
print(exec_cmd("strings /usr/bin/fota | grep -E 'openssl|enc|aes|-K|-iv'"))

print("=== UCI CONFIG FOR OTA ===")
print(exec_cmd("uci show acer_ota"))

print("=== NVRAM OTA SETTINGS ===")
print(exec_cmd("nvram show | grep -iE 'fota|ota|firmware|update|url'"))

print("=== CHECK HOW FOTA IS CALLED IN CRON OR INIT ===")
print(exec_cmd("grep -rn 'fota' /etc/ /rom/etc/ 2>/dev/null"))

tn.close()
