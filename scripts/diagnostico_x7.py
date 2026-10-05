#!/usr/bin/env python3
"""
diagnostico_x7.py
Modulo de Pesquisa, Diagnostico e Dump Seguro (Somente Leitura) para Acer Predator Connect X7 (5G CPE)

AVISO DE SEGURANCA:
- As imagens de firmware do Acer Predator Connect T7 (v27) sao INCOMPATIVEIS com o X7.
- O X7 possui modem celular 5G (Snapdragon X62) e particionamento especifico.
- A gravacao direta da ROM do T7 no X7 esta BLOQUEADA para evitar brick.
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
    for cand in ["192.168.76.1", "192.168.1.1", "192.168.73.2"]:
        if test_port(cand, 23) or test_port(cand, 22) or test_port(cand, 80):
            return cand
    return "192.168.76.1"

def run_cmd(tn, cmd, timeout=10):
    tn.write(cmd + "\n")
    time.sleep(0.4)
    out = tn.read_until("/ # ", timeout=timeout).decode(errors="replace")
    return out

def exibir_termo_x7():
    print("=" * 78)
    print("       ACER PREDATOR CONNECT X7 (5G CPE) - STATUS E AUDITORIA")
    print("=" * 78)
    print("""
[!] AVISO IMPORTANTE SOBRE O ACER PREDATOR CONNECT X7:

1. O Acer Predator Connect X7 e um roteador hibrido Wi-Fi 7 + Modem Celular 5G
   (Qualcomm Snapdragon X62) com firmware oficial v50.
2. A gravacao das imagens do modelo T7 (v27) no X7 causaria BRICK IRREVERSIVEL
   devido a diferencas nas particoes de modem, kernel e arvore de dispositivos.
3. POR ESSE MOTIVO, TODA ACAO DE ESCRITA OU GRAVACAO NO X7 ESTA BLOQUEADA.

COMO COLABORAR COM O DESENVOLVIMENTO DO SUPORTE AO X7:
- Se voce possui um X7 e deseja ajudar a homologar o suporte:
  a) Gere um backup original (.cfg) do seu roteador pela Web GUI da Acer.
  b) Envie o arquivo de configuracao (.cfg) e os logs de diagnostico para analise.
  c) Esteja ciente de que testes em hardware novo exigem bancada e disposicao
     para acompanhar o processo passo a passo.
  d) RECUPERABILIDADE: O X7 possui a mesma arquitetura Dual-Boot robusta do T7.
     Pelo que comprovamos no T7, desde que a Particao 1 (Slot 1 original)
     NAO seja sobrescrita ou corrompida apos obter o root, a chance de
     recuperacao e chaveamento de seguranca e altissima!
""")
    print("=" * 78)

def coletar_diagnostico_x7(ip):
    print(f"\n[*] Conectando em {ip}:23 para diagnostico seguro...")
    if not test_port(ip, 23):
        print("[-] A porta Telnet (23) nao respondeu.")
        print("    Certifique-se de que o roteador esta ligado e que o desbloqueio .cfg foi aplicado.")
        return

    try:
        tn = Telnet(ip, 23, timeout=5)
        tn.read_until("/ # ", timeout=3)
        print("    [+] Conectado com sucesso (Somente Leitura).")
        print("\n--- [1] Identificacao do Hardware ---")
        print(run_cmd(tn, "cat /tmp/sysinfo/model 2>/dev/null; cat /etc/version 2>/dev/null; uname -a").strip())

        print("\n--- [2] Tabela de Particoes MTD ---")
        print(run_cmd(tn, "cat /proc/mtd").strip())

        print("\n--- [3] Estado do Dual-Boot ---")
        print(run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot 2>/dev/null").strip())

        print("\n--- [4] Dispositivos de Rede e Modem ---")
        print(run_cmd(tn, "ip link show; ls -l /dev/qcqmi* /dev/cdc* 2>/dev/null").strip())

        tn.close()
        print("\n[OK] Diagnostico somente-leitura concluido com sucesso!")
    except Exception as e:
        print(f"[-] Erro durante coleta de diagnostico: {e}")

def main():
    exibir_termo_x7()
    router_ip = detect_router_ip()
    print(f"Roteador detectado: {router_ip}")
    print("\nOpcoes:")
    print("  [1] Executar Diagnostico de Hardware e Particoes (Somente Leitura)")
    print("  [0] Voltar ao Menu Principal")
    opt = input("\nEscolha uma opcao: ").strip()
    if opt == "1":
        coletar_diagnostico_x7(router_ip)

if __name__ == "__main__":
    main()
