import subprocess, base64, sys

def run_remote(cmd):
    # Escape double quotes and dollar signs for bash
    escaped_cmd = cmd.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$')
    full_cmd = f'sshpass -p admin0100 ssh -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.73.2 "{escaped_cmd}"'
    res = subprocess.run(["wsl", "bash", "-c", full_cmd], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] CMD failed: {cmd}")
        print(res.stderr)
    return res.stdout.strip()

print("="*60)
print("=== APLICANDO CORREÇÕES COMPLETAS NO OVERLAY DO SLOT 2 ===")
print("="*60)

# 1. Anexar e montar Slot 2
print("\n[1/7] Anexando mtd20 (rootfs_1) e montando ubi1_3...")
run_remote("grep -q slot2_overlay /proc/mounts || { ubiattach -m 20 2>/dev/null; mkdir -p /tmp/slot2_overlay; mount -t ubifs /dev/ubi1_3 /tmp/slot2_overlay; }")
mounts = run_remote("grep slot2_overlay /proc/mounts")
print(f"Mount: {mounts}")
assert "slot2_overlay" in mounts, "Falha ao montar /tmp/slot2_overlay!"

# 2. Clonar todo o /overlay/upper do Slot 1 via TAR (preserva permissões, donos e whiteouts)
print("\n[2/7] Clonando /overlay/upper do Slot 1 para o Slot 2 via TAR...")
run_remote("mkdir -p /tmp/slot2_overlay/upper /tmp/slot2_overlay/work && chmod 755 /tmp/slot2_overlay/work")
run_remote("cd /overlay/upper && tar cf - . | (cd /tmp/slot2_overlay/upper && tar xf -)")
run_remote("sync")
print("Clone concluido!")

# 3. Verificar shadow e passwd no Slot 2
print("\n[3/7] Verificando credenciais no Slot 2...")
shadow_chk = run_remote("head -n 2 /tmp/slot2_overlay/upper/etc/shadow")
passwd_chk = run_remote("head -n 2 /tmp/slot2_overlay/upper/etc/passwd")
print("Shadow:\n" + shadow_chk)
print("Passwd:\n" + passwd_chk)
assert "root:" in shadow_chk, "Root ausente no shadow do Slot 2!"

# 4. Escrever /etc/config/network com todas as portas bridged em 192.168.73.2
print("\n[4/7] Gravando /etc/config/network estatico com eth0, eth1.1 e eth1.2...")
network_content = """config interface 'loopback'
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
net_b64 = base64.b64encode(network_content.encode('utf-8')).decode('ascii')
run_remote(f"echo '{net_b64}' | base64 -d > /tmp/slot2_overlay/upper/etc/config/network")
net_verify = run_remote("cat /tmp/slot2_overlay/upper/etc/config/network | grep -E 'ipaddr|ifname'")
print("Network verificado:\n" + net_verify)

# 5. Instalar wifi_fw_mount corrigido
print("\n[5/7] Instalando wifi_fw_mount corrigido para Slot 2...")
with open("wifi_fw_mount.patched", "rb") as f:
    wifi_content = f.read()

ssh_cmd = 'sshpass -p admin0100 ssh -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.73.2 "cat > /tmp/slot2_overlay/upper/etc/init.d/wifi_fw_mount && chmod 755 /tmp/slot2_overlay/upper/etc/init.d/wifi_fw_mount"'
res = subprocess.run(["wsl", "bash", "-c", ssh_cmd], input=wifi_content, capture_output=True)
if res.returncode != 0:
    print("[ERROR] Falha ao enviar wifi_fw_mount:", res.stderr)
else:
    print("wifi_fw_mount transferido via stdin com sucesso!")

wifi_chk = run_remote("grep -n -C 2 'ubi_part_name=\"rootfs_1\"' /tmp/slot2_overlay/upper/etc/init.d/wifi_fw_mount")
print("wifi_fw_mount verificado:\n" + wifi_chk)

# 6. Configurar sysctl para desativar kernel panic reboot imediato
print("\n[6/7] Configurando sysctl.conf (panic=0) para estabilidade...")
sysctl_extra = """
kernel.panic = 0
kernel.panic_on_oops = 0
"""
sysctl_b64 = base64.b64encode(sysctl_extra.encode('utf-8')).decode('ascii')
run_remote(f"echo '{sysctl_b64}' | base64 -d >> /tmp/slot2_overlay/upper/etc/sysctl.conf")
print("sysctl.conf atualizado!")

# 7. Sincronizar e desmontar limpo
print("\n[7/7] Sincronizando dados e desmontando...")
run_remote("sync")
run_remote("umount /tmp/slot2_overlay")
run_remote("ubidetach -d 1 2>/dev/null || ubidetach -m 20 2>/dev/null || true")
print("Slot 2 desmontado e desanexado com sucesso!")

print("\n" + "="*60)
print("=== CONFIGURAÇÃO DO OVERLAY DO SLOT 2 CONCLUÍDA COM ÊXITO! ===")
print("="*60)
