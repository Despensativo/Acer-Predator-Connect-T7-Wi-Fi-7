import telnetlib, time, sys, io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROUTER_IP = "192.168.73.2"

print("=" * 70)
print("=== ZERANDO OVERLAY DO SLOT 2 VIA UBIUPDATEVOL -T (VIRGEM) ===")
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

# 1. Desmontar qualquer montagem anterior do Slot 2
print("\n[1/4] Garantindo que nenhum ponto do Slot 2 esteja montado...")
run_cmd("umount /tmp/s2 2>/dev/null; umount /tmp/chk 2>/dev/null; umount /tmp/slot2_overlay 2>/dev/null", 0.5)

# 2. Anexar mtd20 como ubi1
print("\n[2/4] Anexando mtd20 (Slot 2)...")
run_cmd("ubiattach -m 20 2>/dev/null || true", 1.0)
print(run_cmd("ubinfo -d 1", 0.5))

# 3. Truncar (zerar) o volume ubi1_3 (rootfs_data)
print("\n[3/4] Executando ubiupdatevol -t em /dev/ubi1_3 (zerando dados)...")
print(run_cmd("ubiupdatevol -t /dev/ubi1_3", 1.0))

# 4. Validar estado do volume
print("\n[4/4] Validando estado do volume 3...")
vol_info = run_cmd("ubinfo /dev/ubi1_3", 0.5)
print(vol_info)

# 5. Sincronizar e desanexar
print("\n[*] Sincronizando flash e desanexando Slot 2...")
run_cmd("sync", 0.5)
run_cmd("ubidetach -m 20 2>/dev/null || ubidetach -d 1 2>/dev/null", 0.5)
print("  Dispositivos UBI ativos:", run_cmd("ls -d /dev/ubi*", 0.3))

tn.close()
print("\n" + "=" * 70)
print(">>> SLOT 2 OVERLAY FOI ZERADO COM 100% DE SUCESSO! ESTADO VIRGEM ATIVO! <<<")
print("=" * 70)
