#!/bin/sh
# Deploy dos pacotes selecionados do Cudy WR11000 para o Acer Predator Connect T7
# Inclui: WireGuard (kernel + tools + netifd), Etherwake, IGMP Proxy, Wi-Fi Scheduler,
# Network Conflict Calc e Correcoes Criticas de Firewall (DNS TCP, IPv6 Guest/IoT, WAN DHCPv6).

set -e

ROUTER_IP="${1:-192.168.76.1}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "===> [1/6] Enviando WireGuard para o roteador $ROUTER_IP..."
scp -O "$SCRIPT_DIR/wireguard/wireguard.ko" "root@$ROUTER_IP:/lib/modules/5.4.213/wireguard.ko"
scp -O "$SCRIPT_DIR/wireguard/wg" "root@$ROUTER_IP:/usr/bin/wg"
scp -O "$SCRIPT_DIR/wireguard/wireguard.sh" "root@$ROUTER_IP:/lib/netifd/proto/wireguard.sh"
scp -O "$SCRIPT_DIR/wireguard/wireguard_watchdog" "root@$ROUTER_IP:/usr/bin/wireguard_watchdog"
scp -O "$SCRIPT_DIR/wireguard/16-wireguard" "root@$ROUTER_IP:/etc/hotplug.d/iface/16-wireguard"
scp -O "$SCRIPT_DIR/wireguard/wireguard" "root@$ROUTER_IP:/etc/modules.d/wireguard"
ssh "root@$ROUTER_IP" "
chmod 755 /usr/bin/wg /usr/bin/wireguard_watchdog /lib/netifd/proto/wireguard.sh /etc/hotplug.d/iface/16-wireguard
lsmod | grep wireguard >/dev/null || insmod /lib/modules/5.4.213/wireguard.ko || true
"

echo "===> [2/6] Enviando Utilitarios (Etherwake e Network Conflict Calc)..."
scp -O "$SCRIPT_DIR/etherwake/etherwake" "root@$ROUTER_IP:/usr/bin/etherwake"
scp -O "$SCRIPT_DIR/utils/network-conflict-calc.sh" "root@$ROUTER_IP:/bin/network-conflict-calc.sh"
ssh "root@$ROUTER_IP" "chmod 755 /usr/bin/etherwake /bin/network-conflict-calc.sh"

echo "===> [3/6] Enviando IGMP Proxy (IPTV - Desativado por padrao)..."
scp -O "$SCRIPT_DIR/igmpproxy/igmpproxy" "root@$ROUTER_IP:/usr/sbin/igmpproxy"
scp -O "$SCRIPT_DIR/igmpproxy/igmpproxy" "root@$ROUTER_IP:/etc/init.d/igmpproxy"
ssh "root@$ROUTER_IP" "
chmod 755 /usr/sbin/igmpproxy /etc/init.d/igmpproxy
[ -f /etc/config/igmpproxy ] || cat > /etc/config/igmpproxy << 'EOF'
config igmpproxy
	option quickleave 1

config phyint
	option network wan
	option zone wan
	option direction upstream
	list altnet 0.0.0.0/0

config phyint
	option network lan
	option zone lan
	option direction downstream
EOF
/etc/init.d/igmpproxy disable 2>/dev/null || true
"

echo "===> [4/6] Enviando Wi-Fi Scheduler (Desativado por padrao)..."
scp -O "$SCRIPT_DIR/wifi_schedule/wifi_schedule.sh" "root@$ROUTER_IP:/usr/bin/wifi_schedule.sh"
ssh "root@$ROUTER_IP" "
chmod 755 /usr/bin/wifi_schedule.sh
[ -f /etc/config/wifi_schedule ] || cat > /etc/config/wifi_schedule << 'EOF'
config global
	option logging '1'
	option enabled '0'
	option recheck_interval '10'
	option modules_retries '10'
EOF
"

echo "===> [5/6] Aplicando Correcoes de Firewall (DNS TCP, IPv6 Guest/IoT, WAN DHCPv6)..."
ssh "root@$ROUTER_IP" "
[ -f /etc/config/firewall.bak.20261013 ] || cp -p /etc/config/firewall /etc/config/firewall.bak.20261013

# 1. Liberar TCP e UDP no DNS de Guest e IoT
uci set firewall.guest_dns.proto='tcp udp'
uci set firewall.iot_dns.proto='tcp udp'

# 2. Corrigir regra WAN Allow-DHCPv6 (remover filtro fc00::/6 que bloqueia provedor)
uci delete firewall.@rule[3].src_ip 2>/dev/null || true
uci delete firewall.@rule[3].dest_ip 2>/dev/null || true

# 3. Adicionar regras de entrada IPv6 para Guest e IoT (DHCPv6 e ICMPv6 Discovery)
uci -q get firewall.guest_dhcpv6 || {
	uci set firewall.guest_dhcpv6=rule
	uci set firewall.guest_dhcpv6.name='guest_DHCPv6'
	uci set firewall.guest_dhcpv6.src='guest'
	uci set firewall.guest_dhcpv6.proto='udp'
	uci set firewall.guest_dhcpv6.src_port='546'
	uci set firewall.guest_dhcpv6.dest_port='547'
	uci set firewall.guest_dhcpv6.family='ipv6'
	uci set firewall.guest_dhcpv6.target='ACCEPT'
}

uci -q get firewall.guest_icmpv6 || {
	uci set firewall.guest_icmpv6=rule
	uci set firewall.guest_icmpv6.name='guest_ICMPv6'
	uci set firewall.guest_icmpv6.src='guest'
	uci set firewall.guest_icmpv6.proto='icmp'
	uci add_list firewall.guest_icmpv6.icmp_type='echo-request'
	uci add_list firewall.guest_icmpv6.icmp_type='echo-reply'
	uci add_list firewall.guest_icmpv6.icmp_type='router-solicitation'
	uci add_list firewall.guest_icmpv6.icmp_type='neighbour-solicitation'
	uci add_list firewall.guest_icmpv6.icmp_type='neighbour-advertisement'
	uci set firewall.guest_icmpv6.family='ipv6'
	uci set firewall.guest_icmpv6.target='ACCEPT'
}

uci -q get firewall.iot_dhcpv6 || {
	uci set firewall.iot_dhcpv6=rule
	uci set firewall.iot_dhcpv6.name='iot_DHCPv6'
	uci set firewall.iot_dhcpv6.src='iot'
	uci set firewall.iot_dhcpv6.proto='udp'
	uci set firewall.iot_dhcpv6.src_port='546'
	uci set firewall.iot_dhcpv6.dest_port='547'
	uci set firewall.iot_dhcpv6.family='ipv6'
	uci set firewall.iot_dhcpv6.target='ACCEPT'
}

uci -q get firewall.iot_icmpv6 || {
	uci set firewall.iot_icmpv6=rule
	uci set firewall.iot_icmpv6.name='iot_ICMPv6'
	uci set firewall.iot_icmpv6.src='iot'
	uci set firewall.iot_icmpv6.proto='icmp'
	uci add_list firewall.iot_icmpv6.icmp_type='echo-request'
	uci add_list firewall.iot_icmpv6.icmp_type='echo-reply'
	uci add_list firewall.iot_icmpv6.icmp_type='router-solicitation'
	uci add_list firewall.iot_icmpv6.icmp_type='neighbour-solicitation'
	uci add_list firewall.iot_icmpv6.icmp_type='neighbour-advertisement'
	uci set firewall.iot_icmpv6.family='ipv6'
	uci set firewall.iot_icmpv6.target='ACCEPT'
}

uci commit firewall

# 4. Idempotencia em /etc/firewall.d/qca-nss-ecm
cat > /etc/firewall.d/qca-nss-ecm << 'EOF'
#!/bin/sh
iptables -C FORWARD -m physdev --physdev-is-bridged -j ACCEPT 2>/dev/null || iptables -A FORWARD -m physdev --physdev-is-bridged -j ACCEPT
iptables -N RATE-LIMIT 2>/dev/null || iptables -F RATE-LIMIT
iptables -F RATE-LIMIT
iptables -A RATE-LIMIT -m limit --limit 1000/sec --limit-burst 1000 -j RETURN
iptables -A RATE-LIMIT -j DROP
iptables -C zone_wan_forward -m conntrack --ctstate NEW -j RATE-LIMIT 2>/dev/null || iptables -I zone_wan_forward 5 -m conntrack --ctstate NEW -j RATE-LIMIT
EOF
chmod 755 /etc/firewall.d/qca-nss-ecm

# 5. Idempotencia em /etc/firewall.d/99-predator-fixes
cat > /etc/firewall.d/99-predator-fixes << 'EOF'
#!/bin/sh
iptables -t mangle -C FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null || iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
iptables -t mangle -C FORWARD -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 1453:1536 -j TCPMSS --set-mss 1452 2>/dev/null || iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 1453:1536 -j TCPMSS --set-mss 1452

ip6tables -t mangle -C FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null || ip6tables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
ip6tables -t mangle -C FORWARD -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 1433:1536 -j TCPMSS --set-mss 1432 2>/dev/null || ip6tables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 1433:1536 -j TCPMSS --set-mss 1432

iptables -C FORWARD -p udp --dport 443 -j REJECT --reject-with icmp-port-unreachable 2>/dev/null || iptables -I FORWARD 1 -p udp --dport 443 -j REJECT --reject-with icmp-port-unreachable
ip6tables -C FORWARD -p udp --dport 443 -j REJECT --reject-with icmp6-port-unreachable 2>/dev/null || ip6tables -I FORWARD 1 -p udp --dport 443 -j REJECT --reject-with icmp6-port-unreachable
EOF
chmod 755 /etc/firewall.d/99-predator-fixes

/etc/init.d/firewall reload
"

echo "===> [6/6] Verificando status dos componentes instalados..."
ssh "root@$ROUTER_IP" "
echo '--- Wireguard: ---'
wg --version
lsmod | grep wireguard
echo '--- Etherwake: ---'
which etherwake
echo '--- IGMP Proxy: ---'
which igmpproxy
echo '--- Wi-Fi Schedule: ---'
ls -l /usr/bin/wifi_schedule.sh
echo '--- Firewall Chains: ---'
iptables -S zone_guest_input
ip6tables -S zone_guest_input
"

echo "===> Todos os pacotes e correcoes foram aplicados com sucesso!"
