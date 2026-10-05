#!/usr/bin/env python3
"""
launcher_t7.py
Central Unificada de Gerenciamento, Pre-Flight Check e Deploy
Acer Predator Connect T7 (Qualcomm IPQ5332) & X7 (Pesquisa)
Suporte Bilingue: English (Default) / Portugues (Brasil)
Compativel com Windows, macOS e Linux (Python 3.8 ate 3.14+)
"""

import sys
import os
import platform
import socket
import time
import hashlib
import subprocess
import webbrowser
import argparse

try:
    from telnet_compat import Telnet
except ImportError:
    try:
        from Scripts_Automacao.telnet_compat import Telnet
    except ImportError:
        import telnetlib
        Telnet = telnetlib.Telnet

def find_repo_root():
    cur = os.path.dirname(os.path.abspath(__file__))
    while cur and cur != os.path.dirname(cur):
        if os.path.exists(os.path.join(cur, "01_FIRMWARES_E_IMAGENS")):
            return cur
        cur = os.path.dirname(cur)
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

REPO_DIR = find_repo_root()
V27_DIR = os.path.join(REPO_DIR, "01_FIRMWARES_E_IMAGENS", "Official_v27_Componentes")

TEXTS = {
    "en": {
        "title": "ACER PREDATOR CONNECT T7 & X7 MANAGEMENT SUITE",
        "preflight_header": "RUNNING PRE-FLIGHT CHECK (ENVIRONMENT VALIDATION)",
        "os": "Operating System",
        "python": "Python Version",
        "rom_files": "v27 ROM Files",
        "rom_ok": "[OK] 3/3 files verified",
        "rom_fail": "[-] FILE VALIDATION FAILED",
        "file_missing": "[-] Missing file",
        "file_corrupt": "[!] Corrupted file or size/MD5 mismatch",
        "tftp_port": "PC TFTP Port (UDP 69)",
        "tftp_free": "[OK] Available",
        "tftp_blocked": "[!] In use or blocked by firewall",
        "router_found": "Router Detected",
        "router_model": "Hardware Model",
        "router_version": "Firmware Version",
        "active_slot": "Active Slot",
        "slot1": "Slot 1 (OEM Factory)",
        "slot2": "Slot 2 (Pure OpenWrt)",
        "locked_notice": "NOTICE: Router Web GUI is up, but Telnet/SSH are closed (Factory Locked)!\n      Restore config_v27_ssh_unlocked.cfg via Web GUI to unlock.",
        "locked_status": "Locked (OEM Stock - Telnet Closed)",
        "unknown_locked": "Locked (Unlock via .cfg required)",
        "terminal_required": "ACTION REQUIRED: This option requires terminal access (Telnet / root).\nYour router Web GUI is responding, but Telnet (port 23) is closed (Locked).\n\nHow to unlock in 1 minute:\n1. Open your browser at http://{rip}\n2. Log in and navigate to: System -> Backup and restore\n3. Under 'Restore backup', upload the file:\n   02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_ssh_unlocked.cfg\n4. Wait 2 minutes for the router to reboot, then run this option again!",
        "status_router": "Router",
        "status_web_only": "Web Active (Terminal Locked)",
        "status_offline": "Unreachable / Disconnected",
        "menu_1": "[1] Run Full Pre-Flight Check (Environment Validation)",
        "menu_2": "[2] Flash Firmware v27 to Slot 2 (Clean OpenWrt) [T7 Exclusive]",
        "menu_3": "[3] Optimize & Activate LuCI on Port 80 (Slot 2)",
        "menu_4": "[4] Manage Dual-Boot (Switch Slot 1 / Slot 2)",
        "menu_5": "[5] Manage Telnet (Hardening / Disable or Enable)",
        "menu_6": "[6] Open Web GUI in Browser (http://{rip})",
        "menu_7": "[7] Acer Connect X7 Research & Diagnostic Area (Read-Only)",
        "menu_0": "[0] Exit",
        "prompt_choice": "Choose an option (0-7): ",
        "press_enter": "\nPress ENTER to return to menu...",
        "goodbye": "\nExiting management suite. Goodbye!"
    },
    "pt": {
        "title": "CENTRAL DE GERENCIAMENTO - ACER PREDATOR CONNECT T7 & X7",
        "preflight_header": "EXECUTANDO PRE-FLIGHT CHECK (VALIDACAO PREVIA DO AMBIENTE)",
        "os": "Sistema Operacional",
        "python": "Versao do Python",
        "rom_files": "Arquivos v27 (ROM)",
        "rom_ok": "[OK] 3/3 arquivos validados",
        "rom_fail": "[-] FALHA NOS ARQUIVOS",
        "file_missing": "[-] Arquivo ausente",
        "file_corrupt": "[!] Arquivo corrompido ou divergente",
        "tftp_port": "Porta TFTP PC (UDP 69)",
        "tftp_free": "[OK] Livre",
        "tftp_blocked": "[!] Em uso ou bloqueada",
        "router_found": "Roteador Detectado",
        "router_model": "Modelo do Hardware",
        "router_version": "Versao do Firmware",
        "active_slot": "Particao Ativa",
        "slot1": "Slot 1 (Acer Original)",
        "slot2": "Slot 2 (OpenWrt Puro)",
        "locked_notice": "AVISO: O roteador responde na Web, mas Telnet e SSH estao fechados (Bloqueado de fábrica)!\n      Restaure o arquivo config_v27_ssh_unlocked.cfg pela Web GUI para liberar.",
        "locked_status": "Bloqueado (OEM Fábrica - Telnet Fechado)",
        "unknown_locked": "Bloqueado (Necessita desbloqueio via .cfg)",
        "terminal_required": "AÇÃO NECESSÁRIA: Esta opção requer acesso ao terminal (Telnet / root).\nO painel Web do roteador responde, mas o Telnet (porta 23) está fechado (Bloqueado de fábrica).\n\nComo desbloquear em 1 minuto:\n1. Abra seu navegador em http://{rip}\n2. Faça login e acesse: System -> Backup and restore\n3. Na opção 'Restore backup', envie o arquivo:\n   02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_ssh_unlocked.cfg\n4. Aguarde 2 minutos o roteador reiniciar e execute esta opção novamente!",
        "status_router": "Roteador",
        "status_web_only": "Web Ativa (Terminal Bloqueado)",
        "status_offline": "Inacessivel / Desconectado",
        "menu_1": "[1] Executar Diagnóstico Completo (Pre-Flight Check)",
        "menu_2": "[2] Gravar Firmware v27 no Slot 2 (OpenWrt Puro) [Exclusivo T7]",
        "menu_3": "[3] Otimizar e Ativar LuCI na Porta 80 (Slot 2)",
        "menu_4": "[4] Gerenciar Dual-Boot (Alternar Slot 1 / Slot 2)",
        "menu_5": "[5] Gerenciar Telnet (Hardening / Desativar ou Reativar)",
        "menu_6": "[6] Abrir Painel no Navegador (http://{rip})",
        "menu_7": "[7] Area de Pesquisa e Diagnostico do Modelo X7 (Somente Leitura)",
        "menu_0": "[0] Sair",
        "prompt_choice": "Escolha uma opcao (0-7): ",
        "press_enter": "\nPressione ENTER para voltar ao menu...",
        "goodbye": "\nEncerrando central. Ate logo!"
    }
}

CURRENT_LANG = "en"

def t(key):
    return TEXTS.get(CURRENT_LANG, TEXTS["en"]).get(key, key)

def check_port(ip, port, timeout=1.2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False

def check_udp_bind(port=69):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", port))
        s.close()
        return True
    except Exception:
        return False

def detect_router_ip():
    candidates = ["192.168.76.1", "192.168.73.2", "192.168.1.1"]
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        my_ip = s.getsockname()[0]
        s.close()
        parts = my_ip.split(".")
        guess = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
        if guess not in candidates:
            candidates.insert(0, guess)
    except Exception:
        pass

    for cand in candidates:
        if check_port(cand, 23, 0.6):
            return cand

    for cand in candidates:
        if check_port(cand, 80, 0.6) or check_port(cand, 22, 0.6):
            return cand

    return "192.168.76.1"

def calc_md5(file_path):
    if not os.path.isfile(file_path):
        return None
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()

def preflight_check(quiet=False):
    if not quiet:
        print("\n" + "=" * 75)
        print(f"  {t('preflight_header')}")
        print("=" * 75)

    info = {
        "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "python": platform.python_version(),
        "files_ok": True,
        "router_ip": detect_router_ip(),
        "http_ok": False,
        "telnet_ok": False,
        "ssh_ok": False,
        "model": "N/A",
        "version": "N/A",
        "slot": "N/A",
        "tftp_port_ok": check_udp_bind(69)
    }

    expected = {
        "kernel.bin": {"size": 4237480, "md5": "ade31977f9c740a36ecfe50ac9e335d9"},
        "wifi_fw.bin": {"size": 8554496, "md5": "f1091a9c062ff50dd3348e06a8a5457e"},
        "rootfs.squashfs": {"size": 39616512, "md5": "99df532f68c147355c894611d1977cbf"}
    }
    for fname, exp in expected.items():
        fpath = os.path.join(V27_DIR, fname)
        if not os.path.isfile(fpath):
            info["files_ok"] = False
            if not quiet:
                print(f"  [-] {t('file_missing')}: {fname}")
        else:
            sz = os.path.getsize(fpath)
            f_md5 = calc_md5(fpath)
            if sz != exp["size"] or f_md5 != exp["md5"]:
                info["files_ok"] = False
                if not quiet:
                    print(f"  [!] {t('file_corrupt')}: {fname}")

    rip = info["router_ip"]
    info["http_ok"] = check_port(rip, 80, 1.0)
    info["telnet_ok"] = check_port(rip, 23, 1.0)
    info["ssh_ok"] = check_port(rip, 22, 1.0)

    if info["telnet_ok"]:
        try:
            tn = Telnet(rip, 23, timeout=3)
            tn.read_until("/ # ", timeout=2)

            def get_single_line(cmd):
                tn.write(cmd + "\n")
                time.sleep(0.15)
                res = tn.read_until("/ # ", timeout=2).decode(errors="replace")
                valid = [l.strip() for l in res.splitlines() if l.strip() and not l.startswith(cmd) and not l.startswith("/ #") and not l.startswith("cat ")]
                return valid[-1] if valid else ""

            info["model"] = get_single_line("cat /tmp/sysinfo/model 2>/dev/null")
            info["version"] = get_single_line("cat /etc/version 2>/dev/null")
            slot_raw = get_single_line("cat /proc/boot_info/bootconfig0/rootfs/primaryboot 2>/dev/null")
            info["slot"] = t("slot1") if slot_raw == "1" else t("slot2")
            tn.close()
        except Exception:
            pass
    elif info["http_ok"]:
        try:
            import urllib.request
            req = urllib.request.Request(f"http://{rip}/", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                if "luci" in content.lower():
                    info["model"] = "Acer Predator Connect (LuCI UI)"
                elif "predator" in content.lower() or "acer" in content.lower():
                    info["model"] = "Acer Predator Connect (Stock OEM Web)"
                else:
                    info["model"] = "Web Device (HTTP Port 80 Active)"
        except Exception:
            info["model"] = "Web Device (HTTP Port 80 Active)"
        info["version"] = t("locked_status")
        info["slot"] = t("unknown_locked")

    if not quiet:
        print(f"  [+] {t('os'):<24}: {info['os']}")
        print(f"  [+] {t('python'):<24}: {info['python']}")
        print(f"  [+] {t('rom_files'):<24}: {t('rom_ok') if info['files_ok'] else t('rom_fail')}")
        print(f"  [+] {t('tftp_port'):<24}: {t('tftp_free') if info['tftp_port_ok'] else t('tftp_blocked')}")
        print(f"  [+] {t('router_found'):<24}: {rip}")
        print(f"      - Web GUI (Port 80) : {'[YES/SIM]' if info['http_ok'] else '[NO/NAO]'}")
        print(f"      - Telnet  (Port 23) : {'[YES/SIM]' if info['telnet_ok'] else '[NO/NAO]'}")
        print(f"      - SSH     (Port 22) : {'[YES/SIM]' if info['ssh_ok'] else '[NO/NAO]'}")
        if info["telnet_ok"]:
            print(f"  [+] {t('router_model'):<24}: {info['model']}")
            print(f"  [+] {t('router_version'):<24}: {info['version']}")
            print(f"  [+] {t('active_slot'):<24}: {info['slot']}")
        elif info["http_ok"]:
            print(f"  [+] {t('router_model'):<24}: {info['model']}")
            print(f"  [+] {t('router_version'):<24}: {info['version']}")
            print(f"  [+] {t('active_slot'):<24}: {info['slot']}")
            print(f"\n  [!] {t('locked_notice')}")
        print("=" * 75)

    return info

def safe_input(prompt=""):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return None

def get_script_path(script_name):
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    if os.path.isfile(local):
        return local
    cand1 = os.path.join(REPO_DIR, "Scripts_Automacao", script_name)
    if os.path.isfile(cand1):
        return cand1
    cand2 = os.path.join(REPO_DIR, "04_SCRIPTS_E_FERRAMENTAS", "Automacao_e_Unlock", script_name)
    if os.path.isfile(cand2):
        return cand2
    cand3 = os.path.join(REPO_DIR, "scripts", script_name)
    if os.path.isfile(cand3):
        return cand3
    return local

def main_menu():
    global CURRENT_LANG
    parser = argparse.ArgumentParser(description="Acer Predator T7/X7 Management Suite")
    parser.add_argument("--lang", "-l", choices=["en", "pt"], default=None, help="Interface language (en or pt)")
    args = parser.parse_args()

    if args.lang:
        CURRENT_LANG = args.lang
    else:
        # Default is English
        CURRENT_LANG = "en"

    while True:
        info = preflight_check(quiet=True)
        rip = info["router_ip"]
        status_line = f"{t('status_router')}: {rip} | "
        if info["telnet_ok"]:
            status_line += f"{info['model']} | {info['slot']}"
        elif info["http_ok"]:
            status_line += t("status_web_only")
        else:
            status_line += t("status_offline")

        print("\n" + "=" * 75)
        print(f"     {t('title')}")
        print(f"     Status: {status_line}")
        print("=" * 75)
        print(f"  {t('menu_1')}")
        print(f"  {t('menu_2')}")
        print(f"  {t('menu_3')}")
        print(f"  {t('menu_4')}")
        print(f"  {t('menu_5')}")
        print(f"  {t('menu_6').format(rip=rip)}")
        print(f"  {t('menu_7')}")
        print(f"  {t('menu_0')}")
        print("=" * 75)

        choice = safe_input(t("prompt_choice"))
        if choice is None or choice == "0":
            print(t("goodbye"))
            break

        if choice in ["2", "3", "4", "5", "7"] and not info["telnet_ok"]:
            print("\n" + "=" * 75)
            print(t("terminal_required").format(rip=rip))
            print("=" * 75)
            safe_input(t("press_enter"))
            continue

        if choice == "1":
            preflight_check(quiet=False)
            safe_input(t("press_enter"))
        elif choice == "2":
            script = get_script_path("gravar_v27_slot2.py")
            subprocess.call([sys.executable, script])
            safe_input(t("press_enter"))
        elif choice == "3":
            script = get_script_path("otimizar_e_ativar_luci_slot2.py")
            subprocess.call([sys.executable, script])
            safe_input(t("press_enter"))
        elif choice == "4":
            script = get_script_path("switch_boot_slot.py")
            subprocess.call([sys.executable, script])
            safe_input(t("press_enter"))
        elif choice == "5":
            script = get_script_path("gerenciar_telnet.py")
            subprocess.call([sys.executable, script])
            safe_input(t("press_enter"))
        elif choice == "6":
            webbrowser.open(f"http://{rip}")
        elif choice == "7":
            script = get_script_path("diagnostico_x7.py")
            subprocess.call([sys.executable, script])
            safe_input(t("press_enter"))

if __name__ == "__main__":
    main_menu()
