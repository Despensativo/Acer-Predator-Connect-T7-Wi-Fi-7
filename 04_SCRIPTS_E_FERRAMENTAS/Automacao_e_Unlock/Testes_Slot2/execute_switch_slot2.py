import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.73.2', port=22, username='root', password='admin0100', timeout=5, look_for_keys=False, allow_agent=False)

def run(cmd):
    _, out, err = ssh.exec_command(cmd)
    o = out.read().decode('latin1', errors='ignore').strip()
    e = err.read().decode('latin1', errors='ignore').strip()
    print(f'$ {cmd}')
    if o: print(o)
    if e: print('[stderr]', e)
    return o

print("=== 1. CONFIGURANDO FSBOOTARGS NO U-BOOT ENV PARA SLOT 2 ===")
run('fw_setenv fsbootargs "ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs"')
run('fw_printenv fsbootargs')

print("\n=== 2. CONFIGURANDO BOOTCONFIG PARA SLOT 2 (primaryboot=0) ===")
run('echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot')
run('echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot')
run('cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin')
run('cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin')
run('mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3')
run('mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4')
run('rm -f /tmp/bc0.bin /tmp/bc1.bin')
run('sync')

print("\n=== 3. CHAVEAMENTO CONCLUIDO! DISPARANDO REBOOT DO ROTEADOR ===")
ssh.exec_command('reboot')
ssh.close()
print("[+] Comando de reboot enviado! O roteador está reiniciando agora no Slot 2.")
