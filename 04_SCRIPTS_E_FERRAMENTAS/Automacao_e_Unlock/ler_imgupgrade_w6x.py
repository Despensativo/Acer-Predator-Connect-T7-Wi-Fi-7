import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.73.1', port=22, username='root', password='admin0100', timeout=5)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='ignore').strip()

print("=== /tmp/w6x_oem/sbin/imgupgrade ===")
print(run("cat /tmp/w6x_oem/sbin/imgupgrade"))

print("=== /tmp/w6x_oem/lib/upgrade/platform.sh ===")
print(run("head -n 50 /tmp/w6x_oem/lib/upgrade/platform.sh 2>/dev/null"))

print("=== /tmp/w6x_oem/etc/banner OR VERSION DETAILS ===")
print(run("cat /tmp/w6x_oem/etc/version 2>/dev/null"))

client.close()
