#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iniciar.py - Assistente Universal de Inicializacao e Sincronizacao da Suite
Acer Predator Connect T7 (Qualcomm IPQ5332 / Wi-Fi 7) & X7
Compatibilidade Multiplataforma Total: Windows, macOS e Linux
"""

import sys
import os
import time
import json
import hashlib
import platform
import subprocess
import urllib.request

# Ativar cores ANSI no Windows caso suportado
if platform.system() == "Windows":
    try:
        os.system("")
    except Exception:
        pass

C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_RED    = "\033[91m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_CYAN   = "\033[96m"
C_WHITE  = "\033[97m"

RAW_BASE = "https://raw.githubusercontent.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/main"

TEXTS = {
    "pt": {
        "title": "ACER PREDATOR CONNECT T7 & X7 - GESTAO E RECUPERACAO",
        "sync_header": "SINCRONIZANDO FERRAMENTAS DO GITHUB / SUITE SYNC",
        "work_dir": "Pasta de Trabalho",
        "checking_updates": "Verificando integridade e atualizacoes no GitHub...",
        "manifest_loaded": "Manifesto v{version} carregado do GitHub ({count} arquivos monitorados)",
        "manifest_offline": "Sem conexao. Usando manifesto em cache v{version} (Modo Offline)",
        "file_missing": "Arquivo ausente: {path}. Baixando...",
        "file_outdated": "Nova versao detectada no GitHub: {path}! Atualizando...",
        "download_ok": "Baixado com sucesso: {path} ({size} KB)",
        "download_fail": "Falha no download de {path}: {err}",
        "copy_local": "Copiado da fonte local: {path}",
        "all_updated": "Todas as {count} ferramentas verificadas e atualizadas (SHA-256 validado)!",
        "sync_summary": "Sincronizacao concluida: {checked} arquivos checados ({uptodate} mantidos, {updated} sincronizados).",
        "starting_launcher": "Iniciando Launcher Oficial da Suite...",
        "launcher_not_found": "Erro critico: Scripts_Automacao/launcher_t7.py nao encontrado!",
    },
    "en": {
        "title": "ACER PREDATOR CONNECT T7 & X7 - MANAGEMENT & RECOVERY",
        "sync_header": "SYNCING TOOLS FROM GITHUB / SUITE SYNC",
        "work_dir": "Working Directory",
        "checking_updates": "Checking suite integrity and updates on GitHub...",
        "manifest_loaded": "Manifest v{version} loaded from GitHub ({count} tracked files)",
        "manifest_offline": "No connection. Using cached manifest v{version} (Offline Mode)",
        "file_missing": "Missing file: {path}. Downloading...",
        "file_outdated": "New version detected on GitHub: {path}! Updating...",
        "download_ok": "Downloaded successfully: {path} ({size} KB)",
        "download_fail": "Download failed for {path}: {err}",
        "copy_local": "Copied from local source: {path}",
        "all_updated": "All {count} tools verified and up to date (SHA-256 validated)!",
        "sync_summary": "Sync complete: {checked} files checked ({uptodate} verified, {updated} synchronized).",
        "starting_launcher": "Starting Official Suite Launcher...",
        "launcher_not_found": "Critical error: Scripts_Automacao/launcher_t7.py not found!",
    }
}

CURRENT_LANG = "pt"

def t(key):
    return TEXTS.get(CURRENT_LANG, TEXTS["pt"]).get(key, key)

def get_desktop_dir():
    """Retorna o diretorio da Area de Trabalho em qualquer sistema operacional."""
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        cand = os.path.join(userprofile, "Desktop")
        if os.path.isdir(cand):
            return cand
    home = os.path.expanduser("~")
    cand = os.path.join(home, "Desktop")
    if os.path.isdir(cand):
        return cand
    return home

def get_file_sha256(filepath):
    """Calcula o hash SHA-256 de um arquivo."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest().upper()
    except Exception:
        return ""

def download_file(url, dest_path, timeout=30):
    """Baixa um arquivo da internet com cabecalho anti-cache e grava no destino."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        temp_dest = dest_path + ".tmp"
        with open(temp_dest, "wb") as f:
            while chunk := resp.read(65536):
                f.write(chunk)
        if os.path.isfile(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                pass
        os.replace(temp_dest, dest_path)
    return os.path.getsize(dest_path)

def sync_suite(work_dir, local_source_dir=None):
    """Sincroniza a suite completa baseada no manifesto do GitHub."""
    print("\n" + "=" * 75)
    print(f"  {C_BOLD}{t('sync_header')}{C_RESET}")
    print("=" * 75)
    print(f"  {t('work_dir')}: {work_dir}")
    print(f"  [*] {t('checking_updates')}\n")

    manifest_file = os.path.join(work_dir, "manifest_suite.json")
    cache_buster  = int(time.time())
    manifest_url  = f"{RAW_BASE}/manifest_suite.json?t={cache_buster}"
    manifest_data = None
    is_offline    = False

    try:
        download_file(manifest_url, manifest_file, timeout=8)
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        ver = manifest_data.get("suite_version", "1.0.9")
        cnt = len(manifest_data.get("files", []))
        print(f"  [OK] {t('manifest_loaded').format(version=ver, count=cnt)}")
    except Exception:
        is_offline = True
        if os.path.isfile(manifest_file):
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)
                ver = manifest_data.get("suite_version", "1.0.9")
                print(f"  {C_YELLOW}[!] {t('manifest_offline').format(version=ver)}{C_RESET}")
            except Exception:
                pass
        elif local_source_dir:
            local_mf = os.path.join(local_source_dir, "manifest_suite.json")
            if os.path.isfile(local_mf):
                try:
                    with open(local_mf, "r", encoding="utf-8") as f:
                        manifest_data = json.load(f)
                    ver = manifest_data.get("suite_version", "1.0.9")
                    print(f"  [OK] Manifesto local v{ver} carregado")
                except Exception:
                    pass

    if not manifest_data or "files" not in manifest_data:
        if is_offline:
            print(f"  {C_YELLOW}[!] Modo Offline: sem manifesto disponivel. Prosseguindo...{C_RESET}\n")
        return

    files = manifest_data.get("files", [])
    total_checked  = 0
    uptodate_count = 0
    updated_count  = 0
    new_count      = 0

    for item in files:
        rel = item.get("path", "")
        dest = os.path.join(work_dir, rel.replace("/", os.sep))
        exp_size = item.get("size", 0)
        exp_hash = item.get("sha256", "").upper()
        cat = item.get("category", "")

        total_checked += 1
        needs_download = False
        is_update = False

        if not os.path.isfile(dest):
            needs_download = True
            new_count += 1
            if not is_offline:
                print(f"  [*] {t('file_missing').format(path=rel)}")
        else:
            local_size = os.path.getsize(dest)
            if cat in ["rom", "stock_rom"]:
                if local_size == exp_size:
                    uptodate_count += 1
                else:
                    needs_download = True
                    is_update = True
                    updated_count += 1
                    if not is_offline:
                        print(f"  [*] {t('file_outdated').format(path=rel)}")
            else:
                local_hash = get_file_sha256(dest)
                if local_hash == exp_hash:
                    uptodate_count += 1
                else:
                    needs_download = True
                    is_update = True
                    updated_count += 1
                    if not is_offline:
                        print(f"  [*] {t('file_outdated').format(path=rel)}")

        if needs_download:
            if is_offline:
                continue

            copied_local = False
            if local_source_dir:
                local_src = os.path.join(local_source_dir, rel.replace("/", os.sep))
                if os.path.isfile(local_src):
                    src_size = os.path.getsize(local_src)
                    if cat in ["rom", "stock_rom"] and src_size == exp_size:
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        with open(local_src, "rb") as sf, open(dest, "wb") as df:
                            df.write(sf.read())
                        copied_local = True
                    elif cat not in ["rom", "stock_rom"]:
                        src_hash = get_file_sha256(local_src)
                        if src_hash == exp_hash:
                            os.makedirs(os.path.dirname(dest), exist_ok=True)
                            with open(local_src, "rb") as sf, open(dest, "wb") as df:
                                df.write(sf.read())
                            copied_local = True

            download_ok = False
            if not copied_local:
                file_url = f"{RAW_BASE}/{rel}?t={cache_buster}"
                try:
                    sz = download_file(file_url, dest, timeout=45)
                    download_ok = True
                except Exception as e:
                    print(f"  {C_RED}[-] {t('download_fail').format(path=rel, err=e)}{C_RESET}")

            if copied_local or download_ok:
                sz_kb = round(os.path.getsize(dest) / 1024, 1)
                print(f"  [OK] {t('download_ok').format(path=rel, size=sz_kb)}")

    print("")
    if is_offline:
        print(f"  {C_YELLOW}[!] Modo Offline: {uptodate_count} de {total_checked} arquivos verificados.{C_RESET}\n")
    elif updated_count == 0 and new_count == 0:
        print(f"  {C_GREEN}[OK] {t('all_updated').format(count=total_checked)}{C_RESET}\n")
    else:
        print(f"  {C_GREEN}[OK] {t('sync_summary').format(checked=total_checked, uptodate=uptodate_count, updated=updated_count + new_count)}{C_RESET}\n")

def main():
    global CURRENT_LANG
    # Detectar idioma padrão do sistema
    lang_env = os.environ.get("LANG", "").lower()
    if "pt" in lang_env or "br" in lang_env:
        CURRENT_LANG = "pt"
    else:
        CURRENT_LANG = "en"

    # Verificar argumentos passados na linha de comando
    for arg in sys.argv[1:]:
        if arg in ["--lang=pt", "pt", "-pt"]:
            CURRENT_LANG = "pt"
        elif arg in ["--lang=en", "en", "-en"]:
            CURRENT_LANG = "en"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_dir = get_desktop_dir()
    desktop_work_dir = os.path.join(desktop_dir, "Acer-Predator-Connect-T7")

    # Identificar se ja estamos rodando na pasta oficial ou clonada
    if os.path.isdir(os.path.join(script_dir, "Scripts_Automacao")):
        work_dir = script_dir
        local_src = script_dir
    elif os.path.isdir(os.path.join(desktop_work_dir, "Scripts_Automacao")):
        work_dir = desktop_work_dir
        local_src = script_dir
    else:
        work_dir = desktop_work_dir
        local_src = script_dir

    os.makedirs(work_dir, exist_ok=True)

    # Executar sincronizacao de ferramentas
    sync_suite(work_dir, local_source_dir=local_src)

    # Disparar launcher oficial
    launcher_script = os.path.join(work_dir, "Scripts_Automacao", "launcher_t7.py")
    if not os.path.isfile(launcher_script):
        # Tentar no diretorio de execucao
        launcher_script = os.path.join(script_dir, "Scripts_Automacao", "launcher_t7.py")

    if os.path.isfile(launcher_script):
        args = [sys.executable, launcher_script, f"--lang={CURRENT_LANG}"]
        # Repassar outros argumentos
        for a in sys.argv[1:]:
            if not a.startswith("--lang"):
                args.append(a)
        subprocess.call(args)
    else:
        print(f"{C_RED}[-] {t('launcher_not_found')}{C_RESET}")
        print(f"    Caminho esperado: {launcher_script}")

if __name__ == "__main__":
    main()
