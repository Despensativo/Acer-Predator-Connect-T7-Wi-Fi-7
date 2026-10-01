import subprocess

cmd = [
    'wsl', '-d', 'Ubuntu', '-u', 'builder',
    'sshpass', '-p', 'admin0100',
    'ssh', '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=/dev/null',
    'root@192.168.73.1',
    'tail -n 60 /tmp/tftp_capture.log'
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("TAIL OF CAPTURE LOG:")
print(res.stdout)
