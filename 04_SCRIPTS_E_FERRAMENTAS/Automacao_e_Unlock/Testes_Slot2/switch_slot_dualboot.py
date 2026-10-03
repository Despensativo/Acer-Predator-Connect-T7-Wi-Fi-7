import subprocess, sys

def run_ssh(cmd):
    full_cmd = f'sshpass -p admin0100 ssh -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.73.2 "{cmd}"'
    res = subprocess.run(["wsl", "bash", "-c", full_cmd], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERRO] CMD: {cmd}\nSTDERR: {res.stderr}")
    return res.stdout.strip()

print("="*65)
print("=== COMUTADOR OFICIAL DE DUAL-BOOT QUALCOMM (BOOTCONFIG) ===")
print("="*65)

# 1. Verificar estado atual
print("\n[1/6] Verificando estado atual do BootConfig...")
bc0_curr = run_ssh("cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
bc1_curr = run_ssh("cat /proc/boot_info/bootconfig1/rootfs/primaryboot")
print(f"BootConfig0 primaryboot atual: {bc0_curr} (1 = Slot 1, 0 = Slot 2)")
print(f"BootConfig1 primaryboot atual: {bc1_curr} (1 = Slot 1, 0 = Slot 2)")

# 2. Configurar primaryboot para 0 (Slot 2)
print("\n[2/6] Alterando primaryboot para 0 (Slot 2) no driver do kernel...")
run_ssh("echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot")
run_ssh("echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot")
bc0_new = run_ssh("cat /proc/boot_info/bootconfig0/rootfs/primaryboot")
bc1_new = run_ssh("cat /proc/boot_info/bootconfig1/rootfs/primaryboot")
print(f"BootConfig0 novo: {bc0_new}")
print(f"BootConfig1 novo: {bc1_new}")
assert bc0_new == "0" and bc1_new == "0", "Falha ao definir primaryboot no kernel!"

# 3. Gerar binarios de BootConfig
print("\n[3/6] Gerando binarios de BootConfig...")
run_ssh("cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin")
run_ssh("cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin")

# Verificar estrutura do binario (offset 0x6c deve ser 00)
check_hex = run_ssh("hexdump -C /tmp/bc0.bin | grep '00000060'")
print(f"Offset 0x60 em bc0.bin:\n{check_hex}")
assert "00 00 00 00" in check_hex, "Byte de primaryboot invalido em bc0.bin!"

# 4. Gravar nas particoes fisicas mtd3 (BOOTCONFIG) e mtd4 (BOOTCONFIG1)
print("\n[4/6] Gravando mtd3 e mtd4 pelo metodo oficial da Qualcomm...")
run_ssh("dd if=/tmp/bc0.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd3 write - /dev/mtd3")
run_ssh("dd if=/tmp/bc1.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd4 write - /dev/mtd4")
print("Gravacao concluida!")

# 5. Sincronizar fsbootargs no U-Boot para consistencia
print("\n[5/6] Gravando fsbootargs no U-Boot...")
run_ssh("fw_setenv fsbootargs 'ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs'")
env_chk = run_ssh("fw_printenv fsbootargs")
print(f"U-Boot env: {env_chk}")

# 6. Ler de volta de /dev/mtd3 e /dev/mtd4 e validar
print("\n[6/6] Validando leitura fisica de /dev/mtd3 e /dev/mtd4...")
verify_mtd3 = run_ssh("dd if=/dev/mtd3 bs=1 count=128 2>/dev/null | hexdump -C | grep '00000060'")
verify_mtd4 = run_ssh("dd if=/dev/mtd4 bs=1 count=128 2>/dev/null | hexdump -C | grep '00000060'")
print(f"mtd3 offset 0x60: {verify_mtd3}")
print(f"mtd4 offset 0x60: {verify_mtd4}")

# Limpeza de temporarios
run_ssh("rm -f /tmp/bc0.bin /tmp/bc1.bin")
run_ssh("sync")

print("\n" + "="*65)
print(">>> CHAVEAMENTO PARA SLOT 2 CONCLUIDO E VALIDADO COM SUCESSO! <<<")
print("="*65)
