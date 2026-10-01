import subprocess

remote_script = '''
cat /proc/net/nf_conntrack | grep -E "192.168.73." | head -n 30
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
print("CONNTRACK:")
print(res.stdout)
