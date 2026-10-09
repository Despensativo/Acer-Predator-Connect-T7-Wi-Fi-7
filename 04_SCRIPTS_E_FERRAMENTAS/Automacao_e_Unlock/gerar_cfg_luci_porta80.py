import tarfile
import gzip
import os
import io
import re

src_path = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\Meus_Backups_Pessoais\config_ap_debloated_luci.cfg"
out_path = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\Configuracoes_Roteador\restaurar_openwrt_luci_porta80.cfg"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

members_data = {}
members_info = {}

with gzip.open(src_path, "rb") as f:
    with tarfile.open(fileobj=f) as t:
        for m in t.getmembers():
            if m.isfile():
                members_data[m.name] = t.extractfile(m).read()
                members_info[m.name] = m

# 1. Update rc.local to run LuCI on port 80/443 without lighttpd
rc_local = """# Put your custom commands here that should be executed once
# the system init finished. By default this file does nothing.

# Desativar lighttpd
/etc/init.d/lighttpd stop 2>/dev/null
killall lighttpd 2>/dev/null

# Habilitar Dropbear e Telnet
uci set dropbear.@dropbear[0].enable='1' 2>/dev/null
uci commit dropbear 2>/dev/null

DROPBEAR=$(command -v dropbear || echo "/usr/sbin/dropbear")
[ -x "$DROPBEAR" ] && $DROPBEAR -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B

TELNETD=$(command -v telnetd || echo "/usr/sbin/telnetd")
[ -x "$TELNETD" ] && $TELNETD -l /bin/ash

/etc/init.d/cron restart 2>/dev/null

# Iniciar LuCI diretamente na porta 80 e 443
/usr/sbin/uhttpd -p 0.0.0.0:80 -s 0.0.0.0:443 -h /www -x /cgi-bin

exit 0
"""
members_data["etc/rc.local"] = rc_local.encode("utf-8")

# 2. Update hostname in etc/config/system
if "etc/config/system" in members_data:
    sys_conf = members_data["etc/config/system"].decode("utf-8", errors="ignore")
    sys_conf = re.sub(r"option hostname '[^']*'", "option hostname 'Predator-Connect-T7'", sys_conf)
    members_data["etc/config/system"] = sys_conf.encode("utf-8")

# 3. Update cron keepalive
cron_admin = """* * * * * pgrep dropbear || (/usr/sbin/dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B)
* * * * * pgrep telnetd || (/usr/sbin/telnetd -l /bin/ash)
* * * * * pgrep uhttpd || (/usr/sbin/uhttpd -p 0.0.0.0:80 -s 0.0.0.0:443 -h /www -x /cgi-bin)
"""
members_data["etc/crontabs/Admin"] = cron_admin.encode("utf-8")

# Write output tar.gz
with gzip.open(out_path, "wb") as f_out:
    with tarfile.open(fileobj=f_out, mode="w") as t_out:
        for name, data in members_data.items():
            ti = tarfile.TarInfo(name=name)
            ti.size = len(data)
            ti.mtime = 1737086574
            ti.mode = 0o775 if name == "etc/rc.local" else 0o644
            t_out.addfile(ti, io.BytesIO(data))

print("[OK] Arquivo gerado com sucesso:", out_path)
print("Tamanho:", os.path.getsize(out_path), "bytes")
