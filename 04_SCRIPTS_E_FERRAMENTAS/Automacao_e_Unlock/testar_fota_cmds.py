import telnetlib
import time

def run():
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
        return tn.read_very_eager().decode('ascii', errors='ignore')

    print("=== STRINGS NEAR download / install / sysupgrade ===")
    print(exec_cmd("strings /usr/bin/fota | grep -A 10 -B 10 'sysupgrade'"))

    print("=== STRINGS NEAR nand-4k / /tmp/ ===")
    print(exec_cmd("strings /usr/bin/fota | grep -A 10 -B 10 'nand-4k'"))

    print("=== TEST fota ipq check_version ===")
    print(exec_cmd("fota ipq check_version", wait=3))

    tn.close()

if __name__ == '__main__':
    run()
