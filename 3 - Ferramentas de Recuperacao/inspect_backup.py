import gzip
import tarfile

with gzip.open(r"C:\Users\User\Downloads\config(1).cfg", "rb") as f:
    with tarfile.open(fileobj=f) as t:
        files = {m.name: t.extractfile(m).read().decode("utf-8", errors="ignore") for m in t.getmembers() if m.isfile()}

print(f"Total files in config(1).cfg: {len(files)}")

print("\n" + "="*50)
print("1. NETWORK (etc/config/network)")
print("="*50)
if "etc/config/network" in files:
    for block in files["etc/config/network"].split("config interface "):
        first_line = block.splitlines()[0] if block.splitlines() else ""
        if any(target in first_line for target in ["'lan'", "'wan'"]):
            print(f"config interface {block.strip()}\n")

print("="*50)
print("2. DHCP (etc/config/dhcp)")
print("="*50)
if "etc/config/dhcp" in files:
    for block in files["etc/config/dhcp"].split("config dhcp "):
        first_line = block.splitlines()[0] if block.splitlines() else ""
        if "'lan'" in first_line:
            print(f"config dhcp {block.strip()}\n")

print("="*50)
print("3. TRIPLEBAND (etc/config/tripleband)")
print("="*50)
if "etc/config/tripleband" in files:
    print(files["etc/config/tripleband"].strip())

print("\n" + "="*50)
print("4. RC.LOCAL (etc/rc.local)")
print("="*50)
if "etc/rc.local" in files:
    print(files["etc/rc.local"].strip())
else:
    print("etc/rc.local NOT FOUND in archive")

print("\n" + "="*50)
print("5. DROPBEAR (etc/config/dropbear)")
print("="*50)
if "etc/config/dropbear" in files:
    print(files["etc/config/dropbear"].strip())

print("\n" + "="*50)
print("6. WIRELESS (etc/config/wireless)")
print("="*50)
if "etc/config/wireless" in files:
    w = files["etc/config/wireless"]
    # Radios
    for block in w.split("config wifi-device "):
        if block.startswith("'"):
            dev_name = block.splitlines()[0]
            options = [l.strip() for l in block.splitlines() if any(k in l for k in ["channel", "htmode", "txpower", "country", "psc", "blockdfs"])]
            print(f"RADIO wifi-device {dev_name}")
            for opt in options:
                print(f"   {opt}")
    print("\nINTERFACES:")
    for block in w.split("config wifi-iface"):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        opts = {}
        for l in lines:
            if l.startswith("option"):
                parts = l.split(None, 2)
                if len(parts) >= 3:
                    opts[parts[1]] = parts[2]
        if "device" in opts:
            print(f"  Device: {opts.get('device'):8} SSID: {opts.get('ssid', 'N/A'):20} Disabled: {opts.get('disabled', '0'):3} Net: {opts.get('network', 'N/A')}")
    print("\nMLD:")
    for block in w.split("config wifi-mld "):
        if block.startswith("'"):
            print("config wifi-mld " + block.strip())
