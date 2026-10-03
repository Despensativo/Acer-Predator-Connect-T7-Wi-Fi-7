import subprocess

remote_script = '''
cat /tmp/dhcp.leases | grep -E "70:5a:6f:5d"
echo "--- LOGREAD DHCP ---"
logread | grep -E "70:5a:6f:5d"
echo "--- ALL DHCP REQUESTS LAST 50 LINES ---"
logread | grep -i dhcp | tail -n 20
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
