import subprocess
import time

for i in range(15):
    time.sleep(2)
    remote_cmd = 'dmesg | tail -n 5; echo "--- TFTP LOGS ---"; logread | grep -i tftp | tail -n 5; echo "--- PCAP LOGS ---"; tail -n 10 /tmp/tftp_capture.log 2>/dev/null'
    cmd = [
        'wsl', '-d', 'Ubuntu', '-u', 'builder',
        'sshpass', '-p', 'admin0100',
        'ssh', '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        'root@192.168.73.1',
        remote_cmd
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"=== Check {i+1} ===")
    print(res.stdout)
    if "sent /tmp/tftp/openwrt.itb" in res.stdout and ("02:13" in res.stdout or "02:14" in res.stdout):
        print(">>> TFTP TRANSFER DETECTED! <<<")
        break
