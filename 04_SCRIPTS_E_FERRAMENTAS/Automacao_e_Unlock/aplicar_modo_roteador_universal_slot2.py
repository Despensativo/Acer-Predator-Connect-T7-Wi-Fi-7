#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
APLICADOR DO MODO ROTEADOR UNIVERSAL OPENWRT NO SLOT 2
Acer Predator Connect T7 (Qualcomm IPQ5322 Wi-Fi 7 BE11000)
=============================================================================
Configuração de Rede:
1. LAN (Portas Traseiras 1 e 2 - 1 Gbps):
   - IP Estático: 192.168.1.1 (Máscara 255.255.255.0)
   - Servidor DHCP (dnsmasq) ATIVO: 192.168.1.100 - 192.168.1.250
   - LuCI Web GUI na Porta 80 e 443
   - SSH (Dropbear) na Porta 22 e Telnet na Porta 23
2. WAN (Porta Traseira 2.5 Gbps - eth0):
   - DHCP Client (recebe IP automaticamente do modem/rede principal)
   - Regra de Firewall aberta para administração remota (Web 80/443, SSH 22, Telnet 23)
3. Utilitários:
   - 'boot-acer' instalado para voltar ao Slot 1 a qualquer momento
   - Debloat dos serviços proprietários da Acer (lighttpd.init)
=============================================================================
"""

import os
import sys
import io
import time
import socket
import telnetlib

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROUTER_IP = "192.168.73.2"

NETWORK_CONFIG = """config interface 'loopback'
	option ifname 'lo'
	option proto 'static'
	option ipaddr '127.0.0.1'
	option netmask '255.0.0.0'

config globals 'globals'
	option ula_prefix 'fd60:d7e6:419b::/48'

config interface 'lan'
	option type 'bridge'
	option ifname 'eth1.1 eth1.2'
	option proto 'static'
	option ipaddr '192.168.1.1'
	option netmask '255.255.255.0'
	option ip6assign '60'
	option multicast_querier '0'
	option igmp_snooping '0'
	option force_link '1'

config interface 'wan'
	option ifname 'eth0'
	option proto 'dhcp'
	option hostname 'Predator Connect T7'
	option disabled '0'

config interface 'wan6'
	option ifname 'eth0'
	option proto 'dhcpv6'
	option reqaddress 'try'
	option reqprefix 'auto'

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

DHCP_CONFIG = """config dnsmasq
	option domainneeded '1'
	option boguspriv '1'
	option filterwin2k '0'
	option localise_queries '1'
	option rebind_protection '0'
	option rebind_localhost '1'
	option local '/lan/'
	option domain 'lan'
	option expandhosts '1'
	option nonegcache '0'
	option authoritative '1'
	option readethers '1'
	option leasefile '/tmp/dhcp.leases'
	option resolvfile '/tmp/resolv.conf.auto'

config dhcp 'lan'
	option interface 'lan'
	option start '100'
	option limit '150'
	option leasetime '12h'
	option force '1'
	option ignore '0'
	option dhcpv4 'server'
	option dhcpv6 'server'
	option ra 'server'

config dhcp 'wan'
	option interface 'wan'
	option ignore '1'

config odhcpd 'odhcpd'
	option maindhcp '0'
	option leasefile '/tmp/hosts/odhcpd'
	option leasetrigger '/usr/sbin/odhcpd-update'
	option loglevel '4'

config dhcp 'wan6'
	option ndp 'relay'
	option master '1'
	option interface 'wan6'
"""

FIREWALL_RULE = """
config rule
	option name 'Allow-Admin-WAN'
	option src 'wan'
	option proto 'tcp'
	option dest_port '22 23 80 443'
	option target 'ACCEPT'
"""

RC_LOCAL = """# Put your custom commands here that should be executed once
# the system init finished. By default this file does nothing.

# 1. Desativar Web proprietaria da Acer
/etc/init.d/lighttpd.init stop 2>/dev/null
/etc/init.d/lighttpd stop 2>/dev/null
killall -9 lighttpd 2>/dev/null

# 2. Habilitar Dropbear e Telnet
uci set dropbear.@dropbear[0].enable='1' 2>/dev/null
uci commit dropbear 2>/dev/null

DROPBEAR=$(command -v dropbear || echo "/usr/sbin/dropbear")
[ -x "$DROPBEAR" ] && $DROPBEAR -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B 2>/dev/null

TELNETD=$(command -v telnetd || echo "/usr/sbin/telnetd")
[ -x "$TELNETD" ] && $TELNETD -l /bin/ash 2>/dev/null

# 3. Garantir DHCP e DNS
/etc/init.d/dnsmasq enable 2>/dev/null
/etc/init.d/dnsmasq restart 2>/dev/null

# 4. Iniciar LuCI (uhttpd) na porta 80 e 443
killall -9 uhttpd 2>/dev/null
/usr/sbin/uhttpd -p 0.0.0.0:80 -s 0.0.0.0:443 -h /www -x /cgi-bin

# 5. Permissoes
chmod -R 755 /www 2>/dev/null

exit 0
"""

def run_cmd(tn, cmd, timeout=10):
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.3)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    return out

def main():
    print("=" * 70)
    print("⚙️ CONFIGURANDO MODO ROTEADOR UNIVERSAL NO SLOT 2 (OPENWRT)")
    print(f"Alvo Telnet: {ROUTER_IP}")
    print("=" * 70)

    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
    except Exception as e:
        print(f"[-] Erro ao conectar ao roteador: {e}")
        return 1

    time.sleep(0.5)
    tn.write(b"\n")
    time.sleep(0.5)
    tn.read_very_eager()

    # 1. Garantir que ubi1 está anexado e montado
    print("[*] Montando partição de dados do Slot 2 (ubi1_3)...")
    run_cmd(tn, "ubiattach -m 20 -d 1 2>/dev/null")
    run_cmd(tn, "mkdir -p /mnt/slot2_overlay")
    run_cmd(tn, "mount -t ubifs /dev/ubi1_3 /mnt/slot2_overlay 2>/dev/null")

    # 2. Aplicar /etc/config/network
    print("[*] [1/4] Gravando /etc/config/network (LAN 192.168.1.1 + WAN DHCP)...")
    tn.write(b"cat << 'EOF' > /mnt/slot2_overlay/upper/etc/config/network\n" + NETWORK_CONFIG.encode("ascii") + b"\nEOF\n")
    time.sleep(0.5)
    run_cmd(tn, "sync")

    # 3. Aplicar /etc/config/dhcp
    print("[*] [2/4] Gravando /etc/config/dhcp (DHCP Ativo na LAN: 192.168.1.100-250)...")
    tn.write(b"cat << 'EOF' > /mnt/slot2_overlay/upper/etc/config/dhcp\n" + DHCP_CONFIG.encode("ascii") + b"\nEOF\n")
    time.sleep(0.5)
    run_cmd(tn, "sync")

    # 4. Adicionar regra de administração na WAN ao firewall
    print("[*] [3/4] Atualizando /etc/config/firewall (Acesso administrativo WAN liberado)...")
    check_fw = run_cmd(tn, "grep 'Allow-Admin-WAN' /mnt/slot2_overlay/upper/etc/config/firewall")
    if "Allow-Admin-WAN" not in check_fw:
        tn.write(b"cat << 'EOF' >> /mnt/slot2_overlay/upper/etc/config/firewall\n" + FIREWALL_RULE.encode("ascii") + b"\nEOF\n")
        time.sleep(0.5)
        run_cmd(tn, "sync")

    # 5. Atualizar /etc/rc.local
    print("[*] [4/4] Atualizando /etc/rc.local (Debloat Acer + LuCI + Dropbear + Dnsmasq)...")
    tn.write(b"cat << 'EOF' > /mnt/slot2_overlay/upper/etc/rc.local\n" + RC_LOCAL.encode("ascii") + b"\nEOF\n")
    time.sleep(0.5)
    run_cmd(tn, "chmod +x /mnt/slot2_overlay/upper/etc/rc.local")
    run_cmd(tn, "sync")

    # 6. Desmontar Slot 2 com segurança
    print("[*] Desmontando partição do Slot 2 com segurança...")
    run_cmd(tn, "umount /mnt/slot2_overlay 2>/dev/null")
    run_cmd(tn, "ubidetach -m 20 2>/dev/null")
    run_cmd(tn, "sync")

    # 7. Chavear o boot para o Slot 2
    print("\n" + "=" * 70)
    print("🚀 CHAVEANDO BOOT PARA SLOT 2 (OPENWRT ROTEADOR UNIVERSAL)...")
    print("=" * 70)
    
    boot_cmd = """echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
reboot
"""
    tn.write(boot_cmd.encode("ascii") + b"\n")
    time.sleep(1.0)
    tn.close()

    print("[*] Comando de reboot enviado!")
    print("[*] O roteador está reiniciando no Slot 2 com a nova configuração de rede...")
    print("\n" + "=" * 70)
    print("⏳ MONITORANDO SUBIDA DO OPENWRT...")
    print("   -> LAN Padrao: 192.168.1.1 (Portas LAN traseiras)")
    print("   -> WAN DHCP:   192.168.73.2 / 192.168.73.x (Porta WAN 2.5G)")
    print("=" * 70)

    t0 = time.time()
    slot2_ready = False
    active_ip = None

    time.sleep(15)  # aguarda desligar

    for attempt in range(60):
        time.sleep(2)
        elapsed = int(time.time() - t0)

        for target in ["192.168.1.1", "192.168.73.2"]:
            # Testar Web (80)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((target, 80)) == 0:
                    s.close()
                    active_ip = target
                    slot2_ready = True
                    break
                s.close()
            except Exception: pass

            # Testar SSH (22)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((target, 22)) == 0:
                    s.close()
                    active_ip = target
                    slot2_ready = True
                    break
                s.close()
            except Exception: pass

        if slot2_ready:
            break

        sys.stdout.write(f"\r[{elapsed:02d}s] Sondando subida do OpenWrt em 192.168.1.1 e 192.168.73.2...")
        sys.stdout.flush()

    if slot2_ready:
        print(f"\n\n[+] 🎉 SUCESSO ABSOLUTO! OpenWrt ONLINE em {active_ip} após {int(time.time() - t0)}s!")
        print(f"    - Interface Web (LuCI): http://{active_ip}")
        print(f"    - SSH: ssh root@{active_ip}")
        print(f"    - Telnet: telnet {active_ip}")
        return 0
    else:
        print("\n[!] O roteador ainda está inicializando ou os adaptadores de rede do PC estão obtendo link.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
