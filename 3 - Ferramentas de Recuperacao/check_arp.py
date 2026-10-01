import subprocess

cmd = [
    'wsl', '-d', 'Ubuntu', '-u', 'builder',
    'sshpass', '-p', 'admin0100',
    'ssh', '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=/dev/null',
    'root@192.168.73.1',
    'cat /proc/net/arp'
]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
