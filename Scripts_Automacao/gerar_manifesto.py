#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_manifesto.py - Gerador e Atualizador do Manifesto da Suite
Acer Predator Connect T7 & X7
Gera 'manifest_suite.json' com SHA-256, tamanhos e timestamps de todos os arquivos vitais.
"""

import os
import json
import hashlib
from datetime import datetime, timezone

SUITE_VERSION = "1.0.1"

TRACKED_FILES = [
    {"path": "Scripts_Automacao/launcher_t7.py", "category": "script"},
    {"path": "Scripts_Automacao/telnet_compat.py", "category": "script"},
    {"path": "Scripts_Automacao/gerenciar_telnet.py", "category": "script"},
    {"path": "Scripts_Automacao/otimizar_e_ativar_luci_slot2.py", "category": "script"},
    {"path": "Scripts_Automacao/gravar_v27_slot2.py", "category": "script"},
    {"path": "Scripts_Automacao/switch_boot_slot.py", "category": "script"},
    {"path": "Scripts_Automacao/diagnostico_x7.py", "category": "script"},
    {"path": "Scripts_Automacao/unlock_only_ssh.py", "category": "script"},
    {"path": "Scripts_Automacao/aplicar_configuracao_pessoal_ap_t7.py", "category": "script"},
    {"path": "02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_ssh_unlocked.cfg", "category": "cfg"},
    {"path": "01_FIRMWARES_E_IMAGENS/Official_v27_Componentes/kernel.bin", "category": "rom"},
    {"path": "01_FIRMWARES_E_IMAGENS/Official_v27_Componentes/wifi_fw.bin", "category": "rom"},
    {"path": "01_FIRMWARES_E_IMAGENS/Official_v27_Componentes/rootfs.squashfs", "category": "rom"},
    {"path": "iniciar.ps1", "category": "launcher"},
    {"path": "EXECUTAR_T7.bat", "category": "launcher"}
]

def get_file_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(repo_root, "manifest_suite.json")

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "suite_version": SUITE_VERSION,
        "updated_at": now_iso,
        "description": "Acer Predator Connect T7 & X7 - Manifest Oficial de Sincronizacao da Suite",
        "files": []
    }

    print(f"[*] Gerando manifesto em: {manifest_path}")

    for item in TRACKED_FILES:
        rel_path = item["path"]
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))

        if not os.path.isfile(abs_path):
            print(f"[-] AVISO: Arquivo nao encontrado: {abs_path}")
            continue

        size = os.path.getsize(abs_path)
        sha256 = get_file_sha256(abs_path)
        mtime = os.path.getmtime(abs_path)
        mtime_iso = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        manifest["files"].append({
            "path": rel_path,
            "category": item["category"],
            "size": size,
            "sha256": sha256,
            "updated_at": mtime_iso
        })
        print(f"  [+] {rel_path} ({size} bytes) -> SHA-256: {sha256[:16]}...")

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Manifesto gerado com sucesso! Total de {len(manifest['files'])} arquivos mapeados.")

if __name__ == "__main__":
    main()
