import telnetlib, time

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=30)
tn.read_until(b'login: ', 3)
tn.write(b'root\n')
tn.read_until(b'Password: ', 3)
tn.write(b'admin0100\n')
tn.read_until(b'#', 3)

def cmd(c, wait=0.5):
    tn.write(c.encode('ascii') + b'\n')
    time.sleep(wait)
    return tn.read_until(b'#', 20).decode()

print("1. Anexando ubi1...")
cmd('ubiattach -m 20 2>/dev/null || true')

print("2. Formatando volume ubi1_3 (rootfs_data)...")
cmd('umount /tmp/chk 2>/dev/null || true')
# Truncate / clean volume
cmd('ubiupdatevol -t /dev/ubi1_3')

print("3. Formatando UBIFS em ubi1_3 e montando...")
cmd('mkdir -p /tmp/chk')
# Ao montar um volume UBI truncado pela primeira vez, o Linux formata UBIFS automaticamente
print(cmd('mount -t ubifs /dev/ubi1_3 /tmp/chk', 1))

print("4. Criando estrutura perfeita do OverlayFS...")
cmd('mkdir -p /tmp/chk/upper/etc/config')
cmd('mkdir -p /tmp/chk/work')
cmd('chmod 755 /tmp/chk/work')

print("5. Copiando configuracoes essenciais do Slot 1...")
cmd('cp -a /overlay/upper/etc/shadow /tmp/chk/upper/etc/shadow')
cmd('cp -a /overlay/upper/etc/config/network /tmp/chk/upper/etc/config/network')
cmd('cp -a /overlay/upper/etc/config/wireless /tmp/chk/upper/etc/config/wireless')
cmd('sync')

print("6. Verificando estrutura em /tmp/chk...")
print(cmd('ls -la /tmp/chk /tmp/chk/upper/etc /tmp/chk/upper/etc/config'))
print(cmd('cat /tmp/chk/upper/etc/config/network | grep -E "ipaddr|gateway"'))

print("7. Desmontando...")
cmd('umount /tmp/chk')
cmd('ubidetach -m 20 2>/dev/null || true')

tn.close()
print("Setup de overlay do Slot 2 concluido com sucesso!")
