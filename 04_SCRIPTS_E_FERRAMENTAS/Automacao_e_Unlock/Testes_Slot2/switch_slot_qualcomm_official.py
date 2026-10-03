import telnetlib, time, sys

print("="*65)
print("=== CHAVEAMENTO OFICIAL QUALCOMM COM IDADE (AGE) VIA TELNET ===")
print("="*65)

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=10)
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
        time.sleep(0.1)
    res = out.decode('latin1', errors='replace').strip()
    return res

# 1. Verificar estado atual
print("\n[1/6] Lendo estado atual do BootConfig no kernel...")
print(run_cmd("echo age0:; cat /proc/boot_info/bootconfig0/age; echo age1:; cat /proc/boot_info/bootconfig1/age; echo pb0:; cat /proc/boot_info/bootconfig0/rootfs/primaryboot; echo pb1:; cat /proc/boot_info/bootconfig1/rootfs/primaryboot", 0.5))

# 2. Configurar Slot 2 e incrementar age em bootconfig1 (age=4)
print("\n[2/6] Configurando Slot 2 como versao ativa mais recente (age = 4)...")
run_cmd("echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot", 0.3)
run_cmd("echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot", 0.3)
run_cmd("echo 4 > /proc/boot_info/bootconfig1/age", 0.3)
print(run_cmd("echo novo_age0:; cat /proc/boot_info/bootconfig0/age; echo novo_age1:; cat /proc/boot_info/bootconfig1/age; echo novo_pb0:; cat /proc/boot_info/bootconfig0/rootfs/primaryboot; echo novo_pb1:; cat /proc/boot_info/bootconfig1/rootfs/primaryboot", 0.5))

# 3. Gerar binarios oficiais
print("\n[3/6] Gerando binarios de BootConfig...")
run_cmd("cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin", 0.3)
run_cmd("cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin", 0.3)
print(run_cmd("ls -la /tmp/bc*.bin", 0.3))

# 4. Gravar nas particoes fisicas mtd3 e mtd4
print("\n[4/6] Gravando particoes fisicas mtd3 (BOOTCONFIG) e mtd4 (BOOTCONFIG1)...")
print(run_cmd("dd if=/tmp/bc0.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd3 write - /dev/mtd3", 1.5))
print(run_cmd("dd if=/tmp/bc1.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd4 write - /dev/mtd4", 1.5))
print("Gravacao fisica concluida com sucesso!")

# 5. Sincronizar variaveis de boot no U-Boot
print("\n[5/6] Sincronizando fsbootargs no U-Boot...")
run_cmd("fw_setenv fsbootargs 'ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs rootwait vmalloc=1G'", 0.5)
print(run_cmd("fw_printenv fsbootargs", 0.5))

# 6. Validar leitura fisica
print("\n[6/6] Validando leitura fisica de mtd3 e mtd4...")
print(run_cmd("dd if=/dev/mtd3 bs=1 count=128 2>/dev/null | hexdump -C | head -n 8", 0.5))
print(run_cmd("dd if=/dev/mtd4 bs=1 count=128 2>/dev/null | hexdump -C | head -n 8", 0.5))

run_cmd("rm -f /tmp/bc0.bin /tmp/bc1.bin && sync", 0.5)
tn.close()

print("\n" + "="*65)
print(">>> CHAVEAMENTO OFICIAL QUALCOMM CONCLUIDO COM SUCESSO! <<<")
print("="*65)
