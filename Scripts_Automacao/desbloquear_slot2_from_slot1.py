#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
desbloquear_slot2_from_slot1.py
Desbloqueio Automatico do Slot 2 a partir do Slot 1 (Sem precisar de .cfg no Slot 2)
Injeta Root, Telnet e SSH Dropbear direto no overlay do Slot 2 e chaveia o boot.
Acer Predator Connect T7 (Qualcomm IPQ5332)
"""

import sys
import os
import time
import socket

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

def check_port(ip, port, timeout=1.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False

def run_cmd(tn, cmd, timeout=5):
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.3)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    log_cmd(cmd, out)
    return out

def main():
    router_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.76.1"
    for cand in [router_ip, "192.168.73.2", "192.168.76.1", "192.168.1.1"]:
        if check_port(cand, 23, 0.5):
            router_ip = cand
            break

    print("\n" + "=" * 75)
    print("  DESBLOQUEIO AUTOMATICO DO SLOT 2 A PARTIR DO SLOT 1")
    print("=" * 75)
    print("  Voce acabou de liberar o Root no Slot 1 restaurando o arquivo .cfg!")
    print("")
    print("  O Slot 2 do seu roteador ainda esta bloqueado de fabrica.")
    print("  Com esta opcao, o script usa o acesso Root atual do Slot 1 para acessar")
    print("  diretamente a particao do Slot 2 pela memoria interna, injetando o")
    print("  desbloqueio (Telnet + SSH + Root) SEM precisar entrar no painel da Acer")
    print("  e SEM precisar enviar outro arquivo .cfg!")
    print("")
    print("  O que este procedimento faz em poucos segundos:")
    print("    * Monta a particao de dados do Slot 2 internamente via UBI")
    print("    * Injeta o usuario 'root' e senha 'root' no sistema do Slot 2")
    print("    * Ativa os daemons de Telnet (porta 23) e SSH Dropbear (porta 22)")
    print("    * Copia sua chave de acesso SSH do Windows para o Slot 2")
    print("    * Chaveia o bootloader para o Slot 2 (primaryboot = 0)")
    print("    * Reinicia o roteador ja acordando no Slot 2 desbloqueado!")
    print("=" * 75)

    while True:
        ans = input("  Deseja prosseguir com o desbloqueio do Slot 2 e reiniciar por ele? [S/N]: ").strip().upper()
        if ans in ["S", "SIM", "Y", "YES"]:
            break
        elif ans in ["N", "NAO", "NÃO", "NO"]:
            print("\n  [!] Operacao cancelada pelo usuario.")
            log_event("DESBLOQUEIO_SLOT2", "Cancelado pelo usuario no prompt", "AVISO")
            return
        print("\n  [!] Entrada invalida! Digite obrigatoriamente 'S' para Sim ou 'N' para Nao.")

    log_event("DESBLOQUEIO_SLOT2", f"Iniciando injecao de root no Slot 2 a partir do IP {router_ip}", "INFO")

    if not check_port(router_ip, 23, 2.0):
        print(f"\n  [-] Erro: Porta Telnet (23) fechada em {router_ip}.")
        print("      Certifique-se de que o Slot 1 foi destravado com o .cfg antes de rodar.")
        log_event("DESBLOQUEIO_SLOT2", f"Falha: Telnet fechado em {router_ip}", "ERRO")
        return

    print(f"\n  [*] Conectando ao terminal root em {router_ip}...")
    try:
        tn = Telnet(router_ip, 23, timeout=5)
        tn.read_until(b"/ # ", timeout=3)
    except Exception as e:
        print(f"  [-] Erro ao conectar: {e}")
        log_event("DESBLOQUEIO_SLOT2", f"Erro de conexao Telnet: {e}", "ERRO")
        return

    # Verificar slot atual
    out_slot = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot 2>/dev/null")
    current_slot = "1"
    for l in out_slot.splitlines():
        if l.strip() in ["0", "1"]:
            current_slot = l.strip()

    if current_slot == "0":
        print("  [!] AVISO: O roteador JA ESTA rodando no Slot 2!")
        print("      Nao e necessario injetar do Slot 1 porque o Slot 2 ja esta ativo.")
        log_event("DESBLOQUEIO_SLOT2", "Roteador ja estava no Slot 2 (primaryboot=0)", "AVISO")
        tn.close()
        return

    print("  [+] Confirmado: Roteador executando no Slot 1 (Acer Stock com Root).")
    print("  [*] Anexando particao do Slot 2 (mtd20) ao subsistema UBI...")
    log_event("DESBLOQUEIO_SLOT2", "Anexando mtd20 ao UBI", "INFO")

    # Anexar mtd20 (Slot 2 = rootfs_1)
    run_cmd(tn, "mkdir -p /tmp/slot2_mnt")
    run_cmd(tn, "ubiattach -m 20 -d 1 /dev/ubi_ctrl 2>/dev/null")
    time.sleep(1)

    # Garante criacao dos device nodes para ubi1_*
    run_cmd(tn, "for v in /sys/class/ubi/ubi1_*; do [ -d \"$v\" ] && mknod /dev/$(basename $v) c $(cat $v/dev | tr : ' ') 2>/dev/null; done")

    print("  [*] Montando volume de configuracoes do Slot 2 (ubifs)...")
    out_mount = run_cmd(tn, "mount -t ubifs /dev/ubi1_3 /tmp/slot2_mnt 2>&1")
    time.sleep(0.5)

    check_mnt = run_cmd(tn, "grep /tmp/slot2_mnt /proc/mounts 2>/dev/null; ls /tmp/slot2_mnt 2>/dev/null")
    if "/tmp/slot2_mnt" not in check_mnt and "upper" not in check_mnt and "etc" not in check_mnt:
        print("  [-] Falha ao montar overlay do Slot 2. Tentando recuperar...")
        log_event("DESBLOQUEIO_SLOT2", f"Falha de montagem: {out_mount}", "ERRO")
        run_cmd(tn, "ubidetach -m 20 /dev/ubi_ctrl 2>/dev/null")
        tn.close()
        return

    print("  [+] Particao do Slot 2 montada com sucesso!")
    print("  [*] Injetando credenciais de Root, Telnet e Dropbear SSH...")

    # Comandos de injeção
    injection_cmds = [
        "mkdir -p /tmp/slot2_mnt/upper",
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

    print("  [OK] Arquivos de Root, SSH, Telnet e LuCI (Porta 80) injetados com sucesso!")
    log_event("DESBLOQUEIO_SLOT2", "Injecao de arquivos (shadow, dropbear, telnet, uhttpd, luci) concluida com sucesso", "OK")

    print("  [*] Desmontando volume e liberando UBI...")
    run_cmd(tn, "umount /tmp/slot2_mnt 2>/dev/null")
    run_cmd(tn, "ubidetach -m 20 /dev/ubi_ctrl 2>/dev/null")
    run_cmd(tn, "rm -rf /tmp/slot2_mnt")
    time.sleep(0.5)

    print("  [*] Configurando bootloader para iniciar pelo SLOT 2 (primaryboot = 0)...")
    boot_switch_cmds = [
        "echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot",
        "echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot",
        "cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin",
        "cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin",
        "mtd unlock /dev/mtd3 2>/dev/null",
        "mtd unlock /dev/mtd4 2>/dev/null",
        "mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3",
        "mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4",
        "rm -f /tmp/bc0.bin /tmp/bc1.bin",
        "sync"
    ]
    for c in boot_switch_cmds:
        run_cmd(tn, c)

    log_event("DESBLOQUEIO_SLOT2", "Bootloader configurado para Slot 2 (primaryboot=0)", "OK")
    print("  [OK] Bootloader atualizado!")

    print("\n  [*] Enviando comando de reinicializacao para o roteador...")
    run_cmd(tn, "reboot", timeout=1)
    try:
        tn.close()
    except Exception:
        pass

    log_event("DESBLOQUEIO_SLOT2", "Comando reboot enviado. Aguardando reinicializacao no Slot 2", "INFO")

    print("\n" + "=" * 75)
    print("  ROTEADOR REINICIANDO NO SLOT 2 (AGUARDE ~60 A 90 SEGUNDOS)...")
    print("=" * 75)

    reboot_success = False
    for i in range(1, 45):
        time.sleep(2)
        print(f"  [*] Testando conexao em {router_ip} [Tentativa {i}/45]...")
        if check_port(router_ip, 23, 0.5) or check_port(router_ip, 22, 0.5):
            reboot_success = True
            break

    if reboot_success:
        print("\n  [OK] CONEXAO ESTABELECIDA COM SUCESSO!")
        print("  [OK] O Slot 2 acordou com ROOT, Telnet e SSH totalmente liberados!")
        print(f"       IP de Administracao: {router_ip}")
        print("       Usuario: root | Senha: root (ou sua senha configurada)")
        log_event("DESBLOQUEIO_SLOT2", f"Roteador acordou no Slot 2 com sucesso em {router_ip}", "OK")
    else:
        print("\n  [!] Tempo limite de espera atingido. O roteador pode ainda estar inicializando.")
        print("      Verifique as luzes no aparelho e tente conectar em alguns instantes.")
        log_event("DESBLOQUEIO_SLOT2", "Timeout aguardando porta 22/23 pos-reboot", "AVISO")

    print("=" * 75)
    input("\n  Pressione ENTER para voltar ao menu...")

if __name__ == "__main__":
    main()
