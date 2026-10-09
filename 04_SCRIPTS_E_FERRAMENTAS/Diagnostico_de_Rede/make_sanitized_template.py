import gzip
import tarfile
import io
import os

src_cfg = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\Meus_Backups_Pessoais\config_ap_ssh_unlocked.cfg"
out_cfg = r"H:\FEITOS COM IA\Acer-Predator-Connect-T7\Configuracoes_Roteador\config_ap_ssh_unlocked_template.cfg"

members_data = {}
members_info = {}

with gzip.open(src_cfg, "rb") as f:
    with tarfile.open(fileobj=f) as t:
        for m in t.getmembers():
            if m.isfile():
                members_data[m.name] = t.extractfile(m).read()
                members_info[m.name] = m

print(f"Loaded {len(members_data)} files from {src_cfg}")

# Sanitize wireless
OLD_PWD = os.environ.get("OLD_PWD", "MyOldPassword@")
if "etc/config/wireless" in members_data:
    wireless_text = members_data["etc/config/wireless"].decode("utf-8")
    wireless_text = wireless_text.replace(OLD_PWD, "Predator1234@")
    wireless_text = wireless_text.replace("CASA_ARK_7G", "Predator_T7_MLO")
    wireless_text = wireless_text.replace("CASA_ARK_6G", "Predator_T7_6G")
    wireless_text = wireless_text.replace("CASA_ARK_5G", "Predator_T7_5G")
    wireless_text = wireless_text.replace("CASA_ARK", "Predator_T7_2.4G")
    wireless_text = wireless_text.replace("TV casa", "Predator_T7_IoT")
    members_data["etc/config/wireless"] = wireless_text.encode("utf-8")

# Sanitize tripleband
if "etc/config/tripleband" in members_data:
    tb_text = members_data["etc/config/tripleband"].decode("utf-8")
    tb_text = tb_text.replace(OLD_PWD, "Predator1234@")
    tb_text = tb_text.replace("CASA_ARK", "Predator_T7_2.4G")
    members_data["etc/config/tripleband"] = tb_text.encode("utf-8")

# Sanitize wifi_ssid_pwd
if "etc/config/wifi_ssid_pwd" in members_data:
    sp_text = members_data["etc/config/wifi_ssid_pwd"].decode("utf-8")
    sp_text = sp_text.replace(OLD_PWD, "Predator1234@")
    sp_text = sp_text.replace("CASA_ARK_6G", "Predator_T7_6G")
    sp_text = sp_text.replace("CASA_ARK_5G", "Predator_T7_5G")
    sp_text = sp_text.replace("CASA_ARK", "Predator_T7_2.4G")
    members_data["etc/config/wifi_ssid_pwd"] = sp_text.encode("utf-8")

# Sanitize shadow: use known factory default password ('admin0100')
# Hash MD5-crypt: $1$kMEMhTxY$sPDoqUPT7zj5ats82mEdO0 -> Senha: admin0100
factory_hash = "$1$kMEMhTxY$sPDoqUPT7zj5ats82mEdO0"
shadow_lines = []
for line in members_data["etc/shadow"].decode("utf-8").splitlines():
    parts = line.split(":")
    if parts[0] in ["Admin", "root"]:
        parts[1] = factory_hash
        shadow_lines.append(":".join(parts))
    else:
        shadow_lines.append(line)
members_data["etc/shadow"] = ("\n".join(shadow_lines) + "\n").encode("utf-8")

# Pack sanitized template
out_tar_bytes = io.BytesIO()
with tarfile.open(fileobj=out_tar_bytes, mode="w") as t:
    for name, data in members_data.items():
        info = members_info.get(name)
        ti = tarfile.TarInfo(name=name)
        ti.size = len(data)
        ti.mtime = 1727630000
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
        ti.uname = "root"
        ti.gname = "root"
        t.addfile(ti, io.BytesIO(data))

compressed = gzip.compress(out_tar_bytes.getvalue(), mtime=0)
with open(out_cfg, "wb") as f:
    f.write(compressed)

print(f"Generated sanitized template: {out_cfg} ({len(compressed)} bytes)")
print("=" * 60)
print("  CREDENCIAIS PADRAO EMBUTIDAS NO TEMPLATE SANITIZADO:")
print("  - Root/Admin Web (LuCI) e SSH : admin0100")
print("  - Redes Wi-Fi (SSID): Predator_T7_MLO / Predator_T7_6G / 5G")
print("  - Senha do Wi-Fi: Predator1234@")
print("=" * 60)
