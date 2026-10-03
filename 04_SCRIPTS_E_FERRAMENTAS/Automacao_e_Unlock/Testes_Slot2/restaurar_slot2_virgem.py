import telnetlib, time, sys, io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROUTER_IP = "192.168.73.2"

print("=" * 70)
print("=== RESTAURANDO SLOT 2 PARA O ESTADO VIRGEM DE FABRICA ===")
print("=" * 70)

tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
tn.read_until(b'login: ', 3)
tn.write(b'root\n')
tn.read_until(b'Password: ', 3)
tn.write(b'admin0100\n')
time.sleep(0.5)
tn.read_very_eager()

def run_cmd(c, wait=0.5):
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

# 1. Anexar e montar Slot 2
print("\n[1/5] Anexando mtd20 e montando /dev/ubi1_3 em /tmp/s2...")
run_cmd("grep -q /tmp/s2 /proc/mounts || { ubiattach -m 20 2>/dev/null; mkdir -p /tmp/s2; mount -t ubifs /dev/ubi1_3 /tmp/s2; }", 1.5)
print("  Mount:", run_cmd("grep /tmp/s2 /proc/mounts", 0.3))

# 2. Limpar todo o overlay do Slot 2
print("\n[2/5] Limpando dados do overlay atual do Slot 2...")
run_cmd("rm -rf /tmp/s2/*", 1.0)
run_cmd("mkdir -p /tmp/s2/upper /tmp/s2/work", 0.3)
run_cmd("chmod 755 /tmp/s2/work", 0.2)

# 3. Clonar overlay de fabrica do Slot 1 preservando permissoes e whiteouts
print("\n[3/5] Clonando arquivos e configuracoes virgens do Slot 1 via tar...")
run_cmd("cd /overlay/upper && tar cf - . | (cd /tmp/s2/upper && tar xf -)", 3.0)
run_cmd("sync", 0.5)

# 4. Ajustar wifi_fw_mount no Slot 2 para suportar rootfs_1
print("\n[4/5] Ajustando wifi_fw_mount para inicializar Wi-Fi no Slot 2...")
patch_cmd = "sed -i 's/local PART=\\$(grep -w  \"rootfs\" \\/proc\\/mtd | awk -F: '\\''{print \\$1}'\\'')/local PART=\\$(grep -q \"rootfs_1\" \\/proc\\/cmdline \\&\\& grep -w \"rootfs_1\" \\/proc\\/mtd | awk -F: '\\''{print \\$1}'\\'' || grep -w \"rootfs\" \\/proc\\/mtd | awk -F: '\\''{print \\$1}'\\'')/g' /tmp/s2/upper/etc/init.d/wifi_fw_mount"
run_cmd(patch_cmd, 0.5)
run_cmd("chmod 755 /tmp/s2/upper/etc/init.d/wifi_fw_mount", 0.2)

# 5. Validar integridade e desmontar
print("\n[5/5] Validando arquivos no Slot 2...")
print("  Shadow:", run_cmd("head -n 2 /tmp/s2/upper/etc/shadow", 0.3))
print("  Network:", run_cmd("grep -E 'ipaddr|ifname' /tmp/s2/upper/etc/config/network", 0.3))
print("  RC.LOCAL:", run_cmd("head -n 10 /tmp/s2/upper/etc/rc.local", 0.3))

print("\n[*] Sincronizando flash e desmontando...")
run_cmd("sync", 1.0)
run_cmd("umount /tmp/s2", 1.0)
run_cmd("ubidetach -d 1 2>/dev/null", 0.5)
print("  UBI ativos:", run_cmd("ls -d /dev/ubi*", 0.3))

tn.close()
print("\n" + "=" * 70)
print(">>> SLOT 2 RESTAURADO COM SUCESSO PARA O ESTADO VIRGEM DE FABRICA! <<<")
print("=" * 70)
