#!/bin/sh
# Script de rollback instantaneo para os binarios originais do Acer Predator T7
ROUTER_IP="192.168.76.1"

echo "=== Restaurando binarios originais a partir dos backups ==="
ssh root@${ROUTER_IP} "
if [ -f /usr/sbin/hostapd.bak.20261013 ]; then
    cp -p /usr/sbin/hostapd.bak.20261013 /usr/sbin/hostapd
fi
if [ -f /usr/sbin/hostapd_cli.bak.20261013 ]; then
    cp -p /usr/sbin/hostapd_cli.bak.20261013 /usr/sbin/hostapd_cli
fi
if [ -f /usr/sbin/wpa_supplicant.bak.20261013 ]; then
    cp -p /usr/sbin/wpa_supplicant.bak.20261013 /usr/sbin/wpa_supplicant
fi
chmod 755 /usr/sbin/hostapd /usr/sbin/hostapd_cli /usr/sbin/wpa_supplicant
echo 'Binarios originais restaurados com sucesso.'
/usr/sbin/hostapd -v
/usr/sbin/hostapd_cli -v
"
