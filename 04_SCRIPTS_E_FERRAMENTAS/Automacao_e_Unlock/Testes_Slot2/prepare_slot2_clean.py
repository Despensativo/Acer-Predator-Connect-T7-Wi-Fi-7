import telnetlib, time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
tn.read_until(b'login: ', 3)
tn.write(b'root\n')
tn.read_until(b'Password: ', 3)
tn.write(b'admin0100\n')
time.sleep(0.5)
tn.read_very_eager()

def run_cmd(cmd, delay=0.5):
    tn.write(cmd.encode('ascii') + b'\n')
    time.sleep(delay)
    return tn.read_very_eager().decode('utf-8', errors='replace')

print("1. Anexando Slot 2 (MTD 20) como UBI...")
print(run_cmd("ubiattach -m 20 2>/dev/null || true", 1))

print("2. Verificando volumes em ubi1...")
print(run_cmd("ubinfo /dev/ubi1", 0.5))

print("3. Montando /overlay do Slot 1 e Slot 2...")
run_cmd("mkdir -p /tmp/s1_overlay /tmp/s2_overlay")
run_cmd("mount --bind /overlay /tmp/s1_overlay")
print(run_cmd("mount -t ubifs /dev/ubi1_3 /tmp/s2_overlay", 1))

print("4. Copiando /overlay do Slot 1 para o Slot 2 (sincronizacao limpa)...")
# Limpar /tmp/s2_overlay para remover arquivos modificados anteriores
run_cmd("rm -rf /tmp/s2_overlay/*")
# Copiar tudo de /tmp/s1_overlay para /tmp/s2_overlay preservando permissoes
print(run_cmd("cp -a /tmp/s1_overlay/* /tmp/s2_overlay/", 3))
print(run_cmd("sync", 1))

print("5. Verificando copia no Slot 2...")
print(run_cmd("ls -la /tmp/s2_overlay/upper/etc/config/network /tmp/s2_overlay/upper/etc/shadow", 0.5))
print(run_cmd("cat /tmp/s2_overlay/upper/etc/config/network | grep -E 'ipaddr|gateway'", 0.5))

print("6. Desmontando...")
run_cmd("umount /tmp/s1_overlay 2>/dev/null || true")
run_cmd("umount /tmp/s2_overlay 2>/dev/null || true")
run_cmd("ubidetach -m 20 2>/dev/null || true")

print("7. Configurando fsbootargs completo com vmalloc=1G...")
print(run_cmd('fw_setenv fsbootargs "ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs vmalloc=1G"'))
print(run_cmd("fw_printenv fsbootargs"))
print(run_cmd("fw_printenv bootcmd"))

tn.close()
print("Concluido!")
