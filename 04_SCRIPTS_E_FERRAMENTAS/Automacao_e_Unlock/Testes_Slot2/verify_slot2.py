import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.73.2', port=22, username='root', password='admin0100', timeout=5, look_for_keys=False, allow_agent=False)

def run(cmd):
    _, out, err = ssh.exec_command(cmd)
    o = out.read().decode('latin1', errors='ignore').strip()
    print(f'$ {cmd}\n{o}')
    return o

run('ubiattach -m 20 2>/dev/null; mkdir -p /tmp/chk && mount -t ubifs /dev/ubi1_3 /tmp/chk')
run('cat /tmp/chk/upper/etc/config/network')
run('grep -n "rootfs_1" /tmp/chk/upper/etc/init.d/wifi_fw_mount')
run('umount /tmp/chk')

ssh.close()
