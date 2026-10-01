import subprocess

cmd = [
    'wsl', '-d', 'Ubuntu', '-u', 'builder',
    'sshpass', '-p', 'admin0100',
    'ssh', '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=/dev/null',
    'root@192.168.73.1',
    'grep -i -E "tftp|192.168.73.2|arp" /tmp/tftp_capture.log | head -n 40'
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("CAPTURED PACKETS:")
print(res.stdout)
