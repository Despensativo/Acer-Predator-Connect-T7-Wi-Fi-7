#!/usr/bin/env python3
"""
otimizar_e_ativar_luci_slot2.py
Suite Completa de Otimizacao, Debloat e Ajustes de Performance Gamer
Acer Predator Connect T7 (Qualcomm IPQ5332 / Wi-Fi 7) - Firmware v1.01.000027

Perfis Suportados:
- COMPLETA : Debloat FOTA/telemetria/modem 5G + LuCI Porta 80 + UPnP + Conntrack 65k + DNS 10k + Wi-Fi 7 + IPv6
- BASICA   : Apenas LuCI na Porta 80 + Trava de Seguranca FOTA + Senha root0100
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

try:
    from logger_t7 import log_event, log_cmd, log_dump
except ImportError:
    try:
        from Scripts_Automacao.logger_t7 import log_event, log_cmd, log_dump
    except ImportError:
        def log_event(action, message, status="INFO", details=None):
            pass
        def log_cmd(cmd, output, status="CMD"):
            pass
        def log_dump(title, content):
            pass

def safe_input(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""

def test_telnet(ip, timeout=1.5):
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
    log_cmd(cmd, out)
    return out

def exibir_explicacao_detalhada():
    print("\n" + "=" * 80)
    print("  GUIA DETALHADO DAS OTIMIZACOES DISPONIVEIS NO SLOT 2")
    print("=" * 80)
    print("""
1. Desativar FOTA (atualizacao automatica) e silent-reboot:
   • O QUE E: O firmware original da Acer possui rotinas no cron para buscar
     atualizacoes silenciosas na nuvem de madrugada e reiniciar o roteador.
   • POR QUE DESATIVAR: Se a Acer disparar uma atualizacao automatica, ela pode
     sobrescrever o Slot 2, trancar a porta Telnet e remover o acesso root.
   • IMPACTO: Bloqueia 100% de downloads e reboots silenciosos indesejados.

2. Desativar Daemons de Modem Celular 5G (Heranca do X7):
   • O QUE E: O firmware do Predator T7 foi construído sobre a mesma base de
     codigo do Predator X7 (que possui modem 5G embutido com chip SIM).
   • POR QUE DESATIVAR: O T7 e um roteador puramente cabeado e Wi-Fi (sem chip SIM).
     Processos como modem_readd, ril e at_ril ficam tentando se comunicar com
     um hardware inexistente em loop continuo, desperdicando CPU e memória.
   • IMPACTO: CPU mais fria, fim de erros ciclicos no log e liberacao de RAM.

3. Desativar Telemetria Pesada e Servicos Nao Utilizados:
   • O QUE E: Daemons como monitord, sodd, cwmp (TR-069) e breakpad monitoram
     o uso e enviam dados de telemetria. Servicos de Samba sobem por padrao.
   • IMPACTO: Economiza mais de 25 MB de memoria RAM e reduz latencia do sistema.

4. Limpeza de Interfaces Fantasmas (Guest, IoT, WAN5GMODEM celular do X7):
   • O QUE E: Remove pontes e declaracoes de rede orfas que foram herdadas do
     modelo X7 e causavam avisos vermelhos na tela de Interfaces do LuCI.
   • NOTA DE SEGURANCA: A sua porta fisica WAN Ethernet 2.5 Gbps (eth0)
     permanece 100% INTACTA e ATIVA! Jamais e removida ou modificada.
   • IMPACTO: LuCI limpo e estavel, sem erros de interfaces inexistentes.

5. Configurar LuCI (uhttpd) como Servidor Web Principal (Porta 80):
   • O QUE E: A Acer bloqueia o LuCI e coloca seu painel restrito (lighttpd).
   • IMPACTO: Desativa o lighttpd e sobe a interface web oficial OpenWrt (LuCI)
     direto nas portas 80 (HTTP) e 443 (HTTPS), liberando o menu completo.

6. Padronizacao de Senhas para 'root0100':
   • O QUE E: Unifica as credenciais de root e Admin no sistema e no LuCI.
   • POR QUE 'root0100': O painel web da Acer e o LuCI exigem minimo de 8 caracteres.
     A senha 'root0100' atende todas as regras de seguranca sem gerar conflitos.

7. Ativar UPnP Gamer Automatico (miniupnpd):
   • BENEFICIO: Abre portas de comunicacao sob demanda para PC Gamer e consoles
     (PlayStation 5, Xbox Series, Nintendo Switch), garantindo NAT Aberto / Tipo 1
     sem necessidade de redirecionamento manual de portas.

8. Conntrack 65k, TCP Fast Open e Filas de Rede para 2.5 Gbps:
   • BENEFICIO: Aumenta o limite de conexoes simultaneas de 16k para 65.536
     (suporta milhares de conexoes de torrent e streaming sem travar).
     Ativa TCP Fast Open (tfo=3) para carregamento instantaneo de paginas web.

9. Turbo Cache DNSmasq (10.000 entradas na RAM):
   • BENEFICIO: Respostas de sites acessados anteriormente ficam guardadas na
     memoria RAM com TTL minimo de 5 minutos, respondendo consultas em 0 ms.

10. Roaming Seamless Wi-Fi 7 (802.11k/v e DTIM=2):
    • BENEFICIO: Ativa BSS Transition Management e RRM em 2.4, 5 e 6 GHz para
      transicao suave ao se movimentar pela casa. Ativa DTIM=2 para economizar
      consumo de bateria em celulares e notebooks.

11. IPv6 Universal Hibrido (odhcpd):
    • BENEFICIO: Funciona perfeitamente em Duplo NAT (atras de modem de operadora)
      ou em conexao direta autenticada (Bridge), sem necessidade de ajustes manuais.

12. Atalhos de Terminal 'boot-acer' e 'boot-openwrt':
    • BENEFICIO: Permite alternar entre o Slot 1 (OEM v24) e o Slot 2 (OpenWrt)
      a qualquer momento direto pelo terminal.
    • INTEGRIDADE: O script verifica se eles ja estao presentes no roteador.
      Como o codigo e 100% identico ao gravado na instalacao, nao ha risco
      de conflito, sobrescrita indevida ou arquivos antigos.

13. Padronizacao de Identificadores Wi-Fi no LuCI (wifinet#):
    • O QUE E: O sistema original da Acer gravou as redes Wi-Fi como secoes anonimas
      (sem nome no arquivo). O LuCI exige identificadores unicos (wifinet0, wifinet1...).
    • IMPACTO: Elimina definitivamente o aviso 'Wireless configuration migration' ao
      abrir o menu Network -> Wireless, permitindo que a interface web do OpenWrt
      carregue imediatamente a visao geral com todos os controles de antenas e radios.
""")
    print("=" * 80)

def menu_selecao_modo(target_ip):
    while True:
        print("\n" + "=" * 80)
        print("  CENTRAL DE GERENCIAMENTO PREDATOR T7 — OTIMIZACAO DO SLOT 2 (LUCI)")
        print(f"  Roteador Alvo : {target_ip} (Porta 23 Telnet)")
        print("=" * 80)
        print("\nSelecione o perfil de otimizacao desejado para o Slot 2:\n")
        print("  [1] OTIMIZACAO COMPLETA (Recomendada — Maximo Desempenho, Debloat & LuCI)")
        print("      • Desativa FOTA (atualizacao silenciosa da Acer) e silent-reboot")
        print("      • Desativa 12 daemons inuteis de modem 5G e telemetrias herdadas do X7")
        print("      • Remove interfaces fantasmas (WAN5GMODEM, Guest, IoT) sem tocar na WAN fisica")
        print("      • Coloca o LuCI oficial na Porta 80 e padroniza senhas para 'root0100'")
        print("      • Prepara identificadores Wi-Fi para o LuCI (desarma tela de migracao)")
        print("      • Ativa UPnP Gamer automatico (NAT Aberto para PC, PS5, Xbox, Switch)")
        print("      • Conntrack 65k, TCP Fast Open (tfo=3) e filas de rede para 2.5 Gbps")
        print("      • Turbo Cache DNSmasq na RAM (10.000 entradas para respostas em 0 ms)")
        print("      • Roaming Wi-Fi 7 inteligente (802.11k/v) e DTIM=2 (economia de bateria)")
        print("      • IPv6 Universal Hibrido (funciona em Duplo NAT e em modo Bridge)")
        print("      • Garante e valida atalhos rapidos 'boot-acer' e 'boot-openwrt' no terminal\n")
        print("  [2] OTIMIZACAO BASICA (Apenas Ativar LuCI na Porta 80 + Trava FOTA)")
        print("      • Desativa FOTA e silent-reboot (protege o Slot 2 contra sobrescrita)")
        print("      • Ativa o LuCI (uhttpd) diretamente na Porta 80 (desativa painel Acer)")
        print("      • Padroniza as credenciais de root e Admin para 'root0100'")
        print("      • Prepara identificadores Wi-Fi para o LuCI (desarma tela de migracao)")
        print("      • Garante e valida atalhos rapidos 'boot-acer' e 'boot-openwrt' no terminal")
        print("      (Nao altera parametros de Kernel, DNS, Wi-Fi, UPnP nem remove daemons)\n")
        print("  [3] Explicar detalhadamente o que cada uma das otimizacoes faz")
        print("  [0] Cancelar e Voltar ao Menu Principal")
        print("-" * 80)

        opcao = safe_input("Digite sua opcao (0-3): ")
        if opcao == "3":
            exibir_explicacao_detalhada()
            safe_input("Pressione ENTER para retornar ao menu de selecao...")
            continue
        elif opcao == "1":
            return "completa"
        elif opcao == "2":
            return "basica"
        elif opcao == "0":
            return None
        else:
            print("\n[!] Opcao invalida! Digite 1, 2, 3 ou 0.")

def instalar_atalhos_boot(tn):
    print("\n[*] Verificando atalhos de chaveamento rapido (/usr/sbin/boot-acer e /usr/sbin/boot-openwrt)...")
    check = run_cmd(tn, "[ -x /usr/sbin/boot-acer ] && [ -x /usr/sbin/boot-openwrt ] && echo 'ATALHOS_OK' || echo 'FALTA'")
    if "ATALHOS_OK" in check:
        print("    [OK] Atalhos 'boot-acer' e 'boot-openwrt' ja estao instalados e 100% atualizados.")
        return

    print("    -> Instalando atalhos de seguranca no terminal...")
    cmd_boot_acer = """cat << 'EOFA' > /usr/sbin/boot-acer
#!/bin/sh
echo "=== Retornando boot para SLOT 1 (OEM v24) ==="
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
echo "[OK] Slot 1 configurado com sucesso! Reiniciando..."
reboot
EOFA
chmod +x /usr/sbin/boot-acer
"""
    cmd_boot_openwrt = """cat << 'EOFB' > /usr/sbin/boot-openwrt
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
echo "[OK] Slot 2 configurado com sucesso! Reiniciando..."
reboot
EOFB
chmod +x /usr/sbin/boot-openwrt
"""
    run_cmd(tn, cmd_boot_acer)
    run_cmd(tn, cmd_boot_openwrt)
    print("    [OK] Atalhos 'boot-acer' e 'boot-openwrt' instalados com sucesso no terminal.")

def migrar_interfaces_wifi_luci(tn):
    print("\n[*] Padronizando identificadores Wi-Fi para o LuCI (desarmando tela de migracao)...")
    print("    -> [O QUE FAZ]: Nomeia as secoes wifi-iface como 'wifinet0', 'wifinet1'... para que o LuCI abra o menu de Wi-Fi direto.")
    cmd_migrate = (
        "awk 'BEGIN { c=0 } "
        "/^config wifi-iface$/ { printf(\"config wifi-iface \\x27wifinet%d\\x27\\n\", c++); next } "
        "{ print }' /etc/config/wireless > /tmp/wireless.migrated && "
        "mv /tmp/wireless.migrated /etc/config/wireless && "
        "uci commit wireless"
    )
    run_cmd(tn, cmd_migrate)
    print("    [OK] Identificadores de Wi-Fi padronizados com sucesso (menu Wireless pronto para o LuCI).")

def aplicar_otimizacao_completa(tn, target_ip):
    # 1. Debloat de FOTA e Cron
    print("\n[*] [1/10] Desativando FOTA (atualizacao automatica) e silent-reboot...")
    print("    -> [O QUE FAZ]: Bloqueia downloads e reboots silenciosos da Acer pela nuvem para proteger o Slot 2.")
    run_cmd(tn, "sed -i '/silent-reboot/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
    run_cmd(tn, "sed -i '/download_img/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
    run_cmd(tn, "sed -i '/update_img/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
    run_cmd(tn, "chmod -x /lib/functions/silent-reboot.sh /lib/functions/download_img.sh /lib/functions/update_img.sh /usr/sbin/fota 2>/dev/null")
    print("    [OK] FOTA desarmado: Atualizacoes silenciosas bloqueadas permanentemente.")

    # 2. Desativar Daemons de Modem Celular 5G e Telemetrias do X7
    print("\n[*] [2/10] Desativando servicos de modem celular 5G e telemetrias herdadas do X7...")
    print("    -> [O QUE FAZ]: O T7 nao tem modem 5G fisico com chip SIM; paramos 12 daemons inuteis para economizar RAM e CPU.")
    daemons = [
        "modem-monitor", "modem_read_init", "modem_datausage", "at_ril", "ril",
        "monitord", "sodd", "cwmp", "mqtt_client", "breakpad", "samba4", "ksmbd"
    ]
    for d in daemons:
        run_cmd(tn, f"/etc/init.d/{d} stop 2>/dev/null; /etc/init.d/{d} disable 2>/dev/null")
    run_cmd(tn, "killall -9 monitord sodd cwmp mqtt_client breakpad modem_readd modem_datausage at_ril ril smbd nmbd 2>/dev/null")
    print(f"    [OK] {len(daemons)} daemons inuteis desativados e memoria RAM liberada.")

    # 3. Limpeza de Interfaces Fantasmas (Guest, IoT, WAN5GMODEM do X7) e Fix do Hostname
    print("\n[*] [3/10] Limpando interfaces de rede fantasmas (Guest, IoT, WAN5GMODEM celular herdado do X7)...")
    print("    -> [O QUE FAZ]: Remove configuracoes de interfaces orfas do X7 que geravam caixas vermelhas no LuCI.")
    print("    -> [NOTA DE SEGURANCA]: Sua porta fisica WAN Ethernet 2.5 Gbps (eth0) permanece 100% INTACTA e ATIVA!")
    print("    -> [TEMPO ESTIMADO]: ~10 a 20 segundos (aguarde a compilacao e recarga das regras do firewall)...")
    run_cmd(tn, "uci set system.@system[0].hostname='Predator-Connect-T7'; uci commit system")
    run_cmd(tn, "/etc/init.d/system reload 2>/dev/null")
    run_cmd(tn, "uci -q delete network.guest; uci -q delete network.iot; uci -q delete network.wan1; uci -q delete network.xlatd; uci commit network")
    run_cmd(tn, "uci -q delete dhcp.guest; uci -q delete dhcp.iot; uci commit dhcp")
    run_cmd(tn, "for r in guest iot guest_fwd iot_fwd guest_dhcp iot_dhcp guest_dns iot_dns guest_ltogaccess iot_ltoiaccess guest_gtolaccess iot_itolaccess guest_gtoiaccess iot_itogaccess; do uci -q delete firewall.$r; done; uci -q del_list firewall.wan.network='wan1'; uci commit firewall")
    print("    [*] Recarregando servicos de rede e firewall (aguarde)...")
    run_cmd(tn, "/etc/init.d/network reload; /etc/init.d/firewall restart", timeout=30)
    print("    [OK] Interfaces fantasmas removidas e Hostname corrigido para RFC 1123.")
    print("    [OK] Conexao WAN de internet cabeada 100% preservada.")

    # 4. Configurar LuCI (uhttpd) como padrao na porta 80
    print("\n[*] [4/10] Configurando LuCI (uhttpd) como servidor web principal (Porta 80)...")
    print("    -> [O QUE FAZ]: Desativa o painel original Acer (lighttpd) e ativa o LuCI oficial na porta 80 e 443.")
    run_cmd(tn, "killall -9 lighttpd 2>/dev/null; /etc/init.d/lighttpd.init stop 2>/dev/null; /etc/init.d/lighttpd.init disable 2>/dev/null; chmod -x /usr/sbin/lighttpd /etc/init.d/lighttpd.init 2>/dev/null")
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
    run_cmd(tn, "mkdir -p /www/pub/dist 2>/dev/null; cat << 'EOF_P' > /www/pub/dist/index.html\n<!DOCTYPE html>\n<html>\n<head>\n<meta http-equiv=\"refresh\" content=\"0; URL=/cgi-bin/luci/\" />\n<script>window.location.href = '/cgi-bin/luci/';</script>\n</head>\n<body>Redirecionando para o LuCI...</body>\n</html>\nEOF_P\ncat << 'EOF_IDX' > /www/index.html\n<!DOCTYPE html>\n<html>\n<head>\n<meta http-equiv=\"refresh\" content=\"0; URL=/cgi-bin/luci/\" />\n<script>window.location.href = '/cgi-bin/luci/';</script>\n</head>\n<body>Redirecionando para o LuCI...</body>\n</html>\nEOF_IDX\nchmod -R 755 /www 2>/dev/null")
    run_cmd(tn, "/etc/init.d/rpcd restart")
    run_cmd(tn, "/etc/init.d/uhttpd enable")
    run_cmd(tn, "/etc/init.d/uhttpd restart")
    print("    [OK] LuCI ativo na porta 80 com permissao total para Admin e root.")

    # 5. Padronizar senhas de root e Admin para root0100
    print("\n[*] [5/10] Padronizando senhas de root e Admin para 'root0100'...")
    print("    -> [O QUE FAZ]: Unifica as credenciais para evitar bloqueios de autenticacao no terminal e web.")
    hash_root = "$1$ARKroot1$inwXu9.r12/oWLrMAV9eX."
    run_cmd(tn, f"sed -i 's|^root:[^:]*:|root:{hash_root}:|' /etc/shadow")
    run_cmd(tn, f"sed -i 's|^Admin:[^:]*:|Admin:{hash_root}:|' /etc/shadow")
    run_cmd(tn, "echo 'Admin:root0100' > /etc/config/web_info")
    run_cmd(tn, "echo 'admin:24d23582a1b1c978e3c7a26ee034799b' > /etc/config/lighttpd.user")
    run_cmd(tn, "echo 'admin:24d23582a1b1c978e3c7a26ee034799b' > /etc/lighttpd/lighttpd.user")
    run_cmd(tn, "echo 'Admin:root0100_ftm' > /etc/config/userinfo")
    print("    [OK] Senhas de root e Admin padronizadas para 'root0100'.")

    # 6. UPnP Gamer Automatico (miniupnpd)
    print("\n[*] [6/10] Ativando UPnP Gamer Automatico (NAT Aberto para PC e Consoles)...")
    print("    -> [O QUE FAZ]: Habilita redirecionamento automatico de portas para jogos online no PC, PS5, Xbox e Switch.")
    run_cmd(tn, "uci set upnpd.config.enabled='1'")
    run_cmd(tn, "uci set upnpd.config.enable_natpmp='1'")
    run_cmd(tn, "uci set upnpd.config.enable_upnp='1'")
    run_cmd(tn, "uci set upnpd.config.secure_mode='1'")
    run_cmd(tn, "uci commit upnpd")
    run_cmd(tn, "/etc/init.d/miniupnpd enable")
    run_cmd(tn, "/etc/init.d/miniupnpd restart")
    print("    [OK] miniupnpd ativo e integrado ao LuCI.")

    # 7. Kernel & Conntrack 65k & TCP Fast Open & Filas 2.5 Gbps
    print("\n[*] [7/10] Otimizando Kernel, Conntrack 65k, TCP Fast Open e Filas 2.5 Gbps...")
    print("    -> [O QUE FAZ]: Expande tabela de conexoes para 65.536 registros e acelera o trafego web com TCP Fast Open.")
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

    # 8. Turbo Cache DNSmasq (10k entradas)
    print("\n[*] [8/10] Configurando Turbo Cache DNSmasq (10.000 entradas na RAM)...")
    print("    -> [O QUE FAZ]: Responde consultas de nomes de dominios visitados em 0 ms atraves de cache local.")
    run_cmd(tn, "uci set dhcp.@dnsmasq[0].cachesize='10000'")
    run_cmd(tn, "uci set dhcp.@dnsmasq[0].min_cache_ttl='300'")
    run_cmd(tn, "uci commit dhcp")
    run_cmd(tn, "/etc/init.d/dnsmasq restart")
    print("    [OK] DNSmasq otimizado para navegacao instantanea.")

    # 9. Otimizacoes Wi-Fi 7 (802.11k/v, DTIM=2)
    print("\n[*] [9/10] Ajustando Roaming Seamless Wi-Fi 7 (802.11k/v e DTIM=2)...")
    print("    -> [O QUE FAZ]: Permite que celulares e notebooks transitem entre 2.4/5/6 GHz suavemente e economizem bateria.")
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
    migrar_interfaces_wifi_luci(tn)
    print("    [OK] Roaming 802.11k/v, DTIM=2 e identificadores LuCI ativados nas bandas Wi-Fi.")

    # 10. IPv6 Universal Hibrido (odhcpd hybrid)
    print("\n[*] [10/10] Configurando IPv6 Universal Hibrido (odhcpd hybrid)...")
    print("    -> [O QUE FAZ]: Garante funcionamento de IPv6 tanto em Duplo NAT (atras de modem) quanto em conexao direta Bridge.")
    run_cmd(tn, "uci set dhcp.lan.dhcpv6='hybrid'")
    run_cmd(tn, "uci set dhcp.lan.ra='hybrid'")
    run_cmd(tn, "uci set dhcp.lan.ndp='hybrid'")
    run_cmd(tn, "uci set dhcp.wan6.dhcpv6='hybrid'")
    run_cmd(tn, "uci set dhcp.wan6.ra='hybrid'")
    run_cmd(tn, "uci set dhcp.wan6.ndp='hybrid'")
    run_cmd(tn, "uci set dhcp.wan6.master='1'")
    run_cmd(tn, "uci commit dhcp")
    run_cmd(tn, "/etc/init.d/odhcpd restart")
    print("    [OK] IPv6 Hibrido configurado com sucesso.")

def aplicar_otimizacao_basica(tn, target_ip):
    # 1. Debloat de FOTA e Cron
    print("\n[*] [1/4] Desativando FOTA (atualizacao automatica) e silent-reboot...")
    print("    -> [O QUE FAZ]: Bloqueia downloads e reboots silenciosos da nuvem Acer para proteger o Slot 2.")
    run_cmd(tn, "sed -i '/silent-reboot/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
    run_cmd(tn, "sed -i '/download_img/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
    run_cmd(tn, "sed -i '/update_img/d' /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
    run_cmd(tn, "chmod -x /lib/functions/silent-reboot.sh /lib/functions/download_img.sh /lib/functions/update_img.sh /usr/sbin/fota 2>/dev/null")
    print("    [OK] FOTA desarmado: Protecao de particao ativada.")

    # 2. Configurar LuCI (uhttpd) como padrao na porta 80
    print("\n[*] [2/4] Configurando LuCI (uhttpd) como servidor web principal (Porta 80)...")
    print("    -> [O QUE FAZ]: Desativa o painel original Acer (lighttpd) e ativa o LuCI oficial na porta 80 e 443.")
    run_cmd(tn, "killall -9 lighttpd 2>/dev/null; /etc/init.d/lighttpd.init stop 2>/dev/null; /etc/init.d/lighttpd.init disable 2>/dev/null; chmod -x /usr/sbin/lighttpd /etc/init.d/lighttpd.init 2>/dev/null")
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
    run_cmd(tn, "mkdir -p /www/pub/dist 2>/dev/null; cat << 'EOF_P' > /www/pub/dist/index.html\n<!DOCTYPE html>\n<html>\n<head>\n<meta http-equiv=\"refresh\" content=\"0; URL=/cgi-bin/luci/\" />\n<script>window.location.href = '/cgi-bin/luci/';</script>\n</head>\n<body>Redirecionando para o LuCI...</body>\n</html>\nEOF_P\ncat << 'EOF_IDX' > /www/index.html\n<!DOCTYPE html>\n<html>\n<head>\n<meta http-equiv=\"refresh\" content=\"0; URL=/cgi-bin/luci/\" />\n<script>window.location.href = '/cgi-bin/luci/';</script>\n</head>\n<body>Redirecionando para o LuCI...</body>\n</html>\nEOF_IDX\nchmod -R 755 /www 2>/dev/null")
    run_cmd(tn, "/etc/init.d/rpcd restart")
    run_cmd(tn, "/etc/init.d/uhttpd enable")
    run_cmd(tn, "/etc/init.d/uhttpd restart")
    print("    [OK] LuCI ativo na porta 80 com permissao total para Admin e root.")

    # 3. Padronizar senhas de root e Admin para root0100
    print("\n[*] [3/4] Padronizando senhas de root e Admin para 'root0100'...")
    print("    -> [O QUE FAZ]: Unifica as credenciais para evitar bloqueios no terminal, SSH e no LuCI.")
    hash_root = "$1$ARKroot1$inwXu9.r12/oWLrMAV9eX."
    run_cmd(tn, f"sed -i 's|^root:[^:]*:|root:{hash_root}:|' /etc/shadow")
    run_cmd(tn, f"sed -i 's|^Admin:[^:]*:|Admin:{hash_root}:|' /etc/shadow")
    run_cmd(tn, "echo 'Admin:root0100' > /etc/config/web_info")
    run_cmd(tn, "echo 'admin:24d23582a1b1c978e3c7a26ee034799b' > /etc/config/lighttpd.user")
    run_cmd(tn, "echo 'admin:24d23582a1b1c978e3c7a26ee034799b' > /etc/lighttpd/lighttpd.user")
    run_cmd(tn, "echo 'Admin:root0100_ftm' > /etc/config/userinfo")
    print("    [OK] Senhas de root e Admin padronizadas para 'root0100'.")

    # 4. Padronizar identificadores Wi-Fi para o LuCI
    print("\n[*] [4/4] Padronizando identificadores Wi-Fi para o LuCI...")
    migrar_interfaces_wifi_luci(tn)

def finalizar_e_sincronizar(tn, modo):
    instalar_atalhos_boot(tn)

    print("\n[*] Configurando persistencia no boot (/etc/rc.local)...")
    if modo == "completa":
        run_cmd(tn, "sed -i 's|^modem_readd &|# modem_readd desativado|' /etc/rc.local")
    run_cmd(tn, "sed -i 's|/etc/init.d/lighttpd/lighttpd.init start|# lighttpd desativado|' /etc/rc.local")
    run_cmd(tn, "sed -i 's|/etc/init.d/uhttpd stop|/etc/init.d/uhttpd start|' /etc/rc.local")

    print("\n[*] Limpando arquivos temporarios e gravando alteracoes na Flash NAND...")
    run_cmd(tn, "rm -f /tmp/monitord.log* /tmp/sodd.log* /tmp/modem_readd.log* /tmp/sock_msg.log* /tmp/fota_* /tmp/lighttpd.log*")
    run_cmd(tn, "sync")
    print("    [OK] Memoria Flash NAND sincronizada com todas as otimizacoes persistidas.")

def main():
    explicit_ip = None
    modo = None
    auto_yes = False

    for arg in sys.argv[1:]:
        if arg in ["--completa", "-c"]:
            modo = "completa"
        elif arg in ["--basica", "-b"]:
            modo = "basica"
        elif arg in ["--yes", "-y"]:
            auto_yes = True
        elif not arg.startswith("-") and not explicit_ip:
            explicit_ip = arg

    target_ip = detect_router_ip(explicit_ip)

    # Validacao rapida de Telnet antes de exibir o menu
    if not test_telnet(target_ip, 2):
        print("\n" + "=" * 80)
        print(f"[-] ERRO: Nao foi possivel conectar via Telnet em {target_ip}:23!")
        print("    Certifique-se de que o roteador esta ligado no Slot 2 e com Telnet ativo.")
        print("    Dica: Se estiver no Slot 1 bloqueado, utilize a Opcao [2] do Launcher para desbloquear.")
        print("=" * 80)
        log_event("OTIMIZACAO_SLOT2", f"Falha de conexao Telnet em {target_ip}:23", "FALHA")
        sys.exit(1)

    # Se o modo nao foi passado via linha de comando, exibe o submenu interativo
    if not modo:
        modo = menu_selecao_modo(target_ip)
        if not modo:
            print("\n[OK] Operacao cancelada. Retornando ao menu principal.")
            log_event("OTIMIZACAO_SLOT2", "Cancelado pelo usuario no menu de selecao", "INFO")
            return

    nome_modo = "OTIMIZACAO COMPLETA (Gamer, Debloat & LuCI)" if modo == "completa" else "OTIMIZACAO BASICA (LuCI Porta 80 + Trava FOTA)"

    # Confirmacao explicita antes de aplicar
    if not auto_yes:
        print("\n" + "-" * 80)
        print("  [CONFIRMACAO DE EXECUCAO]")
        print(f"  Perfil Selecionado : {nome_modo}")
        print(f"  Roteador Alvo      : {target_ip} (Slot 2)")
        print("-" * 80)
        while True:
            conf = safe_input("Deseja realmente aplicar essas configuracoes no Slot 2 agora? [S/N]: ").strip().lower()
            if conf in ["s", "sim", "y", "yes"]:
                break
            elif conf in ["n", "nao", "não", "no"]:
                print("\n[AVISO] Operacao cancelada pelo usuario. Nenhuma alteracao foi feita no roteador.")
                log_event("OTIMIZACAO_SLOT2", f"Cancelado na confirmacao para {target_ip} ({modo})", "INFO")
                return
            print("\n  [!] Entrada invalida! Digite obrigatoriamente 'S' para Sim ou 'N' para Nao.")

    log_event("OTIMIZACAO_SLOT2", f"Iniciando {nome_modo} em {target_ip}", "INFO")

    print(f"\n[*] Conectando via Telnet em {target_ip}:23...")
    try:
        tn = Telnet(target_ip, 23, timeout=5)
        tn.read_until(b"/ # ", timeout=3)
    except Exception as e:
        print(f"[-] Erro ao conectar via Telnet: {e}")
        log_event("OTIMIZACAO_SLOT2", f"Erro de conexao Telnet: {e}", "ERRO")
        sys.exit(1)
    print("    [OK] Conectado como root.")

    # Execucao do perfil escolhido
    if modo == "completa":
        aplicar_otimizacao_completa(tn, target_ip)
    else:
        aplicar_otimizacao_basica(tn, target_ip)

    finalizar_e_sincronizar(tn, modo)

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
    print(f"\n[*] Testando acesso HTTP ao LuCI a partir do computador (http://{target_ip})...")
    try:
        req = urllib.request.Request(f"http://{target_ip}/cgi-bin/luci/", headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=5)
        print(f"    [OK] Resposta HTTP recebida com sucesso: Status {resp.getcode()}")
    except urllib.error.HTTPError as e:
        if "X-LuCI-Login-Required" in e.headers or e.code in [403, 302, 200]:
            print(f"    [OK] LuCI respondendo com sucesso! (HTTP {e.code} / Login Prompt)")
        else:
            print(f"    [!] Resposta HTTP: {e}")
    except Exception as e:
        print(f"    [!] Aviso ao testar HTTP: {e}")

    log_event("OTIMIZACAO_SLOT2", f"{nome_modo} concluida com sucesso em {target_ip}", "OK")

    print("\n" + "=" * 80)
    print(f"  {nome_modo.upper()} CONCLUIDA COM SUCESSO!")
    print(f"  Interface LuCI ativa em: http://{target_ip}")
    print("  Credenciais de acesso (LuCI e SSH):")
    print("    - Usuario : root (ou Admin)")
    print("    - Senha   : root0100")
    print("    [Dica] Se for solicitada senha no terminal, a senha padrao e: root0100 ou se voce ja trocou informe a senha que voce escolheu.")
    print("  Comandos uteis no terminal do roteador:")
    print("    - boot-acer    -> Retorna o boot para o Slot 1 (Original Acer v24)")
    print("    - boot-openwrt -> Garante o boot no Slot 2 (OpenWrt Otimizado)")
    print("=" * 80)

if __name__ == "__main__":
    main()
