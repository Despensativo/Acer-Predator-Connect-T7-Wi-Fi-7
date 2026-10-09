import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.73.1', port=22, username='root', password='admin0100', timeout=5)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='ignore').strip()

print("=== CHECKING MTD8 CONTENT ON W6X ===")
print(run("hexdump -C /dev/mtd8ro | head -n 30"))

print("=== CHECKING /mnt/ssd OR OTHER STORAGE FOR W6X OEM BACKUPS ===")
print(run("ls -la /mnt/ssd; find /mnt/ssd -maxdepth 3 2>/dev/null"))

client.close()
