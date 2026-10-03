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

print("=== CHECK HOW WEB UI TRIGGERS FIRMWARE UPDATE ===")
print(exec_cmd("grep -rn 'fota' /webapps /www /usr/lib/lua 2>/dev/null | head -n 30"))

print("=== CHECK BINARIES HANDLING UPDATE IN /usr/bin OR /sbin ===")
print(exec_cmd("ls -la /usr/sbin/*upgrade* /usr/bin/*upgrade* /usr/bin/*fota* /sbin/*upgrade* 2>/dev/null"))

print("=== SEARCH FOR UPDATE URLS IN THE WHOLE ROOTFS ===")
print(exec_cmd("grep -rn 'acervcon.com' /etc /usr /rom /lib 2>/dev/null"))

tn.close()
