import subprocess

remote_script = '''
python3 -c "
import socket, subprocess
for i in range(1, 30):
    ip = f'192.168.73.{i}'
    subprocess.Popen(['ping', '-c', '1', '-W', '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
" 2>/dev/null || (for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do ping -c 1 -W 1 192.168.73.$i >/dev/null 2>&1 & done)
sleep 2
cat /proc/net/arp | grep 70:5a
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
print("OUTPUT:")
print(res.stdout)
