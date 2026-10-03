import telnetlib
import time

tn = telnetlib.Telnet("192.168.73.2", 23, timeout=5)
tn.read_until(b"/ # ", timeout=3)

cmd = """
sed -i 's|^exit 0|chmod -R 755 /www 2>/dev/null\\nexit 0|g' /etc/rc.local
sync
tail -n 10 /etc/rc.local
"""

for line in cmd.strip().splitlines():
    tn.write(line.encode("ascii") + b"\n")
    time.sleep(0.3)

out = tn.read_until(b"/ # ", timeout=5).decode("ascii", errors="ignore")
print(out)
tn.close()
