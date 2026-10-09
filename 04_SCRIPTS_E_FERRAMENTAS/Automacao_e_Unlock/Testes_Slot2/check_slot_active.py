import telnetlib
import time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
tn.read_until(b"/ # ", timeout=4)

def run(cmd):
    tn.write(cmd.encode('ascii') + b'\n')
    time.sleep(0.4)
    out = tn.read_until(b"/ # ", timeout=10).decode('utf-8', errors='replace')
    lines = [l.strip() for l in out.strip().split('\n') if l.strip() and not l.startswith(cmd) and not l.startswith('/ #')]
    return '\n'.join(lines)

print("=== 1. LINHA DE COMANDO DO KERNEL ATUAL (/proc/cmdline) ===")
print(run("cat /proc/cmdline"))

print("\n=== 2. QUAL ROOTFS O KERNEL MONTOU (/proc/mtd e mounts) ===")
print(run("mount | grep -E 'rom|overlay|wifi'"))

print("\n=== 3. QUAL SLOT DO UBI ESTA ATIVO EM UBI0 (/sys/class/ubi/ubi0/mtd_num) ===")
print(run("cat /sys/class/ubi/ubi0/mtd_num 2>/dev/null"))

print("\n=== 4. STATUS DO WI-FI E REDE ===")
print(run("uci show wireless | grep ssid"))

tn.close()
