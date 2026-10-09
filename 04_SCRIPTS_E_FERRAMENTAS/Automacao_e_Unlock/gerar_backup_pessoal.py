#!/usr/bin/env python3
"""
gerar_backup_pessoal.py
Gera e Baixa Automaticamente Backups Atualizados do Acer Predator Connect T7 para o PC
Salva:
1. Snapshot Completo do Overlay NAND (1:1)
2. Arquivo Sysupgrade do LuCI (.tar.gz)
"""

import os
import sys
import time
import telnetlib
import urllib.request
from datetime import datetime

ROUTER_IPS = ["192.168.73.2", "192.168.76.1", "192.168.1.1"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "02_BACKUPS_E_DUMPS", "Backups_Configuracao_Pessoal"))
os.makedirs(DEST_DIR, exist_ok=True)

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

def run_cmd(tn, cmd, timeout=30):
    tn.read_very_eager()
    tn.write(cmd.strip().encode("ascii") + b"\n")
    time.sleep(0.3)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    return out

def main():
    print("=" * 75)
    print("  GERADOR DE BACKUP AUTOMATICO - ACER PREDATOR CONNECT T7")
    print("=" * 75)

    print("[*] Localizando roteador...")
    router_ip = find_router()
    if not router_ip:
        print("[-] Roteador nao encontrado em 192.168.73.2 ou 192.168.76.1.")
        print("    Verifique a conexao de rede.")
        sys.exit(1)

    print(f"    [OK] Roteador conectado em: {router_ip}")

    tn = telnetlib.Telnet(router_ip, 23, timeout=5)
    tn.read_until(b"/ # ", timeout=3)

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n[*] [1/3] Gerando Sysupgrade Backup (LuCI)...")
    run_cmd(tn, "sysupgrade -b /tmp/backup_luci.tar.gz 2>/dev/null", timeout=20)

    print(f"[*] [2/3] Gerando Snapshot Completo da particao Overlay Flash...")
    run_cmd(tn, "tar -czf /tmp/backup_overlay.tar.gz -C /overlay/upper .", timeout=30)

    # Move temporariamente para /www para download HTTP rapido
    run_cmd(tn, "cp /tmp/backup_luci.tar.gz /www/_bkp_luci.tar.gz", timeout=5)
    run_cmd(tn, "cp /tmp/backup_overlay.tar.gz /www/_bkp_overlay.tar.gz", timeout=5)

    f_luci = os.path.join(DEST_DIR, f"backup_luci_sysupgrade_{today}.tar.gz")
    f_overlay = os.path.join(DEST_DIR, f"backup_overlay_completo_{today}.tar.gz")

    print(f"\n[*] [3/3] Baixando arquivos para o computador...")
    try:
        urllib.request.urlretrieve(f"http://{router_ip}/_bkp_luci.tar.gz", f_luci)
        urllib.request.urlretrieve(f"http://{router_ip}/_bkp_overlay.tar.gz", f_overlay)
        print("    [OK] Download concluido com sucesso!")
    finally:
        # Limpa /www imediatamente
        tn.write(b"rm -f /www/_bkp_luci.tar.gz /www/_bkp_overlay.tar.gz /tmp/backup_luci.tar.gz /tmp/backup_overlay.tar.gz\n")
        time.sleep(0.3)
        tn.close()

    print("\n" + "=" * 75)
    print("  BACKUP GERADO E SALVO COM SUCESSO!")
    print("=" * 75)
    print(f"  Destino: {DEST_DIR}")
    print(f"  1. Sysupgrade LuCI:  {os.path.basename(f_luci)} ({os.path.getsize(f_luci):,} bytes)")
    print(f"  2. Overlay Completo: {os.path.basename(f_overlay)} ({os.path.getsize(f_overlay):,} bytes)")
    print("=" * 75)

if __name__ == "__main__":
    main()
