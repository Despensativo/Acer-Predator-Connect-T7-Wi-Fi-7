import paramiko

ip = '192.168.73.1'
user = 'root'
pwd = 'admin0100'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(ip, port=22, username=user, password=pwd, timeout=5)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore').strip()
    return out

print("=== CHECK MTD4 (PROD) STRINGS ===")
print(run("strings /dev/mtd4ro 2>/dev/null | head -n 30"))

print("=== CHECK U-BOOT ENV ON W6X ===")
print(run("fw_printenv 2>/dev/null | head -n 30"))

print("=== CHECK IF BACKUPS EXIST ON W6X ===")
print(run("ls -la /root /tmp /storage 2>/dev/null; df -h"))

print("=== CHECK UBI VOLUMES ON W6X ===")
print(run("ubinfo -a 2>/dev/null"))

print("=== CHECK MTD8 (UBI1 / SECOND SLOT?) ===")
print(run("cat /proc/cmdline"))

client.close()
