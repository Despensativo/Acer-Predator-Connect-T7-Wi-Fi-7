import telnetlib
import time
import re

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)

# Inspect dmesg for timestamps between 25 and 85
cmd = "dmesg | grep -E '\\[ *[3-7][0-9]\\.'\n"
tn.write(cmd.encode('ascii'))
time.sleep(1)
out = tn.read_very_eager().decode('utf-8', errors='ignore')
print("=== DMESG BETWEEN 30s AND 79s ===")
lines = [l for l in out.splitlines() if re.search(r'\[ *[3-7][0-9]\.', l)]
print(f"Total lines found: {len(lines)}")
for l in lines[:30]:
    print(l)

# Check S96wifi_fw_done or S13qca-hostapd
tn.write(b"cat /etc/init.d/wifi_fw_done 2>/dev/null; cat /etc/init.d/qca-hostapd 2>/dev/null | head -n 30\n")
time.sleep(1)
out2 = tn.read_very_eager().decode('utf-8', errors='ignore')
print("\n=== WIFI INIT SCRIPTS ===")
print(out2[:800])

tn.close()
