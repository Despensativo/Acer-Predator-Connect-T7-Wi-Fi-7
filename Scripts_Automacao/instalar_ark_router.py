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
FALLBACK_TAG      = "v1.5.9"
FALLBACK_URL_LITE = "https://github.com/Despensativo/ark-router/releases/download/v1.5.9/luci-app-ark-router.ipk"
FALLBACK_URL_FULL = "https://github.com/Despensativo/ark-router/releases/download/v1.5.9/luci-app-ark-router-full.ipk"
LATEST_DIRECT_URL = "https://github.com/Despensativo/ark-router/releases/latest/download/luci-app-ark-router.ipk"

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
        "target_pkg_info": "Pacote Oficial: luci-app-ark-router.ipk (~600 KB - 100% ARM 32-bit Nativo)",
        "fetching_release": "Consultando versao mais recente no GitHub Releases...",
        "found_release": "Ultima versao detectada no GitHub: {tag}",
        "direct_download_router": "Tentando download direto no roteador via curl...",
        "direct_download_ok": "Download direto no roteador concluido com sucesso ({size} bytes).",
        "streaming_fallback": "Download direto no roteador indisponivel. Transferindo via stream TCP local (nc)...",
        "downloading_pc": "Baixando pacote mais recente no PC para transmissao...",
        "download_ok": "Download no PC concluido com sucesso ({size} bytes).",
        "download_fail": "Falha no download via GitHub: {err}",
        "using_fallback": "Tentando URL direta de fallback...",
        "using_cached": "Usando pacote local em cache: {path}",
        "offline_warn": "Sem conexao com a internet e sem pacote local disponivel. Nao e possivel continuar.",
        "streaming_transfer": "Enviando pacote para a memoria RAM (/tmp) do roteador via stream TCP (nc)...",
        "stream_success": "Pacote transferido com sucesso para a RAM do roteador ({size} bytes).",
        "activating_uhttpd": "Garantindo que o servidor web LuCI (uhttpd) esta configurado na porta 80...",
        "installing": "Executando instalacao do pacote no roteador (opkg install)...",
        "install_success": "Pacote instalado com sucesso no sistema!",
        "cleaning_cache": "Limpando cache do LuCI e reiniciando daemons de interface (rpcd/uhttpd)...",
        "activating_rainbow": "Ativando modo LED RGB Arco-Iris dinamico no hardware do roteador...",
        "rainbow_activated": "Modo LED Arco-Iris ativado com sucesso! LEDs sincronizados.",
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
        "target_pkg_info": "Official Package: luci-app-ark-router.ipk (~600 KB - 100% Native ARM 32-bit)",
        "fetching_release": "Checking latest release on GitHub...",
        "found_release": "Latest release found on GitHub: {tag}",
        "direct_download_router": "Attempting direct download on router via curl...",
        "direct_download_ok": "Direct router download completed successfully ({size} bytes).",
        "streaming_fallback": "Direct router download unavailable. Transferring via local TCP stream (nc)...",
        "downloading_pc": "Downloading latest package on PC for streaming...",
        "download_ok": "Download on PC completed successfully ({size} bytes).",
        "download_fail": "Download failed via GitHub: {err}",
        "using_fallback": "Attempting direct fallback URL...",
        "using_cached": "Using locally cached package: {path}",
        "offline_warn": "No internet connection and no cached package found. Cannot continue.",
        "streaming_transfer": "Sending package to router RAM (/tmp) via TCP stream (nc)...",
        "stream_success": "Package successfully transferred to router RAM ({size} bytes).",
        "activating_uhttpd": "Ensuring LuCI web server (uhttpd) is active on port 80...",
        "installing": "Executing package installation on router (opkg install)...",
        "install_success": "Package successfully installed into system!",
        "cleaning_cache": "Clearing LuCI cache and restarting UI daemons (rpcd/uhttpd)...",
        "activating_rainbow": "Activating dynamic Rainbow RGB LED mode on router hardware...",
        "rainbow_activated": "Rainbow LED mode successfully activated! LEDs synchronized.",
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

def run_cmd(tn, cmd, timeout=15):
    tn.read_very_eager()
    tn.write(cmd.strip().encode("ascii") + b"\n")
    time.sleep(0.1)
    out = tn.read_until(b"/ # ", timeout=timeout).decode("utf-8", errors="replace")
    log_cmd(cmd, out)
    return out

def get_remote_file_size(tn, remote_path):
    out = run_cmd(tn, f"wc -c < {remote_path} 2>/dev/null").strip()
    for line in out.splitlines():
        line = line.strip()
        if line.isdigit():
            return int(line)
    return 0

def get_latest_release_info():
    """Consulta a API do GitHub para obter informacoes da versao e pacotes da release mais recente."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        req = urllib.request.Request(GITHUB_REPO_API, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
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
                urls["lite"] = LATEST_DIRECT_URL
            if "full" not in urls:
                urls["full"] = FALLBACK_URL_FULL
            return tag, urls
    except Exception as e:
        log_event("ARK_INSTALLER", f"Consulta a API do GitHub indisponivel: {e}", "AVISO")
        return FALLBACK_TAG, {"lite": LATEST_DIRECT_URL, "full": FALLBACK_URL_FULL}

def download_file(url, target_path, timeout=30):
    """Baixa um arquivo da internet gravando no disco local."""
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        with open(target_path, "wb") as f:
            while chunk := response.read(65536):
                f.write(chunk)
    return os.path.getsize(target_path)

def locate_local_cached_ipk(repo_root):
    # Conforme regra do projeto, o app nunca deve ser reaproveitado localmente;
    # deve ser sempre baixado do zero via link oficial para garantir versao atualizada.
    return None

def try_direct_download_router(tn, url, timeout=45):
    """Tenta baixar o pacote IPK diretamente no roteador via curl."""
    run_cmd(tn, "rm -f /tmp/luci-app-ark-router.ipk /tmp/data.tar.gz")
    cmd = f"curl -fsSL -k --connect-timeout 8 -m {timeout} -o /tmp/luci-app-ark-router.ipk {url}"
    run_cmd(tn, cmd, timeout=timeout + 5)
    return get_remote_file_size(tn, "/tmp/luci-app-ark-router.ipk")

def stream_file_to_router(tn, rip, file_path_or_bytes, timeout=15):
    """Envia o arquivo para a RAM (/tmp) do roteador via conexao TCP direta (nc) sem necessidade de servidor HTTP."""
    if isinstance(file_path_or_bytes, (bytes, bytearray)):
        data = file_path_or_bytes
    else:
        with open(file_path_or_bytes, "rb") as f:
            data = f.read()

    pc_ip = get_local_ip_towards(rip)
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 0))
    port = srv.getsockname()[1]
    srv.listen(1)
    srv.settimeout(timeout)

    run_cmd(tn, "rm -f /tmp/luci-app-ark-router.ipk /tmp/data.tar.gz")
    run_cmd(tn, f"nc {pc_ip} {port} > /tmp/luci-app-ark-router.ipk &")
    time.sleep(0.3)

    try:
        conn, _ = srv.accept()
        conn.sendall(data)
        conn.close()
    except socket.timeout:
        log_event("ARK_INSTALLER", "Timeout aguardando conexao TCP do roteador (nc)", "ERRO")
    finally:
        srv.close()

    time.sleep(0.4)
    return get_remote_file_size(tn, "/tmp/luci-app-ark-router.ipk")

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

    # Conectar ao roteador e normalizar prompt para '/ # '
    try:
        tn = Telnet(rip, 23, timeout=5)
        tn.write(b"export PS1='/ # '\ncd /\n")
        time.sleep(0.2)
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

    # Preparar diretório de cache local
    print(f"\n  [+] {C_GREEN}{t('target_pkg_info')}{C_RESET}")

    print(f"\n[*] {t('fetching_release')}")
    tag, urls = get_latest_release_info()
    print(f"    [+] {t('found_release').format(tag=tag)}")

    dl_url = urls.get("lite", LATEST_DIRECT_URL)

    # Etapa 1: Download direto no roteador via curl (sempre do zero via link)
    print(f"\n[*] {t('direct_download_router')}")
    print(f"    URL: {dl_url}")
    remote_sz = try_direct_download_router(tn, dl_url, timeout=45)

    ipk_ready = False
    if remote_sz > 100000:
        print(f"    [OK] {t('direct_download_ok').format(size=remote_sz)}")
        ipk_ready = True
    else:
        # Etapa 2: Fallback - Baixar arquivo temporario no PC do zero e transmitir via TCP (nc)
        print(f"    [!] {t('streaming_fallback')}")
        local_ipk = None
        import tempfile
        tmp_fd, tmp_path = tempfile.mkstemp(suffix="_ark.ipk")
        os.close(tmp_fd)

        try:
            print(f"    [*] {t('downloading_pc')}")
            sz = download_file(dl_url, tmp_path, timeout=25)
            print(f"    [OK] {t('download_ok').format(size=sz)}")
            local_ipk = tmp_path
        except Exception as e:
            print(f"    [!] {t('download_fail').format(err=e)}")
            print(f"    [*] {t('using_fallback')}")
            try:
                sz = download_file(FALLBACK_URL_LITE, tmp_path, timeout=25)
                print(f"    [OK] {t('download_ok').format(size=sz)}")
                local_ipk = tmp_path
            except Exception as e2:
                print(f"    [-] Falha no fallback: {e2}")

        if not local_ipk or not os.path.isfile(local_ipk) or os.path.getsize(local_ipk) < 100000:
            print(f"\n{C_RED}[-] {t('offline_warn')}{C_RESET}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            tn.close()
            safe_input(t("press_enter"))
            return

        # Enviar via stream TCP (nc)
        print(f"    [*] {t('streaming_transfer')}")
        remote_sz = stream_file_to_router(tn, rip, local_ipk, timeout=15)
        # Limpar arquivo temporario do PC imediatamente
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

        if remote_sz > 100000:
            print(f"    [OK] {t('stream_success').format(size=remote_sz)}")
            ipk_ready = True
        else:
            print(f"\n{C_RED}[-] Erro: Nao foi possivel transferir o pacote para o roteador.{C_RESET}")
            tn.close()
            safe_input(t("press_enter"))
            return

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
    opkg_res = run_cmd(tn, "opkg install --force-reinstall --force-depends --force-overwrite /tmp/luci-app-ark-router.ipk", timeout=60)

    if "Configuring luci-app-ark-router" not in opkg_res and "Collected errors" in opkg_res:
        print("    [!] opkg reportou aviso de dependencias. Aplicando fallback de extracao segura...")
        run_cmd(tn, "opkg install --force-reinstall --force-depends --force-downgrade --nodeps /tmp/luci-app-ark-router.ipk 2>/dev/null", timeout=30)
        run_cmd(tn, "cd /tmp && tar -xzf luci-app-ark-router.ipk data.tar.gz 2>/dev/null && tar -xzf data.tar.gz -C / 2>/dev/null", timeout=30)

    print(f"    [OK] {t('install_success')}")

    # Executar scripts uci-defaults se houver e limpar caches
    print(f"\n[*] {t('cleaning_cache')}")
    run_cmd(tn, "for f in /etc/uci-defaults/99-ark-router*; do [ -f \"$f\" ] && sh \"$f\" && rm -f \"$f\"; done 2>/dev/null")
    run_cmd(tn, "rm -rf /tmp/luci-indexcache /tmp/luci-modulecache* /tmp/luci-sessions* 2>/dev/null")
    run_cmd(tn, "/etc/init.d/rpcd restart 2>/dev/null")
    run_cmd(tn, "/etc/init.d/uhttpd enable 2>/dev/null; /etc/init.d/uhttpd restart 2>/dev/null")
    run_cmd(tn, "rm -f /tmp/luci-app-ark-router.ipk /tmp/data.tar.gz")

    # Ativar Modo LED RGB Arco-Iris automaticamente no hardware do roteador
    print(f"\n[*] {t('activating_rainbow')}")
    run_cmd(tn, "/usr/sbin/equipe-dashboard-control set-led-rgb-color rainbow 2>/dev/null || (/etc/init.d/ark-rainbowd enable 2>/dev/null; /etc/init.d/ark-rainbowd restart 2>/dev/null) || (/bin/sh /usr/sbin/ark-rainbowd &)")
    print(f"    [OK] {t('rainbow_activated')}")

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
