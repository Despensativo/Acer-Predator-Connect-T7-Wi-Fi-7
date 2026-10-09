import telnetlib
import time

try:
    tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
    time.sleep(0.5)
    cmd = "cat /proc/mtd\necho '=== UNAME ==='\nuname -a\necho '=== MEMORY ==='\nfree\necho '=== DISK ==='\ndf -h\n"
    tn.write(cmd.encode('ascii'))
    time.sleep(1.5)
    out = tn.read_very_eager().decode('utf-8', errors='ignore')
    print(out)
    tn.close()
except Exception as e:
    print('Error:', e)
