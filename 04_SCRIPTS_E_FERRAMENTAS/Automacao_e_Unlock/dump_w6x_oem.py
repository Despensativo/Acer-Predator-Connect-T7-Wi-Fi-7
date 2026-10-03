import paramiko
import os

target_dir = os.path.join("Backups_MTD", "Acer_Predator_Connect_W6x")
os.makedirs(target_dir, exist_ok=True)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("[*] Connecting to 192.168.73.1 (Acer Predator Connect W6x)...")
client.connect('192.168.73.1', port=22, username='root', password='admin0100', timeout=5)

def exec_cmd(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='ignore').strip()

print("[*] Extracting W6x metadata...")
prod_data = exec_cmd("cat /dev/mtd4ro")
with open(os.path.join(target_dir, "w6x_prod_info.txt"), "w") as f:
    f.write(prod_data)
print(f"[+] Saved w6x_prod_info.txt")

dumps = [
    ("mtd0_bl2.bin", "/dev/mtd0ro"),
    ("mtd2_factory_calibracao.bin", "/dev/mtd2ro"),
    ("mtd3_fip_bootloader.bin", "/dev/mtd3ro"),
    ("mtd4_prod_serial.bin", "/dev/mtd4ro"),
    ("ubi1_0_kernel_oem.bin", "/dev/ubi1_0"),
    ("ubi1_1_rootfs_oem.squashfs", "/dev/ubi1_1"),
]

for filename, devpath in dumps:
    local_file = os.path.join(target_dir, filename)
    print(f"[*] Dumping {devpath} -> {filename} via SSH stream...")
    stdin, stdout, stderr = client.exec_command(f"cat {devpath}")
    with open(local_file, "wb") as f:
        total = 0
        while True:
            chunk = stdout.channel.recv(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
            print(f"    Received {total // (1024*1024)} MB...", end='\r')
    size = os.path.getsize(local_file)
    print(f"\n[+] Successfully saved {filename} ({size} bytes / {size / (1024*1024):.2f} MB)")

client.close()
print("\n[+] ALL W6X FACTORY FIRMWARE AND HARDWARE PARTITIONS DOWNLOADED SUCCESSFULLY!")
