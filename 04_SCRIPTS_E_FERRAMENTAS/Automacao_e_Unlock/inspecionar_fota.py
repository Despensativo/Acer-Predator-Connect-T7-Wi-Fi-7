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

    print("=== /rom/etc/*.pem and ssl_file ===")
    print(exec_cmd("ls -la /rom/etc/*.pem /rom/etc/config/ssl_file/ 2>/dev/null"))

    print("=== STRINGS NEAR OPENSSL ===")
    print(exec_cmd("strings /usr/bin/fota | grep -A 10 -B 10 'openssl enc'"))

    print("=== CHECK HOW FOTA EXECUTES ===")
    print(exec_cmd("/usr/bin/fota -h 2>&1; /usr/bin/fota --help 2>&1"))

    print("=== CHECK FOTA ARGS ===")
    print(exec_cmd("strings /usr/bin/fota | grep -E '^[a-z_]+ [a-z_]+' | head -n 30"))

    print("=== RUNNING FOTA WITH NO ARGS TO SEE USAGE ===")
    print(exec_cmd("/usr/bin/fota 2>&1"))

    tn.close()

if __name__ == '__main__':
    run()
