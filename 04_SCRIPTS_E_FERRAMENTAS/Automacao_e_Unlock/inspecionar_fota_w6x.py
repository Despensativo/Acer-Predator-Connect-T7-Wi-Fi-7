import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.73.1', port=22, username='root', password='admin0100', timeout=5)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='ignore').strip()

print("=== VERSION AND FOTA ON W6X OEM ===")
print(run("ls -la /tmp/w6x_oem/etc/*version* /tmp/w6x_oem/etc/config/*fota* /tmp/w6x_oem/etc/config/*ota* 2>/dev/null"))
print(run("cat /tmp/w6x_oem/etc/version 2>/dev/null"))
print(run("cat /tmp/w6x_oem/etc/config/default_fota_config 2>/dev/null"))
print(run("cat /tmp/w6x_oem/etc/config/fota_enc.txt 2>/dev/null"))
print("=== FOTA STRINGS URLS ===")
print(run("strings /tmp/w6x_oem/usr/bin/fota 2>/dev/null | grep -E 'https?://'"))
print("=== FOTA PROJECT NAME ===")
print(run("strings /tmp/w6x_oem/usr/bin/fota 2>/dev/null | grep -E 'W6|project' | head -n 30"))

client.close()
