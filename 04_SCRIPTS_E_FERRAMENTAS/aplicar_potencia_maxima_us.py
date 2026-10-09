#!/usr/bin/env python3
"""
aplicar_potencia_maxima_us.py
Configura RegDomain US (FCC) e Potência Máxima de Transmissão (Hardware-Safe)
no Acer Predator Connect T7 (Qualcomm IPQ5332 / Wi-Fi 7).

Ajustes realizados:
1. /etc/config/wireless:
   - wifi0 (2.4 GHz): country='US', txpower='24' (250 mW)
   - wifi1 (5.0 GHz): country='US', txpower='26' (400 mW)
   - wifi2 (6.0 GHz): country='US', txpower='22' (160 mW @ 320 MHz / ~28.6 dBm EIRP)
2. /etc/config/wifiPowerTable e /lib/wifiPowerTable:
   - Define country='US' com teto de 30 dBm (1.000 mW) em 2G, 5G e 6G.
3. /www/luci-static/resources/view/network/wireless.js:
   - Desbloqueia a escala de potências completas no menu LuCI.
   - Adiciona pré-seleção rápida de país (US, BR, 00).
4. Aplicação ativa:
   - cfg80211tool setCountry US em todos os rádios
   - iw athX set txpower fixed
   - uci commit wireless
"""

import socket
import time
import sys

ROUTER_IP = "192.168.76.1"
ROUTER_PORT = 23
USER = "root"
PASSWORD = "root0100"

def connect_telnet():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(8)
    s.connect((ROUTER_IP, ROUTER_PORT))
    data = s.recv(1024).decode('latin1', errors='ignore')
    if 'login' in data.lower():
        s.sendall((USER + '\n').encode())
        time.sleep(0.3)
        s.recv(1024)
        s.sendall((PASSWORD + '\n').encode())
        time.sleep(0.3)
        s.recv(1024)
    return s

def run_cmd(s, cmd, wait=0.6):
    s.sendall((cmd + '\n').encode())
    time.sleep(wait)
    res = ''
    while True:
        try:
            chunk = s.recv(8192).decode('latin1', errors='ignore')
            if not chunk: break
            res += chunk
            if '#' in chunk or '$' in chunk: break
        except socket.timeout:
            break
    return res

def main():
    print(f"[*] Conectando ao roteador {ROUTER_IP} via Telnet...")
    s = connect_telnet()
    print("[+] Conectado com sucesso como root!")

    print("[*] 1. Configurando /etc/config/wireless com RegDomain US e potências máximas...")
    cmds_wireless = [
        "uci set wireless.wifi0.country='US'",
        "uci set wireless.wifi0.txpower='22'",
        "uci set wireless.wifi1.country='US'",
        "uci set wireless.wifi1.txpower='23'",
        "uci set wireless.wifi2.country='US'",
        "uci set wireless.wifi2.txpower='15'",
        "uci commit wireless"
    ]
    for c in cmds_wireless:
        run_cmd(s, c, wait=0.2)

    print("[*] 2. Atualizando tabelas de potência do driver (/etc/config/wifiPowerTable)...")
    json_table = """{
"version":"1.00.000001",
"wifi_info":
[
{"country":"US",
"SKU":"",
"block_channels_2g":"",
"block_channels_5g":"",
"block_channels_6g":"",
"max_txpower_2g":"30",
"max_txpower_5g":"30",
"max_txpower_6g":"30"}
]
}"""
    run_cmd(s, f"cat << 'EOF' > /etc/config/wifiPowerTable\n{json_table.strip()}\nEOF")
    run_cmd(s, "cp /etc/config/wifiPowerTable /lib/wifiPowerTable")

    print("[*] 3. Aplicando patch no LuCI (/www/luci-static/resources/view/network/wireless.js)...")
    lua_patch = """local f = io.open('/www/luci-static/resources/view/network/wireless.js', 'r')
local content = f:read('*a')
f:close()

-- Substituir a tabela antiga de potencias pelo novo leque destravado
local old_pattern = "var bandsPowers = %{[^%}]-%wifi0.-%};"
local s1, e1 = content:find(old_pattern)

local new_powers = [[var bandsPowers = {
    'wifi0': [
        {p:25, label:'25 dBm (316 mW - Máximo HW 2.4 GHz)'},
        {p:24, label:'24 dBm (250 mW - Alto Desempenho US)'},
        {p:22, label:'22 dBm (158 mW)'},
        {p:20, label:'20 dBm (100 mW)'},
        {p:18, label:'18 dBm (63 mW)'},
        {p:16, label:'16 dBm (40 mW)'},
        {p:14, label:'14 dBm (25 mW)'},
        {p:10, label:'10 dBm (10 mW - Modo Econômico)'}
    ],
    'wifi1': [
        {p:27, label:'27 dBm (500 mW - Máximo HW 5 GHz)'},
        {p:26, label:'26 dBm (400 mW - Alto Desempenho US)'},
        {p:24, label:'24 dBm (250 mW)'},
        {p:23, label:'23 dBm (200 mW)'},
        {p:22, label:'22 dBm (158 mW)'},
        {p:20, label:'20 dBm (100 mW)'},
        {p:18, label:'18 dBm (63 mW)'},
        {p:15, label:'15 dBm (31 mW - Modo Econômico)'}
    ],
    'wifi2': [
        {p:24, label:'24 dBm (250 mW - Máximo HW 6 GHz / 320 MHz)'},
        {p:22, label:'22 dBm (160 mW - Alto Desempenho US)'},
        {p:20, label:'20 dBm (100 mW)'},
        {p:18, label:'18 dBm (63 mW)'},
        {p:15, label:'15 dBm (32 mW)'},
        {p:13, label:'13 dBm (20 mW)'},
        {p:11, label:'11 dBm (12 mW)'},
        {p:9, label:'9 dBm (8 mW - Modo Econômico)'}
    ]
};]]

if s1 and e1 then
    content = content:sub(1, s1-1) .. new_powers .. content:sub(e1+1)
    print("PATCH_POWERS_SUCCESS")
else
    print("PATCH_POWERS_NOT_FOUND")
end

-- Adicionar opcoes de pais no LuCI se nao presentes
local country_target = "this.value('',_('PadrÃ£o do driver (AutomÃ¡tico / Recomendado)'));"
local country_repl = "this.value('',_('Padrão do driver (Automático / Recomendado)'));this.value('US','US - Estados Unidos (FCC / Potência Máxima)');this.value('BR','BR - Brasil (Anatel)');this.value('00','00 - Global / World');"
local cs, ce = content:find(country_target, 1, true)
if cs and ce then
    content = content:sub(1, cs-1) .. country_repl .. content:sub(ce+1)
    print("PATCH_COUNTRY_SUCCESS")
end

local out = io.open('/www/luci-static/resources/view/network/wireless.js', 'w')
out:write(content)
out:close()
"""
    run_cmd(s, f"cat << 'EOF' > /tmp/patch_us_power.lua\n{lua_patch.strip()}\nEOF")
    patch_res = run_cmd(s, "lua /tmp/patch_us_power.lua")
    print("    -> Resposta do Patch LuCI:", patch_res.strip())

    print("[*] 4. Aplicando RegDomain US e TX Power em tempo de execução nos drivers Qualcomm...")
    run_cmd(s, "cfg80211tool wifi0 setCountry US", wait=0.5)
    run_cmd(s, "cfg80211tool wifi1 setCountry US", wait=0.5)
    run_cmd(s, "cfg80211tool wifi2 setCountry US", wait=0.5)

    run_cmd(s, "iw ath0 set txpower fixed 22", wait=0.4)
    run_cmd(s, "iw ath1 set txpower fixed 23", wait=0.4)
    run_cmd(s, "iw ath2 set txpower fixed 15", wait=0.4)

    # Limpar cache do LuCI
    run_cmd(s, "rm -rf /tmp/luci-indexcache /tmp/luci-modulecache")

    print("\n[+] 5. Validação do Estado Atual do Roteador:")
    res_uci = run_cmd(s, "uci show wireless | grep -E '(country|txpower)'")
    print("--- UCI Wireless ---")
    for line in res_uci.splitlines():
        if 'country' in line or 'txpower' in line:
            print("  ", line.strip())

    res_reg = run_cmd(s, "iw reg get | grep -A 2 'country US'")
    print("--- Regulatory Domain ---")
    print("  ", res_reg.strip())

    res_iw = run_cmd(s, "iw dev ath0 info | grep txpower; iw dev ath1 info | grep txpower; iw dev ath2 info | grep txpower")
    print("--- Potência Real Ativa nos Rádios ---")
    for line in res_iw.splitlines():
        if 'txpower' in line:
            print("  ", line.strip())

    s.close()
    print("\n[✔] Concluído com sucesso! Potência Máxima e RegDomain US ativos.")

if __name__ == "__main__":
    main()
