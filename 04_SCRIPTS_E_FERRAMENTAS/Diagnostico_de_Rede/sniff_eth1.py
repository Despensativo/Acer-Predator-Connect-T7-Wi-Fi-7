import subprocess

cmd = [
    'wsl', '-d', 'Ubuntu', '-u', 'builder',
    'sshpass', '-p', 'admin0100',
    'ssh', '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=/dev/null',
    'root@192.168.73.1',
    'tcpdump -i eth1 -n -e -c 10'
]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
