#!/usr/bin/env python3
"""
gerar_cfg_personalizado.py
==========================
Gerador Automatizado de Pacote de Restauração Personalizado (.cfg) para Acer Predator Connect T7.

Combina a base de restauração MASTER V2 (com 100% das otimizações de kernel, RF, MSS clamping,
DNS Anycast dual-stack, roaming 802.11k/v, coldboot bringup e debloat) com as configurações
pessoais de um usuário específico (IP de LAN, SSIDs, senhas Wi-Fi, MACs de hardware e senha de root).

Uso:
    # 1. Modo Automático (Extrai direto de um backup antigo do usuário):
    python3 dev/gerar_cfg_personalizado.py --from-backup ~/Downloads/backup-PREDATOR-2026-10-12.tar.gz --output cfg_restauracao_diego_v2.cfg

    # 2. Modo Manual (Passando parâmetros específicos):
    python3 dev/gerar_cfg_personalizado.py --lan-ip 192.168.1.1 --ssid-base KING_COSMAKER --wifi-key magnetic_field --output cfg_restauracao_custom.cfg
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def log(msg, symbol="ℹ️"):
    print(f"{symbol} {msg}")


def parse_uci_config(content: str) -> list:
    """Parseia arquivo de configuração UCI simples em blocos estruturados."""
    sections = []
    current_section = None

    for line in content.splitlines():
        trimmed = line.strip()
        m_sec = re.match(r"^config\s+([a-zA-Z0-9_\-]+)(?:\s+'([^']*)'|\s+(\S+))?", trimmed)
        if m_sec:
            stype = m_sec.group(1)
            sname = m_sec.group(2) or m_sec.group(3) or ""
            current_section = {
                "type": stype,
                "name": sname,
                "raw_header": line,
                "options": [],
            }
            sections.append(current_section)
        elif current_section is not None:
            current_section["options"].append(line)
        else:
            # Comentários ou linhas no topo
            sections.append({"type": "_raw", "line": line})

    return sections


def get_uci_option(section: dict, opt_name: str) -> str:
    """Retorna o valor de uma opção UCI em uma seção."""
    if "options" not in section:
        return ""
    pattern = re.compile(rf"^\s*(?:option|list)\s+{re.escape(opt_name)}\s+'([^']*)'")
    for opt_line in section["options"]:
        m = pattern.match(opt_line)
        if m:
            return m.group(1)
    return ""


def set_uci_option(section: dict, opt_name: str, opt_value: str, create: bool = True):
    """Atualiza ou insere uma opção UCI em uma seção."""
    if "options" not in section:
        return
    pattern = re.compile(rf"^(\s*)(option\s+{re.escape(opt_name)}\s+)'.*?'(.*)$")
    replaced = False
    new_options = []
    for opt_line in section["options"]:
        if pattern.match(opt_line):
            m = pattern.match(opt_line)
            indent = m.group(1) or "\t"
            rest = m.group(3) or ""
            new_options.append(f"{indent}option {opt_name} '{opt_value}'{rest}")
            replaced = True
        else:
            new_options.append(opt_line)

    if not replaced and create:
        new_options.append(f"\toption {opt_name} '{opt_value}'")

    section["options"] = new_options


def serialize_uci(sections: list) -> str:
    """Serializa os blocos UCI de volta para formato texto."""
    lines = []
    for sec in sections:
        if sec.get("type") == "_raw":
            lines.append(sec["line"])
        else:
            lines.append(sec["raw_header"])
            for opt in sec["options"]:
                lines.append(opt)
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def extract_data_from_backup(backup_path: Path) -> dict:
    """Extrai parâmetros pessoais de um arquivo de backup (.tar.gz) existente."""
    extracted = {
        "lan_ip": None,
        "wifi0_mac": None,
        "wifi1_mac": None,
        "wifi2_mac": None,
        "ssid_2g": None,
        "ssid_5g": None,
        "ssid_6g": None,
        "key_2g": None,
        "key_5g": None,
        "key_6g": None,
        "root_shadow": None,
    }

    log(f"Lendo dados pessoais do backup: {backup_path.name}", "🔍")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_p = Path(tmpdir)
        try:
            subprocess.run(["tar", "-zxf", str(backup_path), "-C", str(tmp_p)], check=True, capture_output=True)
        except Exception as e:
            log(f"Erro ao extrair backup: {e}", "❌")
            sys.exit(1)

        # 1. Network (LAN IP)
        net_cfg = tmp_p / "etc" / "config" / "network"
        if net_cfg.exists():
            content = net_cfg.read_text(encoding="utf-8", errors="ignore")
            sections = parse_uci_config(content)
            for sec in sections:
                if sec.get("type") == "interface" and sec.get("name") == "lan":
                    extracted["lan_ip"] = get_uci_option(sec, "ipaddr")

        # 2. Wireless (MACs, SSIDs, Senhas)
        wl_cfg = tmp_p / "etc" / "config" / "wireless"
        if wl_cfg.exists():
            content = wl_cfg.read_text(encoding="utf-8", errors="ignore")
            sections = parse_uci_config(content)
            for sec in sections:
                stype = sec.get("type")
                sname = sec.get("name")
                if stype == "wifi-device":
                    mac = get_uci_option(sec, "macaddr")
                    if sname == "wifi0":
                        extracted["wifi0_mac"] = mac
                    elif sname == "wifi1":
                        extracted["wifi1_mac"] = mac
                    elif sname == "wifi2":
                        extracted["wifi2_mac"] = mac
                elif stype == "wifi-iface":
                    ssid = get_uci_option(sec, "ssid")
                    key = get_uci_option(sec, "key") or get_uci_option(sec, "sae_password")
                    if sname == "wifi0_ap":
                        extracted["ssid_2g"] = ssid
                        extracted["key_2g"] = key
                    elif sname == "wifi1_ap":
                        extracted["ssid_5g"] = ssid
                        extracted["key_5g"] = key
                    elif sname == "wifi2_ap":
                        extracted["ssid_6g"] = ssid
                        extracted["key_6g"] = key

        # 3. Shadow (Root password hash)
        shadow_f = tmp_p / "etc" / "shadow"
        if shadow_f.exists():
            for line in shadow_f.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("root:"):
                    parts = line.split(":")
                    if len(parts) >= 2 and parts[1]:
                        extracted["root_shadow"] = parts[1]
                    break

    return extracted


def build_custom_cfg(
    master_cfg_path: Path,
    output_cfg_path: Path,
    lan_ip: str,
    wifi0_mac: str,
    wifi1_mac: str,
    wifi2_mac: str,
    ssid_2g: str,
    ssid_5g: str,
    ssid_6g: str,
    key_2g: str,
    key_5g: str,
    key_6g: str,
    root_shadow: str,
):
    """Descompacta o master v2, injeta as configurações pessoais e empacota o novo .cfg limpo."""
    log(f"Utilizando como base: {master_cfg_path.name}", "📦")

    with tempfile.TemporaryDirectory() as staging_dir:
        staging_p = Path(staging_dir)

        # Descompacta o Master V2
        subprocess.run(["tar", "-zxf", str(master_cfg_path), "-C", str(staging_p)], check=True, capture_output=True)

        # 1. Customizar etc/config/network
        net_path = staging_p / "etc" / "config" / "network"
        if net_path.exists():
            net_content = net_path.read_text(encoding="utf-8", errors="ignore")
            net_sections = parse_uci_config(net_content)
            for sec in net_sections:
                if sec.get("type") == "interface" and sec.get("name") == "lan":
                    old_ip = get_uci_option(sec, "ipaddr")
                    if lan_ip:
                        set_uci_option(sec, "ipaddr", lan_ip)
                        log(f"LAN IP ajustado: {old_ip} -> {lan_ip}", "✅")
            net_path.write_text(serialize_uci(net_sections), encoding="utf-8")

        # 2. Customizar etc/config/wireless
        wl_path = staging_p / "etc" / "config" / "wireless"
        if wl_path.exists():
            wl_content = wl_path.read_text(encoding="utf-8", errors="ignore")
            wl_sections = parse_uci_config(wl_content)
            for sec in wl_sections:
                stype = sec.get("type")
                sname = sec.get("name")

                # Atualiza MACs de Hardware (se fornecidos)
                if stype == "wifi-device":
                    if sname == "wifi0" and wifi0_mac:
                        set_uci_option(sec, "macaddr", wifi0_mac)
                        log(f"wifi0 MAC: {wifi0_mac}", "📶")
                    elif sname == "wifi1" and wifi1_mac:
                        set_uci_option(sec, "macaddr", wifi1_mac)
                        log(f"wifi1 MAC: {wifi1_mac}", "📶")
                    elif sname == "wifi2" and wifi2_mac:
                        set_uci_option(sec, "macaddr", wifi2_mac)
                        log(f"wifi2 MAC: {wifi2_mac}", "📶")

                # Atualiza SSIDs e Senhas
                elif stype == "wifi-iface":
                    if sname == "wifi0_ap":
                        if ssid_2g:
                            set_uci_option(sec, "ssid", ssid_2g)
                        if key_2g:
                            set_uci_option(sec, "key", key_2g)
                            set_uci_option(sec, "sae_password", key_2g)
                        # Garante criptografia psk2+aes compatível
                        set_uci_option(sec, "encryption", "psk2+aes")
                        log(f"2.4 GHz SSID: {ssid_2g or 'Inalterado'} (WPA2-PSK puro)", "📶")
                    elif sname == "wifi1_ap":
                        if ssid_5g:
                            set_uci_option(sec, "ssid", ssid_5g)
                        if key_5g:
                            set_uci_option(sec, "key", key_5g)
                            set_uci_option(sec, "sae_password", key_5g)
                        set_uci_option(sec, "encryption", "psk2+aes")
                        log(f"5.0 GHz SSID: {ssid_5g or 'Inalterado'} (WPA2-PSK puro)", "📶")
                    elif sname == "wifi2_ap":
                        if ssid_6g:
                            set_uci_option(sec, "ssid", ssid_6g)
                        if key_6g:
                            set_uci_option(sec, "key", key_6g)
                            set_uci_option(sec, "sae_password", key_6g)
                        set_uci_option(sec, "encryption", "sae")
                        set_uci_option(sec, "sae", "1")
                        set_uci_option(sec, "ieee80211w", "2")
                        log(f"6.0 GHz SSID: {ssid_6g or 'Inalterado'} (WPA3-SAE puro)", "📶")

            wl_path.write_text(serialize_uci(wl_sections), encoding="utf-8")

        # 3. Customizar etc/shadow (Senha do Root)
        if root_shadow:
            shadow_path = staging_p / "etc" / "shadow"
            if shadow_path.exists():
                lines = shadow_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                new_lines = []
                for line in lines:
                    if line.startswith("root:"):
                        parts = line.split(":")
                        parts[1] = root_shadow
                        new_lines.append(":".join(parts))
                        log("Hash de senha do root sincronizado", "🔑")
                    else:
                        new_lines.append(line)
                shadow_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

        # 4. Empacotar o novo tarball .cfg sem metadados Apple
        log(f"Empacotando arquivo de restauração: {output_cfg_path}", "⚙️")
        tar_cmd = [
            "tar",
            "--no-mac-metadata",
            "-czf",
            str(output_cfg_path.resolve()),
            "etc",
        ]
        env = os.environ.copy()
        env["COPYFILE_DISABLE"] = "1"

        proc = subprocess.run(tar_cmd, cwd=str(staging_p), env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            log(f"Falha ao empacotar tar: {proc.stderr}", "❌")
            sys.exit(1)

        size_kb = output_cfg_path.stat().st_size / 1024
        log(f"Pacote gerado com sucesso: {output_cfg_path.name} ({size_kb:.1f} KB)", "🎉")


def main():
    parser = argparse.ArgumentParser(
        description="Gerador de Pacote de Restauração Personalizado (.cfg) para Acer Predator Connect T7"
    )
    parser.add_argument(
        "--master-cfg",
        type=Path,
        default=Path("cfg_restauracao_master_v2.cfg"),
        help="Caminho do master .cfg base (padrão: cfg_restauracao_master_v2.cfg)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("cfg_restauracao_personalizado.cfg"),
        help="Arquivo de saída gerado (padrão: cfg_restauracao_personalizado.cfg)",
    )
    parser.add_argument(
        "--from-backup",
        type=Path,
        help="Extrair automaticamente dados pessoais de um backup existente (.tar.gz)",
    )
    parser.add_argument("--lan-ip", type=str, help="IP da interface LAN (ex: 192.168.1.1)")
    parser.add_argument("--ssid-base", type=str, help="Nome base para as redes Wi-Fi (ex: BESTYALL)")
    parser.add_argument("--ssid-2g", type=str, help="SSID da banda 2.4 GHz")
    parser.add_argument("--ssid-5g", type=str, help="SSID da banda 5.0 GHz")
    parser.add_argument("--ssid-6g", type=str, help="SSID da banda 6.0 GHz")
    parser.add_argument("--wifi-key", type=str, help="Senha das redes Wi-Fi")
    parser.add_argument("--mac-wifi0", type=str, help="MAC address do rádio wifi0 (2.4G)")
    parser.add_argument("--mac-wifi1", type=str, help="MAC address do rádio wifi1 (5G)")
    parser.add_argument("--mac-wifi2", type=str, help="MAC address do rádio wifi2 (6G)")

    args = parser.parse_args()

    # Localiza o master cfg
    master_p = args.master_cfg
    if not master_p.exists():
        # Tenta buscar na raiz do repositório
        repo_root = Path(__file__).resolve().parent.parent
        alt_master = repo_root / "cfg_restauracao_master_v2.cfg"
        if alt_master.exists():
            master_p = alt_master
        else:
            log(f"Arquivo master {master_p} não encontrado!", "❌")
            sys.exit(1)

    # Valores padrão
    lan_ip = args.lan_ip
    wifi0_mac = args.mac_wifi0
    wifi1_mac = args.mac_wifi1
    wifi2_mac = args.mac_wifi2
    ssid_2g = args.ssid_2g
    ssid_5g = args.ssid_5g
    ssid_6g = args.ssid_6g
    key_2g = args.wifi_key
    key_5g = args.wifi_key
    key_6g = args.wifi_key
    root_shadow = None

    if args.ssid_base:
        if not ssid_2g:
            ssid_2g = args.ssid_base
        if not ssid_5g:
            ssid_5g = f"{args.ssid_base}_5G"
        if not ssid_6g:
            ssid_6g = f"{args.ssid_base}_6G"

    # Se fornecido backup de origem, lê os dados
    if args.from_backup:
        backup_p = args.from_backup.expanduser()
        if not backup_p.exists():
            log(f"Arquivo de backup {backup_p} não existe!", "❌")
            sys.exit(1)
        data = extract_data_from_backup(backup_p)
        if not lan_ip:
            lan_ip = data.get("lan_ip")
        if not wifi0_mac:
            wifi0_mac = data.get("wifi0_mac")
        if not wifi1_mac:
            wifi1_mac = data.get("wifi1_mac")
        if not wifi2_mac:
            wifi2_mac = data.get("wifi2_mac")
        if not ssid_2g:
            ssid_2g = data.get("ssid_2g")
        if not ssid_5g:
            ssid_5g = data.get("ssid_5g")
        if not ssid_6g:
            ssid_6g = data.get("ssid_6g")
        if not key_2g:
            key_2g = data.get("key_2g")
        if not key_5g:
            key_5g = data.get("key_5g")
        if not key_6g:
            key_6g = data.get("key_6g")
        root_shadow = data.get("root_shadow")

    log("=" * 60, "🛠️")
    log("GERADOR DE RESTAURAÇÃO PERSONALIZADA - ACER PREDATOR CONNECT T7", "🚀")
    log("=" * 60, "🛠️")
    log(f"IP LAN de Destino : {lan_ip or '192.168.76.1 (Padrão Master)'}")
    log(f"SSID 2.4 GHz      : {ssid_2g or 'PREDATOR T7_2.4GHz'}")
    log(f"SSID 5.0 GHz      : {ssid_5g or 'PREDATOR T7_5GHz'}")
    log(f"SSID 6.0 GHz      : {ssid_6g or 'PREDATOR T7_6GHz'}")
    log(f"Senha Wi-Fi       : {'*' * len(key_2g) if key_2g else '123456789 (Padrão)'}")
    log(f"MACs de Hardware  : wifi0={wifi0_mac or 'Stock'} | wifi1={wifi1_mac or 'Stock'} | wifi2={wifi2_mac or 'Stock'}")
    log("-" * 60, "🛠️")

    build_custom_cfg(
        master_cfg_path=master_p,
        output_cfg_path=args.output,
        lan_ip=lan_ip,
        wifi0_mac=wifi0_mac,
        wifi1_mac=wifi1_mac,
        wifi2_mac=wifi2_mac,
        ssid_2g=ssid_2g,
        ssid_5g=ssid_5g,
        ssid_6g=ssid_6g,
        key_2g=key_2g,
        key_5g=key_5g,
        key_6g=key_6g,
        root_shadow=root_shadow,
    )


if __name__ == "__main__":
    main()
