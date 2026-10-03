import telnetlib
import time
import urllib.request
import os

print("Connecting to router...")
tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)

# Dump ART (mtd18) and APPSBLENV (mtd13) to /webapps/web/pub/
cmd = "dd if=/dev/mtdblock18 of=/webapps/web/pub/art.bin bs=64k; dd if=/dev/mtdblock13 of=/webapps/web/pub/uboot_env.bin bs=64k\n"
tn.write(cmd.encode('ascii'))
time.sleep(2)
out = tn.read_very_eager().decode('utf-8', errors='ignore')
print(out)
tn.close()

# Download via HTTP
files = {
    'art.bin': r'C:\Users\User\Downloads\backup_predator_t7_art.bin',
    'uboot_env.bin': r'C:\Users\User\Downloads\backup_predator_t7_uboot_env.bin'
}

for remote, local in files.items():
    url = f"http://192.168.73.2/pub/{remote}"
    print(f"Downloading {url} -> {local}")
    urllib.request.urlretrieve(url, local)
    size = os.path.getsize(local)
    print(f"  Saved {local} ({size} bytes)")

# Remove temporary files on router
tn = telnetlib.Telnet('192.168.73.2', 23, timeout=3)
time.sleep(0.5)
tn.write(b"rm -f /webapps/web/pub/art.bin /webapps/web/pub/uboot_env.bin\n")
time.sleep(0.5)
tn.close()
print("Cleaned up temporary files on router.")
