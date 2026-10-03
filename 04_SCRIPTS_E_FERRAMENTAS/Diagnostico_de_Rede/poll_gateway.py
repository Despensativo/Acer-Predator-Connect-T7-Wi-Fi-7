import subprocess
import time

for i in range(25):
    time.sleep(2)
    remote_cmd = 'dmesg | tail -n 5; echo "--- LOGREAD TFTP ---"; logread | tail -n 20 | grep -i tftp; echo "--- ETH1 LINK ---"; ip link show eth1'
    cmd = [
        'wsl', '-d', 'Ubuntu', '-u', 'builder',
        'sshpass', '-p', 'admin0100',
        'ssh', '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        'root@192.168.73.1',
        remote_cmd
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"=== Poll {i+1} ===")
    print(res.stdout)
    if "sent /tmp/tftp/openwrt.itb" in res.stdout and ("02:13" in res.stdout or "02:14" in res.stdout or "02:15" in res.stdout):
        print("*** SUCCESS! TFTP DOWNLOADED! ***")
        break
