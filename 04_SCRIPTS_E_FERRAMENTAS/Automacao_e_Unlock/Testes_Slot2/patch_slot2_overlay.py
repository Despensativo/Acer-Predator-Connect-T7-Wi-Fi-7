import paramiko
import re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.73.2', port=22, username='root', password='admin0100', timeout=5, look_for_keys=False, allow_agent=False)

def run(cmd, stdin_data=None):
    stdin, out, err = ssh.exec_command(cmd)
    if stdin_data:
        stdin.write(stdin_data)
        stdin.flush()
        stdin.channel.shutdown_write()
    o = out.read().decode('latin1', errors='ignore')
    e = err.read().decode('latin1', errors='ignore')
    print(f'$ {cmd}')
    if o.strip(): print(o.strip())
    if e.strip(): print('[stderr]', e.strip())
    return o

# 1. Ensure /mnt/slot2_overlay is mounted
run('mkdir -p /mnt/slot2_overlay')
run('mount | grep -q slot2_overlay || mount -t ubifs /dev/ubi1_3 /mnt/slot2_overlay')

# 2. Fix /etc/config/network in Slot 2
network_cfg = """config interface 'loopback'
	option ifname 'lo'
	option proto 'static'
	option ipaddr '127.0.0.1'
	option netmask '255.0.0.0'

config globals 'globals'
	option ula_prefix 'fd60:d7e6:419b::/48'

config interface 'lan'
	option type 'bridge'
	option ifname 'eth0 eth1.1 eth1.2'
	option proto 'static'
	option ipaddr '192.168.1.1'
	option netmask '255.255.255.0'
	list ipaddr '192.168.73.2/24'
	option ip6assign '60'
	option multicast_querier '0'
	option igmp_snooping '0'
	option force_link '1'

config switch
	option name 'switch1'
	option reset '1'
	option enable_vlan '1'

config switch_vlan
	option device 'switch1'
	option vlan '1'
	option ports '1 0t'

config switch_vlan
	option device 'switch1'
	option vlan '2'
	option ports '2 0t'

config interface 'guest'
	option ifname 'eth1.1093'
	option force_link '1'
	option type 'bridge'
	option proto 'static'
	option ipaddr '192.168.2.1'
	option netmask '255.255.255.0'

config interface 'iot'
	option ifname 'eth1.3093'
	option force_link '1'
	option type 'bridge'
	option proto 'static'
	option ipaddr '192.168.3.1'
	option netmask '255.255.255.0'
"""

run('cat > /mnt/slot2_overlay/upper/etc/config/network', stdin_data=network_cfg)
print('[+] /mnt/slot2_overlay/upper/etc/config/network written successfully!')

# 3. Patch /etc/init.d/wifi_fw_mount in Slot 2
wifi_script = run('cat /rom/etc/init.d/wifi_fw_mount')

old_pattern = r'local PART=\$\(grep -w\s+"rootfs" /proc/mtd \| awk -F: \'\{print \$1\}\'\)'
new_replacement = 'local PART=$(grep -q "rootfs_1" /proc/cmdline && grep -w "rootfs_1" /proc/mtd | awk -F: \'{print $1}\' || grep -w "rootfs" /proc/mtd | awk -F: \'{print $1}\')'

if re.search(old_pattern, wifi_script):
    wifi_script = re.sub(old_pattern, new_replacement, wifi_script)
    print('[+] Replaced hardcoded rootfs partition search in wifi_fw_mount!')
else:
    print('[-] Pattern not found in wifi_fw_mount!')

wifi_script = wifi_script.replace('/bin/mount -t squashfs $ubi_part', '/bin/mount -t squashfs ${ubi_part%% *}')

run('mkdir -p /mnt/slot2_overlay/upper/etc/init.d')
run('cat > /mnt/slot2_overlay/upper/etc/init.d/wifi_fw_mount', stdin_data=wifi_script)
run('chmod 755 /mnt/slot2_overlay/upper/etc/init.d/wifi_fw_mount')
print('[+] /mnt/slot2_overlay/upper/etc/init.d/wifi_fw_mount written and chmod 755!')

# 4. Sync filesystems
run('sync')
run('umount /mnt/slot2_overlay')
print('[+] Slot 2 overlay unmounted cleanly!')

ssh.close()
