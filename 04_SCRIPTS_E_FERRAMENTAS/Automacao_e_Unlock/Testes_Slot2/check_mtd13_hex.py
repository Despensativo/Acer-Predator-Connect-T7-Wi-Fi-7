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

print("First 64 bytes of /dev/mtd13:")
print(run("hexdump -C -n 64 /dev/mtd13"))

print("\nfw_printenv status:")
print(run("fw_printenv"))

tn.close()
