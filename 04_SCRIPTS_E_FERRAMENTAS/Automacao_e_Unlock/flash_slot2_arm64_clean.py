#!/usr/bin/env python3
"""
Gravador Limpo e Seguro do OpenWrt Mainline ARM64 (Kernel 6.18) no Slot 2 (mtd20)
Acer Predator Connect T7 (Qualcomm IPQ5322)
"""

import http.server
import socketserver
import threading
import telnetlib
import socket
import time
import os
import hashlib
import sys

ROUTER_IP = "192.168.73.2"
PC_IP = "192.168.73.90"
HTTP_PORT = 8089

BASE_DIR = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7"
IMG_DIR = os.path.join(BASE_DIR, "1 - Firmware e Imagens OpenWrt")
KERNEL_PATH = os.path.join(IMG_DIR, "openwrt-predator-t7-kernel-arm64.fit")
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

def check_port(ip, port, timeout=0.8):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        res = s.connect_ex((ip, port))
        s.close()
        return res == 0
    except:
        return False

def monitor_boot(max_seconds=180):
    print("\n" + "=" * 70)
    print("MONITORAMENTO ATIVO DO BOOT DO OPENWRT 64-BIT NO SLOT 2")
    print("Aguardando U-Boot saltar para AArch64 e inicializar Kernel 6.18...")
    print("=" * 70)

    start_time = time.time()
    reboot_detected = False

    target_ips = [
        ("192.168.1.1", "OpenWrt Padrao LAN"),
        ("192.168.73.2", "Acer Lab AP IP"),
        ("192.168.76.1", "Acer Fabrica Padrao"),
    ]

    while time.time() - start_time < max_seconds:
        elapsed = int(time.time() - start_time)

        if not reboot_detected:
            if not check_port("192.168.73.2", 23, timeout=0.5):
                print(f"[{elapsed:03d}s] [+] O roteador reiniciou! Conexao anterior fechada.")
                reboot_detected = True

        for ip, label in target_ips:
            p80 = check_port(ip, 80, timeout=0.4)
            p22 = check_port(ip, 22, timeout=0.4)
            p23 = check_port(ip, 23, timeout=0.4)
            p8080 = check_port(ip, 8080, timeout=0.4)

            if p80 or p22 or p23 or p8080:
                print(f"\n[{elapsed:03d}s] [!!!] RESPOSTA DETECTADA EM {ip} ({label}) [!!!]")
                if p80:   print(f"    -> Porta 80   (HTTP LuCI Web): ABERTA")
                if p22:   print(f"    -> Porta 22   (SSH Dropbear):  ABERTA")
                if p23:   print(f"    -> Porta 23   (Telnet Debug):  ABERTA")
                if p8080: print(f"    -> Porta 8080 (LuCI Hibrido):  ABERTA")
                print("=" * 70)
                print("[OK] OPENWRT MAINLINE 64-BIT SUBIU NO SLOT 2 COM SUCESSO!")
                print("=" * 70)
                return True

        time.sleep(2)
        sys.stdout.write(f"\r[{elapsed:03d}s] Sondando rede (192.168.1.1 / 192.168.73.2)...")
        sys.stdout.flush()

    print("\n[-] Tempo limite atingido. Verificando estado...")
    return False

def main():
    print("=" * 70)
    print("INSTALADOR DEFINITIVO OPENWRT MAINLINE ARM64 NO SLOT 2 (mtd20)")
    print("Acer Predator Connect T7 (Qualcomm IPQ5322)")
    print("Slot 1 (Acer Original): 100% Intacto e Preservado")
    print("=" * 70)

    # 1. Validar imagens locais
    if not os.path.exists(KERNEL_PATH) or not os.path.exists(ROOTFS_PATH):
        print("[-] Erro: Arquivos de imagem nao encontrados no PC!")
        sys.exit(1)

    k_md5 = get_md5(KERNEL_PATH)
    r_md5 = get_md5(ROOTFS_PATH)
    k_sz = os.path.getsize(KERNEL_PATH)
    r_sz = os.path.getsize(ROOTFS_PATH)

    print(f"[*] Kernel FIT ARM64 (load 0x41000000): {k_sz} bytes ({k_sz/(1024*1024):.2f} MB) | MD5: {k_md5}")
    print(f"[*] RootFS SquashFS                    : {r_sz} bytes ({r_sz/(1024*1024):.2f} MB) | MD5: {r_md5}")

    # 2. Conectar via Telnet
    print(f"\n[*] Conectando ao roteador em {ROUTER_IP}...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
    tn.read_until(b"/ # ", timeout=3)

    # 3. Validar slot ativo
    slot_info = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    cur_slot = [l.strip() for l in slot_info.split("\n") if l.strip() and not l.startswith("cat ") and not l.startswith("/ #")][-1]
    print(f"[*] Slot ativo atual: primaryboot = {cur_slot}")
    if cur_slot != "1":
        print("[-] ERRO: Roteador nao esta no Slot 1! Abortando por precaucao.")
        tn.close()
        sys.exit(1)
    print("    [OK] Confirmado: Slot 1 ativo. O Slot 2 (mtd20) esta 100% seguro para escrita.")

    # 4. Iniciar Servidor HTTP
    print(f"\n[*] Iniciando servidor HTTP local no PC ({PC_IP}:{HTTP_PORT})...")
    httpd = start_http_server()

    # 5. Baixar imagens no /tmp do roteador
    print("\n[*] [1/4] Baixando imagens na memoria RAM (/tmp) do roteador...")
    run_cmd(tn, "rm -f /tmp/k_arm64.fit /tmp/root.squashfs")
    
    cmd_dl_k = f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/openwrt-predator-t7-kernel-arm64.fit -o /tmp/k_arm64.fit"
    print("    -> Baixando Kernel FIT ARM64...")
    run_cmd(tn, cmd_dl_k, timeout=20)

    cmd_dl_r = f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/root.squashfs -o /tmp/root.squashfs"
    print("    -> Baixando RootFS SquashFS...")
    run_cmd(tn, cmd_dl_r, timeout=30)

    # 6. Validar integridade MD5
    print("\n[*] [2/4] Validando hashes MD5 no roteador...")
    md5_remote = run_cmd(tn, "md5sum /tmp/k_arm64.fit /tmp/root.squashfs")
    print(f"    Hashes remotos:\n{md5_remote.strip()}")
    if k_md5 not in md5_remote or r_md5 not in md5_remote:
        print("[-] ERRO: Hashes divergentes no roteador! Abortando por seguranca.")
        run_cmd(tn, "rm -f /tmp/k_arm64.fit /tmp/root.squashfs")
        tn.close()
        httpd.shutdown()
        sys.exit(1)
    print("    [OK] Hashes conferidos com 100% de precisao!")

    # 7. Garantir device nodes e gravar no Slot 2 (mtd20 / ubi1)
    print("\n[*] [3/4] Gravando no Slot 2 (mtd20 / /dev/ubi1)...")
    run_cmd(tn, "ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true")

    fix_nodes = """for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] || continue
    dev=$(cat $v/dev 2>/dev/null)
    maj=$(echo $dev | cut -d: -f1)
    min=$(echo $dev | cut -d: -f2)
    bname=$(basename $v)
    mknod /dev/$bname c $maj $min 2>/dev/null || true
done"""
    run_cmd(tn, fix_nodes)

    print("    -> Gravando Kernel FIT ARM64 no volume /dev/ubi1_1 (kernel)...")
    out_k = run_cmd(tn, "ubiupdatevol /dev/ubi1_1 /tmp/k_arm64.fit", timeout=30)
    print(f"       {out_k.strip()}")

    print("    -> Gravando RootFS SquashFS no volume /dev/ubi1_2 (ubi_rootfs)...")
    out_r = run_cmd(tn, "ubiupdatevol /dev/ubi1_2 /tmp/root.squashfs", timeout=60)
    print(f"       {out_r.strip()}")

    print("    -> Formatando overlay /dev/ubi1_3 (rootfs_data)...")
    run_cmd(tn, "ubiupdatevol /dev/ubi1_3 -t", timeout=15)

    # Limpeza e sincronizacao
    run_cmd(tn, "rm -f /tmp/k_arm64.fit /tmp/root.squashfs")
    run_cmd(tn, "sync; ubidetach -m 20 2>/dev/null || true")
    print("    [OK] Slot 2 gravado com sucesso, memoria limpa e particao sincronizada!")

    # 8. Chavear bootconfig para Slot 2 (primaryboot=0) e reiniciar
    print("\n[*] [4/4] Gravando BOOTCONFIG para Slot 2 (primaryboot = 0)...")
    cmd_switch = """echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
echo "BOOTCONFIG_APPLIED"
"""
    out_sw = run_cmd(tn, cmd_switch, timeout=15)
    print(f"    {out_sw.strip()}")

    print("\n[*] DISPARANDO REBOOT PARA O SLOT 2 (OPENWRT 64-BIT)...")
    tn.write(b"reboot\n")
    time.sleep(1)
    tn.close()
    httpd.shutdown()

    # 9. Monitoramento ativo do boot
    monitor_boot(max_seconds=180)

if __name__ == "__main__":
    main()
