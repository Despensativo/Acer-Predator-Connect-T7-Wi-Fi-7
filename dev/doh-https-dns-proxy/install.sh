#!/bin/sh
# Script de instalacao e ativacao de DoH (DNS over HTTPS) no Acer Predator Connect T7
# Utiliza https-dns-proxy apontando para servidores livres (Cloudflare 1.1.1.1 e Google 8.8.8.8)
# Sem bloqueios de anunciantes / sem adblock ou amarras proprietarias.

ROUTER_IP="${1:-192.168.76.1}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "===> Instalando DoH (https-dns-proxy) no roteador $ROUTER_IP..."

# 1. Copiar biblioteca libev
echo "[1/5] Enviando libev..."
scp -O "$SCRIPT_DIR/libev.so.4.0.0" "root@$ROUTER_IP:/usr/lib/libev.so.4.0.0"
ssh "root@$ROUTER_IP" "ln -sf /usr/lib/libev.so.4.0.0 /usr/lib/libev.so.4 && ln -sf /usr/lib/libev.so.4.0.0 /usr/lib/libev.so"

# 2. Copiar binario https-dns-proxy
echo "[2/5] Enviando https-dns-proxy..."
scp -O "$SCRIPT_DIR/https-dns-proxy" "root@$ROUTER_IP:/usr/sbin/https-dns-proxy"
ssh "root@$ROUTER_IP" "chmod +x /usr/sbin/https-dns-proxy"

# 3. Configurar e habilitar servico
echo "[3/5] Configurando servico procd..."
scp -O "$SCRIPT_DIR/https-dns-proxy.config" "root@$ROUTER_IP:/etc/config/https-dns-proxy"
scp -O "$SCRIPT_DIR/https-dns-proxy.init" "root@$ROUTER_IP:/etc/init.d/https-dns-proxy"
ssh "root@$ROUTER_IP" "chmod +x /etc/init.d/https-dns-proxy && /etc/init.d/https-dns-proxy enable && /etc/init.d/https-dns-proxy restart"

# 4. Configurar dnsmasq para apontar para DoH local (5053 e 5054)
echo "[4/5] Integrando dnsmasq ao DoH..."
ssh "root@$ROUTER_IP" "
uci delete dhcp.@dnsmasq[0].server 2>/dev/null || true
uci add_list dhcp.@dnsmasq[0].server='127.0.0.1#5053'
uci add_list dhcp.@dnsmasq[0].server='127.0.0.1#5054'
uci set dhcp.@dnsmasq[0].noresolv='1'
uci set dhcp.@dnsmasq[0].allservers='1'
uci set dhcp.@dnsmasq[0].cachesize='5000'
uci del_list dhcp.lan.dhcp_option='6,1.1.1.1,8.8.8.8' 2>/dev/null || true
uci delete dhcp.lan.dns 2>/dev/null || true
uci commit dhcp
/etc/init.d/dnsmasq restart
"

# 5. Teste de resolucao e latencia
echo "[5/5] Testando resolucao DNS..."
ssh "root@$ROUTER_IP" "nslookup google.com 127.0.0.1"

echo "===> DoH instalado e ativo com sucesso!"
