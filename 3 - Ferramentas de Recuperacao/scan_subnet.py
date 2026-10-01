import subprocess

remote_script = '''
for i in $(seq 1 50); do
    ping -c 1 -W 1 192.168.73.$i >/dev/null 2>&1 &
done
sleep 2
cat /proc/net/arp | grep -E "70:5a|0x2"
'''

cmd = [
    'wsl', '-d', 'Ubuntu', '-u', 'builder',
    'sshpass', '-p', 'admin0100',
    'ssh', '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=/dev/null',
    'root@192.168.73.1',
    remote_script
]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
