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

print("=== /rom/etc/version ===")
print(exec_cmd("cat /rom/etc/version 2>/dev/null"))

print("=== /overlay/upper/etc/version ===")
print(exec_cmd("cat /overlay/upper/etc/version 2>/dev/null"))

print("=== version.json ROM ===")
print(exec_cmd("cat /rom/webapps/web/pub/dist/version.json 2>/dev/null"))

print("=== version.json OVERLAY ===")
print(exec_cmd("cat /overlay/upper/webapps/web/pub/dist/version.json 2>/dev/null"))

print("=== /var/log/faiot_fcgi_messages ===")
print(exec_cmd("tail -n 30 /var/log/faiot_fcgi_messages"))

print("=== /overlay/upper/etc/config/default_fota_config ===")
print(exec_cmd("cat /overlay/upper/etc/config/default_fota_config 2>/dev/null"))

tn.close()
