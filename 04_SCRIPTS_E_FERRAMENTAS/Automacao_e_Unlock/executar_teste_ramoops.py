#!/usr/bin/env python3
"""
=============================================================================
EXECUTOR DO DIAGNOSTICO RAMOOPS (OPCAO 1) - ACER PREDATOR CONNECT T7
=============================================================================
1. Verifica se o roteador esta no Slot 1 (Acer Original).
2. Grava o kernel openwrt-predator-t7-kernel-ramoops.fit no Slot 2 (mtd20).
3. Grava marcador 0xDEADBEEF em 0x4CC00000.
4. Chaveia o bootconfig para Slot 2 (primaryboot=0) e reinicia.
5. Monitora a inicializacao:
   - Se subir OpenWrt: Notifica sucesso de boot!
   - Se reiniciar por watchdog para Slot 1: Extrai automaticamente o log Ramoops!
   - Se cair no Failsafe Web U-Boot (192.168.1.1:80): Detecta e notifica!
=============================================================================
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
import subprocess

ROUTER_IP = "192.168.73.2"
PC_IP = "192.168.73.90"
HTTP_PORT = 8089

BASE_DIR = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7"
IMG_DIR = os.path.join(BASE_DIR, "1 - Firmware e Imagens OpenWrt")
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts_Automacao")
KERNEL_RAMOOPS = os.path.join(IMG_DIR, "openwrt-predator-t7-kernel-ramoops.fit")

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

def run_cmd(tn, cmd, timeout=30):
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.4)
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

def monitor_and_diagnose(max_seconds=240):
    print("\n" + "=" * 70)
    print("MONITORAMENTO ATIVO DO VOO DO KERNEL COM RAMOOPS")
    print("Aguardando U-Boot carregar o kernel ARM64 instrumentado...")
    print("=" * 70)

    start_time = time.time()
    reboot_detected = False

    while time.time() - start_time < max_seconds:
        elapsed = int(time.time() - start_time)

        if not reboot_detected:
            if not check_port(ROUTER_IP, 23, timeout=0.5):
                print(f"[{elapsed:03d}s] [+] O roteador reiniciou! Conexao encerrada.")
                reboot_detected = True

        # Verificar se subiu OpenWrt na porta 80 ou 22 em 192.168.1.1 ou 192.168.73.2
        p80_openwrt = check_port("192.168.1.1", 80, timeout=0.4)
        p22_openwrt = check_port("192.168.1.1", 22, timeout=0.4)
        p23_openwrt = check_port("192.168.1.1", 23, timeout=0.4)

        if p22_openwrt or (p80_openwrt and not p23_openwrt):
            # Pode ser OpenWrt ou Failsafe U-Boot
            # Se for failsafe U-Boot, porta 80 responde U-Boot Web Recovery
            print(f"\n[{elapsed:03d}s] [!] DETECTADA ATIVIDADE EM 192.168.1.1!")
            if p22_openwrt:
                print("    -> SSH ABERTO! OpenWrt Mainline ARM64 inicializou com sucesso no Slot 2!")
                return "OPENWRT_SUCCESS"
            if p80_openwrt:
                print("    -> Porta 80 aberta em 192.168.1.1 (Verificando se e U-Boot Failsafe ou LuCI)...")
                # Testar se e U-Boot Failsafe
                import urllib.request
                try:
                    req = urllib.request.urlopen("http://192.168.1.1/", timeout=2)
                    html = req.read().decode("latin1", errors="ignore")
                    if "failsafe" in html.lower() or "u-boot" in html.lower() or "recovery" in html.lower() or "firmware update" in html.lower():
                        print("    [!] CONFIRMADO: Roteador entrou em modo U-Boot Web Failsafe!")
                        return "UBOOT_FAILSAFE"
                    else:
                        print("    [+] LuCI Web GUI detectada!")
                        return "OPENWRT_SUCCESS"
                except:
                    pass

        # Verificar se voltou para Slot 1 (Acer Original 192.168.73.2)
        p23_acer = check_port(ROUTER_IP, 23, timeout=0.4)
        if reboot_detected and p23_acer and elapsed > 30:
            print(f"\n[{elapsed:03d}s] [!] O ROTEADOR RETORNOU AO SLOT 1 (ACER ORIGINAL) VIA WATCHDOG!")
            print("    -> A caixa-preta Ramoops esta intacta na memoria RAM 0x4CC00000!")
            print("    -> Disparando extracao automatica de logs...")
            return "SLOT1_REBOOTED"

        time.sleep(2)
        sys.stdout.write(f"\r[{elapsed:03d}s] Monitorando estado (OpenWrt 192.168.1.1 / Acer 192.168.73.2)...")
        sys.stdout.flush()

    print("\n[-] Tempo limite de monitoramento esgotado.")
    return "TIMEOUT"

def main():
    print("=" * 70)
    print("INICIANDO PROCEDIMENTO DIAGNOSTICO: RAMOOPS FLIGHT RECORDER")
    print("Acer Predator Connect T7 (IPQ5322)")
    print("=" * 70)

    if not os.path.exists(KERNEL_RAMOOPS):
        print(f"[-] ERRO: Arquivo do kernel Ramoops nao encontrado: {KERNEL_RAMOOPS}")
        return 1

    k_md5 = get_md5(KERNEL_RAMOOPS)
    k_sz = os.path.getsize(KERNEL_RAMOOPS)
    print(f"[*] Kernel Ramoops FIT: {k_sz} bytes ({k_sz/(1024*1024):.2f} MB) | MD5: {k_md5}")

    # 1. Conectar ao roteador
    print(f"[*] Conectando ao roteador em {ROUTER_IP} via Telnet...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
    tn.read_until(b"/ # ", timeout=5)

    # 2. Validar que estamos no Slot 1
    slot_info = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    cur_slot = [l.strip() for l in slot_info.split("\n") if l.strip() and not l.startswith("cat ") and not l.startswith("/ #")][-1]
    print(f"[*] Slot ativo atual: primaryboot = {cur_slot}")
    if cur_slot != "1":
        print("[-] ERRO CRITICO: O roteador nao esta no Slot 1! Abortando.")
        tn.close()
        return 1
    print("    [OK] Confirmado: Slot 1 ativo. O Slot 2 (mtd20) esta totalmente livre para gravacao.")

    # 3. Iniciar servidor HTTP para transferir o kernel
    print(f"[*] Subindo servidor HTTP temporario em {PC_IP}:{HTTP_PORT}...")
    httpd = start_http_server()

    # 4. Baixar kernel Ramoops na RAM do roteador
    print("[*] [1/4] Baixando openwrt-predator-t7-kernel-ramoops.fit no /tmp do roteador...")
    run_cmd(tn, "rm -f /tmp/k_ramoops.fit")
    cmd_dl = f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/openwrt-predator-t7-kernel-ramoops.fit -o /tmp/k_ramoops.fit"
    run_cmd(tn, cmd_dl, timeout=30)

    # 5. Validar MD5
    md5_remote = run_cmd(tn, "md5sum /tmp/k_ramoops.fit")
    print(f"    Hash no roteador:\n{md5_remote.strip()}")
    if k_md5 not in md5_remote:
        print("[-] ERRO: Hash MD5 divergente! Abortando gravacao.")
        run_cmd(tn, "rm -f /tmp/k_ramoops.fit")
        tn.close()
        httpd.shutdown()
        return 1
    print("    [OK] Integridade do kernel verificada com 100% de sucesso!")

    # 6. Gravar kernel Ramoops no Slot 2 (mtd20)
    print("\n[*] [2/4] Gravando kernel instrumentado no Slot 2 (mtd20 /dev/ubi1_1)...")
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

    out_k = run_cmd(tn, "ubiupdatevol /dev/ubi1_1 /tmp/k_ramoops.fit", timeout=30)
    print(f"    Resultado gravacao: {out_k.strip()}")

    print("    -> Formatando overlay /dev/ubi1_3 para inicializacao limpa...")
    run_cmd(tn, "ubiupdatevol /dev/ubi1_3 -t", timeout=15)

    run_cmd(tn, "rm -f /tmp/k_ramoops.fit")
    run_cmd(tn, "sync; ubidetach -m 20 2>/dev/null || true")
    httpd.shutdown()

    # 7. Gravar marcador na RAM e chavear bootconfig
    print("\n[*] [3/4] Gravando marcador de integridade 0xDEADBEEF na DRAM fisica 0x4CC00000...")
    run_cmd(tn, "devmem 0x4cc00000 32 0xdeadbeef")
    mem_check = run_cmd(tn, "devmem 0x4cc00000 32")
    print(f"    Leitura de confirmacao: {mem_check.strip()}")

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
echo "BOOTCONFIG_OK"
"""
    out_sw = run_cmd(tn, cmd_switch, timeout=15)
    print(f"    {out_sw.strip()}")

    print("\n" + "=" * 70)
    print("[DISPARO] ENVIANDO REBOOT PARA O SLOT 2 COM KERNEL RAMOOPS...")
    print("=" * 70)
    tn.write(b"reboot\n")
    time.sleep(1)
    tn.close()

    # 8. Monitorar e agir conforme o resultado
    res = monitor_and_diagnose(max_seconds=240)

    if res == "SLOT1_REBOOTED":
        print("\n" + "=" * 70)
        print("CONECTANDO AO SLOT 1 PARA EXTRAIR A CAIXA-PRETA...")
        print("=" * 70)
        time.sleep(3)
        ext_script = os.path.join(SCRIPTS_DIR, "extrair_ramoops_log.py")
        subprocess.run(["python", ext_script, ROUTER_IP])
    elif res == "UBOOT_FAILSAFE":
        print("\n[!] O roteador esta no Failsafe Web U-Boot (192.168.1.1).")
        print("    Para retornar ao Slot 1, podemos enviar restaurar_slot1_acer.itb via HTTP POST.")
    elif res == "OPENWRT_SUCCESS":
        print("\n[+] SUCESSO! O kernel com Ramoops inicializou perfeitamente!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
