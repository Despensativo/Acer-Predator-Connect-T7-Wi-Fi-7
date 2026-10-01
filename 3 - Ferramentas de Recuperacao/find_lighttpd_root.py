import telnetlib
import time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)
tn.write(b"grep -i 'server.document-root' /etc/lighttpd/*.conf; grep -i 'pub' /etc/lighttpd/*.conf\n")
time.sleep(1)
out = tn.read_very_eager().decode('utf-8', errors='ignore')
print(out)
tn.close()
