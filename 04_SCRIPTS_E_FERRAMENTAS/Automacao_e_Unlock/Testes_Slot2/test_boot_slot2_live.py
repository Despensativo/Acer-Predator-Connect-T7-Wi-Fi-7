import subprocess, time, socket, sys

def run_ssh(cmd, ip="192.168.73.2", timeout=10):
    full_cmd = f'sshpass -p admin0100 ssh -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa -o ConnectTimeout={timeout} root@{ip} "{cmd}"'
    res = subprocess.run(["wsl", "bash", "-c", full_cmd], capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

print("="*65)
print("=== INICIANDO PROCEDIMENTO DE BOOT NO SLOT 2 (MTD20) ===")
print("="*65)

# 1. Configurar fsbootargs para apontar para o Slot 2
print("\n[Passo 1] Definindo fsbootargs para rootfs_1 (Slot 2)...")
rc, out, err = run_ssh('fw_setenv fsbootargs "ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs" && fw_printenv fsbootargs')
print(f"Resultado fw_setenv: {out}")
if "ubi.mtd=rootfs_1" not in out:
    print("[ERRO] Nao foi possivel definir fsbootargs!")
    sys.exit(1)

# 2. Sincronizar e emitir reboot
print("\n[Passo 2] Enviando sync e reboot para o roteador...")
run_ssh("sync && reboot")
print("Comando de reboot enviado com sucesso!")

# 3. Monitorar o retorno da rede
print("\n[Passo 3] Aguardando o roteador reiniciar (ciclo de boot ~35-45s)...")
time.sleep(20)

ips_to_check = ["192.168.73.2", "192.168.76.1", "192.168.1.1"]
ports_to_check = [22, 23, 80]

start_time = time.time()
active_ip = None
active_port = None

while time.time() - start_time < 90:
    for ip in ips_to_check:
        for port in ports_to_check:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            try:
                s.connect((ip, port))
                active_ip = ip
                active_port = port
                s.close()
                break
            except:
                s.close()
        if active_ip:
            break
    if active_ip:
        elapsed = int(time.time() - start_time + 20)
        print(f"\n>>> SUCESSO! Roteador respondeu em {active_ip}:{active_port} apos {elapsed}s! <<<")
        break
    time.sleep(1)

if not active_ip:
    print("\n[AVISO] O roteador nao respondeu nos IPs 192.168.73.2 / 76.1 / 1.1 apos 90s.")
    print("Verifique se os LEDs estao acesos ou piscando.")
    sys.exit(2)

# 4. Coletar diagnostico do Slot 2 ativo
print(f"\n[Passo 4] Coletando relatorio do sistema em {active_ip}...")
time.sleep(3) # Aguardar servicos estabilizarem

rc, cmdline, _ = run_ssh("cat /proc/cmdline", ip=active_ip)
rc, mtd_num, _ = run_ssh("cat /sys/class/ubi/ubi0/mtd_num 2>/dev/null || echo N/A", ip=active_ip)
rc, mounts, _ = run_ssh("mount | grep -E 'ubi|rom|firmware'", ip=active_ip)
rc, wifi_stat, _ = run_ssh("ls -la /lib/firmware/IPQ5332/WIFI_FW/ 2>/dev/null | head -n 8", ip=active_ip)
rc, uptime, _ = run_ssh("uptime", ip=active_ip)

print("\n" + "="*65)
print("=== RELATÓRIO OFICIAL DE EXECUÇÃO DO SLOT 2 ===")
print("="*65)
print(f"Uptime:        {uptime}")
print(f"CMDLINE:       {cmdline}")
print(f"MTD Atual:     mtd{mtd_num} (mtd20 = Slot 2, mtd21 = Slot 1)")
print("\nMontagens ativas:")
print(mounts)
print("\nFirmware Wi-Fi montado:")
print(wifi_stat)
print("="*65)

if mtd_num.strip() == "20" or "rootfs_1" in cmdline:
    print("\n>>> CONFIRMAÇÃO: O SLOT 2 ESTÁ 100% OPERACIONAL E ATIVO! <<<")
else:
    print("\n[INFO] O roteador subiu no Slot 1 (fallback ativo).")
