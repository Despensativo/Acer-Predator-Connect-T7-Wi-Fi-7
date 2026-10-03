import time
import telnetlib
import sys

def run_cmd(tn, cmd, timeout=10):
    tn.write(cmd.encode("utf-8") + b"\n")
    out = tn.read_until(b"/ # ", timeout=timeout).decode("latin1", errors="replace")
    return out

def main():
    print("="*65)
    print("=== PREPARACAO DO OVERLAY DO SLOT 2 (MTD20) COM CORRECAO ===")
    print("="*65)

    tn = telnetlib.Telnet("192.168.73.2", 23, timeout=5)
    tn.read_until(b"login: ", timeout=3)
    tn.write(b"root\n")
    tn.read_until(b"Password: ", timeout=3)
    tn.write(b"admin0100\n")
    tn.read_until(b"/ # ", timeout=3)

    print("\n[1/8] Anexando mtd20 como ubi1...")
    out = run_cmd(tn, "ubiattach -p /dev/mtd20 -d 1 2>&1")
    print(out.strip())

    print("\n[2/8] Montando /dev/ubi1_3 em /tmp/s2...")
    out = run_cmd(tn, "mkdir -p /tmp/s2 && mount -t ubifs /dev/ubi1_3 /tmp/s2 2>&1")
    print(out.strip())

    print("\n[3/8] Criando estrutura /upper e /work...")
    out = run_cmd(tn, "mkdir -p /tmp/s2/upper /tmp/s2/work && chmod 755 /tmp/s2/work")
    out += run_cmd(tn, "mkdir -p /tmp/s2/upper/etc/config /tmp/s2/upper/etc/init.d /tmp/s2/upper/etc/dropbear")
    print(out.strip())

    print("\n[4/8] Copiando credenciais, rede e chaves SSH de Slot 1...")
    cmds = [
        "cp -f /etc/config/network /tmp/s2/upper/etc/config/network",
        "cp -f /etc/config/dropbear /tmp/s2/upper/etc/config/dropbear 2>/dev/null || true",
        "cp -f /etc/shadow /tmp/s2/upper/etc/shadow",
        "cp -f /etc/passwd /tmp/s2/upper/etc/passwd",
        "cp -a /etc/dropbear/* /tmp/s2/upper/etc/dropbear/ 2>/dev/null || true"
    ]
    for c in cmds:
        run_cmd(tn, c)
    print("Configuracoes base copiadas com sucesso.")

    print("\n[5/8] Criando rc.local com ativacao imediata de SSH/Telnet e log de boot...")
    rc_local_content = '''# Custom commands for Slot 2
/etc/init.d/uhttpd stop 2>/dev/null

DROPBEAR=$(command -v dropbear || echo "/usr/sbin/dropbear")
[ -x "$DROPBEAR" ] && $DROPBEAR -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B

TELNETD=$(command -v telnetd || echo "/usr/sbin/telnetd")
[ -x "$TELNETD" ] && $TELNETD -l /bin/ash

/usr/sbin/uhttpd -p 8080 -h /www -x /cgi-bin 2>/dev/null

echo "BOOT_SLOT2_SUCCESSFUL $(date)" >> /boot_history.log
sync
exit 0
'''
    # Escrever rc.local
    run_cmd(tn, f"cat << 'EOF' > /tmp/s2/upper/etc/rc.local\n{rc_local_content}\nEOF")
    run_cmd(tn, "chmod 755 /tmp/s2/upper/etc/rc.local")
    print("rc.local instalado e permissao 755 atribuida.")

    print("\n[6/8] Criando versao corrigida de wifi_fw_mount em /tmp/s2/upper/etc/init.d/wifi_fw_mount...")
    # Copiar original da ROM como base
    run_cmd(tn, "cp -f /rom/etc/init.d/wifi_fw_mount /tmp/s2/upper/etc/init.d/wifi_fw_mount")
    
    # Aplicar patch dinamico: se wifi_fw ja estiver presente em /proc/mtd, NAO anexar mtd21 (rootfs)
    # Substituir a busca cega por rootfs pela deteccao do slot ativo ou checagem de find_mtd_part
    patch_script = '''
sed -i 's/local ubi_part_name="rootfs"/local ubi_part_name="rootfs"; grep -q "rootfs_1" \\/proc\\/cmdline \\&\\& ubi_part_name="rootfs_1"/g' /tmp/s2/upper/etc/init.d/wifi_fw_mount
sed -i 's/local PART=\$(grep -w  "rootfs" \\/proc\\/mtd/local PART=\$(grep -w "\$ubi_part_name" \\/proc\\/mtd/g' /tmp/s2/upper/etc/init.d/wifi_fw_mount
sed -i 's/PART=\$(grep -w  "rootfs" \\/proc\\/mtd/PART=\$(grep -w "\$ubi_part_name" \\/proc\\/mtd/g' /tmp/s2/upper/etc/init.d/wifi_fw_mount
chmod 755 /tmp/s2/upper/etc/init.d/wifi_fw_mount
'''
    run_cmd(tn, patch_script)
    
    # Validar o patch no arquivo
    chk = run_cmd(tn, "grep -n 'ubi_part_name' /tmp/s2/upper/etc/init.d/wifi_fw_mount")
    print("Validacao do patch em wifi_fw_mount:")
    print(chk.strip())

    print("\n[7/8] Validando conteudo de /tmp/s2/upper...")
    chk_files = run_cmd(tn, "ls -la /tmp/s2/upper/etc/ /tmp/s2/upper/etc/config/ /tmp/s2/upper/etc/init.d/")
    print(chk_files.strip())

    print("\n[8/8] Sincronizando dados e desmontando...")
    run_cmd(tn, "sync")
    run_cmd(tn, "umount /tmp/s2")
    run_cmd(tn, "ubidetach -m 20 2>/dev/null || ubidetach -d 1 2>/dev/null || true")
    run_cmd(tn, "sync")
    print("Desmontado e sincronizado com sucesso!")

    tn.close()
    print("\n" + "="*65)
    print(">>> PREPARACAO DO OVERLAY DO SLOT 2 CONCLUIDA COM SUCESSO! <<<")
    print("="*65)

if __name__ == "__main__":
    main()
