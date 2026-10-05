#!/usr/bin/env python3
"""
gerenciar_telnet.py
Gerenciador de Acesso Telnet (Hardening de Seguranca) para Acer Predator Connect T7
Permite verificar status, desativar ou reativar o servico Telnet (porta 23) na rede local.
"""

import sys
import os
import socket
import time

try:
    from telnet_compat import Telnet
except ImportError:
    try:
        from Scripts_Automacao.telnet_compat import Telnet
    except ImportError:
        import telnetlib
        Telnet = telnetlib.Telnet

def test_port(ip, port, timeout=1.5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False

def detect_router_ip(explicit_ip=None):
    if explicit_ip:
        return explicit_ip
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        my_ip = s.getsockname()[0]
        s.close()
        parts = my_ip.split(".")
        guess = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
        if test_port(guess, 23) or test_port(guess, 22) or test_port(guess, 80):
            return guess
    except Exception:
        pass
    for cand in ["192.168.76.1", "192.168.73.2", "192.168.1.1"]:
        if test_port(cand, 23) or test_port(cand, 22) or test_port(cand, 80):
            return cand
    return "192.168.76.1"

def run_cmd(tn, cmd, timeout=5):
    tn.write(cmd + "\n")
    time.sleep(0.3)
    return tn.read_until("/ # ", timeout=timeout).decode(errors="replace")

def status_telnet(ip):
    active = test_port(ip, 23, timeout=1.5)
    ssh_active = test_port(ip, 22, timeout=1.5)
    print(f"\n[*] Status de Acesso Remoto em {ip}:")
    print(f"    - Telnet (Porta 23) : {'[ATIVO]' if active else '[DESATIVADO / FECHADO]'}")
    print(f"    - SSH    (Porta 22) : {'[ATIVO]' if ssh_active else '[DESATIVADO / FECHADO]'}")
    return active

def desativar_telnet(ip):
    print(f"\n[*] Conectando em {ip}:23 para desativar Telnet...")
    if not test_port(ip, 23):
        print("[-] A porta Telnet (23) ja esta fechada ou inacessivel!")
        return
    try:
        tn = Telnet(ip, 23, timeout=5)
        tn.read_until("/ # ", timeout=3)
        print("    [+] Conectado como root.")
        print("    [*] Removendo Telnet do boot (/etc/rc.local e crontabs)...")
        run_cmd(tn, "sed -i '/telnetd/d' /etc/rc.local /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
        run_cmd(tn, "sync")
        print("    [*] Finalizando processos telnetd ativos...")
        run_cmd(tn, "killall -9 telnetd 2>/dev/null")
        tn.close()
    except Exception as e:
        print(f"[-] Erro ao executar desativacao: {e}")
        return

    time.sleep(1)
    if not test_port(ip, 23):
        print("\n[OK] Telnet DESATIVADO com sucesso!")
        print("     A porta 23 foi fechada. Seu roteador agora responde exclusivamente via SSH (porta 22).")
    else:
        print("\n[!] Aviso: A porta 23 ainda parece responder. Verifique se o processo foi reiniciado pelo watchdog.")

def ativar_telnet(ip):
    print(f"\n[*] Para ativar o Telnet, conectando via SSH ou terminal...")
    print("    Dica: Se você possui acesso SSH, pode executar:")
    print("    ssh root@" + ip + " '/usr/sbin/telnetd -l /bin/ash'")
    print("    Ou, se o helper 'ativar-telnet' estiver instalado no roteador, digite apenas: ativar-telnet")

def main():
    explicit_ip = None
    action = None
    for arg in sys.argv[1:]:
        if arg in ["status", "desativar", "ativar"]:
            action = arg
        elif "." in arg:
            explicit_ip = arg

    router_ip = detect_router_ip(explicit_ip)

    print("=" * 65)
    print("  GERENCIADOR DE ACESSO TELNET - HARDENING DE SEGURANCA")
    print(f"  Roteador Alvo: {router_ip}")
    print("=" * 65)

    if not action:
        status_telnet(router_ip)
        print("\nEscolha uma opcao:")
        print("  [1] Desativar Telnet agora (Hardening - manter apenas SSH)")
        print("  [2] Verificar status das portas (Telnet / SSH)")
        print("  [0] Sair")
        opt = input("\nOpcao: ").strip()
        if opt == "1":
            action = "desativar"
        elif opt == "2":
            return
        else:
            return

    if action == "status":
        status_telnet(router_ip)
    elif action == "desativar":
        desativar_telnet(router_ip)
    elif action == "ativar":
        ativar_telnet(router_ip)

if __name__ == "__main__":
    main()
