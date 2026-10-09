import subprocess, sys

def run_ssh(cmd):
    full_cmd = f'sshpass -p admin0100 ssh -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.73.2 "{cmd}"'
    res = subprocess.run(["wsl", "bash", "-c", full_cmd], capture_output=True, text=True)
    print(f"CMD: {cmd}")
    if res.stdout.strip():
        print(f"STDOUT:\n{res.stdout.strip()}")
    if res.stderr.strip():
        # filter out the standard openssh post-quantum warning
        err_lines = [l for l in res.stderr.splitlines() if "WARNING" not in l and "vulnerable" not in l and "upgraded" not in l]
        if err_lines:
            print("STDERR:\n" + "\n".join(err_lines))
    return res.stdout

print("=== 1. Garantindo que o Slot 2 esteja anexado e montado ===")
run_ssh("grep -q slot2_overlay /proc/mounts || { ubiattach -m 20 2>/dev/null; mkdir -p /tmp/slot2_overlay; mount -t ubifs /dev/ubi1_3 /tmp/slot2_overlay; }")

print("\n=== 2. Clonando todo o /overlay/upper do Slot 1 para o Slot 2 via TAR ===")
run_ssh("mkdir -p /tmp/slot2_overlay/upper /tmp/slot2_overlay/work && chmod 755 /tmp/slot2_overlay/work")
run_ssh("cd /overlay/upper && tar cf - . | (cd /tmp/slot2_overlay/upper && tar xf -)")
run_ssh("sync")

print("\n=== 3. Verificando shadow e passwd no Slot 2 ===")
run_ssh("head -n 2 /tmp/slot2_overlay/upper/etc/shadow; head -n 2 /tmp/slot2_overlay/upper/etc/passwd")

print("\n=== 4. Garantindo configuracao de rede com todas as portas bridged ===")
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
	option ipaddr '192.168.73.2'
	option gateway '192.168.73.1'
	list dns '192.168.73.1'
	list dns '8.8.8.8'
	option netmask '255.255.255.0'
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
"""
with open("temp_network.cfg", "w", newline="\n") as f:
    f.write(network_cfg)

subprocess.run(["wsl", "bash", "-c", "sshpass -p admin0100 scp -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa temp_network.cfg root@192.168.73.2:/tmp/slot2_overlay/upper/etc/config/network"])
run_ssh("cat /tmp/slot2_overlay/upper/etc/config/network | grep -E 'ipaddr|ifname'")

print("\n=== 5. Patching wifi_fw_mount no Slot 2 ===")
# Obter o script original de /rom/etc/init.d/wifi_fw_mount
run_ssh("mkdir -p /tmp/slot2_overlay/upper/etc/init.d")
run_ssh("cp -a /rom/etc/init.d/wifi_fw_mount /tmp/slot2_overlay/upper/etc/init.d/wifi_fw_mount")

# Patch da logica ubiattach / find_mtd_part wifi_fw
patch_sed = r"""sed -i 's/local PART=\$(grep -w  "rootfs" \/proc\/mtd | awk -F: '\''{print \$1}'\'')/local PART=\$(grep -q "rootfs_1" \/proc\/cmdline \&\& grep -w "rootfs_1" \/proc\/mtd | awk -F: '\''{print \$1}'\'' || grep -w "rootfs" \/proc\/mtd | awk -F: '\''{print \$1}'\'')/g' /tmp/slot2_overlay/upper/etc/init.d/wifi_fw_mount"""
run_ssh(patch_sed)
run_ssh("chmod 755 /tmp/slot2_overlay/upper/etc/init.d/wifi_fw_mount")
run_ssh("grep -n -C 3 'PART=' /tmp/slot2_overlay/upper/etc/init.d/wifi_fw_mount")

print("\n=== 6. Garantindo rc.local funcional com Dropbear e Telnet ===")
run_ssh("cp -a /overlay/upper/etc/rc.local /tmp/slot2_overlay/upper/etc/rc.local")
run_ssh("chmod 755 /tmp/slot2_overlay/upper/etc/rc.local")
run_ssh("head -n 25 /tmp/slot2_overlay/upper/etc/rc.local")

print("\n=== 7. Sincronizando e desmontando Slot 2 ===")
run_ssh("sync")
run_ssh("umount /tmp/slot2_overlay")
run_ssh("ubidetach -m 20")
print("=== SETUP DO SLOT 2 FINALIZADO COM SUCESSO! ===")
