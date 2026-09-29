import gzip
import tarfile
import io
import os

src_cfg = r"C:\Users\User\Downloads\config(1).cfg"
out_cfg = r"C:\Users\User\Downloads\config_ap_ssh_unlocked.cfg"

# Read all files from config(1).cfg
members_data = {}
members_info = {}

with gzip.open(src_cfg, "rb") as f:
    with tarfile.open(fileobj=f) as t:
        for m in t.getmembers():
            if m.isfile():
                members_data[m.name] = t.extractfile(m).read()
                members_info[m.name] = m

print(f"Loaded {len(members_data)} files from {src_cfg}")

# 1. Update /etc/config/dropbear
dropbear_conf = """config dropbear
\toption PasswordAuth 'on'
\toption RootPasswordAuth 'on'
\toption Port '22'
\toption enable '1'
"""
members_data["etc/config/dropbear"] = dropbear_conf.encode("utf-8")

# 2. Update /etc/rc.local
rc_local = """# Put your custom commands here that should be executed once
# the system init finished. By default this file does nothing.
modem_readd &
##disable default web server and enable lighttpd as web server. by zhanglei
/etc/init.d/uhttpd stop
##this should at the end of this file.

if [ "$(uci -q get network.xlatd.disabled)" == "" ]; then
    uci set network.xlatd=interface
    uci set network.xlatd.proto='464xlat'
    uci set network.xlatd.tunlink='wan1'
    uci set network.xlatd.ip6prefix='64:ff9b::/96'
    uci set network.xlatd.disabled='1'
    uci commit network
fi

/etc/init.d/lighttpd/lighttpd.init start

# Enable dropbear in UCI
uci set dropbear.@dropbear[0].enable='1' 2>/dev/null
uci commit dropbear 2>/dev/null

# Start Dropbear directly in background with RSA key and generate missing keys as needed
DROPBEAR=$(command -v dropbear || echo "/usr/sbin/dropbear")
[ -x "$DROPBEAR" ] && $DROPBEAR -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B

# Start Telnet daemon on port 23
TELNETD=$(command -v telnetd || echo "/usr/sbin/telnetd")
[ -x "$TELNETD" ] && $TELNETD -l /bin/ash

# Ensure crond is running and reload
/etc/init.d/cron restart 2>/dev/null

exit 0
"""
members_data["etc/rc.local"] = rc_local.encode("utf-8")

# 3. Update /etc/crontabs/Admin
admin_cron = """0 3 * * * /lib/functions/silent-reboot.sh
54 0 * * * /lib/functions/download_img.sh
12 2 * * * /lib/functions/update_img.sh
* * * * * pgrep dropbear || (dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B || /usr/sbin/dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B)
* * * * * pgrep telnetd || (telnetd -l /bin/ash || /usr/sbin/telnetd -l /bin/ash)
"""
members_data["etc/crontabs/Admin"] = admin_cron.encode("utf-8")
members_data["etc/crontabs/root"] = admin_cron.encode("utf-8")

# 4. Add root user to etc/passwd and etc/shadow
passwd_text = members_data["etc/passwd"].decode("utf-8")
if "root:x:0:0" not in passwd_text:
    passwd_text = "root:x:0:0:root:/root:/bin/ash\n" + passwd_text
    members_data["etc/passwd"] = passwd_text.encode("utf-8")
    print("Added root:x:0:0 to etc/passwd")

shadow_text = members_data["etc/shadow"].decode("utf-8")
admin_shadow_line = ""
for line in shadow_text.splitlines():
    if line.startswith("Admin:"):
        admin_shadow_line = line
        break

if admin_shadow_line and not any(line.startswith("root:") for line in shadow_text.splitlines()):
    root_shadow_line = "root:" + admin_shadow_line.split(":", 1)[1]
    shadow_text = root_shadow_line + "\n" + shadow_text
    members_data["etc/shadow"] = shadow_text.encode("utf-8")
    print("Added root line to etc/shadow")

# 5. Lock optimal channels in etc/config/wireless:
# 2.4 GHz (wifi0) -> channel 1
# 5 GHz (wifi1)   -> channel 36
# 6 GHz (wifi2)   -> channel 37 (PSC)
wireless_text = members_data["etc/config/wireless"].decode("utf-8")
wireless_blocks = []
current_device = None

for block in wireless_text.split("config wifi-device "):
    if not block.strip():
        continue
    dev_header = block.splitlines()[0]
    dev_name = dev_header.strip("'").strip('"')
    
    # Process options in this device block
    lines = block.splitlines()
    new_lines = []
    for line in lines:
        if "option channel" in line:
            if dev_name == "wifi0":
                new_lines.append("\toption channel '1'")
                print("Set wifi0 channel to 1")
            elif dev_name == "wifi1":
                new_lines.append("\toption channel '36'")
                print("Set wifi1 channel to 36")
            elif dev_name == "wifi2":
                new_lines.append("\toption channel '37'")
                print("Set wifi2 channel to 37")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    wireless_blocks.append("\n".join(new_lines))

members_data["etc/config/wireless"] = ("config wifi-device " + "config wifi-device ".join(wireless_blocks)).encode("utf-8")

# 6. Pack into new .cfg
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
with open(out_cfg, "wb") as f:
    f.write(compressed)

print(f"Generated {out_cfg} successfully! Size: {len(compressed)} bytes.")
