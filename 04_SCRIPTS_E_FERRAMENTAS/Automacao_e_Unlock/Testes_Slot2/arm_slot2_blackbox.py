import telnetlib, time, base64, hashlib, sys

print("="*65)
print("=== ARMANDO CAIXA-PRETA NO SLOT 2 COM UPLOAD CHUNKED E MD5 ===")
print("="*65)

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=10)
tn.read_until(b'login: ', 3)
tn.write(b'root\n')
tn.read_until(b'Password: ', 3)
tn.write(b'admin0100\n')
time.sleep(0.5)
tn.read_very_eager()

def run_cmd(c, wait=0.4):
    tn.write(c.encode('ascii') + b'\n')
    time.sleep(wait)
    out = b''
    while True:
        chunk = tn.read_very_eager()
        if not chunk:
            break
        out += chunk
        time.sleep(0.05)
    return out.decode('latin1', errors='replace').strip()

def send_file_chunked(content_bytes, remote_path):
    b64 = base64.b64encode(content_bytes).decode('ascii')
    local_md5 = hashlib.md5(content_bytes).hexdigest()
    chunk_size = 400
    run_cmd("rm -f /tmp/_upload.b64", 0.1)
    for i in range(0, len(b64), chunk_size):
        chunk = b64[i:i+chunk_size]
        run_cmd(f"printf '%s' '{chunk}' >> /tmp/_upload.b64", 0.05)
    run_cmd(f"base64 -d /tmp/_upload.b64 > {remote_path} && rm -f /tmp/_upload.b64", 0.2)
    remote_out = run_cmd(f"md5sum {remote_path}", 0.2)
    match = (local_md5 in remote_out)
    remote_md5 = [t for t in remote_out.split() if len(t) == 32 and all(ch in '0123456789abcdef' for ch in t.lower())]
    rem_str = remote_md5[0] if remote_md5 else "NOT_FOUND"
    print(f"  -> {remote_path}: Local={local_md5} | Remote={rem_str} | Match={'OK' if match else 'FAIL'}")
    if not match:
        raise RuntimeError(f"MD5 mismatch writing {remote_path}")

# 1. Montar Slot 2 em /tmp/s2
print("\n[1/5] Verificando montagem do Slot 2 (/dev/ubi1_3 em /tmp/s2)...")
run_cmd("grep -q /tmp/s2 /proc/mounts || { ubiattach -m 20 2>/dev/null; mkdir -p /tmp/s2; mount -t ubifs /dev/ubi1_3 /tmp/s2; }", 1.5)
print("  Mount:", run_cmd("grep /tmp/s2 /proc/mounts", 0.3))

# 2. Ler /rom/etc/rc.common do roteador via base64 chunked
print("\n[2/5] Lendo /rom/etc/rc.common e gerando rc.common instrumentado...")
run_cmd("base64 /rom/etc/rc.common > /tmp/_rom_rc_common.b64", 0.3)
raw_b64 = run_cmd("cat /tmp/_rom_rc_common.b64", 0.5)
run_cmd("rm -f /tmp/_rom_rc_common.b64", 0.1)

lines_b64 = [l.strip() for l in raw_b64.splitlines() if l.strip() and not l.startswith('cat ') and not l.startswith('/ #')]
clean_b64 = "".join(lines_b64)
rc_common_orig = base64.b64decode(clean_b64).decode('utf-8')

target = '$action "$@"'
if target not in rc_common_orig:
    print("ERRO: $action \"$@\" nao encontrado em /rom/etc/rc.common!")
    sys.exit(1)

logging_hook = '''if [ -f /ultimo_passo.log ]; then
\techo "[$(date +%T)] START: $initscript $action" >> /ultimo_passo.log 2>/dev/null
\tsync
fi

$action "$@"
_RC_RET=$?

if [ -f /ultimo_passo.log ]; then
\techo "[$(date +%T)] DONE($_RC_RET): $initscript $action" >> /ultimo_passo.log 2>/dev/null
\tsync
fi
'''

rc_common_mod = rc_common_orig.replace(target, logging_hook)
send_file_chunked(rc_common_mod.encode('utf-8'), "/tmp/s2/upper/etc/rc.common")
run_cmd("chmod 755 /tmp/s2/upper/etc/rc.common", 0.2)

# 3. Preparar rc.local limpo com heartbeat de fundo e serviços vitais
print("\n[3/5] Preparando rc.local com serviços vitais (dropbear, telnetd) e heartbeat...")
rc_local_clean = '''# Put your custom commands here that should be executed once
# the system init finished. By default this file does nothing.

if [ -f /ultimo_passo.log ]; then
    echo "[$(date +%T)] === CHEGOU EM RC.LOCAL COM SUCESSO! ===" >> /ultimo_passo.log
    sync
    (
        while true; do
            sleep 1
            UP=$(cat /proc/uptime 2>/dev/null | cut -d' ' -f1)
            MEM=$(cat /proc/meminfo 2>/dev/null | grep MemFree | awk '{print $2}')
            echo "[$(date +%T)] VIVO | Uptime: ${UP}s | MemFree: ${MEM}kB" >> /ultimo_passo.log
            sync
        done
    ) &
fi

/etc/init.d/uhttpd stop

if [ "$(uci -q get network.xlatd.disabled)" == "" ]; then
    uci set network.xlatd=interface
    uci set network.xlatd.proto='464xlat'
    uci set network.xlatd.tunlink='wan1'
    uci set network.xlatd.ip6prefix='64:ff9b::/96'
    uci set network.xlatd.disabled='1'
    uci commit network
fi

/etc/init.d/lighttpd/lighttpd.init start
/etc/init.d/sodd start 2>/dev/null

# Enable dropbear in UCI
uci set dropbear.@dropbear[0].enable='1' 2>/dev/null
uci commit dropbear 2>/dev/null

# Start Dropbear directly in background with RSA key
DROPBEAR=$(command -v dropbear || echo "/usr/sbin/dropbear")
[ -x "$DROPBEAR" ] && $DROPBEAR -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B

# Start Telnet daemon on port 23
TELNETD=$(command -v telnetd || echo "/usr/sbin/telnetd")
[ -x "$TELNETD" ] && $TELNETD -l /bin/ash

# Ensure crond is running and reload
/etc/init.d/cron restart 2>/dev/null

/usr/sbin/uhttpd -p 8080 -h /www -x /cgi-bin
sysctl -w net.bridge.bridge-nf-call-ip6tables=0
sysctl -w net.bridge.bridge-nf-call-iptables=0
sysctl -w net.bridge.bridge-nf-call-arptables=0
sysctl -w net.ipv6.conf.all.accept_ra=2
sysctl -w net.ipv6.conf.default.accept_ra=2
sysctl -w net.ipv6.conf.br-lan.accept_ra=2

echo 1 > /sys/class/net/mld0/bonding/all_slaves_active 2>/dev/null
echo 2 > /sys/class/net/eth0/brport/multicast_router 2>/dev/null
echo 2 > /sys/class/net/mld0/brport/multicast_router 2>/dev/null
echo 0 > /proc/sys/net/ipv6/conf/eth0/disable_ipv6 2>/dev/null
exit 0
'''

send_file_chunked(rc_local_clean.encode('utf-8'), "/tmp/s2/upper/etc/rc.local")
run_cmd("chmod 755 /tmp/s2/upper/etc/rc.local", 0.2)

# 4. Inicializar /ultimo_passo.log limpo
print("\n[4/5] Inicializando /ultimo_passo.log limpo...")
run_cmd("printf '=== INICIO DO BOOT DO SLOT 2 ===\\n' > /tmp/s2/upper/ultimo_passo.log", 0.2)
run_cmd("chmod 666 /tmp/s2/upper/ultimo_passo.log", 0.2)
print("  Log inicial:", run_cmd("cat /tmp/s2/upper/ultimo_passo.log", 0.2))

# 5. Sincronizar e desmontar
print("\n[5/5] Sincronizando e desmontando Slot 2...")
run_cmd("sync", 1.0)
run_cmd("umount /tmp/s2", 1.0)
run_cmd("ubidetach -d 1 2>/dev/null", 0.5)
print("  Dispositivos UBI ativos:", run_cmd("ls -d /dev/ubi*", 0.3))

tn.close()
print("\n" + "="*65)
print(">>> CAIXA-PRETA DO SLOT 2 ARMADA COM 100% DE SUCESSO E MD5 CONFIRMADO! <<<")
print("="*65)
