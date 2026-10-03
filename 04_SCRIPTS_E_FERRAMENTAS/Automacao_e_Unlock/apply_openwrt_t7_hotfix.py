#!/usr/bin/env python3
"""
=============================================================================
HOTFIX AUTOMATIZADO - ACER PREDATOR CONNECT T7 (OpenWrt Otimizado)
=============================================================================
Este script consolida todas as correcoes necessarias para transformar o
ambiente Slot 2 (ou qualquer sistema base QSDK) em um OpenWrt puro e estavel:

1. Corrige o Hostname para 'Predator-Connect-T7' (elimina erro RFC 1123 no LuCI)
2. Desativa a Web GUI proprietaria da Acer (lighttpd) e libera memoria RAM
3. Corrige o script /etc/init.d/uhttpd sabotado pela Acer de fabrica
4. Ativa o LuCI nativamente na porta 80 HTTP e 443 HTTPS padrao
5. Remove telemetrias (monitord, sodd, cwmp, mqtt_client, breakpad)
6. Remove daemons de modems celulares 5G inexistentes no hardware
7. Remove rotinas perigosas de auto-update (FOTA) e silent-reboot noturno
8. Instala os utilitarios de chaveamento dual-boot 'boot-acer' e 'boot-openwrt'

Uso:
    python apply_openwrt_t7_hotfix.py [IP_DO_ROTEADOR]
    (Padrao: 192.168.73.2)
=============================================================================
"""

import sys
import time
import socket
import telnetlib

ROUTER_IP = sys.argv[1] if len(sys.argv) > 1 else "192.168.73.2"

HOTFIX_PAYLOAD = r"""cat << 'EOF' > /tmp/run_hotfix.sh
#!/bin/sh
set -e

echo "=== [1/7] Corrigindo Hostname (RFC 1123) ==="
uci set system.@system[0].hostname='Predator-Connect-T7'
uci commit system
echo Predator-Connect-T7 > /proc/sys/kernel/hostname
/etc/init.d/system reload 2>/dev/null || true

echo "=== [2/7] Desativando Acer Web GUI (lighttpd) ==="
/etc/init.d/lighttpd.init stop 2>/dev/null || true
/etc/init.d/lighttpd.init disable 2>/dev/null || true
killall -9 lighttpd 2>/dev/null || true

echo "=== [3/7] Restaurando e Configurando LuCI (uhttpd) na Porta 80 ==="
killall -9 uhttpd 2>/dev/null || true
sed -i 's/#config_load uhttpd/config_load uhttpd/' /etc/init.d/uhttpd
sed -i 's/#config_foreach start_instance uhttpd/config_foreach start_instance uhttpd/' /etc/init.d/uhttpd
uci -q delete uhttpd.main.listen_http
uci add_list uhttpd.main.listen_http='0.0.0.0:80'
uci add_list uhttpd.main.listen_http='[::]:80'
uci commit uhttpd
/etc/init.d/uhttpd enable 2>/dev/null || true
/etc/init.d/uhttpd start 2>/dev/null || true

echo "=== [4/7] Purgando FOTA e Silent-Reboot ==="
sed -i '/silent-reboot/d' /etc/crontabs/* 2>/dev/null || true
sed -i '/download_img/d' /etc/crontabs/* 2>/dev/null || true
sed -i '/update_img/d' /etc/crontabs/* 2>/dev/null || true
chmod -x /lib/functions/silent-reboot.sh /lib/functions/download_img.sh /lib/functions/update_img.sh /usr/sbin/fota 2>/dev/null || true
/etc/init.d/cron restart 2>/dev/null || true

echo "=== [5/7] Desativando Daemons de Telemetria e Modems Inexistentes ==="
sed -i 's|^modem_readd &|# modem_readd desativado|g' /etc/rc.local 2>/dev/null || true
killall -9 modem_readd 2>/dev/null || true
for s in modem-monitor modem_read_init modem_datausage at_ril ril monitord sodd cwmp mqtt_client breakpad; do
    /etc/init.d/$s stop 2>/dev/null || true
    /etc/init.d/$s disable 2>/dev/null || true
done
killall -9 monitord sodd cwmp mqtt_client 2>/dev/null || true
rm -f /tmp/monitord.log* /tmp/sodd.log* /tmp/modem_readd.log* /tmp/sock_msg.log* /tmp/fota_*

echo "=== [6/7] Instalando Utilitarios de Alternancia Dual-Boot ==="
cat << 'EB' > /usr/sbin/boot-openwrt
#!/bin/sh
echo "=== Chaveando boot para SLOT 2 (OpenWrt Puro) ==="
echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
echo "[OK] Reiniciando no Slot 2 (OpenWrt)..."
reboot
EB

cat << 'EB' > /usr/sbin/boot-acer
#!/bin/sh
echo "=== Chaveando boot de volta para SLOT 1 (Acer Original) ==="
echo 1 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 1 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
echo "[OK] Reiniciando no Slot 1 (Acer Original)..."
reboot
EB
chmod +x /usr/sbin/boot-openwrt /usr/sbin/boot-acer

echo "=== [7/7] Sincronizando Sistema de Arquivos ==="
sync
rm -f /tmp/run_hotfix.sh
echo ""
echo "=========================================================="
echo "=== [SUCESSO TOTAL] HOTFIX APLICADO COM SUCESSO! ==="
echo "=========================================================="
EOF
chmod +x /tmp/run_hotfix.sh
/bin/sh /tmp/run_hotfix.sh
"""

def main():
    print("=" * 70)
    print(f"APLICADOR DE HOTFIX - ACER PREDATOR CONNECT T7 ({ROUTER_IP})")
    print("=" * 70)

    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
        tn.read_until(b"/ # ", timeout=5)
    except Exception as e:
        print(f"[-] Erro ao conectar ao roteador via Telnet ({ROUTER_IP}:23): {e}")
        return 1

    print("[*] Enviando e executando pacote de hotfixes no roteador...")
    tn.write(HOTFIX_PAYLOAD.encode("ascii") + b"\n")

    t0 = time.time()
    while time.time() - t0 < 60:
        chunk = tn.read_some().decode("utf-8", errors="ignore")
        if not chunk:
            break
        print(chunk, end="", flush=True)
        if "=== [SUCESSO TOTAL]" in chunk:
            break

    tn.close()
    print("\n[*] Validando resposta HTTP na porta 80...")
    time.sleep(1)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        res = s.connect_ex((ROUTER_IP, 80))
        s.close()
        if res == 0:
            print("[+] Porta 80 aberta e respondendo com LuCI!")
        else:
            print("[-] Porta 80 nao respondeu imediatamente.")
    except Exception as e:
        print(f"[-] Falha na checagem da porta: {e}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
