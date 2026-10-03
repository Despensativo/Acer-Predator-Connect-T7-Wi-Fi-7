import telnetlib
import time
import sys

def run_telnet_cmds():
    tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
    time.sleep(0.5)
    data = tn.read_very_eager().decode('ascii', errors='ignore')
    if 'login:' in data:
        tn.write(b'root\n')
        time.sleep(0.5)
        data += tn.read_very_eager().decode('ascii', errors='ignore')
        if 'Password:' in data:
            tn.write(b'admin\n')
            time.sleep(0.5)

    def exec_cmd(cmd, wait=1.5):
        tn.write(cmd.encode('ascii') + b'\n')
        time.sleep(wait)
        res = tn.read_very_eager().decode('ascii', errors='ignore')
        return res

    print("=== STRINGS FROM /usr/bin/fota ===")
    out = exec_cmd("strings /usr/bin/fota | grep -iE 'http|connect|acer|update|key|sign|crypt|aes|pem|sysupgrade|tar|md5|sha'")
    print(out)

    print("\n=== EXAMINING /etc/ipq.com.pem ===")
    out = exec_cmd("head -n 5 /etc/ipq.com.pem; tail -n 5 /etc/ipq.com.pem")
    print(out)

    print("\n=== EXAMINING /lib/upgrade/platform.sh ===")
    out = exec_cmd("cat /lib/upgrade/platform.sh | head -n 80")
    print(out)

    print("\n=== EXAMINING platform_do_upgrade in /lib/upgrade/platform.sh ===")
    out = exec_cmd("grep -A 40 'platform_do_upgrade()' /lib/upgrade/platform.sh")
    print(out)

    print("\n=== EXAMINING platform_check_image in /lib/upgrade/platform.sh ===")
    out = exec_cmd("grep -A 30 'platform_check_image()' /lib/upgrade/platform.sh")
    print(out)

    tn.close()

if __name__ == '__main__':
    run_telnet_cmds()
