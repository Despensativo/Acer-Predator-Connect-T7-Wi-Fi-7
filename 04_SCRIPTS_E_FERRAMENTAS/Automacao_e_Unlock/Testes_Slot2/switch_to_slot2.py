import time
import telnetlib
import sys

def run_cmd(tn, cmd, timeout=10):
    tn.write(cmd.encode("utf-8") + b"\n")
    out = tn.read_until(b"/ # ", timeout=timeout).decode("latin1", errors="replace")
    return out

def main():
    print("="*65)
    print("=== CHAVEANDO PARA O SLOT 2 E REINICIANDO ===")
    print("="*65)

    tn = telnetlib.Telnet("192.168.73.2", 23, timeout=5)
    tn.read_until(b"login: ", timeout=3)
    tn.write(b"root\n")
    tn.read_until(b"Password: ", timeout=3)
    tn.write(b"admin0100\n")
    tn.read_until(b"/ # ", timeout=3)

    print("\n[1/6] Configurando primaryboot=0 no driver do kernel...")
    run_cmd(tn, "echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot")
    run_cmd(tn, "echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot")
    bc0 = run_cmd(tn, "cat /proc/boot_info/bootconfig0/rootfs/primaryboot").strip()
    bc1 = run_cmd(tn, "cat /proc/boot_info/bootconfig1/rootfs/primaryboot").strip()
    print(f"Driver state: bc0={bc0}, bc1={bc1}")

    print("\n[2/6] Gerando binarios de BootConfig...")
    run_cmd(tn, "cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin")
    run_cmd(tn, "cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin")

    chk_hex = run_cmd(tn, "hexdump -C /tmp/bc0.bin | grep '00000060'")
    print(f"Hexdump 0x60 em bc0.bin:\n{chk_hex.strip()}")

    print("\n[3/6] Gravando em mtd3 (BOOTCONFIG) e mtd4 (BOOTCONFIG1)...")
    out_mtd3 = run_cmd(tn, "dd if=/tmp/bc0.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd3 write - /dev/mtd3")
    print(f"mtd3 write: {out_mtd3.strip()}")
    out_mtd4 = run_cmd(tn, "dd if=/tmp/bc1.bin bs=4096 conv=sync 2>/dev/null | mtd -e /dev/mtd4 write - /dev/mtd4")
    print(f"mtd4 write: {out_mtd4.strip()}")

    print("\n[4/6] Configurando fsbootargs no U-Boot...")
    run_cmd(tn, "fw_setenv fsbootargs 'ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs'")
    env_chk = run_cmd(tn, "fw_printenv fsbootargs")
    print(f"U-Boot env: {env_chk.strip()}")

    print("\n[5/6] Validando leitura fisica de mtd3 e mtd4...")
    v_mtd3 = run_cmd(tn, "dd if=/dev/mtd3 bs=1 count=128 2>/dev/null | hexdump -C | grep '00000060'")
    v_mtd4 = run_cmd(tn, "dd if=/dev/mtd4 bs=1 count=128 2>/dev/null | hexdump -C | grep '00000060'")
    print(f"mtd3 verif: {v_mtd3.strip()}")
    print(f"mtd4 verif: {v_mtd4.strip()}")

    run_cmd(tn, "rm -f /tmp/bc0.bin /tmp/bc1.bin")
    run_cmd(tn, "sync")

    print("\n[6/6] Enviando comando reboot...")
    try:
        tn.write(b"sync && reboot\n")
        time.sleep(1)
        tn.close()
    except Exception as e:
        print(f"Conexao encerrada durante o reboot: {e}")

    print("\n" + "="*65)
    print(">>> COMANDO DE REBOOT ENVIADO COM SUCESSO! <<<")
    print("Aguardando inicializacao do Slot 2...")
    print("="*65)

if __name__ == "__main__":
    main()
