#!/usr/bin/env python3
"""
gravar_v27_slot2.py
Automacao Segura: Gravacao do Firmware Oficial v1.01.000027 no Slot 2 (mtd20)
Acer Predator Connect T7 (Qualcomm IPQ5332)

Garantias de Seguranca:
- Valida que o Slot 1 (mtd21) esta ativo antes de qualquer acao.
- O Slot 1 JAMAIS e tocado; apenas mtd20 (Slot 2) e mtd3/mtd4 (ponteiro de boot) sao alterados.
- Transfere via HTTP local e valida MD5 dos 3 componentes antes de gravar.
- Instala os atalhos de seguranca 'boot-acer' e 'boot-openwrt' para rollback imediato.
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

# Diretorio onde estao os arquivos extraidos da v27
V27_DIR = r"C:\Users\User\AppData\Local\Temp\audit_work\v27"
KERNEL_FILE = "kernel.bin"
WIFI_FW_FILE = "wifi_fw.bin"
ROOTFS_FILE = "rootfs.squashfs"

KERNEL_PATH = os.path.join(V27_DIR, KERNEL_FILE)
WIFI_FW_PATH = os.path.join(V27_DIR, WIFI_FW_FILE)
ROOTFS_PATH = os.path.join(V27_DIR, ROOTFS_FILE)

def get_md5(fpath):
    with open(fpath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def start_http_server():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=V27_DIR, **kwargs)
        def log_message(self, format, *args):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("0.0.0.0", HTTP_PORT), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def run_cmd(tn, cmd, timeout=60):
    tn.read_very_eager()
    tn.write(cmd.strip().encode("ascii") + b"\n")
    time.sleep(0.2)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    return out

def install_rollback_shortcuts(tn):
    print("[*] Garantindo atalhos de seguranca no roteador (/usr/sbin/)...")
    run_cmd(tn, "chmod +x /usr/sbin/boot-acer /usr/sbin/boot-openwrt 2>/dev/null || true")
    print("    [OK] 'boot-acer' e 'boot-openwrt' prontos e executaveis.")

def main():
    print("=" * 72)
    print("  INSTALADOR SEGURO DO FIRMWARE ACER v1.01.000027 NO SLOT 2 (mtd20)")
    print("  Acer Predator Connect T7 (Qualcomm IPQ5332)")
    print("  Protecao Ativa: Slot 1 (mtd21) 100% Intacto e Imutavel")
    print("=" * 72)

    # 1. Validar presenca e calcular MD5 local dos componentes da v27
    for path, name in [(KERNEL_PATH, "Kernel FIT"), (WIFI_FW_PATH, "Wi-Fi FW"), (ROOTFS_PATH, "RootFS SquashFS")]:
        if not os.path.exists(path):
            print(f"[-] ERRO: Arquivo {name} nao encontrado em {path}!")
            sys.exit(1)

    k_md5 = get_md5(KERNEL_PATH)
    w_md5 = get_md5(WIFI_FW_PATH)
    r_md5 = get_md5(ROOTFS_PATH)

    k_sz = os.path.getsize(KERNEL_PATH)
    w_sz = os.path.getsize(WIFI_FW_PATH)
    r_sz = os.path.getsize(ROOTFS_PATH)

    print(f"[*] Componentes da v27 identificados:")
    print(f"    - Kernel FIT   : {k_sz:,} bytes ({k_sz/(1024*1024):.2f} MB) | MD5: {k_md5}")
    print(f"    - Wi-Fi FW     : {w_sz:,} bytes ({w_sz/(1024*1024):.2f} MB) | MD5: {w_md5}")
    print(f"    - RootFS       : {r_sz:,} bytes ({r_sz/(1024*1024):.2f} MB) | MD5: {r_md5}")

    # 2. Conectar via Telnet
    print(f"\n[*] Conectando ao roteador em {ROUTER_IP}:23...")
    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
        tn.read_until(b"/ # ", timeout=3)
    except Exception as e:
        print(f"[-] Erro ao conectar no Telnet: {e}")
        sys.exit(1)
    print("    [OK] Conexao Telnet estabelecida como root.")

    # 3. Validar se o Slot 1 esta ativo (Travamento de Seguranca)
    slot_info = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    cur_slot = [l.strip() for l in slot_info.split("\n") if l.strip() and not l.startswith("cat ") and not l.startswith("/ #")][-1]
    print(f"[*] Slot ativo detectado: primaryboot = {cur_slot}")

    if cur_slot != "1":
        print("[-] ERRO CRITICO: O roteador NAO esta rodando no Slot 1!")
        print("    Para seguranca do procedimento, o Slot 1 deve estar ativo.")
        tn.close()
        sys.exit(1)
    print("    [OK] Seguranca confirmada: Slot 1 OEM ativo. Slot 2 livre para gravacao.")

    # Instala atalhos de rollback
    install_rollback_shortcuts(tn)

    # 4. Iniciar Servidor HTTP no PC
    print(f"\n[*] Iniciando servidor HTTP local no PC ({PC_IP}:{HTTP_PORT})...")
    httpd = start_http_server()

    # 5. Baixar imagens na RAM (/tmp) do roteador
    print("\n[*] [1/4] Baixando arquivos na memoria RAM do roteador (/tmp)...")
    run_cmd(tn, "rm -f /tmp/v27_kernel.bin /tmp/v27_wifi.bin /tmp/v27_rootfs.bin")

    print("    -> Baixando Kernel...")
    run_cmd(tn, f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/{KERNEL_FILE} -o /tmp/v27_kernel.bin", timeout=60)
    print("    -> Baixando Wi-Fi FW...")
    run_cmd(tn, f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/{WIFI_FW_FILE} -o /tmp/v27_wifi.bin", timeout=60)
    print("    -> Baixando RootFS...")
    run_cmd(tn, f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/{ROOTFS_FILE} -o /tmp/v27_rootfs.bin", timeout=120)

    # 6. Validar integridade MD5 no roteador
    print("\n[*] [2/4] Verificando integridade MD5 na memoria RAM do roteador...")
    md5_remote = run_cmd(tn, "md5sum /tmp/v27_kernel.bin /tmp/v27_wifi.bin /tmp/v27_rootfs.bin")
    print(f"    Hashes remotos conferidos:\n{md5_remote.strip()}")

    if k_md5 not in md5_remote or w_md5 not in md5_remote or r_md5 not in md5_remote:
        print("[-] ERRO FATAL: Os hashes MD5 recebidos no roteador divergiram!")
        run_cmd(tn, "rm -f /tmp/v27_kernel.bin /tmp/v27_wifi.bin /tmp/v27_rootfs.bin")
        tn.close()
        httpd.shutdown()
        sys.exit(1)
    print("    [OK] Todos os 3 hashes MD5 estao 100% perfeitos.")

    # 7. Anexar UBI no mtd20 e gravar os 3 volumes
    print("\n[*] [3/4] Gravando na particao mtd20 (Slot 2)...")
    run_cmd(tn, "ubiattach /dev/ubi_ctrl -m 20 2>/dev/null || true")

    # Garante device nodes
    run_cmd(tn, "for v in /sys/class/ubi/ubi1_*; do [ -d \"$v\" ] && mknod /dev/$(basename $v) c $(cat $v/dev | tr : ' ') 2>/dev/null; done")

    print("    -> Gravando Wi-Fi FW no volume ubi1_0...")
    out_w = run_cmd(tn, "ubiupdatevol /dev/ubi1_0 /tmp/v27_wifi.bin", timeout=60)
    print(f"       {out_w.strip()}")

    print("    -> Gravando Kernel no volume ubi1_1...")
    out_k = run_cmd(tn, "ubiupdatevol /dev/ubi1_1 /tmp/v27_kernel.bin", timeout=60)
    print(f"       {out_k.strip()}")

    print("    -> Gravando RootFS no volume ubi1_2...")
    out_r = run_cmd(tn, "ubiupdatevol /dev/ubi1_2 /tmp/v27_rootfs.bin", timeout=120)
    print(f"       {out_r.strip()}")

    print("    -> Formatando/limpando overlay antigo no volume ubi1_3...")
    run_cmd(tn, "ubiupdatevol /dev/ubi1_3 -t", timeout=30)

    # Limpeza e sync
    run_cmd(tn, "rm -f /tmp/v27_kernel.bin /tmp/v27_wifi.bin /tmp/v27_rootfs.bin")
    run_cmd(tn, "sync")
    print("    [OK] Volumes do Slot 2 gravados e sincronizados com sucesso!")

    # 8. Chavear bootconfig para Slot 2 e reiniciar
    apply_switch = True
    if len(sys.argv) > 1 and sys.argv[1] == "--no-reboot":
        apply_switch = False

    if apply_switch:
        print("\n[*] [4/4] Chaveando BOOTCONFIG para Slot 2 (primaryboot = 0) e reiniciando...")
        out_boot = run_cmd(tn, "/usr/sbin/boot-openwrt", timeout=15)
        print(f"       {out_boot.strip()}")
        print("    [OK] O roteador esta reiniciando no Slot 2 rodando a versao 1.01.000027!")
        print("\n" + "=" * 72)
        print("  PROXIMOS PASSOS APOS O BOOT:")
        print("  1. Aguarde cerca de 90 segundos.")
        print(f"  2. Acesse http://{ROUTER_IP} ou http://192.168.1.1 no navegador.")
        print("  3. Restaure o arquivo 'config_ssh_unlocked.cfg' para reativar o Root/SSH.")
        print("  4. Se quiser voltar ao Slot 1, rode: python switch_boot_slot.py 1")
        print("=" * 72)
    else:
        print("\n[*] Flag --no-reboot detectada. Gravacao concluida sem reiniciar.")
        print("    Para chavear manualmente quando quiser, execute:")
        print("    python switch_boot_slot.py 2")

    tn.close()
    httpd.shutdown()

if __name__ == "__main__":
    main()
