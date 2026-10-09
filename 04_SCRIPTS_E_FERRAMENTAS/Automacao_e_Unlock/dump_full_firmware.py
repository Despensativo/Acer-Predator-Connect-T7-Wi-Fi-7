#!/usr/bin/env python3
"""
Extracao Completa de Firmware, Particoes MTD e Diretorios do Sistema
Acer Predator Connect T7 (Qualcomm IPQ5332)
"""

import telnetlib
import time
import urllib.request
import os
import sys

ROUTER_IP = "192.168.73.2"
DEFAULT_FACTORY_IP = "192.168.76.1"

BASE_DIR = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7"
MTD_DIR = os.path.join(BASE_DIR, "Backups_MTD")
RE_DIR = os.path.join(BASE_DIR, "Engenharia_Reversa_OpenWrt")

os.makedirs(MTD_DIR, exist_ok=True)
os.makedirs(RE_DIR, exist_ok=True)

def run_telnet_cmd(tn, cmd, timeout=120):
    print(f"[*] Executando no roteador: {cmd.strip()} (timeout {timeout}s)...")
    tn.write(cmd.encode("ascii") + b"\n")
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="ignore")
    return out

def download_file(url, target_path):
    print(f"[*] Baixando: {url} -> {os.path.basename(target_path)} ...")
    start = time.time()
    urllib.request.urlretrieve(url, target_path)
    elapsed = time.time() - start
    size = os.path.getsize(target_path) / (1024 * 1024)
    print(f"    [OK] Salvo com sucesso: {size:.2f} MB em {elapsed:.2f}s ({size/max(elapsed, 0.001):.2f} MB/s)")

def main():
    print("=" * 70)
    print("CONTINUANDO DUMP COMPLETO DO ACER PREDATOR CONNECT T7")
    print(f"Alvo ativo no lab: {ROUTER_IP} (Nota: IP de fabrica original eh {DEFAULT_FACTORY_IP})")
    print("=" * 70)

    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
        tn.read_until(b"/ # ", timeout=5)
        run_telnet_cmd(tn, "mkdir -p /webapps/web/dump")
    except Exception as e:
        print(f"[-] Erro ao conectar ao roteador: {e}")
        sys.exit(1)

    # 1. Particao MTD27 (ubi_rootfs - ~38 MB)
    rootfs_bin = os.path.join(MTD_DIR, "backup_predator_t7_ubi_rootfs.bin")
    if not os.path.exists(rootfs_bin) or os.path.getsize(rootfs_bin) < 30 * 1024 * 1024:
        print("\n--- DUMP MTD27 (ubi_rootfs - 38MB) ---")
        run_telnet_cmd(tn, "dd if=/dev/mtd27 of=/tmp/backup_predator_t7_ubi_rootfs.bin", timeout=60)
        run_telnet_cmd(tn, "ln -sf /tmp/backup_predator_t7_ubi_rootfs.bin /webapps/web/dump/backup_predator_t7_ubi_rootfs.bin")
        download_file(f"http://{ROUTER_IP}/dump/backup_predator_t7_ubi_rootfs.bin", rootfs_bin)
        run_telnet_cmd(tn, "rm -f /tmp/backup_predator_t7_ubi_rootfs.bin /webapps/web/dump/backup_predator_t7_ubi_rootfs.bin")

    # 2. Diretorios do Sistema (Tarballs)
    dir_targets = [
        ("tar -czf /tmp/kernel_modules_5.4.213.tar.gz -C /lib/modules 5.4.213",
         "kernel_modules_5.4.213.tar.gz",
         os.path.join(RE_DIR, "kernel_modules_5.4.213.tar.gz"),
         60),
        ("tar -czf /tmp/webapps_acer_oem.tar.gz -C / webapps",
         "webapps_acer_oem.tar.gz",
         os.path.join(RE_DIR, "webapps_acer_oem.tar.gz"),
         30),
        ("tar -czf /tmp/qualcomm_ini_and_sawf.tar.gz -C / ini sawf",
         "qualcomm_ini_and_sawf.tar.gz",
         os.path.join(RE_DIR, "qualcomm_ini_and_sawf.tar.gz"),
         15),
        ("tar -czf /tmp/etc_factory_tree.tar.gz -C /rom etc",
         "etc_factory_tree.tar.gz",
         os.path.join(RE_DIR, "etc_factory_tree.tar.gz"),
         30),
    ]

    print("\n--- ETAPA 2: COMPACTACAO E DUMP DE DIRETORIOS DO SISTEMA ---")
    for tar_cmd, fname, dest_path, t_out in dir_targets:
        print(f"\n[*] Processando {fname}...")
        run_telnet_cmd(tn, tar_cmd, timeout=t_out)
        run_telnet_cmd(tn, f"ln -sf /tmp/{fname} /webapps/web/dump/{fname}")
        download_file(f"http://{ROUTER_IP}/dump/{fname}", dest_path)
        run_telnet_cmd(tn, f"rm -f /tmp/{fname} /webapps/web/dump/{fname}")

    # Limpeza final no roteador
    run_telnet_cmd(tn, "rm -rf /webapps/web/dump")
    tn.close()

    print("\n" + "=" * 70)
    print("DUMP COMPLETO CONCLUIDO COM SUCESSO!")
    print(f"Particoes salvas em: {MTD_DIR}")
    print(f"Diretorios e modulos salvos em: {RE_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
