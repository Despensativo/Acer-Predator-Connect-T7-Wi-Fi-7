import telnetlib, time, sys, socket, io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROUTER_IP = "192.168.73.2"

print("=" * 70)
print("=== CHAVEAMENTO OFICIAL QUALCOMM E DIAGNOSTICO AUTOMATICO ===")
print("=" * 70)

def connect_telnet(ip, timeout=5):
    try:
        tn = telnetlib.Telnet(ip, 23, timeout=timeout)
        idx, _, _ = tn.expect([b'login: ', b'/ # '], timeout=3)
        if idx == 0:
            tn.write(b'root\n')
            tn.read_until(b'Password: ', timeout=3)
            tn.write(b'admin0100\n')
            time.sleep(0.3)
        tn.read_very_eager()
        return tn
    except Exception as e:
        return None

def run_cmd(tn, c, wait=0.5):
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

# 1. Conectar e aplicar chaveamento oficial
print("\n[Passo 1/4] Conectando ao roteador para aplicar chaveamento oficial...")
tn = connect_telnet(ROUTER_IP, 10)
if not tn:
    print(f"[-] Nao foi possivel conectar a {ROUTER_IP}:23")
    sys.exit(1)

print("  -> Lendo estado atual do BootConfig:")
print("    " + run_cmd(tn, "echo age0=$(cat /proc/boot_info/bootconfig0/age) age1=$(cat /proc/boot_info/bootconfig1/age) pb=$(cat /proc/boot_info/bootconfig0/rootfs/primaryboot)", 0.3))

print("  -> Configurando Slot 2 (primaryboot=0, age1=4)...")
run_cmd(tn, "echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot", 0.2)
run_cmd(tn, "echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot", 0.2)
run_cmd(tn, "echo 4 > /proc/boot_info/bootconfig1/age", 0.2)

print("  -> Gerando e gravando binarios nas particoes fisicas mtd3 e mtd4...")
run_cmd(tn, "cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin", 0.2)
run_cmd(tn, "cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin", 0.2)
run_cmd(tn, "dd if=/tmp/bc0.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd3 write - /dev/mtd3", 1.5)
run_cmd(tn, "dd if=/tmp/bc1.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd4 write - /dev/mtd4", 1.5)

print("  -> Ajustando fsbootargs no U-Boot para rootfs_1...")
run_cmd(tn, "fw_setenv fsbootargs 'ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs rootwait vmalloc=1G'", 0.3)
run_cmd(tn, "rm -f /tmp/bc0.bin /tmp/bc1.bin && sync", 0.2)

print("\n[Passo 2/4] Disparando REBOOT...")
tn.write(b"sync && reboot\n")
time.sleep(1)
try:
    tn.close()
except:
    pass

print("[+] Comando de reboot enviado. Aguardando a placa reiniciar...")

# 2. Aguardar a placa desligar
t0 = time.time()
time.sleep(2)

print("\n[Passo 3/4] Monitorando inicializacao...")
online_ip = None
online_port = None

for sec in range(1, 120):
    time.sleep(1)
    for ip in ["192.168.73.2", "192.168.1.1"]:
        for port in [23, 22, 8080]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.2)
                res = s.connect_ex((ip, port))
                s.close()
                if res == 0:
                    online_ip = ip
                    online_port = port
                    break
            except:
                pass
        if online_ip:
            break
    if online_ip:
        print(f"\n[+] DETECTADO! Porta {online_port} aberta em {online_ip} aos {sec}s!")
        break
    sys.stdout.write(f"\r  [{sec:02d}s] Aguardando boot do chip e carregamento dos servicos...")
    sys.stdout.flush()

if not online_ip:
    print("\n[-] Timeout: nenhuma porta respondeu apos 120 segundos.")
    sys.exit(1)

# Aguarda 3 segundos para estabilizar servicos
print("\n[Passo 4/4] Analisando o estado pos-boot...")
time.sleep(3)

tn2 = connect_telnet(online_ip, 10)
if not tn2:
    print(f"[-] Nao foi possivel abrir sessao Telnet em {online_ip}")
    sys.exit(1)

mounts = run_cmd(tn2, "grep ubi /proc/mounts", 0.5)
slot_info = run_cmd(tn2, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot 2>/dev/null", 0.3)

print("=" * 70)
if "ubi1_3" in mounts or "rootfs_1" in mounts:
    print(">>> SUCESSO TOTAL! O ROTEADOR ESTA RODANDO NO SLOT 2! <<<")
    print(f"Montagens ativas:\n{mounts}")
    print("\nVerificando uptime e log da caixa-preta:")
    print(run_cmd(tn2, "cat /ultimo_passo.log 2>/dev/null | tail -n 25", 0.5))
else:
    print(">>> O ROTEADOR REINICIOU E VOLTOU PARA O SLOT 1! <<<")
    print(f"Particao atual: Slot 1 (primaryboot = {slot_info})")
    print("\n[*] Lendo a CAIXA-PRETA gravada no Slot 2 para descobrir o culpado exato:")
    run_cmd(tn2, "grep -q /tmp/s2 /proc/mounts || { ubiattach -m 20 2>/dev/null; mkdir -p /tmp/s2; mount -t ubifs /dev/ubi1_3 /tmp/s2; }", 1.5)
    log_content = run_cmd(tn2, "cat /tmp/s2/upper/ultimo_passo.log 2>/dev/null", 0.8)
    print("-" * 70)
    print(log_content)
    print("-" * 70)
    print("[*] Desmontando Slot 2...")
    run_cmd(tn2, "sync && umount /tmp/s2 && ubidetach -d 1 2>/dev/null", 0.5)

tn2.close()
print("=" * 70)
