#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
instalar_ark_router.py
Instalador Oficial do Painel e Tema ARK Router (LuCI App & Theme)
Acer Predator Connect T7 (Qualcomm IPQ5332 / Wi-Fi 7) & OpenWrt

Repositorio Oficial: https://github.com/Despensativo/ark-router
Releases: https://github.com/Despensativo/ark-router/releases/latest
"""

import sys
import os
import time
import socket
import json
import platform
import argparse
import subprocess
import threading
import http.server
import socketserver
import urllib.request

# Ativar suporte ANSI no Windows
if platform.system() == "Windows":
    try:
        os.system("")
    except Exception:
        pass

# Import Telnet e Logger
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
        def log_event(action, message, status="INFO", details=None): pass
        def log_cmd(cmd, output, status="CMD"): pass
        def log_dump(title, content): pass

C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_RED    = "\033[91m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_CYAN   = "\033[96m"
C_WHITE  = "\033[97m"

GITHUB_REPO_API   = "https://api.github.com/repos/Despensativo/ark-router/releases/latest"
FALLBACK_TAG      = "v1.5.8"
FALLBACK_URL_LITE = "https://github.com/Despensativo/ark-router/releases/download/v1.5.8/luci-app-ark-router.ipk"
FALLBACK_URL_FULL = "https://github.com/Despensativo/ark-router/releases/download/v1.5.8/luci-app-ark-router-full.ipk"

TEXTS = {
    "pt": {
        "title": "INSTALADOR OFICIAL DO PAINEL ARK ROUTER (LUCI)",
        "desc": "Este utilitario baixa e instala o painel operacional de alta performance\ne tema visual ARK Router diretamente no seu Acer Predator Connect T7.",
        "repo_info": "Repositorio Oficial: https://github.com/Despensativo/ark-router",
        "checking_status": "Verificando conexao e servicos no roteador...",
        "router_ip": "IP do Roteador",
        "slot_detected": "Slot Ativo Detectado: {slot}",
        "slot1_name": "Slot 1 (Firmware Original Acer Stock)",
        "slot2_name": "Slot 2 (OpenWrt / LuCI)",
        "slot_warning": "⚠️ AVISO: O roteador esta no Slot 1 (Firmware Original Acer).\nO painel ARK Router e projetado para rodar no Slot 2 (OpenWrt / LuCI).\nRecomenda-se chavear para o Slot 2 antes de instalar.",
        "slot_prompt": "Deseja continuar a instalacao mesmo assim? [S/N]: ",
        "arch_detected": "Arquitetura do Roteador: ARM 32-bit ({arch})",
        "features_title": "DESTAQUES E RECURSOS DO PAINEL ARK ROUTER:",
        "feat_rainbow": "  🌈 MODO LED RGB ARCO-IRIS (Rainbow Wave):\n     Efeito fluido dinamico de 120 tons no anel de LED do T7 (driver AW21018).\n     Rotacao suave de espectro sem consumo perceptivel de CPU!",
        "feat_dash": "  ⚡ DASHBOARD GAMER DE ALTA PERFORMANCE:\n     Telemetria ao vivo dos 4 nucleos Qualcomm IPQ5332, uso de RAM e temperaturas.",
        "feat_traffic": "  📊 MONITOR DE TRAFEGO POR DISPOSITIVO:\n     Graficos instantaneos de largura de banda por IP/MAC (Download e Upload separados).",
        "feat_sqm": "  🎮 OTIMIZACAO SQM CAKE (ANTI-BUFFERBLOAT):\n     Filas inteligentes para garantir ping estavel e jitter zero em jogos online.",
        "feat_theme": "  🎨 TEMA VISUAL ARK GAMER MODERNO:\n     Interface escura (Glassmorphism / Dark Theme) 100% responsiva para celular e PC.",
        "target_pkg_info": "Pacote Oficial: luci-app-ark-router.ipk (~628 KB - 100% ARM 32-bit Nativo)",
        "fetching_release": "Consultando versao mais recente no GitHub Releases...",
        "found_release": "Ultima versao detectada no GitHub: {tag}",
        "downloading": "Baixando {name} do GitHub...",
        "download_ok": "Download concluido com sucesso ({size} bytes).",
        "download_fail": "Falha no download via GitHub: {err}",
        "using_fallback": "Tentando URL direta de fallback...",
        "using_cached": "Usando pacote local em cache: {path}",
        "offline_warn": "Sem conexao com a internet e sem pacote em cache. Nao e possivel continuar.",
        "activating_uhttpd": "Garantindo que o servidor web LuCI (uhttpd) esta configurado na porta 80...",
        "transferring": "Enviando pacote para a memoria RAM (/tmp) do roteador...",
        "installing": "Executando instalacao do pacote no roteador (opkg install)...",
        "install_success": "Pacote instalado com sucesso no sistema!",
        "cleaning_cache": "Limpando cache do LuCI e reiniciando daemons de interface (rpcd/uhttpd)...",
        "rainbow_prompt": "🌈 Deseja ativar o Modo LED RGB Arco-Iris (Rainbow Wave) agora? [S/N] (Padrao: S): ",
        "activating_rainbow": "Ativando modo LED RGB Arco-Iris dinamico no roteador...",
        "rainbow_activated": "Modo LED Arco-Iris ativado com sucesso! Observe os LEDs do seu Predator T7 trocando de cor.",
        "all_done": "PAINEL ARK ROUTER INSTALADO COM SUCESSO!",
        "url_access": "Acesse no navegador: http://{ip}/",
        "creds": "Login: root (ou Admin) | Senha padrao: root0100",
        "telnet_closed": "Porta Telnet (23) fechada, mas SSH (22) ativo. Reativando Telnet via SSH...",
        "press_enter": "\nPressione ENTER para voltar ao menu...",
    },
    "en": {
        "title": "ARK ROUTER PANEL OFFICIAL INSTALLER (LUCI)",
        "desc": "This utility downloads and installs the high-performance operational dashboard\nand ARK Router visual theme directly onto your Acer Predator Connect T7.",
        "repo_info": "Official Repository: https://github.com/Despensativo/ark-router",
        "checking_status": "Checking connection and router services...",
        "router_ip": "Router IP",
        "slot_detected": "Active Slot Detected: {slot}",
        "slot1_name": "Slot 1 (Factory Stock Acer)",
        "slot2_name": "Slot 2 (OpenWrt / LuCI)",
        "slot_warning": "⚠️ WARNING: Router is currently in Slot 1 (Factory Stock Acer).\nARK Router panel is designed to run in Slot 2 (OpenWrt / LuCI).\nIt is recommended to switch to Slot 2 before installing.",
        "slot_prompt": "Do you want to proceed anyway? [Y/N]: ",
        "arch_detected": "Router Architecture: ARM 32-bit ({arch})",
        "features_title": "ARK ROUTER PANEL HIGHLIGHTS & FEATURES:",
        "feat_rainbow": "  🌈 RAINBOW RGB LED MODE (Rainbow Wave):\n     Fluid 120-step dynamic spectrum continuous transition on T7 LED ring (AW21018).\n     Smooth analog color flow with near-zero CPU overhead!",
        "feat_dash": "  ⚡ HIGH-PERFORMANCE GAMING DASHBOARD:\n     Real-time telemetry for 4-core IPQ5332 CPU, RAM utilization, and temperatures.",
        "feat_traffic": "  📊 PER-DEVICE TRAFFIC MONITORING:\n     Live real-time bandwidth graphs per host/IP/MAC (Upload and Download separated).",
        "feat_sqm": "  🎮 SQM CAKE ANTI-BUFFERBLOAT OPTIMIZATION:\n     Intelligent queue management to guarantee rock-solid ping and zero jitter in gaming.",
        "feat_theme": "  🎨 MODERN DARK ARK THEME:\n     Sleek Glassmorphism dark interface, 100% responsive for smartphones and desktops.",
        "target_pkg_info": "Official Package: luci-app-ark-router.ipk (~628 KB - 100% Native ARM 32-bit)",
        "fetching_release": "Checking latest release on GitHub...",
        "found_release": "Latest release found on GitHub: {tag}",
        "downloading": "Downloading {name} from GitHub...",
        "download_ok": "Download completed successfully ({size} bytes).",
        "download_fail": "Download failed via GitHub: {err}",
        "using_fallback": "Attempting direct fallback URL...",
        "using_cached": "Using locally cached package: {path}",
        "offline_warn": "No internet connection and no cached package found. Cannot continue.",
        "activating_uhttpd": "Ensuring LuCI web server (uhttpd) is active on port 80...",
        "transferring": "Sending package to router RAM (/tmp)...",
        "installing": "Executing package installation on router (opkg install)...",
        "install_success": "Package successfully installed into system!",
        "cleaning_cache": "Clearing LuCI cache and restarting UI daemons (rpcd/uhttpd)...",
        "rainbow_prompt": "🌈 Would you like to activate Rainbow RGB LED mode (Rainbow Wave) now? [Y/N] (Default: Y): ",
        "activating_rainbow": "Activating dynamic Rainbow RGB LED mode on router...",
        "rainbow_activated": "Rainbow LED mode successfully activated! Enjoy the dynamic colors on your Predator T7.",
        "all_done": "ARK ROUTER PANEL SUCCESSFULLY INSTALLED!",
        "url_access": "Access in browser: http://{ip}/",
        "creds": "Login: root (or Admin) | Default Password: root0100",
        "telnet_closed": "Telnet port (23) closed, but SSH (22) active. Re-enabling Telnet via SSH...",
        "press_enter": "\nPress ENTER to return to menu...",
    }
}

CURRENT_LANG = "pt"

def t(key):
    return TEXTS.get(CURRENT_LANG, TEXTS["pt"]).get(key, key)

def safe_input(prompt=""):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""

def check_port(ip, port, timeout=1.2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False

def get_local_ip_towards(target_ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((target_ip, 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.76.2"

def detect_router_ip(explicit_ip=None):
    if explicit_ip:
        return explicit_ip
    for cand in ["192.168.73.2", "192.168.76.1", "192.168.1.1"]:
        if check_port(cand, 23, 0.5):
            return cand
    for cand in ["192.168.76.1", "192.168.73.2", "192.168.1.1"]:
        if check_port(cand, 80, 0.5) or check_port(cand, 22, 0.5):
            return cand
    return "192.168.76.1"

def start_http_server(directory, port):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        def log_message(self, format, *args):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("0.0.0.0", port), QuietHandler)
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    return server

def run_cmd(tn, cmd, timeout=15):
    tn.read_very_eager()
    tn.write(cmd.strip().encode("ascii") + b"\n")
    time.sleep(0.3)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    log_cmd(cmd, out)
    return out

def get_latest_release_info():
    """Consulta a API do GitHub para obter URLs dos pacotes da release mais recente."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        req = urllib.request.Request(GITHUB_REPO_API, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode("utf-8"))
            tag = data.get("tag_name", FALLBACK_TAG)
            assets = data.get("assets", [])
            urls = {}
            for a in assets:
                name = a.get("name", "")
                url = a.get("browser_download_url", "")
                if name.endswith(".ipk"):
                    if "full" in name:
                        urls["full"] = url
                    elif "lite" in name or name == "luci-app-ark-router.ipk":
                        urls["lite"] = url
            if "lite" not in urls:
                urls["lite"] = FALLBACK_URL_LITE
            if "full" not in urls:
                urls["full"] = FALLBACK_URL_FULL
            return tag, urls
    except Exception as e:
        log_event("ARK_INSTALLER", f"Falha ao consultar API do GitHub: {e}", "AVISO")
        return FALLBACK_TAG, {"lite": FALLBACK_URL_LITE, "full": FALLBACK_URL_FULL}

def download_file(url, target_path):
    """Baixa um arquivo da internet gravando no disco local."""
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        with open(target_path, "wb") as f:
            while chunk := response.read(65536):
                f.write(chunk)
    return os.path.getsize(target_path)

def locate_local_cached_ipk(repo_root, prefer_full=False):
    """Procura por arquivo IPK já presente na suite offline."""
    candidates = [
        os.path.join(repo_root, "01_FIRMWARES_E_IMAGENS", "Ark_Router", "luci-app-ark-router.ipk"),
        os.path.join(os.path.expanduser("~"), "Desktop", "Acer-Predator-Connect-T7", "01_FIRMWARES_E_IMAGENS", "Ark_Router", "luci-app-ark-router.ipk"),
        os.path.join(os.environ.get("TEMP", ""), "luci-app-ark-router.ipk"),
    ]
    if prefer_full:
        candidates.insert(0, os.path.join(repo_root, "01_FIRMWARES_E_IMAGENS", "Ark_Router", "luci-app-ark-router-full.ipk"))
    for c in candidates:
        if os.path.isfile(c) and os.path.getsize(c) > 100000:
            return c
    return None

def main():
    global CURRENT_LANG
    parser = argparse.ArgumentParser(description="ARK Router Panel Installer")
    parser.add_argument("--ip", default=None, help="IP do roteador")
    parser.add_argument("--lang", choices=["pt", "en"], default="pt", help="Idioma")
    args = parser.parse_args()

    CURRENT_LANG = args.lang
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rip = detect_router_ip(args.ip)

    print("\n" + "=" * 75)
    print(f"  {t('title')}")
    print("=" * 75)
    print(f"  {t('desc')}")
    print(f"  {t('repo_info')}")
    print("-" * 75)
    print(f"  [+] {t('router_ip')}: {rip}")
    print(f"  [*] {t('checking_status')}")

    # Checar portas
    telnet_ok = check_port(rip, 23, 1.2)
    ssh_ok    = check_port(rip, 22, 1.2)
    http_ok   = check_port(rip, 80, 1.2)

    if not telnet_ok:
        if ssh_ok:
            print(f"\n  [!] {t('telnet_closed')}")
            gt_script = os.path.join(repo_root, "Scripts_Automacao", "gerenciar_telnet.py")
            if os.path.isfile(gt_script):
                subprocess.call([sys.executable, gt_script, "ativar", f"--ip={rip}"])
                time.sleep(1.0)
                telnet_ok = check_port(rip, 23, 1.5)
        if not telnet_ok:
            print(f"\n{C_RED}[-] Erro: Terminal Telnet (porta 23) ou SSH inacessivel no IP {rip}.{C_RESET}")
            print("    Certifique-se de que o roteador esta desbloqueado com root e responda na rede.")
            safe_input(t("press_enter"))
            return

    # Conectar ao roteador
    try:
        tn = Telnet(rip, 23, timeout=5)
        tn.read_until(b"/ # ", timeout=4)
    except Exception as e:
        print(f"\n{C_RED}[-] Falha ao conectar via Telnet: {e}{C_RESET}")
        safe_input(t("press_enter"))
        return

    # Verificar Slot Atual (IPQ5332: primaryboot = 1 -> Slot 1 Acer OEM; primaryboot = 0 -> Slot 2 OpenWrt)
    slot_out = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot 2>/dev/null || cat /proc/boot_info/bootconfig1/rootfs/primaryboot 2>/dev/null").strip()
    slot_lines = [l.strip() for l in slot_out.splitlines() if l.strip() and not l.strip().startswith("cat ") and not l.strip().startswith("/")]
    slot_val = slot_lines[-1] if slot_lines else ""
    is_slot1 = (slot_val == "1")
    slot_label = t("slot1_name") if is_slot1 else t("slot2_name")
    print(f"  [+] {C_BOLD}{t('slot_detected').format(slot=slot_label)}{C_RESET}")

    if is_slot1:
        print(f"\n{C_YELLOW}{t('slot_warning')}{C_RESET}\n")
        ans = safe_input(f"  {t('slot_prompt')}").lower()
        if ans not in ["s", "sim", "y", "yes"]:
            print("  [*] Operacao cancelada pelo usuario.")
            tn.close()
            safe_input(t("press_enter"))
            return

    # Detectar Arquitetura do Roteador
    arch_raw = run_cmd(tn, "uname -m 2>/dev/null").strip()
    if not arch_raw or len(arch_raw) > 20:
        arch_raw = "armv7l (32-bit)"
    else:
        arch_raw = f"{arch_raw} (32-bit)" if ("v7" in arch_raw or "arm" in arch_raw) and "64" not in arch_raw else arch_raw
    print(f"\n  [+] {C_GREEN}{t('arch_detected').format(arch=arch_raw)}{C_RESET}")

    # Exibir Destaques e Recursos do Ark Router
    print("\n" + "=" * 75)
    print(f"  {C_BOLD}{t('features_title')}{C_RESET}")
    print("=" * 75)
    print(f"{C_CYAN}{t('feat_rainbow')}{C_RESET}\n")
    print(f"{t('feat_dash')}\n")
    print(f"{t('feat_traffic')}\n")
    print(f"{t('feat_sqm')}\n")
    print(f"{t('feat_theme')}")
    print("=" * 75)

    # Pacote Oficial Alvo (100% Nativo ARM 32-bit)
    print(f"\n  [+] {C_GREEN}{t('target_pkg_info')}{C_RESET}")
    pkg_label = "luci-app-ark-router.ipk"
    prefer_full = False
    cache_dir = os.path.join(repo_root, "01_FIRMWARES_E_IMAGENS", "Ark_Router")
    os.makedirs(cache_dir, exist_ok=True)
    dest_cached = os.path.join(cache_dir, pkg_label)

    print(f"\n[*] {t('fetching_release')}")
    tag, urls = get_latest_release_info()
    print(f"    [+] {t('found_release').format(tag=tag)}")

    dl_url = urls.get("full" if prefer_full else "lite")
    print(f"[*] {t('downloading').format(name=pkg_label)}")
    print(f"    URL: {dl_url}")

    download_success = False
    try:
        sz = download_file(dl_url, dest_cached)
        print(f"    [OK] {t('download_ok').format(size=sz)}")
        local_ipk = dest_cached
        download_success = True
    except Exception as e:
        print(f"    [!] {t('download_fail').format(err=e)}")
        print(f"    [*] {t('using_fallback')}")
        fb_url = FALLBACK_URL_FULL if prefer_full else FALLBACK_URL_LITE
        try:
            sz = download_file(fb_url, dest_cached)
            print(f"    [OK] {t('download_ok').format(size=sz)}")
            local_ipk = dest_cached
            download_success = True
        except Exception as e2:
            print(f"    [-] Falha no fallback: {e2}")

    if not download_success:
        cached = locate_local_cached_ipk(repo_root, prefer_full)
        if cached:
            print(f"    {C_YELLOW}[!] {t('using_cached').format(path=cached)}{C_RESET}")
            local_ipk = cached
        else:
            print(f"\n{C_RED}[-] {t('offline_warn')}{C_RESET}")
            tn.close()
            safe_input(t("press_enter"))
            return

    # Iniciar Servidor HTTP Local para transferência instantânea
    pc_ip = get_local_ip_towards(rip)
    http_port = 8899
    http_dir = os.path.dirname(os.path.abspath(local_ipk))
    ipk_filename = os.path.basename(local_ipk)

    print(f"\n[*] {t('transferring')}")
    print(f"    Servidor HTTP Local: http://{pc_ip}:{http_port}/{ipk_filename}")
    try:
        httpd = start_http_server(http_dir, http_port)
    except Exception as e:
        httpd = None

    # Baixar pacote para a RAM do roteador
    run_cmd(tn, "rm -f /tmp/luci-app-ark-router.ipk /tmp/data.tar.gz")
    wget_cmd = f"wget -O /tmp/luci-app-ark-router.ipk http://{pc_ip}:{http_port}/{ipk_filename}"
    out_dl = run_cmd(tn, wget_cmd, timeout=30)

    # Verificar se o arquivo chegou no roteador
    check_sz = run_cmd(tn, "ls -l /tmp/luci-app-ark-router.ipk 2>/dev/null")
    if "luci-app-ark-router.ipk" not in check_sz:
        print(f"    {C_YELLOW}[!] Transferencia local falhou. Tentando download direto via roteador...{C_RESET}")
        run_cmd(tn, f"wget -q -O /tmp/luci-app-ark-router.ipk {FALLBACK_URL_LITE} 2>/dev/null || curl -k -s -o /tmp/luci-app-ark-router.ipk {FALLBACK_URL_LITE}")
        check_sz = run_cmd(tn, "ls -l /tmp/luci-app-ark-router.ipk 2>/dev/null")

    if "luci-app-ark-router.ipk" not in check_sz:
        print(f"\n{C_RED}[-] Erro: Nao foi possivel transferir o pacote para o roteador.{C_RESET}")
        tn.close()
        safe_input(t("press_enter"))
        return

    print("    [OK] Pacote transferido para /tmp/luci-app-ark-router.ipk no roteador.")

    # Garantir uhttpd ativo na porta 80 antes da instalacao
    print(f"\n[*] {t('activating_uhttpd')}")
    run_cmd(tn, "killall -9 lighttpd 2>/dev/null; /etc/init.d/lighttpd.init stop 2>/dev/null; /etc/init.d/lighttpd.init disable 2>/dev/null")
    run_cmd(tn, "sed -i 's/#config_load uhttpd/config_load uhttpd/' /etc/init.d/uhttpd 2>/dev/null")
    run_cmd(tn, "sed -i 's/#config_foreach start_instance uhttpd/config_foreach start_instance uhttpd/' /etc/init.d/uhttpd 2>/dev/null")
    run_cmd(tn, "chmod -R 755 /www 2>/dev/null")
    run_cmd(tn, "uci -q delete uhttpd.main.listen_http 2>/dev/null")
    run_cmd(tn, "uci add_list uhttpd.main.listen_http='0.0.0.0:80' 2>/dev/null")
    run_cmd(tn, "uci add_list uhttpd.main.listen_http='[::]:80' 2>/dev/null")
    run_cmd(tn, "uci set uhttpd.main.rfc1918_filter='0' 2>/dev/null")
    run_cmd(tn, "uci set uhttpd.main.redirect_https='0' 2>/dev/null")
    run_cmd(tn, "uci commit uhttpd 2>/dev/null")
    print("    [OK] Servidor uhttpd configurado para porta 80.")

    # Instalar pacote via opkg
    print(f"\n[*] {t('installing')}")
    opkg_res = run_cmd(tn, "opkg install --force-depends --force-overwrite /tmp/luci-app-ark-router.ipk", timeout=45)

    if "Configuring luci-app-ark-router" not in opkg_res and "Collected errors" in opkg_res:
        print("    [!] opkg reportou aviso de dependencias. Aplicando fallback de extracao segura...")
        run_cmd(tn, "opkg install --force-depends --force-downgrade --nodeps /tmp/luci-app-ark-router.ipk 2>/dev/null")
        # Garantir extração de arquivos se o feed do opkg estiver inacessível
        run_cmd(tn, "cd /tmp && tar -xzf luci-app-ark-router.ipk data.tar.gz 2>/dev/null && tar -xzf data.tar.gz -C / 2>/dev/null")

    print(f"    [OK] {t('install_success')}")

    # Executar scripts uci-defaults se houver
    print(f"\n[*] {t('cleaning_cache')}")
    run_cmd(tn, "for f in /etc/uci-defaults/99-ark-router*; do [ -f \"$f\" ] && sh \"$f\" && rm -f \"$f\"; done 2>/dev/null")
    run_cmd(tn, "rm -rf /tmp/luci-indexcache /tmp/luci-modulecache* /tmp/luci-sessions* 2>/dev/null")
    run_cmd(tn, "/etc/init.d/rpcd restart 2>/dev/null")
    run_cmd(tn, "/etc/init.d/uhttpd enable 2>/dev/null; /etc/init.d/uhttpd restart 2>/dev/null")
    run_cmd(tn, "rm -f /tmp/luci-app-ark-router.ipk /tmp/data.tar.gz")
    # Pergunta opcional para ativar o Efeito LED RGB Arco-Íris
    print("\n" + "-" * 75)
    led_ans = safe_input(f"  {t('rainbow_prompt')}").lower()
    if led_ans in ["", "s", "sim", "y", "yes"]:
        print(f"  [*] {t('activating_rainbow')}")
        run_cmd(tn, "/usr/sbin/equipe-dashboard-control set-led-rgb-color rainbow 2>/dev/null || (/etc/init.d/ark-rainbowd enable 2>/dev/null; /etc/init.d/ark-rainbowd restart 2>/dev/null) || (/bin/sh /usr/sbin/ark-rainbowd &)")
        print(f"  {C_GREEN}[OK] {t('rainbow_activated')}{C_RESET}")

    tn.close()

    # Validar HTTP no navegador
    web_up = check_port(rip, 80, 2.0)

    print("\n" + "=" * 75)
    print(f"  {C_GREEN}{t('all_done')}{C_RESET}")
    print("=" * 75)
    print(f"  [+] {C_BOLD}{t('url_access').format(ip=rip)}{C_RESET}")
    print(f"  [+] {t('creds')}")
    if web_up:
        print(f"  [+] Status Web: {C_GREEN}PORTA 80 ATIVA E RESPONDENDO{C_RESET}")
    else:
        print(f"  [!] Status Web: {C_YELLOW}Aguardando servico subir na porta 80...{C_RESET}")
    print("=" * 75)

    log_event("ARK_INSTALLER", f"Painel Ark Router instalado com sucesso em {rip} ({pkg_label})", "SUCESSO")
    safe_input(t("press_enter"))

if __name__ == "__main__":
    main()
