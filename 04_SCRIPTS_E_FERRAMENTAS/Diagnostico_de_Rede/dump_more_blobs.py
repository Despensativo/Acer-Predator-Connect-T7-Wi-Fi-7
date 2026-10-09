import telnetlib
import time
import urllib.request
import os

print("Connecting to router via telnet...")
tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)

# Dump ETHPHYFW (mtd16), LICENSE (mtd19), DEVCFG (mtd8), CDT (mtd12)
cmd = (
    "dd if=/dev/mtdblock16 of=/webapps/web/pub/ethphy_fw.bin bs=64k 2>/dev/null; "
    "dd if=/dev/mtdblock19 of=/webapps/web/pub/license.bin bs=64k 2>/dev/null; "
    "dd if=/dev/mtdblock8 of=/webapps/web/pub/devcfg.bin bs=64k 2>/dev/null; "
    "dd if=/dev/mtdblock12 of=/webapps/web/pub/cdt.bin bs=64k 2>/dev/null\n"
)
tn.write(cmd.encode('ascii'))
time.sleep(2)
out = tn.read_very_eager().decode('utf-8', errors='ignore')
print(out)
tn.close()

# Download to temp
temp_files = {
    'ethphy_fw.bin': r'C:\Users\User\Downloads\backup_predator_t7_ethphy_fw.bin',
    'license.bin': r'C:\Users\User\Downloads\backup_predator_t7_license.bin',
    'devcfg.bin': r'C:\Users\User\Downloads\backup_predator_t7_devcfg.bin',
    'cdt.bin': r'C:\Users\User\Downloads\backup_predator_t7_cdt.bin'
}

for remote, local in temp_files.items():
    try:
        url = f"http://192.168.73.2/pub/{remote}"
        urllib.request.urlretrieve(url, local)
        print(f"Downloaded {remote} -> {local} ({os.path.getsize(local)} bytes)")
    except Exception as e:
        print(f"Failed {remote}: {e}")

# Clean up on router
tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)
tn.write(b"rm -f /webapps/web/pub/ethphy_fw.bin /webapps/web/pub/license.bin /webapps/web/pub/devcfg.bin /webapps/web/pub/cdt.bin\n")
time.sleep(0.5)
tn.close()
print("Router clean up done.")
