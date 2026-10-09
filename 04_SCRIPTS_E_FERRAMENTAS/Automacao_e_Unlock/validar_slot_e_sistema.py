import telnetlib
import time

tn = telnetlib.Telnet("192.168.73.2", 23, timeout=5)
tn.read_until(b"/ # ", timeout=3)

cmds = [
    ("SLOT ATIVO (PRIMARYBOOT)", "cat /proc/boot_info/bootconfig0/rootfs/primaryboot"),
    ("LINHA DE COMANDO DO KERNEL (CMDLINE)", "cat /proc/cmdline"),
    ("MONTAGENS DE DISCO (ROOTFS E OVERLAY)", "mount"),
    ("ESPACO EM DISCO (DF)", "df -h"),
    ("UBI ATIVO E MTD ASSOCIADO", "ubinfo -a"),
    ("LOGS DE ERROS/ECC NO DMESG", "dmesg | grep -i -E 'ubi|ecc|corrupt|panic|fail' | tail -n 30")
]

for title, cmd in cmds:
    print("=" * 60)
    print(f"[*] {title}")
    print("=" * 60)
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.5)
    out = tn.read_until(b"/ # ", timeout=5).decode("ascii", errors="ignore")
    print(out)

tn.close()
