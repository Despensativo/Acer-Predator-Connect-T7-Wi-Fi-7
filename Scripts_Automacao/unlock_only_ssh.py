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

def unlock_cfg(input_path, output_path):
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

    # 4. Ajustar etc/passwd e etc/shadow (criar usuario 'root' com a mesma senha do 'Admin')
    passwd_text = members_data["etc/passwd"].decode("utf-8", errors="ignore")
    if "root:x:0:0" not in passwd_text:
        passwd_text = "root:x:0:0:root:/root:/bin/ash\n" + passwd_text
        members_data["etc/passwd"] = passwd_text.encode("utf-8")
        print("   [+] Usuario 'root' adicionado no etc/passwd")

    shadow_text = members_data["etc/shadow"].decode("utf-8", errors="ignore")
    admin_line = ""
    for l in shadow_text.splitlines():
        if l.startswith("Admin:"):
            admin_line = l
            break
    if admin_line and not any(l.startswith("root:") for l in shadow_text.splitlines()):
        root_line = "root:" + admin_line.split(":", 1)[1]
        shadow_text = root_line + "\n" + shadow_text
        members_data["etc/shadow"] = shadow_text.encode("utf-8")
        print("   [+] Senha do 'root' espelhada da senha do 'Admin' no etc/shadow")

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
    print("     Restaure esse arquivo no painel do roteador e o SSH/Telnet estarao ativos!")

if __name__ == "__main__":
    in_file = sys.argv[1] if len(sys.argv) > 1 else "config.cfg"
    out_file = "config_ssh_unlocked.cfg"
    unlock_cfg(in_file, out_file)
