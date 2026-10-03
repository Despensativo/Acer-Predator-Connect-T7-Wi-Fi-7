import paramiko
import sys

ip = '192.168.73.1'
user = 'root'
passwords = ['admin', 'admin0100', 'password', 'root', '']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

connected = False
for pwd in passwords:
    try:
        print(f"Trying SSH root@{ip} with password: '{pwd}'...")
        client.connect(ip, port=22, username=user, password=pwd, timeout=3, look_for_keys=False, allow_agent=False)
        print(f"[+] SUCCESS! Connected with password: '{pwd}'")
        connected = True
        break
    except paramiko.AuthenticationException:
        print(f"[-] Authentication failed for '{pwd}'")
    except Exception as e:
        print(f"[!] Error: {e}")
        break

if connected:
    commands = [
        "uname -a",
        "cat /tmp/sysinfo/model 2>/dev/null",
        "cat /etc/openwrt_release 2>/dev/null",
        "cat /etc/version 2>/dev/null",
        "cat /etc/device_info 2>/dev/null",
        "cat /proc/mtd 2>/dev/null",
        "ls -la /etc/config/fota* /etc/config/acer* 2>/dev/null"
    ]
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='ignore').strip()
        err = stderr.read().decode('utf-8', errors='ignore').strip()
        print(f"\n$ {cmd}\n{out}")
        if err:
            print(f"[stderr] {err}")
    client.close()
