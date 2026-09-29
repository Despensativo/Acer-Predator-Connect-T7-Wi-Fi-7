#!/usr/bin/env python3
"""
apply_debloat.py
Executa a limpeza cirurgica de servicos desnecessarios no Acer Predator Connect T7:
- Desativa FOTA (atualizacao automatica perigosa) e silent-reboot no cron
- Desativa daemons de telemetria (monitord, sodd, cwmp, mqtt_client, breakpad)
- Desativa daemons de modem celular 5G que nao existem neste roteador
- Limpa logs de telemetria do /tmp
- Preserva 100% da interface Acer na porta 80 e LuCI na porta 8080
"""

import telnetlib
import time

ROUTER_IP = "192.168.73.2"

def main():
    print(f"[*] Conectando em {ROUTER_IP} via Telnet...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
    tn.read_until(b"/ # ", timeout=5)

    commands = [
        # 1. Desativar FOTA e auto-reboot no crontab
        "echo '[+] Limpando regras de auto-update e reboot silencioso do crontab...'",
        "sed -i '/silent-reboot/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null",
        "sed -i '/download_img/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null",
        "sed -i '/update_img/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null",
        "chmod -x /lib/functions/silent-reboot.sh /lib/functions/download_img.sh /lib/functions/update_img.sh /usr/sbin/fota 2>/dev/null",

        # 2. Desativar modem_readd do rc.local
        "echo '[+] Removendo modem_readd do rc.local...'",
        "sed -i 's|^modem_readd &|# modem_readd desativado|g' /etc/rc.local",
        "killall -9 modem_readd 2>/dev/null",

        # 3. Parar e desativar servicos de modem celular no boot
        "echo '[+] Desativando daemons de modem celular inexistentes...'",
        "/etc/init.d/modem-monitor stop 2>/dev/null; /etc/init.d/modem-monitor disable 2>/dev/null",
        "/etc/init.d/modem_read_init stop 2>/dev/null; /etc/init.d/modem_read_init disable 2>/dev/null",
        "/etc/init.d/modem_datausage stop 2>/dev/null; /etc/init.d/modem_datausage disable 2>/dev/null",
        "/etc/init.d/at_ril stop 2>/dev/null; /etc/init.d/at_ril disable 2>/dev/null",
        "/etc/init.d/ril stop 2>/dev/null; /etc/init.d/ril disable 2>/dev/null",

        # 4. Parar e desativar telemetrias (monitord, sodd, cwmp, mqtt)
        "echo '[+] Desativando daemons de telemetria pesada (monitord, sodd, cwmp, mqtt)...'",
        "/etc/init.d/monitord stop 2>/dev/null; /etc/init.d/monitord disable 2>/dev/null",
        "/etc/init.d/sodd stop 2>/dev/null; /etc/init.d/sodd disable 2>/dev/null",
        "/etc/init.d/cwmp stop 2>/dev/null; /etc/init.d/cwmp disable 2>/dev/null",
        "/etc/init.d/mqtt_client stop 2>/dev/null; /etc/init.d/mqtt_client disable 2>/dev/null",
        "/etc/init.d/breakpad stop 2>/dev/null; /etc/init.d/breakpad disable 2>/dev/null",
        "killall -9 monitord sodd cwmp mqtt_client 2>/dev/null",

        # 5. Limpar logs acumulados em /tmp
        "echo '[+] Limpando logs de telemetria acumulados no /tmp...'",
        "rm -f /tmp/monitord.log* /tmp/sodd.log* /tmp/modem_readd.log* /tmp/sock_msg.log* /tmp/fota_*",

        # 6. Recarregar cron e verificar processos
        "/etc/init.d/cron restart",
        "echo '[+] Status dos servicos restantes:'; ps | grep -E 'uhttpd|lighttpd|dropbear|telnetd'",
        "echo '[+] Espaco em /tmp apos limpeza:'; df -h /tmp",
        "echo '[+] Concluido!'"
    ]

    for c in commands:
        tn.write(c.encode("ascii") + b"\n")
        time.sleep(0.3)

    out = tn.read_until(b"[+] Concluido!", timeout=15).decode("utf-8", errors="ignore")
    print(out)
    tn.close()

if __name__ == "__main__":
    main()
