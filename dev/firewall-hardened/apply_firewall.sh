#!/bin/sh
# Script para implantar a configuracao completa e blindada de Firewall no Acer Predator T7
ROUTER_IP="${1:-192.168.76.1}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "===> Aplicando firewall blindado no roteador $ROUTER_IP..."

scp -O "$SCRIPT_DIR/firewall.config" "root@$ROUTER_IP:/etc/config/firewall"
scp -O "$SCRIPT_DIR/firewall.user" "root@$ROUTER_IP:/etc/firewall.user"
scp -O "$SCRIPT_DIR/qca-nss-ecm" "root@$ROUTER_IP:/etc/firewall.d/qca-nss-ecm"
scp -O "$SCRIPT_DIR/99-predator-fixes" "root@$ROUTER_IP:/etc/firewall.d/99-predator-fixes"

ssh "root@$ROUTER_IP" "
chmod 755 /etc/firewall.d/qca-nss-ecm /etc/firewall.d/99-predator-fixes
/etc/init.d/firewall reload
"

echo "===> Firewall aplicado com sucesso!"
