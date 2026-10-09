import telnetlib
import time

tn = telnetlib.Telnet("192.168.73.2", 23, timeout=5)
tn.read_until(b"/ # ", timeout=3)

cmds = [
    "strings /usr/bin/fota | grep -E 'nand-4k|upgrade|install|fw_update|tar|bin|img'",
    "strings /usr/bin/fota | grep -iE 'verify|signature|digest|openssl|aes|decrypt|rsa'",
    "ls -la /etc/certs /etc/ssl /etc/*.crt /etc/*.pem 2>/dev/null",
    "find / -name '*cert*' -o -name '*key*' -o -name '*pub*' 2>/dev/null | grep -E 'fota|ota|upgrade|sign' | head -n 30"
]

for cmd in cmds:
    print("=" * 60)
    print(">>>", cmd)
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(1)
    print(tn.read_until(b"/ # ", timeout=10).decode("ascii", errors="ignore"))

tn.close()
