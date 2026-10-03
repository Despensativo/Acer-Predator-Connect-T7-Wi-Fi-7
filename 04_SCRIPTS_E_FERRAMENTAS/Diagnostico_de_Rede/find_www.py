import telnetlib
import time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)
tn.write(b"ls -d /www* /var/www* 2>/dev/null; find /www -name index.html 2>/dev/null\n")
time.sleep(1)
out = tn.read_very_eager().decode('utf-8', errors='ignore')
print(out)
tn.close()
