#!/bin/sh
# Script de instalacao segura do hostapd/wpa_supplicant v2.11-devel no Acer Predator T7
ROUTER_IP="192.168.76.1"

echo "=== 1. Validando conexao com o roteador ==="
ssh root@${ROUTER_IP} "uname -a" || exit 1

echo "=== 2. Garantindo backups no roteador ==="
ssh root@${ROUTER_IP} "
[ ! -f /usr/sbin/hostapd.bak.20261013 ] && cp -p /usr/sbin/hostapd /usr/sbin/hostapd.bak.20261013
[ ! -f /usr/sbin/hostapd_cli.bak.20261013 ] && cp -p /usr/sbin/hostapd_cli /usr/sbin/hostapd_cli.bak.20261013
[ ! -f /usr/sbin/wpa_supplicant.bak.20261013 ] && cp -p /usr/sbin/wpa_supplicant /usr/sbin/wpa_supplicant.bak.20261013
[ ! -f /lib/wifi/hostapd.sh.bak.20261013 ] && cp -p /lib/wifi/hostapd.sh /lib/wifi/hostapd.sh.bak.20261013
echo 'Backups conferidos com sucesso.'
"

echo "=== 3. Enviando script hostapd.sh bi-compativel via SCP (-O) ==="
DIR="$(dirname "$0")"
scp -O "${DIR}/hostapd.sh.patched" root@${ROUTER_IP}:/lib/wifi/hostapd.sh

echo "=== 4. Enviando novos binarios e wrappers via SCP (-O) ==="
scp -O "${DIR}/qca-hapd-supp" root@${ROUTER_IP}:/usr/sbin/qca-hapd-supp
scp -O "${DIR}/hostapd_cli" root@${ROUTER_IP}:/usr/sbin/hostapd_cli
scp -O "${DIR}/hostapd" root@${ROUTER_IP}:/usr/sbin/hostapd
scp -O "${DIR}/wpa_supplicant" root@${ROUTER_IP}:/usr/sbin/wpa_supplicant

echo "=== 5. Ajustando permissoes executaveis ==="
ssh root@${ROUTER_IP} "
chmod 755 /usr/sbin/qca-hapd-supp
chmod 755 /usr/sbin/hostapd_cli
chmod 755 /usr/sbin/hostapd
chmod 755 /usr/sbin/wpa_supplicant
chmod 644 /lib/wifi/hostapd.sh
echo 'Permissoes aplicadas.'
"

echo "=== 6. Testando execucao limpa dos binarios no roteador ==="
ssh root@${ROUTER_IP} "
/usr/sbin/hostapd -v
/usr/sbin/hostapd_cli -v
/usr/sbin/wpa_supplicant -v
"

echo "=== Instalacao concluida com sucesso! ==="
