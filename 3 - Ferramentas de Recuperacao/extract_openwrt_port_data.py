import telnetlib
import time
import urllib.request
import os

dest_dir = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\Engenharia_Reversa_OpenWrt"
os.makedirs(dest_dir, exist_ok=True)

print("Connecting to router via telnet...")
tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)

# 1. Copy FDT (device tree blob) to web directory
# 2. Package /lib/firmware/IPQ5332 to tar.gz
# 3. Dump full GPIO table, board.json, and switch info
cmd = (
    "cp /sys/firmware/fdt /webapps/web/pub/acer_predator_t7.dtb; "
    "tar -czf /webapps/web/pub/ipq5332_wifi_fw.tar.gz -C /lib/firmware IPQ5332; "
    "cat /sys/kernel/debug/gpio > /webapps/web/pub/gpio_table.txt 2>/dev/null; "
    "cat /etc/board.json > /webapps/web/pub/board.json; "
    "swconfig dev switch1 show > /webapps/web/pub/switch_config.txt 2>/dev/null\n"
)
tn.write(cmd.encode('ascii'))
time.sleep(4)
out = tn.read_very_eager().decode('utf-8', errors='ignore')
print(out)
tn.close()

# Download files
files = {
    'acer_predator_t7.dtb': os.path.join(dest_dir, 'acer_predator_t7.dtb'),
    'ipq5332_wifi_fw.tar.gz': os.path.join(dest_dir, 'ipq5332_wifi_fw.tar.gz'),
    'gpio_table.txt': os.path.join(dest_dir, 'gpio_table.txt'),
    'board.json': os.path.join(dest_dir, 'board.json'),
    'switch_config.txt': os.path.join(dest_dir, 'switch_config.txt')
}

for remote, local in files.items():
    try:
        url = f"http://192.168.73.2/pub/{remote}"
        urllib.request.urlretrieve(url, local)
        print(f"Downloaded {remote} -> {local} ({os.path.getsize(local)} bytes)")
    except Exception as e:
        print(f"Failed {remote}: {e}")

# Clean up on router
tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)
tn.write(b"rm -f /webapps/web/pub/acer_predator_t7.dtb /webapps/web/pub/ipq5332_wifi_fw.tar.gz /webapps/web/pub/gpio_table.txt /webapps/web/pub/board.json /webapps/web/pub/switch_config.txt\n")
time.sleep(0.5)
tn.close()
print("Cleaned up web directory on router.")
