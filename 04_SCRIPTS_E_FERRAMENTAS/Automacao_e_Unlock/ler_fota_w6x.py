import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.73.1', port=22, username='root', password='admin0100', timeout=5)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='ignore').strip()

print("=== /tmp/w6x_oem/etc/config/fota ===")
print(run("cat /tmp/w6x_oem/etc/config/fota"))

print("=== /tmp/w6x_oem/etc/openwrt_version ===")
print(run("cat /tmp/w6x_oem/etc/openwrt_version"))

print("=== SEARCHING FOR UPDATE SCRIPTS ON W6X OEM ===")
print(run("ls -la /tmp/w6x_oem/usr/bin/*fota* /tmp/w6x_oem/usr/sbin/*upgrade* /tmp/w6x_oem/sbin/*upgrade* 2>/dev/null"))

print("=== KERNEL VOLUME ON UBI1 ===")
print(run("ls -la /dev/ubi1*"))

client.close()
