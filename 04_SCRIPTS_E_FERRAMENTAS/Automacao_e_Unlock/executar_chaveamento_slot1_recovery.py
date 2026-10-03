#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
CHAVEAMENTO SEGURO PARA SLOT 1 VIA U-BOOT RECOVERY WEB
Acer Predator Connect T7 (IPQ5322 / Wi-Fi 7 BE11000)
=============================================================================
Este script envia o pacote RAM-only 'restaurar_slot1_acer.itb' para a interface
de recovery HTTP do U-Boot (192.168.1.1).

O U-Boot reconhece o cabeçalho 'Flash' e executa o script interno diretamente
da memória RAM sem sobrescrever partições de firmware. O script grava apenas
o ponteiro de BOOTCONFIG (primaryboot=1) e reinicia o roteador no Slot 1.
=============================================================================
"""

import os
import sys
import io
import time
import socket
import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7"
ITB_FILE = os.path.join(BASE_DIR, "3 - Ferramentas de Recuperacao", "restaurar_slot1_acer.itb")
RECOVERY_URL = "http://192.168.1.1/"

def check_socket(ip, port, timeout=0.5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        res = s.connect_ex((ip, port))
        s.close()
        return res == 0
    except Exception:
        return False

def main():
    print("=" * 70)
    print("🔄 CHAVEAMENTO PARA SLOT 1 (ACER FÁBRICA) VIA U-BOOT RECOVERY")
    print("=" * 70)

    if not os.path.exists(ITB_FILE):
        print(f"[-] Erro: Arquivo {ITB_FILE} não encontrado!")
        return 1

    itb_size = os.path.getsize(ITB_FILE)
    print(f"[*] Arquivo ITB: {ITB_FILE} ({itb_size} bytes)")

    # 1. Verificar se o U-Boot Recovery está respondendo
    print("[*] Verificando interface de recuperação em http://192.168.1.1/ ...")
    try:
        r = requests.get(RECOVERY_URL, timeout=3)
        if r.status_code == 200 and "FIRMWARE UPDATE" in r.text.upper():
            print("[+] U-Boot Recovery Web ativo e respondendo perfeitamente!")
        else:
            print(f"[!] Resposta inesperada do servidor: {r.status_code}")
    except Exception as e:
        print(f"[-] Falha ao conectar em {RECOVERY_URL}: {e}")
        return 1

    # 2. Upload do restaurar_slot1_acer.itb
    print("\n" + "=" * 70)
    print("⚡ ENVIANDO SCRIPT DE CHAVEAMENTO (restaurar_slot1_acer.itb)...")
    print("   (Execução puramente em RAM via U-Boot 'source $imgaddr:script')")
    print("=" * 70)

    with open(ITB_FILE, "rb") as f:
        files = {
            'firmware': ('restaurar_slot1_acer.itb', f, 'application/octet-stream')
        }
        try:
            resp = requests.post(RECOVERY_URL, files=files, timeout=10)
            print(f"[+] Resposta do U-Boot: HTTP {resp.status_code}")
            if resp.text:
                print(f"[+] Mensagem: {resp.text[:200].strip()}")
        except requests.exceptions.ReadTimeout:
            print("[+] Envio concluído! O U-Boot encerrou a conexão e está processando o script.")
        except requests.exceptions.ConnectionError:
            print("[+] Conexão encerrada pelo roteador (U-Boot reiniciando o SoC).")
        except Exception as e:
            print(f"[*] Status da transmissão: {e}")

    # 3. Monitorar reinicialização no Slot 1
    print("\n" + "=" * 70)
    print("⏳ AGUARDANDO REINICIALIZAÇÃO NO SLOT 1 (ACER FÁBRICA)...")
    print("   Sondando portas de gerenciamento (Telnet 23 / SSH 22 / Web 80)")
    print("=" * 70)

    start_time = time.time()
    slot1_ready = False

    target_ips = ["192.168.73.2", "192.168.76.1", "192.168.1.1"]

    for i in range(90):
        time.sleep(2)
        elapsed = int(time.time() - start_time)

        for ip in target_ips:
            # Telnet
            if check_socket(ip, 23):
                print(f"\n[+] SUCESSO! Telnet ativo em {ip}:23 após {elapsed}s!")
                slot1_ready = True
                break
            # SSH
            if check_socket(ip, 22):
                print(f"\n[+] SUCESSO! SSH ativo em {ip}:22 após {elapsed}s!")
                slot1_ready = True
                break
            # Web (evitar falso positivo se ainda estiver no recovery)
            if ip != "192.168.1.1" and check_socket(ip, 80):
                print(f"\n[+] SUCESSO! Web GUI ativa em {ip}:80 após {elapsed}s!")
                slot1_ready = True
                break

        if slot1_ready:
            break

        sys.stdout.write(f"\r[{elapsed:02d}s] Aguardando o boot do Slot 1...")
        sys.stdout.flush()

    if slot1_ready:
        print("\n" + "=" * 70)
        print("🎉 ROTEADOR REINICIADO COM SUCESSO NO SLOT 1!")
        print("=" * 70)
        return 0
    else:
        print("\n[!] O roteador ainda está inicializando ou aguardando link Ethernet.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
