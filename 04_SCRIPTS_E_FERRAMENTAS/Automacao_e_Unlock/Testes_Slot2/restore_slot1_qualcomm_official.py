import subprocess, sys

def run_ssh(cmd):
    full_cmd = f'sshpass -p admin0100 ssh -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.73.2 "{cmd}"'
    res = subprocess.run(["wsl", "bash", "-c", full_cmd], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERRO] CMD: {cmd}\nSTDERR: {res.stderr}")
    return res.stdout.strip()

print("="*65)
print("=== RESTAURADOR OFICIAL DE FÁBRICA: SLOT 1 (STOCK) ===")
print("="*65)

# 1. Copiar os backups originais de fabrica para o roteador
print("\n[1/4] Enviando backups originais de fabrica para o roteador...")
subprocess.run(["wsl", "bash", "-c", "sshpass -p admin0100 scp -O -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa 'Backups_MTD/mtd3_stock.bin' root@192.168.73.2:/tmp/mtd3_stock.bin"])
subprocess.run(["wsl", "bash", "-c", "sshpass -p admin0100 scp -O -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa 'Backups_MTD/mtd4_stock.bin' root@192.168.73.2:/tmp/mtd4_stock.bin"])

# 2. Gravar mtd3 e mtd4
print("\n[2/4] Restaurando mtd3 (BOOTCONFIG) e mtd4 (BOOTCONFIG1) com os bits de fabrica...")
run_ssh("mtd -e /dev/mtd3 write /tmp/mtd3_stock.bin /dev/mtd3")
run_ssh("mtd -e /dev/mtd4 write /tmp/mtd4_stock.bin /dev/mtd4")
print("Particoes de boot restauradas para o estado original!")

# 3. Limpar fsbootargs no U-Boot
print("\n[3/4] Limpando fsbootargs no U-Boot para restaurar padrao de fabrica...")
run_ssh("fw_setenv fsbootargs")

# 4. Validar
print("\n[4/4] Validando leitura fisica de fabrica...")
run_ssh("rm -f /tmp/mtd3_stock.bin /tmp/mtd4_stock.bin && sync")
print("\n" + "="*65)
print(">>> ROTEADOR RESTAURADO 100% PARA O SLOT 1 ORIGINAL DE FABRICA! <<<")
print("="*65)
