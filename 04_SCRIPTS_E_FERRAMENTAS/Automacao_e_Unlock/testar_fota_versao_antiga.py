import telnetlib
import time

def test_fota_version(version_to_test, sku_to_test="BR"):
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

    def exec_cmd(cmd, wait=2.0):
        tn.write(cmd.encode('ascii') + b'\n')
        time.sleep(wait)
        return tn.read_very_eager().decode('ascii', errors='ignore')

    print(f"[*] Setting version to {version_to_test}...")
    exec_cmd(f"uci set acer_ota.ipq.current_version='T7_{sku_to_test}_{version_to_test}'")
    
    print(f"[*] Running 'fota ipq check_version'...")
    res = exec_cmd("fota ipq check_version", wait=5.0)
    print("=== RESULT ===")
    print(res)

    print("[*] Restoring original version...")
    exec_cmd("uci set acer_ota.ipq.current_version='T7_BR_1.01.000024'")
    exec_cmd("uci commit acer_ota")

    tn.close()

if __name__ == '__main__':
    test_fota_version("1.00.000001")
