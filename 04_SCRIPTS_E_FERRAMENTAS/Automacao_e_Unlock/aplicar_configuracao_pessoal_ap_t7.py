#!/usr/bin/env python3
"""
aplicar_configuracao_pessoal_ap_t7.py
Configuracao Pessoal de Ponto de Acesso de Alta Performance (Dumb AP / Mesh AP)
Acer Predator Connect T7 (Qualcomm IPQ5332 / Wi-Fi 7) - Slot 2 (Firmware v27)

Acoes Executadas:
1. REDES WI-FI PERSONALIZADAS:
   - 6 GHz (Qualcomm QCN9224): 320 MHz (EHT320 / 5.76 Gbps), WPA3-SAE (SSID e senha configuráveis).
   - 5 GHz (Qualcomm QCN6432): 80 MHz (HT80 / 1.44 Gbps, 4 antenas beamforming 8.38 dBi), WPA2-PSK AES.
   - 2.4 GHz: Desativado (disabled 1).
   - MLO e Guest: Desativados (disabled 1).
   - Roaming: 802.11k/v (BSS Transition + RRM) e DTIM=2 ativos nas redes ativas.

2. ARQUITETURA DE REDE (PONTO DE ACESSO):
   - Porta WAN 2.5 Gbps (eth0) integrada a ponte br-lan junto com eth1.1 e eth1.2.
   - Interfaces WAN e WAN6 removidas (todas as 4 portas viram switch LAN direto).
   - IP Estatico de Gerencia: 192.168.73.2 / Mascara 255.255.255.0.
   - Gateway e DNS: 192.168.73.1 (e 1.1.1.1).

3. SERVICOS DESATIVADOS NO AP:
   - Servidor DHCPv4 desativado (ignore 1).
   - Servidor DHCPv6 e RA desativados (disabled).
   - Firewall ajustado para forward ACCEPT em toda a LAN.
"""

import os
import telnetlib
import time
import sys
import socket

ROUTER_OLD_IP = "192.168.76.1"
ROUTER_NEW_IP = "192.168.73.2"
GATEWAY_IP   = "192.168.73.1"

# Credenciais Padrao (Substituidas automaticamente por dados_pessoais.env se existir)
WIFI_SSID_6G = "Predator_T7_7G"
WIFI_SSID_5G = "Predator_T7_5G"
WIFI_KEY     = "Predator1234@"

_env_path = os.path.join(os.path.dirname(__file__), "dados_pessoais.env")
if os.path.isfile(_env_path):
    print(f"[*] Carregando credenciais locais de '{os.path.basename(_env_path)}'...")
    with open(_env_path, "r", encoding="utf-8") as _ef:
        for _l in _ef:
            _l = _l.strip()
            if _l and not _l.startswith("#") and "=" in _l:
                _k, _v = _l.split("=", 1)
                _k, _v = _k.strip(), _v.strip()
                if _k == "WIFI_SSID_6G": WIFI_SSID_6G = _v
                elif _k == "WIFI_SSID_5G": WIFI_SSID_5G = _v
                elif _k == "WIFI_KEY": WIFI_KEY = _v
    print(f"    [OK] Configurado: 6G='{WIFI_SSID_6G}', 5G='{WIFI_SSID_5G}'")
else:
    # Modo interativo inteligente se executado no terminal
    if sys.stdin.isatty():
        print("\n[*] Arquivo 'dados_pessoais.env' nao encontrado.")
        print("    Deseja personalizar os nomes e senha das redes Wi-Fi agora? (ou pressione ENTER para usar os padroes)")
        try:
            inp_6g = input(f"    Nome da rede Wi-Fi 7 (6 GHz) [{WIFI_SSID_6G}]: ").strip()
            if inp_6g: WIFI_SSID_6G = inp_6g
            inp_5g = input(f"    Nome da rede Wi-Fi 6 (5 GHz) [{WIFI_SSID_5G}]: ").strip()
            if inp_5g: WIFI_SSID_5G = inp_5g
            inp_key = input(f"    Senha do Wi-Fi (minimo 8 caracteres) [{WIFI_KEY}]: ").strip()
            if inp_key: WIFI_KEY = inp_key

            if len(WIFI_KEY) < 8:
                print("[-] ERRO: A senha do Wi-Fi deve ter no minimo 8 caracteres!")
                sys.exit(1)

            salvar = input("    Deseja salvar essas credenciais em 'dados_pessoais.env' para uso futuro? [S/n]: ").strip().lower()
            if salvar != 'n':
                with open(_env_path, "w", encoding="utf-8") as _ef:
                    _ef.write(f"# Credenciais Pessoais do Ponto de Acesso (Ignorado pelo Git)\n")
                    _ef.write(f"WIFI_SSID_6G={WIFI_SSID_6G}\n")
                    _ef.write(f"WIFI_SSID_5G={WIFI_SSID_5G}\n")
                    _ef.write(f"WIFI_KEY={WIFI_KEY}\n")
                print(f"    [OK] Salvo com sucesso em '{_env_path}'.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperacao cancelada pelo usuario.")
            sys.exit(0)

if len(WIFI_KEY) < 8:
    print("[-] ERRO: Senha do Wi-Fi invalida. O padrao WPA2/WPA3 exige no minimo 8 caracteres.")
    sys.exit(1)

def run_cmd(tn, cmd, timeout=5):
    tn.read_very_eager()
    tn.write(cmd.strip().encode("ascii") + b"\n")
    time.sleep(0.3)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    return out

def main():
    target_ip = sys.argv[1] if len(sys.argv) > 1 else ROUTER_OLD_IP

    print("=" * 75)
    print("  CONFIGURACAO PESSOAL: ACER PREDATOR T7 COMO ACCESS POINT WI-FI 7")
    print(f"  Alvo Atual: {target_ip} -> Novo IP Apos Boot: {ROUTER_NEW_IP}")
    print("=" * 75)

    print(f"\n[*] Conectando via Telnet em {target_ip}:23...")
    try:
        tn = telnetlib.Telnet(target_ip, 23, timeout=5)
        tn.read_until(b"/ # ", timeout=3)
    except Exception as e:
        print(f"[-] Erro ao conectar via Telnet em {target_ip}: {e}")
        sys.exit(1)
    print("    [OK] Conectado como root.")

    # 1. Configuracao Wi-Fi (Wi-Fi 7 / 6 GHz + Wi-Fi 6 / 5 GHz + Aceleracoes Avancadas)
    print("\n[*] [1/4] Configurando redes Wi-Fi e aceleracoes de hardware (TWT, Puncturing, BSS Color)...")
    # 6 GHz -> WIFI_SSID_6G (Wi-Fi 7 / 320 MHz / WPA3-SAE)
    run_cmd(tn, "uci set wireless.wifi2.disabled='0'")
    run_cmd(tn, "uci set wireless.wifi2.htmode='HT320'")
    run_cmd(tn, "uci set wireless.wifi2.channel='auto'")
    run_cmd(tn, "uci set wireless.wifi2.twt_responder='1'")       # Target Wake Time (Economia de bateria)
    run_cmd(tn, "uci set wireless.wifi2.he_puncturing='1'")      # Preamble Puncturing Wi-Fi 6
    run_cmd(tn, "uci set wireless.wifi2.eht_puncturing='1'")     # Preamble Puncturing Wi-Fi 7 (320 MHz estavel)
    run_cmd(tn, "uci set wireless.wifi2.bss_color='auto'")       # BSS Coloring (Filtro de interferencia)
    run_cmd(tn, "uci set wireless.wifi2.he_bss_color='1'")
    run_cmd(tn, "uci set wireless.wifi2.he_spatial_reuse='1'")
    run_cmd(tn, "uci set wireless.wifi2.he_su_beamformer='1'")   # Beamforming Direcional
    run_cmd(tn, "uci set wireless.wifi2.he_mu_beamformer='1'")
    run_cmd(tn, f"uci set wireless.wifinet11.ssid='{WIFI_SSID_6G}'")
    run_cmd(tn, f"uci set wireless.wifinet11.key='{WIFI_KEY}'")
    run_cmd(tn, f"uci set wireless.wifinet11.sae_password='{WIFI_KEY}'")
    run_cmd(tn, "uci set wireless.wifinet11.encryption='ccmp'")
    run_cmd(tn, "uci set wireless.wifinet11.ieee80211w='2'")     # PMF Obrigatorio para WPA3
    run_cmd(tn, "uci set wireless.wifinet11.sae='1'")
    run_cmd(tn, "uci set wireless.wifinet11.disabled='0'")
    run_cmd(tn, "uci set wireless.wifinet11.bss_transition='1'") # Roaming 802.11v
    run_cmd(tn, "uci set wireless.wifinet11.rrm_neighbor_report='1'") # Roaming 802.11k
    run_cmd(tn, "uci set wireless.wifinet11.rrm_beacon_report='1'")
    run_cmd(tn, "uci set wireless.wifinet11.wnm_sleep_mode='1'")
    run_cmd(tn, "uci set wireless.wifinet11.dtim_period='2'")

    # 5 GHz -> WIFI_SSID_5G (Wi-Fi 6 / 80 MHz / WPA2-AES / Fast Transition 802.11r)
    run_cmd(tn, "uci set wireless.wifi1.disabled='0'")
    run_cmd(tn, "uci set wireless.wifi1.htmode='HT80'")
    run_cmd(tn, "uci set wireless.wifi1.channel='auto'")
    run_cmd(tn, "uci set wireless.wifi1.twt_responder='1'")       # Target Wake Time
    run_cmd(tn, "uci set wireless.wifi1.he_puncturing='1'")      # Preamble Puncturing
    run_cmd(tn, "uci set wireless.wifi1.bss_color='auto'")       # BSS Coloring
    run_cmd(tn, "uci set wireless.wifi1.he_bss_color='1'")
    run_cmd(tn, "uci set wireless.wifi1.he_spatial_reuse='1'")
    run_cmd(tn, "uci set wireless.wifi1.he_su_beamformer='1'")   # Beamforming 4x4
    run_cmd(tn, "uci set wireless.wifi1.he_mu_beamformer='1'")
    run_cmd(tn, "uci set wireless.wifi1.he_ul_ofdma='1'")        # OFDMA Multi-usuario
    run_cmd(tn, "uci set wireless.wifi1.he_ul_mumimo='1'")
    run_cmd(tn, f"uci set wireless.wifinet7.ssid='{WIFI_SSID_5G}'")
    run_cmd(tn, f"uci set wireless.wifinet7.key='{WIFI_KEY}'")
    run_cmd(tn, "uci set wireless.wifinet7.encryption='psk2+aes'")
    run_cmd(tn, "uci set wireless.wifinet7.ieee80211w='1'")      # PMF Adaptativo
    run_cmd(tn, "uci set wireless.wifinet7.disabled='0'")
    run_cmd(tn, "uci set wireless.wifinet7.bss_transition='1'")  # 802.11v
    run_cmd(tn, "uci set wireless.wifinet7.rrm_neighbor_report='1'") # 802.11k
    run_cmd(tn, "uci set wireless.wifinet7.rrm_beacon_report='1'")
    run_cmd(tn, "uci set wireless.wifinet7.ieee80211r='1'")      # Fast Transition 802.11r (<50ms roaming)
    run_cmd(tn, "uci set wireless.wifinet7.mobility_domain='a1b2'")
    run_cmd(tn, "uci set wireless.wifinet7.ft_over_ds='1'")
    run_cmd(tn, "uci set wireless.wifinet7.ft_psk_generate_local='1'")
    run_cmd(tn, "uci set wireless.wifinet7.wnm_sleep_mode='1'")
    run_cmd(tn, "uci set wireless.wifinet7.dtim_period='2'")

    # 2.4 GHz e MLO -> Desativados
    run_cmd(tn, "uci set wireless.wifi0.disabled='1'")
    run_cmd(tn, "uci set wireless.wifinet3.disabled='1'")
    run_cmd(tn, "uci set wireless.wifinet2.disabled='1'")
    run_cmd(tn, "uci set wireless.wifinet6.disabled='1'")
    run_cmd(tn, "uci set wireless.wifinet10.disabled='1'")
    run_cmd(tn, "uci commit wireless")
    print(f"    [OK] Wi-Fi configurado: 6 GHz ({WIFI_SSID_6G} @ 5.76 Gbps), 5 GHz ({WIFI_SSID_5G} @ 1.44 Gbps com 802.11r).")
    print("    [OK] Recursos ativos: TWT (bateria), Puncturing (320MHz), BSS Color, Beamforming 4x4.")

    # 2. Arquitetura de Rede (Ponto de Acesso / Ponte WAN + LAN)
    print("\n[*] [2/4] Integrando porta WAN (eth0) a LAN e fixando IP 192.168.73.2...")
    run_cmd(tn, "uci set network.lan.ifname='eth0 eth1.1 eth1.2'")
    run_cmd(tn, f"uci set network.lan.ipaddr='{ROUTER_NEW_IP}'")
    run_cmd(tn, "uci set network.lan.netmask='255.255.255.0'")
    run_cmd(tn, f"uci set network.lan.gateway='{GATEWAY_IP}'")
    run_cmd(tn, "uci -q delete network.lan.dns")
    run_cmd(tn, f"uci add_list network.lan.dns='{GATEWAY_IP}'")
    run_cmd(tn, "uci add_list network.lan.dns='1.1.1.1'")
    run_cmd(tn, "uci -q delete network.wan")
    run_cmd(tn, "uci -q delete network.wan6")
    run_cmd(tn, "uci commit network")
    print("    [OK] Rede configurada: eth0 anexada a br-lan, IP 192.168.73.2, Gateway 192.168.73.1.")

    # 3. Desativar DHCPv4/DHCPv6 e Otimizar Sysctl / Kernel Quad-Core
    print("\n[*] [3/4] Desativando DHCP e calibrando Kernel Multicore / Bridge L2...")
    run_cmd(tn, "uci set dhcp.lan.ignore='1'")
    run_cmd(tn, "uci set dhcp.lan.dhcpv6='disabled'")
    run_cmd(tn, "uci set dhcp.lan.ra='disabled'")
    run_cmd(tn, "uci set dhcp.lan.ndp='disabled'")
    run_cmd(tn, "uci -q set dhcp.@dnsmasq[0].allservers='1'")     # Turbo DNS (Consultas paralelas)
    run_cmd(tn, "uci commit dhcp")

    # Ajuste de Firewall do AP
    run_cmd(tn, "uci set firewall.@zone[0].forward='ACCEPT'")
    run_cmd(tn, "uci -q delete firewall.wan")
    run_cmd(tn, "uci commit firewall")
    run_cmd(tn, "/etc/init.d/firewall stop 2>/dev/null; /etc/init.d/firewall disable 2>/dev/null")
    run_cmd(tn, "/etc/init.d/dnsmasq stop 2>/dev/null; /etc/init.d/dnsmasq disable 2>/dev/null")
    run_cmd(tn, "/etc/init.d/odhcpd stop 2>/dev/null; /etc/init.d/odhcpd disable 2>/dev/null")

    # Calibracao de Performance do Kernel e Bridge Layer-2 pura
    sysctl_conf = \"\"\"net.bridge.bridge-nf-call-iptables = 0
net.bridge.bridge-nf-call-ip6tables = 0
net.bridge.bridge-nf-call-arptables = 0
net.core.netdev_max_backlog = 10000
net.core.netdev_budget = 600
net.core.netdev_budget_usecs = 2000
net.core.rps_sock_flow_entries = 32768
net.ipv4.tcp_rmem = 4096 87380 8388608
net.ipv4.tcp_wmem = 4096 65536 8388608
\"\"\"
    for line in sysctl_conf.strip().splitlines():
        run_cmd(tn, f"echo '{line}' >> /etc/sysctl.d/99-performance.conf")
    run_cmd(tn, "sort -u /etc/sysctl.d/99-performance.conf -o /etc/sysctl.d/99-performance.conf")
    run_cmd(tn, "sysctl -p /etc/sysctl.d/99-performance.conf")

    # Injetar RPS Multicore (4 CPUs Quad-Core) para persistir na inicializacao em /etc/rc.local
    rc_inject = \"\"\"
# Calibracao RPS Multicore (Quad-Core Qualcomm IPQ5332)
for q in /sys/class/net/eth*/queues/rx-*/rps_cpus; do [ -f "$q" ] && echo f > "$q" 2>/dev/null; done
for q in /sys/class/net/eth*/queues/rx-*/rps_flow_cnt; do [ -f "$q" ] && echo 4096 > "$q" 2>/dev/null; done
for i in $(ls /sys/class/net 2>/dev/null | grep -E '^eth'); do ip link set dev "$i" txqueuelen 2048 2>/dev/null; done
\"\"\"
    rc_content = run_cmd(tn, "cat /etc/rc.local")
    if "rps_cpus" not in rc_content:
        run_cmd(tn, f"sed -i '/exit 0/i {rc_inject.replace(chr(10), chr(92)+chr(110))}' /etc/rc.local")
        # Executar agora mesmo em tempo real
        run_cmd(tn, 'for q in /sys/class/net/eth*/queues/rx-*/rps_cpus; do [ -f "$q" ] && echo f > "$q"; done')
        run_cmd(tn, 'for q in /sys/class/net/eth*/queues/rx-*/rps_flow_cnt; do [ -f "$q" ] && echo 4096 > "$q"; done')
        run_cmd(tn, 'ip link set dev eth0 txqueuelen 2048 2>/dev/null || true')

    print("    [OK] DHCP/Firewall desativados. Bridge L2 pura + RPS Multicore (4 CPUs) ativados.")

    # 4. Sincronizacao da Flash NAND e Reboot
    print("\n[*] [4/4] Gravando alteracoes na Flash NAND e reiniciando roteador...")
    run_cmd(tn, "sync")
    time.sleep(0.5)
    run_cmd(tn, "reboot")
    tn.close()
    print("    [OK] Roteador reiniciando com nova configuracao!")

    print("\n" + "=" * 75)
    print("  OPERACAO CONCLUIDA COM SUCESSO!")
    print("=" * 75)
    print("  O que acontece agora:")
    print("  1. O roteador reiniciara em cerca de 45 segundos.")
    print("  2. Seu computador recebera IP automaticamente da rede 192.168.73.x.")
    print(f"  3. Acesse o painel LuCI no novo endereco: http://{ROUTER_NEW_IP}")
    print("     - Usuario: root")
    print("     - Senha padrao (LuCI / SSH): admin0100 (ou a que voce cadastrou no primeiro login)")
    print("  4. Redes Wi-Fi configuradas e ativas:")
    print(f"     - 6 GHz (Wi-Fi 7 / 320 MHz / WPA3-SAE): {WIFI_SSID_6G}")
    print(f"     - 5 GHz (Wi-Fi 6 / 80 MHz / WPA2-AES):  {WIFI_SSID_5G}")
    print(f"     - Senha de ambas as redes Wi-Fi:        {WIFI_KEY}")
    print("=" * 75)

if __name__ == "__main__":
    main()
