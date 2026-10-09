import telnetlib, time, sys, socket, io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROUTER_IP = "192.168.73.2"

print("=" * 70)
print("=== CHAVEANDO PARA SLOT 2 VIRGEM E DISPARANDO REBOOT ===")
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

# 1. Configurar BootConfig para Slot 2 (primaryboot = 0)
print("\n[1/3] Configurando BootConfig para Slot 2 (primaryboot = 0)...")
run_cmd("echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot", 0.2)
run_cmd("echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot", 0.2)

run_cmd("cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin", 0.2)
run_cmd("cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin", 0.2)

print("  Gravando mtd3 e mtd4...")
run_cmd("dd if=/tmp/bc0.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd3 write - /dev/mtd3", 1.5)
run_cmd("dd if=/tmp/bc1.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd4 write - /dev/mtd4", 1.5)
run_cmd("rm -f /tmp/bc0.bin /tmp/bc1.bin", 0.2)

# 2. Configurar fsbootargs no U-Boot para carregar rootfs_1
print("\n[2/3] Configurando fsbootargs no U-Boot...")
run_cmd("fw_setenv fsbootargs 'ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs'", 0.5)
print("  U-Boot fsbootargs:", run_cmd("fw_printenv fsbootargs", 0.3))

# 3. Disparar reboot
print("\n[3/3] Sincronizando flash e enviando REBOOT...")
run_cmd("sync", 1.0)
tn.write(b"reboot\n")
time.sleep(1)
try:
    tn.close()
except:
    pass

print("[+] Comando de reboot enviado! Monitorando subida do Slot 2 virgem...")
print("    (Monitorando 192.168.73.2 e 192.168.1.1 nas portas 80, 443, 22, 23)...")

t0 = time.time()
time.sleep(3)

found_target = None
found_port = None

for sec in range(1, 150):
    time.sleep(1)
    for ip in ["192.168.73.2", "192.168.1.1"]:
        for port in [80, 443, 23, 22]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.2)
                res = s.connect_ex((ip, port))
                s.close()
                if res == 0:
                    found_target = ip
                    found_port = port
                    break
            except:
                pass
        if found_target:
            break
    if found_target:
        print(f"\n\n[+] RESPOSTA DETECTADA! {found_target}:{found_port} respondeu aos {sec}s de boot!")
        break
    sys.stdout.write(f"\r  [{sec:02d}s] Aguardando descompressao do kernel e inicializacao virgem...")
    sys.stdout.flush()

if found_target:
    print("\n" + "=" * 70)
    print(f">>> SUCESSO! ROTEADOR ONLINE EM {found_target}:{found_port} <<<")
    print("=" * 70)
else:
    print("\n[-] Timeout de 150s sem conexao em 192.168.73.2 ou 192.168.1.1.")
