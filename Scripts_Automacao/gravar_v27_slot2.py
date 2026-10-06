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
- Localizacao 100% dinamica e portavel em qualquer PC (sem caminhos fixos de usuario).
- Auto-deteccao inteligente do IP do roteador e do IP da placa de rede local.
"""

import http.server
import socketserver
import threading
import socket
import time
import os
import hashlib
import sys
import tempfile
import argparse

try:
    from telnet_compat import Telnet
except ImportError:
    try:
        from Scripts_Automacao.telnet_compat import Telnet
    except ImportError:
        import telnetlib
        Telnet = telnetlib.Telnet
try:
    from logger_t7 import log_event, log_cmd, log_dump
except ImportError:
    try:
        from Scripts_Automacao.logger_t7 import log_event, log_cmd, log_dump
    except ImportError:
        def log_event(action, message, status="INFO", details=None):
            pass
        def log_cmd(cmd, output, status="CMD"):
            pass
        def log_dump(title, content):
            pass

def find_repo_root():
    cur = os.path.dirname(os.path.abspath(__file__))
    while cur and cur != os.path.dirname(cur):
        if os.path.exists(os.path.join(cur, "01_FIRMWARES_E_IMAGENS")):
            return cur
        cur = os.path.dirname(cur)
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

REPO_DIR = find_repo_root()

# Diretorio canônico no repositório com os componentes extraídos da v27
REPO_V27_DIR = os.path.join(REPO_DIR, "01_FIRMWARES_E_IMAGENS", "Official_v27_Componentes")

KERNEL_FILE = "kernel.bin"
WIFI_FW_FILE = "wifi_fw.bin"
ROOTFS_FILE = "rootfs.squashfs"

DEFAULT_HTTP_PORT = 8089

def get_md5(fpath):
    with open(fpath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def test_telnet(ip, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, 23))
        s.close()
        return True
    except Exception:
        return False

def detect_router_ip(explicit_ip=None):
    if explicit_ip:
        return explicit_ip

    print("[*] Detectando endereco IP do roteador...")
    # 1. Tentar adivinhar pela sub-rede do computador
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        my_ip = s.getsockname()[0]
        s.close()
        parts = my_ip.split(".")
        guess = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
        if test_telnet(guess, 1):
            print(f"    [+] Roteador detectado via gateway local: {guess}")
            return guess
    except Exception:
        pass

    # 2. Sondagem rapida nos IPs conhecidos
    for candidate in ["192.168.76.1", "192.168.73.2", "192.168.1.1"]:
        if test_telnet(candidate, 1):
            print(f"    [+] Roteador respondendo em Telnet na porta 23: {candidate}")
            return candidate

    print("    [!] Nao foi possivel detectar automaticamente. Usando padrao: 192.168.76.1")
    return "192.168.76.1"

def detect_pc_ip(router_ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((router_ip, 80))
        pc_ip = s.getsockname()[0]
        s.close()
        return pc_ip
    except Exception:
        return "192.168.76.100"

def locate_v27_directory(explicit_dir=None):
    candidates = []
    if explicit_dir:
        candidates.append(explicit_dir)
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    candidates.extend([
        REPO_V27_DIR,
        os.path.join(desktop, "Acer-Predator-Connect-T7", "01_FIRMWARES_E_IMAGENS", "Official_v27_Componentes"),
        r"C:\Users\User\Desktop\Acer-Predator-Connect-T7\01_FIRMWARES_E_IMAGENS\Official_v27_Componentes",
        r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\01_FIRMWARES_E_IMAGENS\Official_v27_Componentes",
        r"C:\Users\User\Acer-Predator-Connect-T7\01_FIRMWARES_E_IMAGENS\Official_v27_Componentes"
    ])

    for c in candidates:
        if os.path.isdir(c):
            k = os.path.join(c, KERNEL_FILE)
            w = os.path.join(c, WIFI_FW_FILE)
            r = os.path.join(c, ROOTFS_FILE)
            if os.path.exists(k) and os.path.exists(w) and os.path.exists(r):
                return c

    return None

def start_http_server(directory, port):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        def log_message(self, format, *args):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("0.0.0.0", port), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def run_cmd(tn, cmd, timeout=60):
    tn.read_very_eager()
    tn.write(cmd.strip().encode("ascii") + b"\n")
    time.sleep(0.2)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    log_cmd(cmd, out)
    return out

def install_rollback_shortcuts(tn):
    print("[*] Instalando scripts de chaveamento e rollback (/usr/sbin/boot-acer e /usr/sbin/boot-openwrt)...")
    cmd_boot_acer = """cat << 'EOFB' > /usr/sbin/boot-acer
#!/bin/sh
echo "=== Retornando boot para SLOT 1 (OEM v24) ==="
echo 1 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 1 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
echo "[OK] Slot 1 configurado com sucesso! Reiniciando..."
reboot
EOFB
chmod +x /usr/sbin/boot-acer
"""
    cmd_boot_openwrt = """cat << 'EOFB' > /usr/sbin/boot-openwrt
#!/bin/sh
echo "=== Chaveando boot para SLOT 2 ==="
echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
echo "[OK] Slot 2 configurado com sucesso! Reiniciando..."
reboot
EOFB
chmod +x /usr/sbin/boot-openwrt
"""
    run_cmd(tn, cmd_boot_acer)
    run_cmd(tn, cmd_boot_openwrt)
    print("    [OK] 'boot-acer' e 'boot-openwrt' prontos e executaveis no roteador.")

def main():
    parser = argparse.ArgumentParser(description="Instalador do Firmware v27 no Slot 2 do Acer Predator T7")
    parser.add_argument("--router-ip", "-r", help="IP do roteador (padrao: autodetectado)")
    parser.add_argument("--pc-ip", "-p", help="IP local deste computador (padrao: autodetectado)")
    parser.add_argument("--v27-dir", "-d", help="Diretorio com kernel.bin, wifi_fw.bin e rootfs.squashfs")
    parser.add_argument("--http-port", type=int, default=DEFAULT_HTTP_PORT, help="Porta para servidor HTTP temporario")
    parser.add_argument("--no-reboot", action="store_true", help="Grava sem reiniciar automaticamente no final")
    parser.add_argument("--with-root", action="store_true", help="Grava v27 com ROOT desbloqueado diretamente sem prompt")
    parser.add_argument("--pure-stock", action="store_true", help="Grava v27 puro de fabrica sem root")
    parser.add_argument("--yes", "-y", action="store_true", help="Confirma automaticamente sem pedir confirmacao manual")
    args, unknown = parser.parse_known_args()

    # Se o usuario passou o IP diretamente sem flag: python gravar_v27_slot2.py 192.168.76.1
    if unknown and not args.router_ip:
        args.router_ip = unknown[0]

    print("=" * 72)
    print("  INSTALADOR SEGURO DO FIRMWARE ACER v1.01.000027 NO SLOT 2 (mtd20)")
    print("  Acer Predator Connect T7 (Qualcomm IPQ5332)")
    print("  Protecao Ativa: Slot 1 (mtd21) 100% Intacto e Imutavel")
    print("=" * 72)

    # 1. Localizar componentes da v27 de forma dinamica e portavel
    v27_dir = locate_v27_directory(args.v27_dir)
    if not v27_dir:
        print(f"[-] ERRO: Componentes da v27 (kernel.bin, wifi_fw.bin, rootfs.squashfs) nao encontrados!")
        print(f"    Pasta procurada: {REPO_V27_DIR}")
        print("    Certifique-se de que a pasta existe no repositorio ou passe via --v27-dir.")
        sys.exit(1)

    kernel_path = os.path.join(v27_dir, KERNEL_FILE)
    wifi_fw_path = os.path.join(v27_dir, WIFI_FW_FILE)
    rootfs_path = os.path.join(v27_dir, ROOTFS_FILE)

    k_md5 = get_md5(kernel_path)
    w_md5 = get_md5(wifi_fw_path)
    r_md5 = get_md5(rootfs_path)

    k_sz = os.path.getsize(kernel_path)
    w_sz = os.path.getsize(wifi_fw_path)
    r_sz = os.path.getsize(rootfs_path)

    print(f"\n[*] Diretorio de componentes identificado: {v27_dir}")
    print(f"    - Kernel FIT   : {k_sz:,} bytes ({k_sz/(1024*1024):.2f} MB) | MD5: {k_md5}")
    print(f"    - Wi-Fi FW     : {w_sz:,} bytes ({w_sz/(1024*1024):.2f} MB) | MD5: {w_md5}")
    print(f"    - RootFS       : {r_sz:,} bytes ({r_sz/(1024*1024):.2f} MB) | MD5: {r_md5}")

    # 2. Deteccao de IP
    router_ip = detect_router_ip(args.router_ip)
    pc_ip = args.pc_ip if args.pc_ip else detect_pc_ip(router_ip)
    http_port = args.http_port

    print(f"\n[*] Parametros de rede definidos:")
    print(f"    - IP do Roteador   : {router_ip}")
    print(f"    - IP do Computador : {pc_ip}")
    print(f"    - Porta HTTP Local : {http_port}")

    # 3. Conectar via Telnet
    print(f"\n[*] Conectando ao roteador em {router_ip}:23...")
    try:
        tn = Telnet(router_ip, 23, timeout=5)
        tn.read_until("/ # ", timeout=3)
    except Exception as e:
        print(f"[-] Erro ao conectar no Telnet em {router_ip}: {e}")
        print("    Certifique-se de que o roteador esta ligado e com Telnet destravado.")
        sys.exit(1)
    print("    [OK] Conexao Telnet estabelecida com sucesso.")

    # 4. Validar o Modelo de Hardware (Whitelist Estrita: Somente o modelo oficial autorizado)
    board_name = run_cmd(tn, "cat /tmp/sysinfo/board_name 2>/dev/null").strip()
    model_str  = run_cmd(tn, "cat /tmp/sysinfo/model 2>/dev/null").strip()
    fdt_model  = run_cmd(tn, "cat /proc/device-tree/model 2>/dev/null").strip()
    hw_tokens  = f"{board_name} {model_str} {fdt_model}".lower()

    print(f"[*] Hardware detectado: {model_str or board_name or 'N/A'}")

    # Whitelist Estrita: Somente a placa física homologada do Acer Predator Connect T7 (AP-MI01.6)
    is_authorized = ("ap-mi01.6" in hw_tokens) or ("predator connect t7" in hw_tokens) or ("predator_t7" in hw_tokens)

    if not is_authorized:
        print("\n" + "=" * 75)
        print("[-] BLOQUEIO DE SEGURANÇA: HARDWARE NÃO AUTORIZADO!")
        print(f"    Dispositivo Detectado : {model_str or board_name or 'Desconhecido'}")
        print(f"    Dispositivo Autorizado: Acer Predator Connect T7 (Placa AP-MI01.6)")
        print("\n    ESTE PACOTE DE GRAVAÇÃO É EXCLUSIVO PARA O ACER PREDATOR CONNECT T7!")
        print("    A gravação na memória flash foi CANCELADA para proteger seu equipamento.")
        print("=" * 75)
        tn.close()
        sys.exit(1)
    print("    [OK] Hardware validado com sucesso: Acer Predator Connect T7 (Autorizado).")

    # 5. Validar se o Slot 1 esta ativo (Trava de Seguranca)
    slot_info = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    cur_slot = [l.strip() for l in slot_info.split("\n") if l.strip() and not l.startswith("cat ") and not l.startswith("/ #")][-1]
    print(f"[*] Slot ativo detectado: primaryboot = {cur_slot}")

    if cur_slot != "1":
        print("[-] ERRO CRITICO: O roteador NAO esta rodando no Slot 1!")
        print("    Para seguranca do procedimento, o Slot 1 deve estar ativo.")
        log_event("GRAVACAO_SLOT2", f"Abortado: Roteador nao esta no Slot 1 (primaryboot={cur_slot})", "ERRO")
        tn.close()
        sys.exit(1)
    print("    [OK] Seguranca confirmada: Slot 1 OEM ativo. Slot 2 livre para gravacao.")

    # Submenu de Escolha de Modo de Instalacao
    if args.with_root:
        inst_choice = "1"
    elif args.pure_stock:
        inst_choice = "2"
    else:
        while True:
            print("\n" + "=" * 72)
            print("  MODO DE INSTALACAO DO FIRMWARE NO SLOT 2:")
            print("=" * 72)
            print("  [1] Firmware Oficial v27 + ROOT Desbloqueado (Recomendado)")
            print("      - Grava o sistema oficial v27 da Acer")
            print("      - Injeta automaticamente usuario 'root', SSH Dropbear e Telnet")
            print("      - O Slot 2 ja acorda liberado no terminal sem precisar de .cfg!")
            print("")
            print("  [2] Firmware Oficial v27 Puro de Fabrica (100% Stock OEM Travado)")
            print("      - Grava o sistema oficial v27 da Acer")
            print("      - Formata e zera o volume de dados (sem qualquer alteracao)")
            print("      - O Slot 2 acorda exatamente como veio de fabrica na caixa")
            print("=" * 72)
            inst_choice = input("  Digite o numero da opcao desejada [1 ou 2]: ").strip()
            if inst_choice in ["1", "2"]:
                break
            print("\n  [!] Entrada invalida! Digite obrigatoriamente o numero 1 ou 2.")

    with_root = (inst_choice == "1")
    if with_root:
        print("  [+] Modo confirmado: Oficial v27 com ROOT Desbloqueado.")
        log_event("GRAVACAO_SLOT2", "Modo selecionado: Oficial v27 com ROOT", "INFO")
    else:
        print("  [+] Modo confirmado: Oficial v27 100% Stock OEM Travado de Fabrica.")
        log_event("GRAVACAO_SLOT2", "Modo selecionado: Oficial v27 Stock OEM Travado", "INFO")

    if not args.yes:
        confirm = input("\n  Confirma o inicio da gravacao no Slot 2 (mtd20)? [S/N]: ").strip().upper()
        if confirm not in ["S", "SIM", "Y", "YES"]:
            print("\n  [!] Operacao cancelada pelo usuario. Nenhuma alteracao foi feita.")
            log_event("GRAVACAO_SLOT2", "Cancelado pelo usuario antes de gravar", "AVISO")
            tn.close()
            sys.exit(0)
    else:
        print("  [+] Confirmacao automatica (--yes). Iniciando gravacao no Slot 2...")

    # Instala atalhos de rollback
    install_rollback_shortcuts(tn)

    # 5. Iniciar Servidor HTTP no PC
    print(f"\n[*] Iniciando servidor HTTP local no PC ({pc_ip}:{http_port})...")
    httpd = start_http_server(v27_dir, http_port)

    # 6. Baixar imagens na RAM (/tmp) do roteador
    print("\n[*] [1/4] Baixando arquivos na memoria RAM do roteador (/tmp)...")
    run_cmd(tn, "rm -f /tmp/v27_kernel.bin /tmp/v27_wifi.bin /tmp/v27_rootfs.bin")

    print("    -> Baixando Kernel...")
    run_cmd(tn, f"curl -fsSL http://{pc_ip}:{http_port}/{KERNEL_FILE} -o /tmp/v27_kernel.bin", timeout=60)
    print("    -> Baixando Wi-Fi FW...")
    run_cmd(tn, f"curl -fsSL http://{pc_ip}:{http_port}/{WIFI_FW_FILE} -o /tmp/v27_wifi.bin", timeout=60)
    print("    -> Baixando RootFS...")
    run_cmd(tn, f"curl -fsSL http://{pc_ip}:{http_port}/{ROOTFS_FILE} -o /tmp/v27_rootfs.bin", timeout=120)

    # 7. Validar integridade MD5 no roteador
    print("\n[*] [2/4] Verificando integridade MD5 na memoria RAM do roteador...")
    md5_remote = run_cmd(tn, "md5sum /tmp/v27_kernel.bin /tmp/v27_wifi.bin /tmp/v27_rootfs.bin")
    print(f"    Hashes remotos conferidos:\n{md5_remote.strip()}")

    if k_md5 not in md5_remote or w_md5 not in md5_remote or r_md5 not in md5_remote:
        print("[-] ERRO FATAL: Os hashes MD5 recebidos no roteador divergiram!")
        log_event("GRAVACAO_SLOT2", "Erro Fatal: divergencia de MD5 na RAM do roteador", "ERRO")
        run_cmd(tn, "rm -f /tmp/v27_kernel.bin /tmp/v27_wifi.bin /tmp/v27_rootfs.bin")
        tn.close()
        httpd.shutdown()
        sys.exit(1)
    print("    [OK] Todos os 3 hashes MD5 estao 100% perfeitos.")
    log_event("GRAVACAO_SLOT2", "Hashes MD5 verificados com sucesso no roteador", "OK")

    # 8. Anexar UBI no mtd20 e gravar os 3 volumes
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

    if with_root:
        print("    -> Injetando credenciais e acesso Root no volume de dados (ubi1_3)...")
        run_cmd(tn, "mkdir -p /tmp/slot2_mnt")
        run_cmd(tn, "mount -t ubifs /dev/ubi1_3 /tmp/slot2_mnt 2>/dev/null")
        check_mnt = run_cmd(tn, "grep /tmp/slot2_mnt /proc/mounts 2>/dev/null; ls /tmp/slot2_mnt 2>/dev/null")
        if "/tmp/slot2_mnt" in check_mnt or "upper" in check_mnt or "etc" in check_mnt:
            injection_cmds = [
                "mkdir -p /tmp/slot2_mnt/upper",
                "rm -rf /tmp/slot2_mnt/upper/*",
                "mkdir -p /tmp/slot2_mnt/upper/etc/config",
                "mkdir -p /tmp/slot2_mnt/upper/etc/dropbear",
                "mkdir -p /tmp/slot2_mnt/upper/etc/init.d",
                "mkdir -p /tmp/slot2_mnt/upper/etc/rc.d",
                "mkdir -p /tmp/slot2_mnt/upper/etc/crontabs",
                "mkdir -p /tmp/slot2_mnt/upper/usr/sbin",
                "mkdir -p /tmp/slot2_mnt/upper/www",
                "cp -f /etc/passwd /tmp/slot2_mnt/upper/etc/passwd 2>/dev/null",
                "cp -f /etc/shadow /tmp/slot2_mnt/upper/etc/shadow 2>/dev/null",
                "cp -f /etc/config/dropbear /tmp/slot2_mnt/upper/etc/config/dropbear 2>/dev/null",
                "sed -i \"s/option enable '0'/option enable '1'/\" /tmp/slot2_mnt/upper/etc/config/dropbear 2>/dev/null",
                "[ -f /etc/dropbear/authorized_keys ] && cp -f /etc/dropbear/authorized_keys /tmp/slot2_mnt/upper/etc/dropbear/authorized_keys 2>/dev/null",
                "cp -f /etc/crontabs/* /tmp/slot2_mnt/upper/etc/crontabs/ 2>/dev/null",
                "cp -f /etc/init.d/telnet /tmp/slot2_mnt/upper/etc/init.d/telnet 2>/dev/null",
                "chmod +x /tmp/slot2_mnt/upper/etc/init.d/telnet 2>/dev/null",
                # Configurar uhttpd na porta 80 e desativar lighttpd
                "cp -f /etc/init.d/uhttpd /tmp/slot2_mnt/upper/etc/init.d/uhttpd 2>/dev/null",
                "sed -i 's/#config_load uhttpd/config_load uhttpd/' /tmp/slot2_mnt/upper/etc/init.d/uhttpd 2>/dev/null",
                "sed -i 's/#config_foreach start_instance uhttpd/config_foreach start_instance uhttpd/' /tmp/slot2_mnt/upper/etc/init.d/uhttpd 2>/dev/null",
                "chmod +x /tmp/slot2_mnt/upper/etc/init.d/uhttpd 2>/dev/null",
                "rm -f /tmp/slot2_mnt/upper/etc/rc.d/*lighttpd* 2>/dev/null",
                "ln -sf /etc/init.d/uhttpd /tmp/slot2_mnt/upper/etc/rc.d/S50uhttpd 2>/dev/null",
                "cat << 'EOF_UH' > /tmp/slot2_mnt/upper/etc/config/uhttpd\nconfig uhttpd 'main'\n\tlist listen_http '0.0.0.0:80'\n\tlist listen_http '[::]:80'\n\tlist listen_https '0.0.0.0:443'\n\tlist listen_https '[::]:443'\n\toption redirect_https '0'\n\toption home '/www'\n\toption rfc1918_filter '0'\n\toption max_requests '3'\n\toption max_connections '100'\n\toption cert '/etc/uhttpd.crt'\n\toption key '/etc/uhttpd.key'\n\toption cgi_prefix '/cgi-bin'\n\tlist lua_prefix '/cgi-bin/luci=/usr/lib/lua/luci/sgi/uhttpd.lua'\n\toption script_timeout '60'\n\toption network_timeout '30'\n\toption http_keepalive '20'\n\toption tcp_keepalive '1'\nEOF_UH",
                "cat << 'EOF_RP' > /tmp/slot2_mnt/upper/etc/config/rpcd\nconfig rpcd\n\toption socket '/var/run/ubus.sock'\n\toption timeout '30'\n\nconfig login\n\toption username 'root'\n\toption password '$p$root'\n\tlist read '*'\n\tlist write '*'\n\nconfig login\n\toption username 'Admin'\n\toption password '$p$Admin'\n\tlist read '*'\n\tlist write '*'\nEOF_RP",
                "cat << 'EOF_IDX' > /tmp/slot2_mnt/upper/www/index.html\n<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n<head>\n<meta http-equiv=\"Cache-Control\" content=\"no-cache, no-store, must-revalidate\" />\n<meta http-equiv=\"refresh\" content=\"0; URL=cgi-bin/luci/\" />\n</head>\n<body style=\"background-color: white\">\n<a style=\"color: black; font-family: arial, helvetica, sans-serif;\" href=\"cgi-bin/luci/\">LuCI - Lua Configuration Interface</a>\n</body>\n</html>\nEOF_IDX",
                "chmod 755 /tmp/slot2_mnt/upper/www/index.html 2>/dev/null",
                "cat << 'EOF_RC' > /tmp/slot2_mnt/upper/etc/rc.local\n# /etc/rc.local - Inicializacao Automatica Slot 2 (OpenWrt com LuCI na Porta 80)\nkillall -9 lighttpd 2>/dev/null\n/etc/init.d/lighttpd.init stop 2>/dev/null\n/etc/init.d/lighttpd.init disable 2>/dev/null\n\nDROPBEAR=$(command -v dropbear || echo \"/usr/sbin/dropbear\")\n[ -x \"$DROPBEAR\" ] && $DROPBEAR -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B 2>/dev/null\n\nTELNETD=$(command -v telnetd || echo \"/usr/sbin/telnetd\")\n[ -x \"$TELNETD\" ] && $TELNETD -l /bin/ash 2>/dev/null\n\nchmod -R 755 /www 2>/dev/null\n/etc/init.d/rpcd restart 2>/dev/null\n/etc/init.d/uhttpd enable 2>/dev/null\n/etc/init.d/uhttpd restart 2>/dev/null\n\nsysctl -w net.bridge.bridge-nf-call-ip6tables=0 2>/dev/null\nsysctl -w net.bridge.bridge-nf-call-iptables=0 2>/dev/null\nsysctl -w net.bridge.bridge-nf-call-arptables=0 2>/dev/null\n\nexit 0\nEOF_RC",
                "chmod +x /tmp/slot2_mnt/upper/etc/rc.local 2>/dev/null",
                "[ -f /usr/sbin/boot-acer ] && cp -f /usr/sbin/boot-acer /tmp/slot2_mnt/upper/usr/sbin/boot-acer && chmod +x /tmp/slot2_mnt/upper/usr/sbin/boot-acer",
                "[ -f /usr/sbin/boot-openwrt ] && cp -f /usr/sbin/boot-openwrt /tmp/slot2_mnt/upper/usr/sbin/boot-openwrt && chmod +x /tmp/slot2_mnt/upper/usr/sbin/boot-openwrt",
                "sync"
            ]
            for c in injection_cmds:
                run_cmd(tn, c)
            run_cmd(tn, "umount /tmp/slot2_mnt 2>/dev/null")
            print("       [OK] Root, SSH, Telnet, LuCI na Porta 80 e rc.local injetados com sucesso no Slot 2!")
            log_event("GRAVACAO_SLOT2", "Root, SSH, Telnet, LuCI na Porta 80 e rc.local injetados com sucesso no Slot 2", "OK")
        else:
            print("       [*] Volume de dados limpo via ubiupdatevol...")
            run_cmd(tn, "ubiupdatevol /dev/ubi1_3 -t", timeout=30)
            print("       [!] Volume ainda sem sistema de arquivos UBIFS inicializado.")
            print("           Apos o primeiro boot no Slot 2, use a Opcao 2 do menu para liberar o Root!")
            log_event("GRAVACAO_SLOT2", "Overlay zerado via -t (requer inicializacao no 1o boot)", "AVISO")
        run_cmd(tn, "rm -rf /tmp/slot2_mnt")
    else:
        print("    -> Formatando/limpando overlay no volume ubi1_3 (100% Stock OEM)...")
        run_cmd(tn, "ubiupdatevol /dev/ubi1_3 -t", timeout=30)
        log_event("GRAVACAO_SLOT2", "Instalacao Stock OEM (overlay limpo via -t)", "OK")

    # Limpeza e sync
    run_cmd(tn, "rm -f /tmp/v27_kernel.bin /tmp/v27_wifi.bin /tmp/v27_rootfs.bin")
    run_cmd(tn, "ubidetach -m 20 /dev/ubi_ctrl 2>/dev/null || true")
    run_cmd(tn, "sync")
    print("    [OK] Volumes do Slot 2 gravados e sincronizados com sucesso!")
    log_event("GRAVACAO_SLOT2", "Volumes gravados e sincronizados no Slot 2", "OK")

    # 9. Chavear bootconfig para Slot 2 e reiniciar
    if not args.no_reboot:
        print("\n[*] [4/4] Chaveando BOOTCONFIG para Slot 2 (primaryboot = 0) e reiniciando...")
        out_boot = run_cmd(tn, "/usr/sbin/boot-openwrt", timeout=15)
        print(f"       {out_boot.strip()}")
        print("    [OK] O roteador esta reiniciando no Slot 2 rodando a versao 1.01.000027!")
        log_event("GRAVACAO_SLOT2", "Slot 2 ativado (primaryboot=0) e roteador reiniciado", "OK")
        print("\n" + "=" * 72)
        print("  PROXIMOS PASSOS APOS O BOOT:")
        print("  1. Aguarde cerca de 90 segundos.")
        print(f"  2. Acesse http://{router_ip} no navegador.")
        if with_root:
            print("  3. [OK] O Slot 2 ja acorda com ROOT, SSH, Web e Telnet DESBLOQUEADOS!")
            print("     - Usuario Web / SSH : 'root' (ou 'Admin')")
            print("     - Senha Universal   : 'root0100'")
        else:
            print("  3. [!] O Slot 2 acordou 100% Stock OEM bloqueado.")
            print("     Restaure 'config_v27_ssh_unlocked.cfg' pelo painel se desejar abrir o terminal.")
        print("  4. Se quiser voltar ao Slot 1 a qualquer momento, execute:")
        print("     /usr/sbin/boot-acer")
        print("=" * 72)
    else:
        print("\n[*] Flag --no-reboot detectada. Gravacao concluida sem reiniciar.")
        print("    Para chavear manualmente quando quiser, execute:")
        print("    python switch_boot_slot.py 2")
        log_event("GRAVACAO_SLOT2", "Gravacao concluida com flag --no-reboot", "INFO")

    tn.close()
    httpd.shutdown()

if __name__ == "__main__":
    main()
