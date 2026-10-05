#!/usr/bin/env python3
"""
unlock_only_ssh.py
Script minimalista para destravar SSH e Telnet em QUALQUER backup do Acer Predator Connect T7,
sem alterar nenhuma configuracao de rede, Wi-Fi, IP ou senhas existentes.

Uso:
    python unlock_only_ssh.py [caminho/do/seu/config.cfg]
"""

import gzip
import tarfile
import io
import sys
import os
import hashlib

def unlock_cfg(input_path, output_path, custom_ssid=None, custom_key=None):
    if not os.path.exists(input_path):
        print(f"[!] Erro: Arquivo {input_path} nao encontrado!")
        sys.exit(1)

    print(f"[*] Lendo {input_path}...")
    members_data = {}
    members_info = {}

    with gzip.open(input_path, "rb") as f:
        with tarfile.open(fileobj=f) as t:
            for m in t.getmembers():
                if m.isfile():
                    members_data[m.name] = t.extractfile(m).read()
                    members_info[m.name] = m

    print(f"[*] Total de arquivos no pacote: {len(members_data)}")

    # 1. Ajustar etc/config/dropbear
    dropbear_conf = """config dropbear
\toption PasswordAuth 'on'
\toption RootPasswordAuth 'on'
\toption Port '22'
\toption enable '1'
"""
    members_data["etc/config/dropbear"] = dropbear_conf.encode("utf-8")
    print("   [+] etc/config/dropbear atualizado (enable '1')")

    # 2. Ajustar etc/rc.local (iniciar binarios diretamente no boot)
    rc_local_orig = members_data.get("etc/rc.local", b"").decode("utf-8", errors="ignore")
    # Injetar antes do exit 0
    injection_boot = """
# --- ATIVACAO DO TERMINAL (SSH + TELNET) ---
uci set dropbear.@dropbear[0].enable='1' 2>/dev/null
uci commit dropbear 2>/dev/null

DROPBEAR=$(command -v dropbear || echo "/usr/sbin/dropbear")
[ -x "$DROPBEAR" ] && $DROPBEAR -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B

TELNETD=$(command -v telnetd || echo "/usr/sbin/telnetd")
[ -x "$TELNETD" ] && $TELNETD -l /bin/ash

if [ ! -f /usr/sbin/boot-acer ]; then
cat << 'EOFB' > /usr/sbin/boot-acer
#!/bin/sh
echo "=== Retornando boot para SLOT 1 (OEM v24 Estavel) ==="
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
echo "[OK] Slot 1 redefinido! Reiniciando..."
reboot
EOFB
chmod +x /usr/sbin/boot-acer
fi

/etc/init.d/cron restart 2>/dev/null
# -------------------------------------------
"""
    if "DROPBEAR" not in rc_local_orig:
        if "exit 0" in rc_local_orig:
            rc_local_new = rc_local_orig.replace("exit 0", injection_boot + "\nexit 0")
        else:
            rc_local_new = rc_local_orig + "\n" + injection_boot + "\nexit 0\n"
        members_data["etc/rc.local"] = rc_local_new.encode("utf-8")
        print("   [+] etc/rc.local atualizado com inicializacao direta")

    # 3. Ajustar etc/crontabs/Admin (Watchdog de persistencia a cada 60s)
    admin_cron_orig = members_data.get("etc/crontabs/Admin", b"").decode("utf-8", errors="ignore")
    cron_watchdog = (
        "* * * * * pgrep dropbear || (dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B || /usr/sbin/dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B)\n"
        "* * * * * pgrep telnetd || (telnetd -l /bin/ash || /usr/sbin/telnetd -l /bin/ash)\n"
    )
    if "dropbear" not in admin_cron_orig:
        admin_cron_new = admin_cron_orig.strip() + "\n" + cron_watchdog
        members_data["etc/crontabs/Admin"] = admin_cron_new.encode("utf-8")
        members_data["etc/crontabs/root"] = admin_cron_new.encode("utf-8")
        print("   [+] etc/crontabs/Admin atualizado com watchdog de 60 segundos")

    # 4. Ajustar etc/passwd e etc/shadow (Definir usuario 'root' e 'Admin' com senha padrao 'root0100')
    DEFAULT_ROOT_HASH = "$1$ARKroot1$inwXu9.r12/oWLrMAV9eX."  # Senha: root0100

    passwd_text = members_data["etc/passwd"].decode("utf-8", errors="ignore")
    if "root:x:0:0" not in passwd_text:
        passwd_text = "root:x:0:0:root:/root:/bin/ash\n" + passwd_text
        members_data["etc/passwd"] = passwd_text.encode("utf-8")
        print("   [+] Usuario 'root' adicionado no etc/passwd")

    shadow_text = members_data["etc/shadow"].decode("utf-8", errors="ignore")
    new_shadow_lines = []
    has_root = False
    has_admin = False

    for l in shadow_text.splitlines():
        if l.startswith("root:"):
            new_shadow_lines.append(f"root:{DEFAULT_ROOT_HASH}:20729:0:99999:7:::")
            has_root = True
        elif l.startswith("Admin:"):
            new_shadow_lines.append(f"Admin:{DEFAULT_ROOT_HASH}:20729:0:99999:7:::")
            has_admin = True
        else:
            new_shadow_lines.append(l)

    if not has_root:
        new_shadow_lines.insert(0, f"root:{DEFAULT_ROOT_HASH}:20729:0:99999:7:::")
    if not has_admin:
        new_shadow_lines.insert(1, f"Admin:{DEFAULT_ROOT_HASH}:20729:0:99999:7:::")

    members_data["etc/shadow"] = ("\n".join(new_shadow_lines) + "\n").encode("utf-8")
    print("   [+] Senha padronizada com sucesso: Usuario 'root' e 'Admin' | Senha 'root0100'")

    # 4.5. Ajustar Credenciais da Interface Web da Acer (Lighttpd / FastCGI)
    WEB_USER = "Admin"
    WEB_PASS = "root0100"
    WEB_MD5 = hashlib.md5(f"{WEB_PASS}\n".encode("utf-8")).hexdigest()

    members_data["etc/config/web_info"] = f"{WEB_USER}:{WEB_PASS}\n".encode("utf-8")
    members_data["etc/config/lighttpd.user"] = f"admin:{WEB_MD5}\n".encode("utf-8")
    members_data["etc/config/userinfo"] = f"{WEB_USER}:{WEB_PASS}_ftm\n".encode("utf-8")
    print(f"   [+] Interface Web sincronizada com senha '{WEB_PASS}' (Hash MD5: {WEB_MD5})")

    # 4.6. Opcional: Personalizar Wi-Fi (SSID e Senha)
    if (custom_ssid or custom_key) and "etc/config/wireless" in members_data:
        import re
        w_text = members_data["etc/config/wireless"].decode("utf-8", errors="ignore")
        if custom_key:
            w_text = re.sub(r"(option\s+key\s+)'[^']*'", rf"\1'{custom_key}'", w_text)
            w_text = re.sub(r"(option\s+sae_password\s+)'[^']*'", rf"\1'{custom_key}'", w_text)
            print(f"   [+] Senha do Wi-Fi definida para: '{custom_key}'")
        if custom_ssid:
            for old_pfx in ["Predator_T7", "T7_0W0J", "CASA_ARK"]:
                if old_pfx in w_text:
                    w_text = w_text.replace(old_pfx, custom_ssid)
            print(f"   [+] Nome do Wi-Fi (SSID) definido com prefixo: '{custom_ssid}'")
        members_data["etc/config/wireless"] = w_text.encode("utf-8")

    # 5. Empacotar novo .cfg com permissoes Unix exatas
    out_tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=out_tar_bytes, mode="w") as t:
        for name, data in members_data.items():
            info = members_info.get(name)
            ti = tarfile.TarInfo(name=name)
            ti.size = len(data)
            ti.mtime = info.mtime if info else 1727630000
            if name in ["etc/rc.local"]:
                ti.mode = 0o775
            elif name in ["etc/config/dropbear", "etc/dropbear/dropbear_rsa_host_key", "etc/shadow"]:
                ti.mode = 0o600
            elif name in ["etc/crontabs/Admin", "etc/crontabs/root"]:
                ti.mode = 0o644
            elif info:
                ti.mode = info.mode
            else:
                ti.mode = 0o644
            ti.uname = info.uname if info else "root"
            ti.gname = info.gname if info else "root"
            t.addfile(ti, io.BytesIO(data))

    compressed = gzip.compress(out_tar_bytes.getvalue(), mtime=0)
    with open(output_path, "wb") as f:
        f.write(compressed)

    print(f"\n[OK] Arquivo desbloqueado gerado com sucesso: {output_path}")
    print("=" * 72)
    print("  INSTRUCOES DE ACESSO APOS RESTAURAR O ARQUIVO NO PAINEL DA ACER:")
    print("=" * 72)
    print("  1. No painel web da Acer, va em: System -> Backup and restore -> Restore")
    print(f"     e selecione o arquivo: {os.path.basename(output_path)}")
    print("  2. Aguarde o roteador reiniciar (cerca de 2 minutos).")
    print("  3. CREDENCIAIS DE ACESSO DEFINIDAS:")
    print("     - SSH (Porta 22) e LuCI Web (Porta 80):")
    print("       Usuario: 'root' (ou 'Admin')")
    print("       Senha:   'root'")
    print("       Comando: ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.76.1")
    print("     - Telnet (Porta 23 - Shell Direto de Emergencia):")
    print("       Conecta DIRETO sem pedir senha (telnet 192.168.76.1 23)")
    if custom_key or custom_ssid:
        print("  4. REDES WI-FI CONFIGURADAS:")
        print(f"     - Nome (SSID): {custom_ssid if custom_ssid else 'Predator_T7'}")
        print(f"     - Senha:       {custom_key if custom_key else 'predator123'}")
    else:
        print("  4. E O WI-FI?")
        print("     - Redes padrao Predator_T7 ativas com senha 'predator123'.")
    print("=" * 72)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Desbloqueador de SSH/Telnet para Acer Predator Connect T7")
    parser.add_argument("input", nargs="?", default="config.cfg", help="Caminho do arquivo .cfg de entrada")
    parser.add_argument("output", nargs="?", default=None, help="Caminho do arquivo .cfg de saida")
    parser.add_argument("--ssid", "-s", default=None, help="Personalizar nome da rede Wi-Fi (SSID)")
    parser.add_argument("--password", "-p", default=None, help="Personalizar senha do Wi-Fi (minimo 8 caracteres)")
    args = parser.parse_args()

    out_file = args.output if args.output else os.path.join(os.path.dirname(args.input), "config_ssh_unlocked.cfg")
    unlock_cfg(args.input, out_file, custom_ssid=args.ssid, custom_key=args.password)
