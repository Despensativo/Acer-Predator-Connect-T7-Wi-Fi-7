import telnetlib
import time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
tn.read_until(b"/ # ", timeout=4)

def run(cmd):
    tn.write(cmd.encode('ascii') + b'\n')
    time.sleep(0.3)
    out = tn.read_until(b"/ # ", timeout=10).decode('utf-8', errors='replace')
    lines = [l.strip() for l in out.strip().split('\n') if l.strip() and not l.startswith(cmd) and not l.startswith('/ #')]
    return '\n'.join(lines)

print("=== FW_PRINTENV BOOTCMD ===")
print(run("fw_printenv bootcmd"))
print(run("fw_printenv bootcmd_slot2"))
print(run("fw_printenv fsbootargs"))

tn.close()
