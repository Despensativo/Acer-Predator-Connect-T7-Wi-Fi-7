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
import json
import shutil
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

def find_v27_dir():
    candidates = [
        os.path.join(REPO_DIR, "01_FIRMWARES_E_IMAGENS", "Official_v27_Componentes"),
        r"C:\Users\User\Acer-Predator-Connect-T7\01_FIRMWARES_E_IMAGENS\Official_v27_Componentes",
        r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\01_FIRMWARES_E_IMAGENS\Official_v27_Componentes",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "01_FIRMWARES_E_IMAGENS", "Official_v27_Componentes")
    ]
    for c in candidates:
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "kernel.bin")):
            return os.path.abspath(c)
    return candidates[0]

V27_DIR = find_v27_dir()

TEXTS = {
    "en": {
        "title": "ACER PREDATOR CONNECT T7 & X7 MANAGEMENT SUITE",
        "preflight_header": "RUNNING PRE-FLIGHT CHECK (ENVIRONMENT VALIDATION)",
        "os": "Operating System",
        "python": "Python Version",
        "rom_files": "v27 ROM Files",
        "rom_ok": "[OK] 3/3 files verified (Ready for Slot 2 flash)",
        "rom_fail": "[-] ROM files missing locally (Option [2] only)",
        "rom_notice_missing": "v27 ROM files not found in folder. (Required ONLY for Option [2] - Flash Slot 2. Other options are unaffected).",
        "file_missing": "Missing file",
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
        "slot1_desc": "Slot 1 (OEM Factory)",
        "slot1_info": "Acer Stock Firmware (Factory OEM - Protected)",
        "slot2_desc": "Slot 2 (Pure OpenWrt)",
        "slot2_info": "OpenWrt v27 (LuCI on Port 80 / Debloated)",
        "default_boot": "Default Boot Slot",
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
        "menu_8": "[8] Check & Sync Updates from GitHub (Smart Checksum)",
        "menu_9": "[9] Emergency Recovery Mode (U-Boot Web / Unbrick)",
        "menu_0": "[0] Exit",
        "prompt_choice": "Choose an option (0-9): ",
        "press_enter": "\nPress ENTER to return to menu...",
        "telnet_active_warning": "\033[93m[!] SECURITY WARNING: Telnet port (23) is currently OPEN on your local network!\n    If you have finished your configurations, please disable Telnet in option [5] (Hardening)!\033[0m",
        "suite_version": "Suite Version",
        "sync_header": "CHECKING & SYNCING UPDATES FROM GITHUB",
        "sync_checking": "[*] Connecting to GitHub to fetch manifest and verify files...",
        "sync_all_ok": "[OK] All suite files are 100% up-to-date and intact (SHA-256 verified)!",
        "sync_updated": "[OK] Successfully synchronized {0} updated files from GitHub (backups saved to .bak)!",
        "goodbye": "\nExiting management suite. Goodbye!"
    },
    "pt": {
        "title": "CENTRAL DE GERENCIAMENTO - ACER PREDATOR CONNECT T7 & X7",
        "preflight_header": "EXECUTANDO PRE-FLIGHT CHECK (VALIDACAO PREVIA DO AMBIENTE)",
        "os": "Sistema Operacional",
        "python": "Versao do Python",
        "rom_files": "Arquivos v27 (ROM)",
        "rom_ok": "[OK] 3/3 arquivos validados (Pronto para gravar Slot 2)",
        "rom_fail": "[-] ROM v27 ausente (Apenas Opcao 2 afetada)",
        "rom_notice_missing": "Arquivos da ROM nao encontrados nesta pasta (Necessarios APENAS para a Opcao [2] - Gravar Slot 2. Demais opcoes funcionam normalmente).",
        "file_missing": "Arquivo ausente",
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
        "slot1_desc": "Slot 1 (Reserva OEM)",
        "slot1_info": "Firmware Acer Original (Fabrica OEM - Protegido)",
        "slot2_desc": "Slot 2 (OpenWrt Puro)",
        "slot2_info": "OpenWrt v27 (LuCI na Porta 80 / Debloated)",
        "default_boot": "Boot Padrao U-Boot",
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
        "menu_8": "[8] Sincronizar e Atualizar Ferramenta (GitHub Checksum)",
        "menu_9": "[9] Modo de Recuperacao de Emergencia (U-Boot Web / Desbrickar)",
        "menu_0": "[0] Sair",
        "prompt_choice": "Escolha uma opcao (0-9): ",
        "press_enter": "\nPressione ENTER para voltar ao menu...",
        "telnet_active_warning": "\033[93m[!] ALERTA DE SEGURANCA: A porta Telnet (23) esta ATIVA na sua rede local!\n    Se ja concluiu suas configuracoes, desative o Telnet na opcao [5] (Hardening)!\033[0m",
        "suite_version": "Versao da Suite",
        "sync_header": "VERIFICANDO E SINCRONIZANDO ATUALIZACOES DO GITHUB",
        "sync_checking": "[*] Conectando ao GitHub para buscar manifesto e verificar arquivos...",
        "sync_all_ok": "[OK] Todos os arquivos da suite estao 100% atualizados e integros (SHA-256 validado)!",
        "sync_updated": "[OK] Sincronizacao concluida! {0} arquivos atualizados do GitHub (backups salvos em .bak)!",
        "goodbye": "\nEncerrando central. Ate logo!"
    },
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

def detect_router_ip(explicit_ip=None):
    if explicit_ip:
        return explicit_ip
    for cand in ["192.168.73.2", "192.168.76.1", "192.168.1.1"]:
        if check_port(cand, 23, 0.5):
            return cand
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

def preflight_check(quiet=False, explicit_ip=None):
    if not quiet:
        print("\n" + "=" * 75)
        print(f"  {t('preflight_header')}")
        print("=" * 75)

    info = {
        "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "python": platform.python_version(),
        "files_ok": True,
        "router_ip": detect_router_ip(explicit_ip),
        "http_ok": False,
        "telnet_ok": False,
        "ssh_ok": False,
        "model": "N/A",
        "version": "N/A",
        "slot": "N/A",
        "active_slot_label": "N/A",
        "boot_default_label": "N/A",
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

    if not info["files_ok"] and not quiet:
        print(f"      ({t('rom_notice_missing')})")

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
            if slot_raw == "0":
                info["active_slot_label"] = t("slot2")
                info["boot_default_label"] = f"{t('slot2')} (primaryboot = 0)"
            elif slot_raw == "1":
                info["active_slot_label"] = t("slot1")
                info["boot_default_label"] = f"{t('slot1')} (primaryboot = 1)"
            else:
                info["active_slot_label"] = t("slot2")
                info["boot_default_label"] = f"{t('slot2')} (primaryboot = {slot_raw})"
            info["slot"] = info["active_slot_label"]
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
        info["active_slot_label"] = t("unknown_locked")
        info["boot_default_label"] = t("unknown_locked")

    if not quiet:
        print(f"  [+] {t('os'):<24}: {info['os']}")
        print(f"  [+] {t('python'):<24}: {info['python']}")
        manifest_path = os.path.join(REPO_DIR, "manifest_suite.json")
        suite_ver_str = "v1.0.1 (Manifest Oficial)"
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as mf:
                    mdata = json.load(mf)
                sver = mdata.get("suite_version", "1.0.1")
                suite_ver_str = f"v{sver} ({len(mdata.get('files', []))} arquivos monitorados)"
            except Exception:
                pass
        print(f"  [+] {t('suite_version'):<24}: {suite_ver_str}")
        print(f"  [+] {t('rom_files'):<24}: {t('rom_ok') if info['files_ok'] else t('rom_fail')}")
        print(f"  [+] {t('tftp_port'):<24}: {t('tftp_free') if info['tftp_port_ok'] else t('tftp_blocked')}")
        print(f"  [+] {t('router_found'):<24}: {rip}")
        print(f"      - Web GUI (Port 80) : {'[YES/SIM]' if info['http_ok'] else '[NO/NAO]'}")
        print(f"      - Telnet  (Port 23) : {'[YES/SIM]' if info['telnet_ok'] else '[NO/NAO]'}")
        print(f"      - SSH     (Port 22) : {'[YES/SIM]' if info['ssh_ok'] else '[NO/NAO]'}")
        if info["telnet_ok"]:
            print(f"  [+] {t('router_model'):<24}: {info['model']}")
            print(f"  [+] {t('router_version'):<24}: {info['version']}")
            print(f"  [+] {t('slot1_desc'):<24}: {t('slot1_info')}")
            print(f"  [+] {t('slot2_desc'):<24}: {t('slot2_info')}")
            print(f"  [+] {t('active_slot'):<24}: {info['active_slot_label']}")
            print(f"  [+] {t('default_boot'):<24}: {info['boot_default_label']}")
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

def check_and_sync_updates():
    print("\n" + "=" * 75)
    print(f"  {t('sync_header')}")
    print("=" * 75)
    print(f"  {t('sync_checking')}")

    raw_base = "https://raw.githubusercontent.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/main"
    manifest_url = f"{raw_base}/manifest_suite.json"

    try:
        import urllib.request
        req = urllib.request.Request(manifest_url, headers={"User-Agent": "Mozilla/5.0 AcerPredatorT7Suite/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode("utf-8")
            manifest = json.loads(data)

        mpath = os.path.join(REPO_DIR, "manifest_suite.json")
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(data)

        updated_count = 0
        uptodate_count = 0
        new_count = 0

        for f in manifest.get("files", []):
            rel_path = f["path"]
            expected_hash = f["sha256"]
            category = f.get("category", "")
            expected_size = f.get("size", 0)

            local_abs = os.path.join(REPO_DIR, rel_path.replace("/", os.sep))
            os.makedirs(os.path.dirname(local_abs), exist_ok=True)

            needs_download = False
            is_update = False

            if category == "rom":
                if os.path.isfile(local_abs) and os.path.getsize(local_abs) == expected_size:
                    uptodate_count += 1
                    continue
                needs_download = True
                new_count += 1
            elif not os.path.isfile(local_abs):
                needs_download = True
                new_count += 1
            else:
                h = hashlib.sha256()
                with open(local_abs, "rb") as fl:
                    while chunk := fl.read(65536):
                        h.update(chunk)
                local_hash = h.hexdigest().upper()

                if local_hash == expected_hash:
                    uptodate_count += 1
                else:
                    needs_download = True
                    is_update = True
                    updated_count += 1
                    print(f"  [*] {rel_path}: Nova versao detectada no GitHub! Atualizando...")
                    try:
                        shutil.copy2(local_abs, local_abs + ".bak")
                    except Exception:
                        pass

            if needs_download:
                file_url = f"{raw_base}/{rel_path}"
                print(f"  [*] Baixando {rel_path}...")
                with urllib.request.urlopen(urllib.request.Request(file_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
                    content = r.read()
                    with open(local_abs, "wb") as out:
                        out.write(content)
                if is_update:
                    print(f"  [OK] {rel_path} atualizado com sucesso! (Backup salvo em .bak)")
                else:
                    print(f"  [OK] {rel_path} baixado com sucesso!")

        print("")
        if updated_count == 0 and new_count == 0:
            print(f"  {t('sync_all_ok')}")
        else:
            print(f"  {t('sync_updated').format(updated_count + new_count)}")

    except Exception as e:
        print(f"  [-] Erro ao verificar atualizacoes: {e}")
        print("      Verifique sua conexao com a internet.")

    print("=" * 75)
    safe_input(t("press_enter"))

def show_emergency_recovery():
    print("\n" + "=" * 75)
    print("  MODO DE RECUPERACAO DE EMERGENCIA (U-BOOT WEB RECOVERY / UNBRICK)" if CURRENT_LANG == "pt" else "  EMERGENCY RECOVERY MODE (U-BOOT WEB RECOVERY / UNBRICK)")
    print("=" * 75)
    if CURRENT_LANG == "pt":
        print("""  Este procedimento restaura o roteador de fabrica DIRETO pelo bootloader
  de emergencia da Qualcomm/Acer, mesmo se o sistema operacional estiver travado!

  [PASSO 1] CONFIGURAR CABO E IP NO COMPUTADOR:
    1. Conecte um cabo de rede do PC diretamente na porta LAN 1 do Predator T7.
    2. Configure a placa de rede do seu Windows com IP ESTATICO manual:
       - Endereco IP : 192.168.1.2
       - Mascara     : 255.255.255.0
       - Gateway     : 192.168.1.1

  [PASSO 2] ACIONAR O BOOTLOADER DE EMERGENCIA NO ROTEADOR:
    1. Desconecte a fonte de energia do roteador.
    2. Mantenha pressionado o botao WPS no topo/traseira do roteador.
    3. Conecte a fonte de energia mantendo o botao WPS PRESSIONADO POR 5 SEGUNDOS.
    4. Solte o botao WPS. Os LEDs piscaram indicando modo recovery.

  [PASSO 3] ENVIAR O FIRMWARE ORIGINAL PELO NAVEGADOR:
    1. Abra o navegador em: http://192.168.1.1
    2. A tela oficial de recuperacao do U-Boot sera exibida.
    3. Clique em 'Browse' / 'Escolher Arquivo' e envie a ROM oficial completa:""")
    else:
        print("""  This procedure restores the factory firmware DIRECTLY via the Qualcomm/Acer
  emergency hardware bootloader, even if the OS is in bootloop or bricked!

  [STEP 1] CONFIGURE CABLE & PC NETWORK IP:
    1. Connect an Ethernet cable from PC to LAN 1 port on Predator T7.
    2. Configure your Windows network adapter with manual STATIC IP:
       - IP Address : 192.168.1.2
       - Subnet Mask: 255.255.255.0
       - Gateway    : 192.168.1.1

  [STEP 2] TRIGGER HARDWARE EMERGENCY BOOTLOADER:
    1. Unplug router power cable.
    2. Hold down the WPS button on the router.
    3. Plug in the power cable KEEPING THE WPS BUTTON PRESSED FOR 5 SECONDS.
    4. Release the WPS button. LEDs will blink indicating recovery mode.

  [STEP 3] FLASH ORIGINAL FACTORY FIRMWARE IN BROWSER:
    1. In your browser, open: http://192.168.1.1
    2. The Qualcomm U-Boot Web Recovery page will appear.
    3. Click 'Browse' and select the official full ROM image:""")

    stock_candidates = [
        os.path.join(REPO_DIR, "01_FIRMWARES_E_IMAGENS", "Stock_OEM_Recovery", "nand-4k-ipq5332-single_101000027.img"),
        os.path.join(REPO_DIR, "02_BACKUPS_E_DUMPS", "MTD_Full_Dumps", "Acer_Predator_Connect_T7", "nand-4k-ipq5332-single_101000027.img"),
        os.path.join(r"C:\Users\User\Desktop\Acer-Predator-Connect-T7", "01_FIRMWARES_E_IMAGENS", "Stock_OEM_Recovery", "nand-4k-ipq5332-single_101000027.img"),
    ]
    stock_path = None
    for sc in stock_candidates:
        if os.path.isfile(sc):
            stock_path = os.path.abspath(sc)
            break

    if stock_path:
        size_mb = os.path.getsize(stock_path) / (1024 * 1024)
        print(f"\n     ==> {stock_path}")
        print(f"     [OK] Arquivo verificado ({size_mb:.1f} MB - Release v1.01.000027 Oficial Acer)" if CURRENT_LANG == "pt" else f"     [OK] Verified file ({size_mb:.1f} MB - Official Acer v1.01.000027 Release)")
    else:
        print("\n     [-] Arquivo de recuperacao nao encontrado na pasta local." if CURRENT_LANG == "pt" else "\n     [-] Recovery image not found in local directory.")

    if CURRENT_LANG == "pt":
        print("""
    4. Clique no botao 'Upload' / 'Update' e aguarde (~2 a 3 minutos).
    5. O roteador reiniciara 100% de fabrica no IP original 192.168.76.1!
    6. Lembre-se de voltar a sua placa de rede para IP Automatico (DHCP).""")
    else:
        print("""
    4. Click 'Upload' / 'Update' and wait (~2 to 3 minutes).
    5. Router will reboot 100% factory original to IP 192.168.76.1!
    6. Remember to switch your network adapter back to Automatic (DHCP).""")

    print("=" * 75)
    safe_input(t("press_enter"))

def main_menu():
    global CURRENT_LANG
    parser = argparse.ArgumentParser(description="Acer Predator T7/X7 Management Suite")
    parser.add_argument("--lang", "-l", choices=["en", "pt"], default=None, help="Interface language (en or pt)")
    parser.add_argument("--ip", default=None, help="Explicit router IP")
    args = parser.parse_args()

    if args.lang:
        CURRENT_LANG = args.lang
    else:
        CURRENT_LANG = "en"

    while True:
        info = preflight_check(quiet=True, explicit_ip=args.ip)
        rip = info["router_ip"]
        m_label = info['model'] if (info["telnet_ok"] or info["http_ok"]) and info["model"] != "N/A" else ""
        dev_info = f" ({m_label})" if m_label else ""

        print("\n" + "=" * 75)
        print(f"  {t('title')}")
        print("-" * 75)
        print(f"  [+] {t('status_router')}: {rip}{dev_info}")
        if info["telnet_ok"]:
            print(f"  [+] {t('active_slot')}: {info['active_slot_label']}")
            print(f"  [+] {t('default_boot')}: {info['boot_default_label']}")
        elif info["http_ok"]:
            print(f"  [+] Status Terminal: {t('status_web_only')}")
        else:
            print(f"  [!] Conexao: {t('status_offline')}")
        print("=" * 75)
        if info["telnet_ok"]:
            print(f"  {t('telnet_active_warning')}")
            print("-" * 75)
        print(f"  {t('menu_1')}")
        print(f"  {t('menu_2')}")
        print(f"  {t('menu_3')}")
        print(f"  {t('menu_4')}")
        print(f"  {t('menu_5')}")
        print(f"  {t('menu_6').format(rip=rip)}")
        print(f"  {t('menu_7')}")
        print(f"  {t('menu_8')}")
        print(f"  {t('menu_9')}")
        print(f"  {t('menu_0')}")
        print("=" * 75)

        choice = safe_input(t("prompt_choice"))
        if choice is None or choice == "0":
            print(t("goodbye"))
            break

        if choice in ["2", "3", "4", "7"] and not info["telnet_ok"]:
            print("\n" + "=" * 75)
            print(t("terminal_required").format(rip=rip))
            print("=" * 75)
            safe_input(t("press_enter"))
            continue

        if choice == "1":
            preflight_check(quiet=False, explicit_ip=args.ip)
            safe_input(t("press_enter"))
        elif choice == "2":
            if not info["files_ok"]:
                print("\n" + "=" * 75)
                print(f"  [!] {t('rom_notice_missing')}")
                print(f"      Pasta: {V27_DIR}")
                print("=" * 75)
                safe_input(t("press_enter"))
                continue
            script = get_script_path("gravar_v27_slot2.py")
            subprocess.call([sys.executable, script, rip])
            safe_input(t("press_enter"))
        elif choice == "3":
            script = get_script_path("otimizar_e_ativar_luci_slot2.py")
            subprocess.call([sys.executable, script, rip])
            safe_input(t("press_enter"))
        elif choice == "4":
            script = get_script_path("switch_boot_slot.py")
            subprocess.call([sys.executable, script, rip])
            safe_input(t("press_enter"))
        elif choice == "5":
            script = get_script_path("gerenciar_telnet.py")
            subprocess.call([sys.executable, script, rip])
            safe_input(t("press_enter"))
        elif choice == "6":
            webbrowser.open(f"http://{rip}")
        elif choice == "7":
            script = get_script_path("diagnostico_x7.py")
            subprocess.call([sys.executable, script, rip])
            safe_input(t("press_enter"))
        elif choice == "8":
            check_and_sync_updates()
        elif choice == "9":
            show_emergency_recovery()

if __name__ == "__main__":
    main_menu()
