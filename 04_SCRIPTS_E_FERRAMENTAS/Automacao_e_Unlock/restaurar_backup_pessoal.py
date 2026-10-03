#!/usr/bin/env python3
"""
restaurar_backup_pessoal.py
Restaura o Snapshot Completo do Overlay no Acer Predator Connect T7
Recupera 100% das configuracoes pessoais, LuCI, Wi-Fi 7, rede e chaves SSH.
"""

import os
import sys
import time
import telnetlib
import http.server
import socketserver
import threading

ROUTER_IPS = ["192.168.73.2", "192.168.76.1", "192.168.1.1"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "02_BACKUPS_E_DUMPS", "Backups_Configuracao_Pessoal"))
BACKUP_FILE = os.path.join(BACKUP_DIR, "backup_overlay_completo_2026-10-03.tar.gz")

def find_router():
    for ip in ROUTER_IPS:
        try:
            tn = telnetlib.Telnet(ip, 23, timeout=1.5)
            tn.read_until(b"/ # ", timeout=1.5)
            tn.close()
            return ip
        except Exception:
            pass
    return None

def start_temp_http(port=8888):
    os.chdir(BACKUP_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

def get_local_ip_to(target_ip):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((target_ip, 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "192.168.73.100"
    finally:
        s.close()
    return ip

def main():
    print("=" * 75)
    print("  RESTAURACAO DE BACKUP PESSOAL - ACER PREDATOR CONNECT T7")
    print("=" * 75)

    if not os.path.isfile(BACKUP_FILE):
        print(f"[-] Arquivo de backup nao encontrado: {BACKUP_FILE}")
        sys.exit(1)

    print(f"[*] Arquivo de backup localizado: {os.path.basename(BACKUP_FILE)} ({os.path.getsize(BACKUP_FILE)} bytes)")

    print("[*] Procurando roteador na rede...")
    router_ip = find_router()
    if not router_ip:
        print("[-] Roteador nao respondeu via Telnet em 192.168.73.2 ou 192.168.76.1.")
        print("    Verifique o cabo de rede ou se o roteador ja inicializou.")
        sys.exit(1)

    print(f"    [OK] Roteador detectado em: {router_ip}")

    # Sobe servidor HTTP temporario no PC
    httpd = start_temp_http(8888)
    local_ip = get_local_ip_to(router_ip)
    print(f"[*] Servidor temporario iniciado em http://{local_ip}:8888")

    # Conecta no roteador e baixa o backup
    print(f"[*] Conectando via Telnet em {router_ip}...")
    tn = telnetlib.Telnet(router_ip, 23, timeout=5)
    tn.read_until(b"/ # ", timeout=3)

    print("[*] Baixando arquivo de backup para o roteador...")
    url = f"http://{local_ip}:8888/{os.path.basename(BACKUP_FILE)}"
    tn.write(f"wget -O /tmp/restore.tar.gz {url}\n".encode())
    time.sleep(1.5)

    print("[*] Descompactando snapshot diretamente em /overlay/upper...")
    tn.write(b"tar -xzf /tmp/restore.tar.gz -C /overlay/upper\n")
    time.sleep(2)

    print("[*] Sincronizando memoria Flash NAND...")
    tn.write(b"sync\n")
    time.sleep(0.5)

    print("[*] Reiniciando roteador...")
    tn.write(b"reboot\n")
    time.sleep(0.5)
    tn.close()
    httpd.shutdown()

    print("\n" + "=" * 75)
    print("  RESTAURACAO CONCLUIDA COM SUCESSO!")
    print("  O roteador esta reiniciando com todas as suas configuracoes pessoais.")
    print("  Acesse em ~40 segundos: http://192.168.73.2")
    print("=" * 75)

if __name__ == "__main__":
    main()
