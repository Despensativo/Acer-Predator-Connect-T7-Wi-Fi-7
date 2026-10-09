import sys
import time
import telnetlib

def run_telnet_command(command, host="192.168.73.2", port=23, timeout=5):
    try:
        tn = telnetlib.Telnet(host, port, timeout=timeout)
        tn.read_until(b"login: ", timeout=3)
        tn.write(b"root\n")
        tn.read_until(b"Password: ", timeout=3)
        tn.write(b"admin0100\n")
        tn.read_until(b"/ # ", timeout=3)
        
        tn.write(command.encode("utf-8") + b"\n")
        out = tn.read_until(b"/ # ", timeout=timeout)
        tn.close()
        return out.decode("latin1", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
    else:
        cmd = sys.stdin.read().strip()
    res = run_telnet_command(cmd)
    print(res)
