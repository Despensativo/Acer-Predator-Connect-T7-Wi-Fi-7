#!/usr/bin/env python3
"""
Utilitario de Chaveamento Dual-Boot: Alterna entre Slot 1 (Acer) e Slot 2 (OpenWrt)
Acer Predator Connect T7 (Qualcomm IPQ5332)
"""

import sys
import os
import time
import socket

# Garante prioridade para modulos locais (telnet_compat, logger_t7)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    # 1. Tentar gateway local
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

    # 2. Sondagem nos IPs conhecidos (76.1 = padrao Acer, 73.2 = AP, 1.1 = OpenWrt)
    for candidate in ["192.168.76.1", "192.168.73.2", "192.168.1.1"]:
        if test_telnet(candidate, 1):
            print(f"    [+] Roteador respondendo em Telnet (porta 23): {candidate}")
            return candidate

    print("    [!] Nao foi possivel detectar automaticamente. Usando padrao: 192.168.76.1")
    return "192.168.76.1"

def run_cmd(tn, cmd, timeout=10):
    tn.write(cmd.encode("ascii") + b"\n")
    time.sleep(0.5)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    log_cmd(cmd, out)
    return out

def get_current_slot(tn):
    out = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    lines = [l.strip() for l in out.strip().split("\n") if l.strip() and not l.startswith("cat ") and not l.startswith("/ #")]
    val = lines[-1] if lines else "1"
    return "Slot 1 (Acer Original)" if val == "1" else "Slot 2 (OpenWrt Puro)"

def install_helper_scripts(tn):
    # Script para ir para o OpenWrt
    script_openwrt = """cat << 'EOF' > /usr/sbin/boot-openwrt
#!/bin/sh
echo "=== Chaveando boot para SLOT 2 (OpenWrt Puro) ==="
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
echo "[OK] Ponteiro gravado com sucesso! Reiniciando no OpenWrt..."
reboot
EOF
chmod +x /usr/sbin/boot-openwrt
"""
    # Script para voltar para a Acer
    script_acer = """cat << 'EOF' > /usr/sbin/boot-acer
#!/bin/sh
echo "=== Chaveando boot de volta para SLOT 1 (Acer Original) ==="
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
echo "[OK] Ponteiro gravado com sucesso! Reiniciando na Acer..."
reboot
EOF
chmod +x /usr/sbin/boot-acer
"""
    run_cmd(tn, script_openwrt)
    run_cmd(tn, script_acer)

def main():
    target_slot = None
    explicit_ip = None

    for arg in sys.argv[1:]:
        if arg in ["1", "2", "acer", "openwrt"]:
            target_slot = arg
        elif "." in arg or arg.startswith("--ip="):
            explicit_ip = arg.replace("--ip=", "").strip()

    router_ip = detect_router_ip(explicit_ip)

    print("=" * 65)
    print("GERENCIADOR DE DUAL-BOOT - ACER PREDATOR CONNECT T7")
    print(f"Alvo: {router_ip}:23")
    print("=" * 65)

    try:
        tn = Telnet(router_ip, 23, timeout=5)
        tn.read_until(b"/ # ", timeout=5)
    except Exception as e:
        print(f"[-] Erro ao conectar via Telnet em {router_ip}:23: {e}")
        sys.exit(1)

    out_cmd = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
    raw_val = [l.strip() for l in out_cmd.splitlines() if l.strip() and not l.startswith("cat") and not l.startswith("/ #")][-1] if out_cmd else "?"
    is_slot1 = (raw_val == "1")
    cur_num = "1" if is_slot1 else "2"
    target_num = "2" if is_slot1 else "1"
    cur_label = "SLOT 1 (Firmware OEM Acer Original)" if is_slot1 else "SLOT 2 (OpenWrt Puro / LuCI)"
    target_label = "SLOT 2 (OpenWrt Puro / LuCI)" if is_slot1 else "SLOT 1 (Firmware OEM Acer Original)"

    print(f"[*] Slot ativo atualmente no U-Boot: {cur_label} (primaryboot = {raw_val})")

    install_helper_scripts(tn)
    print("[*] Comandos rapidos instalados no terminal do roteador:")
    print("    - 'boot-openwrt' -> Inicia no OpenWrt puro (Slot 2)")
    print("    - 'boot-acer'    -> Inicia no sistema Acer original (Slot 1)")

    if target_slot in ["openwrt", "2"]:
        print("\n[*] Aplicando chaveamento para SLOT 2 (OpenWrt Puro)...")
        log_event("SWITCH_BOOT", "Chaveamento via argumento para Slot 2", "INFO")
        out = run_cmd(tn, "/usr/sbin/boot-openwrt")
        print(out)
        log_event("SWITCH_BOOT", "Slot 2 ativado e reboot enviado", "OK")
    elif target_slot in ["acer", "1"]:
        print("\n[*] Aplicando chaveamento para SLOT 1 (Acer Original)...")
        log_event("SWITCH_BOOT", "Chaveamento via argumento para Slot 1", "INFO")
        out = run_cmd(tn, "/usr/sbin/boot-acer")
        print(out)
        log_event("SWITCH_BOOT", "Slot 1 ativado e reboot enviado", "OK")
    else:
        while True:
            print("\n" + "=" * 65)
            print(f"  SLOT ATUAL : {cur_label}")
            print(f"  DESTINO    : {target_label}")
            print("=" * 65)
            print(f"  [1] Alternar para o {target_label} e reiniciar")
            print(f"  [2] Forcar reinicializacao no mesmo {cur_label}")
            print("  [0] Voltar ao menu principal sem alterar nada")
            opt = input(f"\nDigite o numero da opcao desejada [1, 2 ou 0]: ").strip()

            if not opt:
                print("\n[!] Nenhuma opcao digitada! Digite obrigatoriamente 1, 2 ou 0.")
                continue

            if opt == "1":
                while True:
                    conf = input(f"\n[?] Tem certeza que deseja alternar para o {target_label} e reiniciar o roteador agora? [S/N]: ").strip().lower()
                    if conf in ["s", "sim", "y", "yes"]:
                        break
                    elif conf in ["n", "nao", "não", "no"]:
                        print("[*] Operacao cancelada pelo usuario.")
                        log_event("SWITCH_BOOT", "Cancelado na confirmacao pelo usuario", "AVISO")
                        return
                    print("\n[!] Entrada invalida! Digite obrigatoriamente 'S' para Sim ou 'N' para Nao.")

                print(f"\n[*] Aplicando chaveamento para {target_label}...")
                log_event("SWITCH_BOOT", f"Alternando do Slot {cur_num} para o Slot {target_num}", "INFO")
                try:
                    if target_num == "2":
                        out = run_cmd(tn, "/usr/sbin/boot-openwrt", timeout=3)
                    else:
                        out = run_cmd(tn, "/usr/sbin/boot-acer", timeout=3)
                    if out:
                        print(out.strip())
                except Exception:
                    pass

                print("\n" + "=" * 65)
                print(f"  [OK] CHAVEAMENTO GRAVADO COM SUCESSO!")
                print(f"  O roteador esta REINICIANDO agora no {target_label}.")
                print("  Aguarde cerca de 60 a 90 segundos para a inicializacao completa.")
                print("=" * 65)
                log_event("SWITCH_BOOT", f"Chaveamento para Slot {target_num} concluido e roteador reiniciando", "OK")
                break
            elif opt == "2":
                while True:
                    conf = input(f"\n[?] Confirma forcar o reinicio no mesmo {cur_label}? [S/N]: ").strip().lower()
                    if conf in ["s", "sim", "y", "yes"]:
                        break
                    elif conf in ["n", "nao", "não", "no"]:
                        print("[*] Operacao cancelada pelo usuario.")
                        return
                    print("\n[!] Entrada invalida! Digite obrigatoriamente 'S' para Sim ou 'N' para Nao.")

                print(f"\n[*] Reiniciando no mesmo Slot {cur_num}...")
                log_event("SWITCH_BOOT", f"Reinicio forcado no mesmo Slot {cur_num}", "INFO")
                out = run_cmd(tn, "reboot")
                print(out)
                break
            elif opt == "0":
                print("\n[*] Nenhuma alteracao efetuada. Retornando ao menu...")
                log_event("SWITCH_BOOT", "Cancelado pelo usuario sem alteracao", "INFO")
                break
            else:
                print(f"\n[!] Opcao '{opt}' invalida. Digite 1, 2 ou 0.")

    tn.close()

if __name__ == "__main__":
    main()

