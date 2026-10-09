import subprocess

cmd_val = "bootipq_var=1; sleep 3; tftpboot 0x44000000 openwrt.itb && bootm 0x44000000 || bootipq"

ssh_cmd = [
    "wsl", "-d", "Ubuntu", "-u", "builder",
    "sshpass", "-p", "admin0100",
    "ssh", "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "HostKeyAlgorithms=+ssh-rsa",
    "-o", "PubkeyAcceptedKeyTypes=+ssh-rsa",
    "root@192.168.73.2",
    f"fw_setenv bootcmd '{cmd_val}' && fw_printenv bootcmd"
]

res = subprocess.run(ssh_cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
