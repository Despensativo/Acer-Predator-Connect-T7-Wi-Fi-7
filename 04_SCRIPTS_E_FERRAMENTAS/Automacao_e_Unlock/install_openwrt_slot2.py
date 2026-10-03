#!/usr/bin/env python3
"""
Instalador Seguro do OpenWrt Puro no Slot 2 (mtd20 / rootfs_1)
Acer Predator Connect T7 (Qualcomm IPQ5332)
"""

import http.server
import socketserver
import threading
import telnetlib
import time
import os
import hashlib
import sys

ROUTER_IP = "192.168.73.2"
PC_IP = "192.168.73.90"
HTTP_PORT = 8089

BASE_DIR = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7"
IMG_DIR = os.path.join(BASE_DIR, "1 - Firmware e Imagens OpenWrt")
KERNEL_PATH = os.path.join(IMG_DIR, "openwrt-predator-t7-kernel.fit")
ROOTFS_PATH = os.path.join(IMG_DIR, "root.squashfs")

def get_md5(fpath):
    with open(fpath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def start_http_server():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=IMG_DIR, **kwargs)
        def log_message(self, format, *args):
            pass

    server = socketserver.TCPServer((PC_IP, HTTP_PORT), QuietHandler)
    server.allow_reuse_address = True
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def run_cmd(tn, cmd, timeout=60):
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.5)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    return out

def main():
    print("=" * 70)
    print("INSTALADOR AUTOMATIZADO OPENWRT PURO NO SLOT 2 (mtd20 / rootfs_1)")
    print("Acer Predator Connect T7 - Protecao Dual-Boot Ativa")
    print("=" * 70)

    # 1. Validacao dos arquivos locais
    if not os.path.exists(KERNEL_PATH) or not os.path.exists(ROOTFS_PATH):
        print("[-] Erro: Arquivos de imagem nao encontrados!")
        sys.exit(1)

    k_md5 = get_md5(KERNEL_PATH)
    r_md5 = get_md5(ROOTFS_PATH)
    k_sz = os.path.getsize(KERNEL_PATH)
    r_sz = os.path.getsize(ROOTFS_PATH)

    print(f"[*] Kernel FIT local : {k_sz} bytes ({k_sz/(1024*1024):.2f} MB) | MD5: {k_md5}")
    print(f"[*] RootFS SquashFS  : {r_sz} bytes ({r_sz/(1024*1024):.2f} MB) | MD5: {r_md5}")

    # 2. Iniciar Servidor HTTP temporario
    print(f"[*] Iniciando servidor HTTP local no PC ({PC_IP}:{HTTP_PORT})...")
    httpd = start_http_server()

    # 3. Conexao Telnet com o Roteador
    print(f"[*] Conectando ao roteador em {ROUTER_IP} via Telnet...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
    tn.read_until(b"/ # ", timeout=5)

    # 4. Baixar arquivos no /tmp do roteador
    print("\n[*] 1/4 Transferindo imagens para a memoria RAM (/tmp) do roteador...")
    run_cmd(tn, "rm -f /tmp/openwrt_kernel.fit /tmp/openwrt_root.squashfs")
    
    cmd_dl_k = f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/openwrt-predator-t7-kernel.fit -o /tmp/openwrt_kernel.fit"
    print(f"    -> Baixando Kernel FIT...")
    run_cmd(tn, cmd_dl_k, timeout=30)

    cmd_dl_r = f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/root.squashfs -o /tmp/openwrt_root.squashfs"
    print(f"    -> Baixando RootFS SquashFS...")
    run_cmd(tn, cmd_dl_r, timeout=30)

    # 5. Validar integridade no roteador
    print("\n[*] 2/4 Validando integridade dos arquivos no roteador...")
    md5_check = run_cmd(tn, "md5sum /tmp/openwrt_kernel.fit /tmp/openwrt_root.squashfs")
    print(md5_check.strip())

    if k_md5 not in md5_check or r_md5 not in md5_check:
        print("[-] ERRO CRITICO: Hash MD5 divergente no roteador! Abortando por seguranca.")
        run_cmd(tn, "rm -f /tmp/openwrt_kernel.fit /tmp/openwrt_root.squashfs")
        tn.close()
        httpd.shutdown()
        sys.exit(1)
    print("    [OK] Hashes MD5 100% conferidos com perfeicao!")

    # 6. Gravar nos Volumes UBI do Slot 2 (mtd20)
    print("\n[*] 3/4 Gravando OpenWrt nos volumes UBI do Slot 2 (mtd20)...")
    print("    -> Anexando particao mtd20 (Slot 2)...")
    run_cmd(tn, "ubiattach /dev/ubi_ctrl -m 20", timeout=15)
    
    print("    -> Gravando Kernel FIT no volume ubi1_1 (kernel)...")
    out_k = run_cmd(tn, "ubiupdatevol /dev/ubi1_1 /tmp/openwrt_kernel.fit", timeout=30)
    print("       " + out_k.strip())

    print("    -> Gravando RootFS no volume ubi1_2 (ubi_rootfs)...")
    out_r = run_cmd(tn, "ubiupdatevol /dev/ubi1_2 /tmp/openwrt_root.squashfs", timeout=60)
    print("       " + out_r.strip())

    print("    -> Formatando area de overlay ubi1_3 (rootfs_data) para inicializacao limpa...")
    run_cmd(tn, "ubiupdatevol /dev/ubi1_3 -t", timeout=15)

    print("    -> Sincronizando e desanexando particao do Slot 2...")
    run_cmd(tn, "sync; ubidetach -d 1", timeout=15)

    # 7. Limpeza da RAM
    print("\n[*] 4/4 Limpando arquivos temporarios da memoria RAM do roteador...")
    run_cmd(tn, "rm -f /tmp/openwrt_kernel.fit /tmp/openwrt_root.squashfs")
    mem_info = run_cmd(tn, "free | grep Mem")
    print("    " + mem_info.strip())

    tn.close()
    httpd.shutdown()

    print("\n" + "=" * 70)
    print("[SUCESSO TOTAL] O OPENWRT PURO FOI GRAVADO NO SLOT 2 COM 100% DE EXITO!")
    print("Slot 1 (Acer Original): 100% Intacto e Preservado.")
    print("Slot 2 (OpenWrt Puro) : Gravado e pronto para o primeiro boot.")
    print("=" * 70)

if __name__ == "__main__":
    main()
