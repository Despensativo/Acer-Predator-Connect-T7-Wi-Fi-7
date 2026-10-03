#!/usr/bin/env python3
"""
Monitor de Inicializacao OpenWrt / Acer Dual-Boot
Verifica status das interfaces de rede, pings e portas HTTP/SSH apos o reboot.
"""

import socket
import time
import subprocess
import sys

TARGET_IPS = [
    ("192.168.1.1", "OpenWrt LAN Padrao"),
    ("192.168.73.2", "Acer Original Lab AP"),
    ("192.168.76.1", "Acer Fabrica Padrao"),
]

def check_port(ip, port, timeout=1.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        res = s.connect_ex((ip, port))
        s.close()
        return res == 0
    except:
        return False

def scan_arp_for_openwrt():
    try:
        res = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        lines = [l for l in res.stdout.split("\n") if "70-5a-6f" in l.lower() or "192.168." in l]
        return lines
    except:
        return []

def main():
    print("=" * 65)
    print("MONITOR DE INICIALIZACAO - ACER PREDATOR CONNECT T7")
    print("Aguardando reinicializacao e detectando portas...")
    print("=" * 65)

    start_time = time.time()
    reboot_detected = False

    while time.time() - start_time < 180:
        elapsed = int(time.time() - start_time)

        # 1. Checa se o IP antigo caiu
        if not reboot_detected:
            if not check_port("192.168.73.2", 23, timeout=0.5):
                print(f"[{elapsed}s] [+] O roteador reiniciou! Conexao anterior desconectada.")
                reboot_detected = True

        # 2. Testa cada um dos IPs alvo
        found = False
        for ip, label in TARGET_IPS:
            p80 = check_port(ip, 80, timeout=0.5)
            p22 = check_port(ip, 22, timeout=0.5)
            p23 = check_port(ip, 23, timeout=0.5)
            p8080 = check_port(ip, 8080, timeout=0.5)

            if p80 or p22 or p23 or p8080:
                print(f"\n[{elapsed}s] [!] RESPOSTA DETECTADA EM {ip} ({label}):")
                if p80:   print(f"    -> Porta 80   (HTTP LuCI/Web): ABERTA")
                if p22:   print(f"    -> Porta 22   (SSH):           ABERTA")
                if p23:   print(f"    -> Porta 23   (Telnet):        ABERTA")
                if p8080: print(f"    -> Porta 8080 (LuCI Hibrido):  ABERTA")
                found = True
                break

        if found:
            print("\n" + "=" * 65)
            print("[OK] Roteador inicializado e respondendo com sucesso na rede!")
            print("=" * 65)
            return

        time.sleep(2)
        sys.stdout.write(f"\r[{elapsed}s] Sondando rede (OpenWrt 192.168.1.1 / Acer 192.168.73.2)...")
        sys.stdout.flush()

    print("\n[-] Tempo limite de 180 segundos atingido.")

if __name__ == "__main__":
    main()
