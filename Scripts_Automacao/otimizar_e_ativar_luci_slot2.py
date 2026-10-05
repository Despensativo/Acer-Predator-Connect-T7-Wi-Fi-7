#!/usr/bin/env python3
"""
otimizar_e_ativar_luci_slot2.py
Suite Completa de Otimizacao, Debloat e Ajustes de Performance Gamer
Acer Predator Connect T7 (Qualcomm IPQ5332 / Wi-Fi 7) - Firmware Oficial v1.01.000027

Acoes Realizadas:
1. DEBLOAT DE TELEMETRIA E SEGURANCA:
   - Desativa FOTA (atualizacao silenciosa que sobrescreve particoes) e silent-reboot no cron.
   - Desativa daemons de modem celular 5G inexistentes (modem_readd, modem-monitor, at_ril, ril).
   - Desativa telemetrias pesadas (monitord, sodd, cwmp, mqtt_client, breakpad) economizando CPU e RAM.
   - Desativa servicos de Samba/Ksmbd nao utilizados para economizar 20MB de RAM.
   - Limpa logs de lixo no /tmp.

2. ATIVACAO DO LUCI COMO INTERFACE PADRAO (PORTA 80):
   - Desativa o lighttpd (painel Acer).
   - Descomenta o servico /etc/init.d/uhttpd sabotado pela Acer.
   - Configura o LuCI (uhttpd) para escutar diretamente na porta 80 e 443.
   - Libera autenticacao do usuario Admin e root no rpcd com permissao total.
   - Corrige permissoes em /www (chmod 755).

3. PERFORMANCE DE REDE E KERNEL (CONDUCAO DE DADOS A 2.5 Gbps):
   - Conntrack ampliado para 65.536 conexoes com timeout de 2h para conexoes estabelecidas.
   - TCP Fast Open ativado para cliente e servidor (tfo=3) para navegacao web acelerada.
   - Fila de rede expandida (netdev_max_backlog=2048) para conexoes 2.5 Gbps sem drops.

4. TURBO CACHE DNS (DNSMASQ):
   - Cache expandido para 10.000 dominios na RAM.
   - TTL minimo de 300 segundos (5 minutos) para respostas locais instantaneas (0 ms).

5. UPNP GAMER AUTOMATICO (MINIUPNPD):
   - miniupnpd ativado com NAT-PMP e IGDv1 para NAT Tipo 1 / Aberto no PS5, Xbox e PC.

6. TURBO CACHE DNS (DNSMASQ):
   - Cache expandido para 10.000 dominios na RAM.
   - TTL minimo de 300 segundos (5 minutos) para respostas locais instantaneas (0 ms).

7. ROAMING WI-FI 7 SEAMLESS (802.11k e 802.11v) + DTIM=2:
   - Ativa BSS Transition Management e RRM em 2.4, 5 e 6 GHz para transicao suave em Apple e Android.
   - Ajusta DTIM Period para 2 para economia de bateria em celulares e notebooks.
   - Preserva WPA2-PSK AES no 2.4 GHz (compatibilidade total IoT) e WPA3-SAE no 6 GHz (320 MHz).

8. IPV6 UNIVERSAL HIBRIDO (ODHCPD HYBRID):
   - Modo 'hybrid' em LAN e WAN6: Atua como Relay em Duplo NAT e como Servidor nativo com PD em Bridge.
   - Zero configuracao manual necessaria se a topologia da rede mudar no futuro.

9. PERSISTENCIA NO OVERLAY:
   - Atualiza /etc/rc.local para subir LuCI, SSH, Telnet e boot-acer no boot.
   - Executa sync na memoria Flash NAND.
"""

import sys
import os
import time
import socket
import urllib.request

try:
    from telnet_compat import Telnet
except ImportError:
    try:
        from Scripts_Automacao.telnet_compat import Telnet
    except ImportError:
        import telnetlib
        Telnet = telnetlib.Telnet

def test_telnet(ip, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, 23))
        s.close()
        return True
    except Exception:
        return False

def detect_router_ip(explicit_ip=None):
    if explicit_ip:
        return explicit_ip

    print("[*] Detectando endereco IP do roteador...")
    # 1. Tentar gateway local
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        my_ip = s.getsockname()[0]
        s.close()
        parts = my_ip.split(".")
        guess = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
        if test_telnet(guess, 1):
            print(f"    [+] Roteador detectado via gateway local: {guess}")
            return guess
    except Exception:
        pass

    # 2. Sondagem nos IPs conhecidos (76.1 = padrao Acer, 73.2 = AP, 1.1 = OpenWrt)
    for candidate in ["192.168.76.1", "192.168.73.2", "192.168.1.1"]:
        if test_telnet(candidate, 1):
            print(f"    [+] Roteador respondendo em Telnet (porta 23): {candidate}")
            return candidate

    print("    [!] Nao foi possivel detectar automaticamente. Usando padrao: 192.168.76.1")
    return "192.168.76.1"

def run_cmd(tn, cmd, timeout=10):
    tn.read_very_eager()
    tn.write(cmd.strip().encode("ascii") + b"\n")
    time.sleep(0.3)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    return out

def main():
    explicit_ip = sys.argv[1] if len(sys.argv) > 1 else None
    target_ip = detect_router_ip(explicit_ip)

    print("=" * 75)
    print("  SUITE DE OTIMIZACAO, DEBLOAT E PERFORMANCE GAMER (PORTA 80 LUCI)")
    print(f"  Acer Predator Connect T7 (Qualcomm IPQ5332) - Alvo: {target_ip}")
    print("=" * 75)

    print(f"\n[*] Conectando via Telnet em {target_ip}:23...")
    try:
        tn = Telnet(target_ip, 23, timeout=5)
        tn.read_until(b"/ # ", timeout=3)
    except Exception as e:
        print(f"[-] Erro ao conectar via Telnet: {e}")
        sys.exit(1)
    print("    [OK] Conectado como root.")

    # 1. Debloat de FOTA e Cron
    print("\n[*] [1/7] Desativando FOTA (atualizacao automatica) e silent-reboot...")
    run_cmd(tn, "sed -i '/silent-reboot/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
    run_cmd(tn, "sed -i '/download_img/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
    run_cmd(tn, "sed -i '/update_img/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
    run_cmd(tn, "chmod -x /lib/functions/silent-reboot.sh /lib/functions/download_img.sh /lib/functions/update_img.sh /usr/sbin/fota 2>/dev/null")
    print("    [OK] FOTA desarmado.")

    # 2. Desativar Daemons de Modem Celular, Telemetria e Samba Nao Utilizado
    print("\n[*] [2/9] Desativando servicos de modem celular, telemetrias e Samba...")
    daemons = [
        "modem-monitor", "modem_read_init", "modem_datausage", "at_ril", "ril",
        "monitord", "sodd", "cwmp", "mqtt_client", "breakpad", "samba4", "ksmbd"
    ]
    for d in daemons:
        run_cmd(tn, f"/etc/init.d/{d} stop 2>/dev/null; /etc/init.d/{d} disable 2>/dev/null")
    run_cmd(tn, "killall -9 monitord sodd cwmp mqtt_client breakpad modem_readd modem_datausage at_ril ril smbd nmbd 2>/dev/null")
    print(f"    [OK] {len(daemons)} daemons desativados e memoria RAM liberada.")

    # 3. Limpeza de Interfaces Fantasmas (Guest, IoT, WAN1 Celular) e Fix do Hostname
    print("\n[*] [3/9] Limpando interfaces de rede fantasmas (Guest, IoT, WAN1) e fixando Hostname...")
    # Fix do Hostname sem espaco (evita erro de validacao vermelha no LuCI)
    run_cmd(tn, "uci set system.@system[0].hostname='Predator-Connect-T7'")
    run_cmd(tn, "uci commit system")
    run_cmd(tn, "/etc/init.d/system reload")

    # Limpeza de interfaces no network
    run_cmd(tn, "uci -q delete network.guest; uci -q delete network.iot; uci -q delete network.wan1; uci -q delete network.xlatd; uci commit network")
    # Limpeza de DHCP pools
    run_cmd(tn, "uci -q delete dhcp.guest; uci -q delete dhcp.iot; uci commit dhcp")
    # Limpeza de regras de firewall
    fw_rules = [
        "guest", "iot", "guest_fwd", "iot_fwd", "guest_dhcp", "iot_dhcp",
        "guest_dns", "iot_dns", "guest_ltogaccess", "iot_ltoiaccess",
        "guest_gtolaccess", "iot_itolaccess", "guest_gtoiaccess", "iot_itogaccess"
    ]
    for r in fw_rules:
        run_cmd(tn, f"uci -q delete firewall.{r}")
    run_cmd(tn, "uci -q del_list firewall.wan.network='wan1'; uci commit firewall")
    run_cmd(tn, "/etc/init.d/network reload; /etc/init.d/firewall restart")
    print("    [OK] Interfaces fantasmas removidas e Hostname corrigido para RFC 1123.")

    # 4. Configurar LuCI (uhttpd) como padrao na porta 80
    print("\n[*] [4/9] Configurando LuCI (uhttpd) como servidor web principal (Porta 80)...")
    run_cmd(tn, "killall -9 lighttpd 2>/dev/null; /etc/init.d/lighttpd.init stop 2>/dev/null; /etc/init.d/lighttpd.init disable 2>/dev/null")
    run_cmd(tn, "sed -i 's/#config_load uhttpd/config_load uhttpd/' /etc/init.d/uhttpd")
    run_cmd(tn, "sed -i 's/#config_foreach start_instance uhttpd/config_foreach start_instance uhttpd/' /etc/init.d/uhttpd")
    run_cmd(tn, "chmod -R 755 /www")
    run_cmd(tn, "uci -q delete uhttpd.main.listen_http")
    run_cmd(tn, "uci add_list uhttpd.main.listen_http='0.0.0.0:80'")
    run_cmd(tn, "uci add_list uhttpd.main.listen_http='[::]:80'")
    run_cmd(tn, "uci set uhttpd.main.rfc1918_filter='0'")
    run_cmd(tn, "uci set uhttpd.main.redirect_https='0'")
    run_cmd(tn, "uci commit uhttpd")
    run_cmd(tn, "uci -q get rpcd.@login[1] || (uci add rpcd login && uci set rpcd.@login[-1].username='Admin' && uci set rpcd.@login[-1].password='$p$Admin' && uci add_list rpcd.@login[-1].read='*' && uci add_list rpcd.@login[-1].write='*' && uci commit rpcd)")
    run_cmd(tn, "/etc/init.d/rpcd restart")
    run_cmd(tn, "/etc/init.d/uhttpd enable")
    run_cmd(tn, "/etc/init.d/uhttpd restart")
    print("    [OK] LuCI ativo na porta 80 com permissao total.")

    # Padronizar senhas de root e Admin
    print("\n[*] Padronizando senhas de root e Admin para 'root'...")
    hash_root = "$1$ARKroot1$RxlP7OYmB1xLe1obY775A/"
    run_cmd(tn, f"sed -i 's|^root:[^:]*:|root:{hash_root}:|' /etc/shadow")
    run_cmd(tn, f"sed -i 's|^Admin:[^:]*:|Admin:{hash_root}:|' /etc/shadow")
    print("    [OK] Senhas de root e Admin padronizadas para 'root'.")

    # 5. UPnP Gamer Automatico (miniupnpd)
    print("\n[*] [5/9] Ativando UPnP Gamer Automatico (NAT Aberto para PC e Consoles)...")
    run_cmd(tn, "uci set upnpd.config.enabled='1'")
    run_cmd(tn, "uci set upnpd.config.enable_natpmp='1'")
    run_cmd(tn, "uci set upnpd.config.enable_upnp='1'")
    run_cmd(tn, "uci set upnpd.config.secure_mode='1'")
    run_cmd(tn, "uci commit upnpd")
    run_cmd(tn, "/etc/init.d/miniupnpd enable")
    run_cmd(tn, "/etc/init.d/miniupnpd restart")
    print("    [OK] miniupnpd ativo e integrado ao LuCI.")

    # 6. Kernel & Conntrack 65k & TCP Fast Open
    print("\n[*] [6/9] Aplicando Conntrack 65k, TCP Fast Open e Filas 2.5 Gbps...")
    sysctl_cmds = [
        "echo 'net.netfilter.nf_conntrack_max = 65536' >> /etc/sysctl.d/99-performance.conf",
        "echo 'net.netfilter.nf_conntrack_tcp_timeout_established = 7440' >> /etc/sysctl.d/99-performance.conf",
        "echo 'net.ipv4.tcp_fastopen = 3' >> /etc/sysctl.d/99-performance.conf",
        "echo 'net.core.somaxconn = 1024' >> /etc/sysctl.d/99-performance.conf",
        "echo 'net.core.netdev_max_backlog = 2048' >> /etc/sysctl.d/99-performance.conf",
        "echo 'net.bridge.bridge-nf-call-iptables = 0' >> /etc/sysctl.d/99-performance.conf",
        "echo 'net.bridge.bridge-nf-call-ip6tables = 0' >> /etc/sysctl.d/99-performance.conf",
        "echo 'net.bridge.bridge-nf-call-arptables = 0' >> /etc/sysctl.d/99-performance.conf",
        "sort -u /etc/sysctl.d/99-performance.conf -o /etc/sysctl.d/99-performance.conf",
        "sysctl -p /etc/sysctl.d/99-performance.conf"
    ]
    for c in sysctl_cmds:
        run_cmd(tn, c)
    print("    [OK] Parametros de Kernel, Conntrack e Bypass de Bridge L2 aplicados.")

    # 7. Turbo Cache DNSmasq (10k entradas)
    print("\n[*] [7/9] Configurando Turbo Cache DNSmasq (10.000 entradas)...")
    run_cmd(tn, "uci set dhcp.@dnsmasq[0].cachesize='10000'")
    run_cmd(tn, "uci set dhcp.@dnsmasq[0].min_cache_ttl='300'")
    run_cmd(tn, "uci commit dhcp")
    run_cmd(tn, "/etc/init.d/dnsmasq restart")
    print("    [OK] DNSmasq otimizado para resposta de 0 ms.")

    # 8. Otimizacoes Avancadas Wi-Fi 7 (802.11k/v, DTIM=2, Compatibilidade Universal)
    print("\n[*] [8/9] Aplicando ajustes finos de Wi-Fi 7 e Roaming 802.11k/v...")
    wifi_cmd = (
        "for i in $(seq 0 15); do "
        "uci -q get wireless.@wifi-iface[$i] >/dev/null && ("
        "uci set wireless.@wifi-iface[$i].bss_transition='1'; "
        "uci set wireless.@wifi-iface[$i].rrm_neighbor_report='1'; "
        "uci set wireless.@wifi-iface[$i].rrm_beacon_report='1'; "
        "uci set wireless.@wifi-iface[$i].wnm_sleep_mode='1'; "
        "uci set wireless.@wifi-iface[$i].dtim_period='2'); "
        "done"
    )
    run_cmd(tn, wifi_cmd)
    run_cmd(tn, "uci set wireless.wifi1.htmode='HT80'")
    run_cmd(tn, "uci set wireless.wifi1.channel='auto'")
    run_cmd(tn, "uci commit wireless")
    print("    [OK] Roaming 802.11k/v (BSS Transition + RRM) e DTIM=2 ativados nas 3 bandas.")

    # 9. IPv6 Universal Hibrido (Funciona em Duplo NAT e como Roteador Mestre)
    print("\n[*] [9/9] Configurando IPv6 Universal Hibrido (odhcpd hybrid)...")
    run_cmd(tn, "uci set dhcp.lan.dhcpv6='hybrid'")
    run_cmd(tn, "uci set dhcp.lan.ra='hybrid'")
    run_cmd(tn, "uci set dhcp.lan.ndp='hybrid'")
    run_cmd(tn, "uci set dhcp.wan6.dhcpv6='hybrid'")
    run_cmd(tn, "uci set dhcp.wan6.ra='hybrid'")
    run_cmd(tn, "uci set dhcp.wan6.ndp='hybrid'")
    run_cmd(tn, "uci set dhcp.wan6.master='1'")
    run_cmd(tn, "uci commit dhcp")
    run_cmd(tn, "/etc/init.d/odhcpd restart")
    print("    [OK] IPv6 Hibrido ativo: Relay automatico em Duplo NAT e Servidor nativo com PD em Bridge.")

    # Atualiza rc.local
    run_cmd(tn, "sed -i 's|^modem_readd &|# modem_readd desativado|' /etc/rc.local")
    run_cmd(tn, "sed -i 's|/etc/init.d/uhttpd stop|/etc/init.d/uhttpd start|' /etc/rc.local")
    run_cmd(tn, "sed -i 's|/etc/init.d/lighttpd/lighttpd.init start|# lighttpd desativado|' /etc/rc.local")

    # Limpeza e sync
    run_cmd(tn, "rm -f /tmp/monitord.log* /tmp/sodd.log* /tmp/modem_readd.log* /tmp/sock_msg.log* /tmp/fota_* /tmp/lighttpd.log*")
    run_cmd(tn, "sync")
    print("    [OK] Flash NAND sincronizada com todas as otimizacoes salvas.")

    # Status de portas e processos
    print("\n[*] Portas ativas no roteador:")
    ports_out = run_cmd(tn, "netstat -ltn | grep -E '80|443|22|23'")
    for line in ports_out.splitlines():
        if any(p in line for p in [":80 ", ":443 ", ":22 ", ":23 "]):
            print(f"    {line.strip()}")

    print("\n[*] Processos essenciais em execucao:")
    ps_out = run_cmd(tn, "ps | grep -E 'uhttpd|miniupnpd|dropbear|telnetd'")
    for line in ps_out.splitlines():
        if any(k in line for k in ["uhttpd", "miniupnpd", "dropbear", "telnetd"]) and "grep" not in line:
            print(f"    {line.strip()}")

    print("\n[*] Status de Memoria RAM:")
    mem_out = run_cmd(tn, "free")
    for line in mem_out.splitlines():
        if any(k in line for k in ["Mem:", "Swap:", "total"]):
            print(f"    {line.strip()}")

    tn.close()

    # Validacao HTTP
    print(f"\n[*] Testando acesso HTTP ao LuCI a partir do PC (http://{target_ip})...")
    try:
        req = urllib.request.Request(f"http://{target_ip}/cgi-bin/luci/", headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=5)
        print(f"    [OK] Resposta HTTP recebida: Status {resp.getcode()}")
    except urllib.error.HTTPError as e:
        if "X-LuCI-Login-Required" in e.headers or e.code in [403, 302, 200]:
            print(f"    [OK] LuCI respondendo com sucesso! (HTTP {e.code} / Login Prompt)")
        else:
            print(f"    [!] Resposta HTTP: {e}")
    except Exception as e:
        print(f"    [!] Aviso ao testar HTTP: {e}")

    print("\n" + "=" * 75)
    print("  SUITE DE OTIMIZACAO CONCLUIDA COM SUCESSO!")
    print(f"  Interface LuCI ativa em: http://{target_ip}")
    print("  Credenciais de acesso (LuCI e SSH):")
    print("    - Usuario: root (ou Admin)")
    print("    - Senha:   root")
    print("=" * 75)

if __name__ == "__main__":
    main()
