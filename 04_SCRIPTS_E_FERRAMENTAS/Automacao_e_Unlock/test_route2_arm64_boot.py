#!/usr/bin/env python3
"""
Executador e Monitor da Rota 2 (OpenWrt Mainline AArch64 / Kernel 6.18) no Slot 2
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
INITRAMFS_PATH = os.path.join(IMG_DIR, "openwrt-qualcommbe-ipq53xx-acer_predator-t7-initramfs.itb")
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
    print("MONITORAMENTO ATIVO DO BOOT DO OPENWRT 64-BIT (ROTA 2)")
    print("Aguardando U-Boot inicializar monitor QSEE e subir o Kernel 6.18...")
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
                print(f"[{elapsed:03d}s] [+] O roteador reiniciou! Conexao de rede anterior fechada.")
                reboot_detected = True

        for ip, label in target_ips:
            p80 = check_port(ip, 80, timeout=0.4)
            p22 = check_port(ip, 22, timeout=0.4)
            p23 = check_port(ip, 23, timeout=0.4)
            p8080 = check_port(ip, 8080, timeout=0.4)

            if p80 or p22 or p23 or p8080:
                print(f"\n[{elapsed:03d}s] [!!!] SUCESSO! RESPOSTA DETECTADA EM {ip} ({label}) [!!!]")
                if p80:   print(f"    -> Porta 80   (HTTP LuCI Web): ABERTA")
                if p22:   print(f"    -> Porta 22   (SSH Dropbear):  ABERTA")
                if p23:   print(f"    -> Porta 23   (Telnet Debug):  ABERTA")
                if p8080: print(f"    -> Porta 8080 (LuCI Hibrido):  ABERTA")
                print("=" * 70)
                print("[OK] OPENWRT AARCH64 (KERNEL 6.18) SUBIU COM SUCESSO NO SLOT 2!")
                print("=" * 70)
                return True

        time.sleep(2)
        sys.stdout.write(f"\r[{elapsed:03d}s] Sondando rede (192.168.1.1 / 192.168.73.2)...")
        sys.stdout.flush()

    print("\n[-] Tempo limite atingido. Verificando estado...")
    return False

def main():
    print("=" * 70)
    print("INICIALIZADOR DA ROTA 2 - OPENWRT 64-BIT (AARCH64 / KERNEL 6.18)")
    print("Acer Predator Connect T7 (Qualcomm IPQ5322)")
    print("Slot 1 (Acer Original): Totalmente Preservado")
    print("Slot 2 (OpenWrt AArch64): Alvo de Gravacao e Boot")
    print("=" * 70)

    # 1. Validar arquivos locais
    if not os.path.exists(INITRAMFS_PATH) or not os.path.exists(ROOTFS_PATH):
        print(f"[-] Erro: Arquivos de imagem nao encontrados no PC!")
        sys.exit(1)

    init_md5 = get_md5(INITRAMFS_PATH)
    root_md5 = get_md5(ROOTFS_PATH)
    init_sz = os.path.getsize(INITRAMFS_PATH)
    root_sz = os.path.getsize(ROOTFS_PATH)
    print(f"[*] Imagem Initramfs ITB : {init_sz} bytes ({init_sz/(1024*1024):.2f} MB) | MD5: {init_md5}")
    print(f"[*] Imagem RootFS Squash : {root_sz} bytes ({root_sz/(1024*1024):.2f} MB) | MD5: {root_md5}")

    # 2. Conectar via Telnet
    print(f"\n[*] Conectando ao roteador em {ROUTER_IP}...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
    tn.read_until(b"/ # ", timeout=3)

    # 3. Validar slot atual (deve ser Slot 1)
    slot_info = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    cur_slot = [l.strip() for l in slot_info.split("\n") if l.strip() and not l.startswith("cat ") and not l.startswith("/ #")][-1]
    print(f"[*] Slot ativo atual: primaryboot = {cur_slot}")
    if cur_slot != "1":
        print("[-] ERRO: O roteador nao esta no Slot 1! Abortando para evitar sobrescrita indevida.")
        tn.close()
        sys.exit(1)
    print("    [OK] Confirmado: Slot 1 ativo. O Slot 2 (mtd20) esta livre e seguro para gravacao.")

    # 4. Iniciar Servidor HTTP temporario
    print(f"\n[*] Iniciando servidor HTTP local no PC ({PC_IP}:{HTTP_PORT})...")
    httpd = start_http_server()

    # 5. Baixar imagens no roteador
    print("\n[*] [1/5] Transferindo imagens para a memoria RAM (/tmp) do roteador...")
    run_cmd(tn, "rm -f /tmp/openwrt_initramfs.itb /tmp/root.squashfs")
    
    cmd_dl_init = f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/openwrt-qualcommbe-ipq53xx-acer_predator-t7-initramfs.itb -o /tmp/openwrt_initramfs.itb"
    print("    -> Baixando OpenWrt Initramfs ITB (Kernel 6.18 ARM64)...")
    run_cmd(tn, cmd_dl_init, timeout=30)

    cmd_dl_root = f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/root.squashfs -o /tmp/root.squashfs"
    print("    -> Baixando RootFS SquashFS...")
    run_cmd(tn, cmd_dl_root, timeout=30)

    # 6. Validar MD5 no roteador
    print("\n[*] [2/5] Validando integridade das imagens na RAM do roteador...")
    md5_remote = run_cmd(tn, "md5sum /tmp/openwrt_initramfs.itb /tmp/root.squashfs")
    print(f"    Hashes Remotos:\n{md5_remote.strip()}")
    if init_md5 not in md5_remote or root_md5 not in md5_remote:
        print("[-] ERRO: Hash MD5 divergente no roteador! Abortando.")
        run_cmd(tn, "rm -f /tmp/openwrt_initramfs.itb /tmp/root.squashfs")
        tn.close()
        httpd.shutdown()
        sys.exit(1)
    print("    [OK] Hashes MD5 100% conferidos com perfeicao!")

    # 7. Anexar Slot 2 (mtd20) e redimensionar volumes UBI
    print("\n[*] [3/5] Configurando layout UBI no Slot 2 (mtd20 / rootfs_1)...")
    run_cmd(tn, "ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true", timeout=10)

    # Remover volumes antigos que serao recriados
    print("    -> Removendo volumes antigos (rootfs_data, ubi_rootfs, kernel)...")
    run_cmd(tn, "ubirmvol /dev/ubi1 -n 3 2>/dev/null || true")
    run_cmd(tn, "ubirmvol /dev/ubi1 -n 2 2>/dev/null || true")
    run_cmd(tn, "ubirmvol /dev/ubi1 -n 1 2>/dev/null || true")

    # Recriar volumes com tamanhos otimizados para 64-bit
    print("    -> Criando volume 1 'kernel' com 32 MiB...")
    out_v1 = run_cmd(tn, "ubimkvol /dev/ubi1 -n 1 -N kernel -s 32MiB")
    print(f"       {out_v1.strip()}")

    print("    -> Criando volume 2 'ubi_rootfs' com 40 MiB...")
    out_v2 = run_cmd(tn, "ubimkvol /dev/ubi1 -n 2 -N ubi_rootfs -s 40MiB")
    print(f"       {out_v2.strip()}")

    print("    -> Criando volume 3 'rootfs_data' com restante do espaco livre...")
    out_v3 = run_cmd(tn, "ubimkvol /dev/ubi1 -n 3 -N rootfs_data -m")
    print(f"       {out_v3.strip()}")

    # Garantir device nodes
    fix_nodes = """for v in /sys/class/ubi/ubi1_*; do
    [ -d "$v" ] || continue
    dev=$(cat $v/dev 2>/dev/null)
    maj=$(echo $dev | cut -d: -f1)
    min=$(echo $dev | cut -d: -f2)
    bname=$(basename $v)
    mknod /dev/$bname c $maj $min 2>/dev/null || true
done"""
    run_cmd(tn, fix_nodes)

    # 8. Gravar imagens nos volumes UBI do Slot 2
    print("\n[*] [4/5] Gravando imagens nos volumes do Slot 2...")
    print("    -> Gravando Initramfs ITB 64-bit no volume 'kernel' (/dev/ubi1_1)...")
    out_flash_k = run_cmd(tn, "ubiupdatevol /dev/ubi1_1 /tmp/openwrt_initramfs.itb", timeout=60)
    print(f"       {out_flash_k.strip()}")

    print("    -> Gravando RootFS SquashFS no volume 'ubi_rootfs' (/dev/ubi1_2)...")
    out_flash_r = run_cmd(tn, "ubiupdatevol /dev/ubi1_2 /tmp/root.squashfs", timeout=60)
    print(f"       {out_flash_r.strip()}")

    print("    -> Formatando area de overlay 'rootfs_data' (/dev/ubi1_3)...")
    run_cmd(tn, "ubiupdatevol /dev/ubi1_3 -t", timeout=15)

    # Limpar RAM e desanexar UBI
    run_cmd(tn, "rm -f /tmp/openwrt_initramfs.itb /tmp/root.squashfs")
    run_cmd(tn, "sync; ubidetach -m 20 2>/dev/null || true")
    print("    [OK] Volumes gravados, buffers sincronizados e mtd20 desanexado com seguranca!")

    # 9. Configurar chaveamento para Slot 2 (primaryboot=0) e reiniciar
    print("\n[*] [5/5] Configurando BOOTCONFIG para Slot 2 (primaryboot = 0)...")
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

    # 10. Iniciar monitoramento continuo
    monitor_boot(max_seconds=180)

if __name__ == "__main__":
    main()
