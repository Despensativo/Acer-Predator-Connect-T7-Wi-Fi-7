#!/usr/bin/env python3
"""
Script de Teste e Diagnostico Rapido - Acer Predator Connect T7
Executa verificacao de portas (SSH, Telnet, HTTP) e consulta status do sistema via terminal.
"""

import socket
import sys

ROUTER_IP = "192.168.73.2"
PORTS = [22, 23, 80, 443]

def check_ports():
    print(f"[*] Verificando portas em {ROUTER_IP}...")
    for p in PORTS:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        res = s.connect_ex((ROUTER_IP, p))
        s.close()
        status = "ABERTA (OK)" if res == 0 else "FECHADA"
        service = {22: "SSH", 23: "Telnet", 80: "HTTP (Web)", 443: "HTTPS"}.get(p, "Outro")
        print(f"   - Porta {p:3} ({service:10}): {status}")

def query_system():
    try:
        import telnetlib
        import time
        print("\n[*] Consultando informacoes do hardware via Telnet...")
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=3)
        time.sleep(0.5)
        cmd = (
            "echo '--- UPTIME ---'; uptime; "
            "echo '--- CANAIS WI-FI ---'; uci show wireless.wifi0.channel; uci show wireless.wifi1.channel; uci show wireless.wifi2.channel; "
            "echo '--- TEMPERATURAS (mC) ---'; cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null; "
            "echo '--- MEMORIA ---'; free | grep Mem\n"
        )
        tn.write(cmd.encode('ascii'))
        time.sleep(1.5)
        out = tn.read_very_eager().decode('utf-8', errors='ignore')
        print(out)
        tn.close()
    except Exception as e:
        print(f"Erro ao consultar via telnet: {e}")

if __name__ == "__main__":
    check_ports()
    query_system()
