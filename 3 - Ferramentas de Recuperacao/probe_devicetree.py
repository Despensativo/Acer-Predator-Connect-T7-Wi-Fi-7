import telnetlib
import time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)

cmd = (
    "ls -la /sys/firmware/fdt 2>/dev/null; "
    "ls -d /sys/firmware/devicetree* 2>/dev/null; "
    "ls -la /lib/firmware/IPQ5332/ 2>/dev/null; "
    "cat /sys/kernel/debug/gpio 2>/dev/null | head -n 30; "
    "cat /etc/board.json 2>/dev/null\n"
)
tn.write(cmd.encode('ascii'))
time.sleep(2)
out = tn.read_very_eager().decode('utf-8', errors='ignore')
print(out)
tn.close()
