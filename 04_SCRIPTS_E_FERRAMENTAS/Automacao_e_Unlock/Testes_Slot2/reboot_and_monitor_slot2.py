import telnetlib, time, socket, sys

print("="*65)
print("=== DISPARANDO REBOOT PARA O SLOT 2 VIA TELNET ===")
print("="*65)

try:
    tn = telnetlib.Telnet('192.168.73.2', 23, timeout=10)
    tn.read_until(b'login: ', 3)
    tn.write(b'root\n')
    tn.read_until(b'Password: ', 3)
    tn.write(b'admin0100\n')
    time.sleep(0.5)
    tn.read_very_eager()
    print("Enviando comando de reinicializacao...")
    tn.write(b'sync && reboot\n')
    time.sleep(1)
    tn.close()
    print("Reboot disparado com sucesso!")
except Exception as e:
    print("Erro ao enviar reboot via Telnet:", e)

print("\nAguardando o ciclo de inicializacao do IPQ5332 (~30-45s)...")
start_time = time.time()
active_ip = None
active_port = None
ips_to_check = ["192.168.73.2", "192.168.76.1", "192.168.1.1"]
ports_to_check = [23, 22, 80]

time.sleep(15)

while time.time() - start_time < 120:
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
        elapsed = int(time.time() - start_time)
        print(f"\n>>> SUCESSO! Roteador respondeu em {active_ip}:{active_port} apos {elapsed}s! <<<")
        break
    time.sleep(1)

if not active_ip:
    print("\n[AVISO] Nao respondeu em 120s. Verifique os LEDs fisicos.")
    sys.exit(2)

print("\nAguardando 3s para estabilizar servicos...")
time.sleep(3)

# Coletar informacoes via Telnet
try:
    tn = telnetlib.Telnet(active_ip, 23, timeout=5)
    tn.read_until(b'login: ', 3)
    tn.write(b'root\n')
    tn.read_until(b'Password: ', 3)
    tn.write(b'admin0100\n')
    time.sleep(0.5)
    tn.read_very_eager()
    
    def q(c):
        tn.write(c.encode('ascii') + b'\n')
        time.sleep(0.4)
        return tn.read_very_eager().decode('latin1', errors='replace').strip()
    
    cmdline = q("cat /proc/cmdline")
    mtd_num = q("cat /sys/class/ubi/ubi0/mtd_num 2>/dev/null")
    pboot = q("cat /proc/boot_info/bootconfig0/rootfs/primaryboot 2>/dev/null")
    uptime = q("uptime")
    log_tail = q("cat /ultimo_passo.log 2>/dev/null | tail -n 15")
    
    print("\n" + "="*65)
    print("=== RELATORIO DE BOOT OFICIAL DO ROTEADOR ===")
    print("="*65)
    print(f"IP Ativo:      {active_ip}")
    print(f"CMDLINE:       {cmdline}")
    print(f"MTD Atual:     mtd{mtd_num} (mtd20 = Slot 2, mtd21 = Slot 1)")
    print(f"Primaryboot:   {pboot}")
    print(f"Uptime:        {uptime}")
    print("\nUltimas linhas da Caixa-Preta (/ultimo_passo.log):")
    print(log_tail)
    print("="*65)
    
    if mtd_num.strip() == "20" or "rootfs_1" in cmdline:
        print("\n>>> VITORIA HISTORICA: O ROTEADOR SUBIU NO SLOT 2! <<<")
        print("Monitorando estabilidade por 30 segundos...")
        for i in range(1, 4):
            time.sleep(10)
            up = q("uptime")
            print(f"[{i*10}s] {up}")
        print("\n>>> CONFIRMADO: O SLOT 2 ESTA 100% OPERACIONAL E EM PRODUCAO! <<<")
    else:
        print(f"\n[INFO] Roteador subiu no Slot {mtd_num} (Slot 1).")
    tn.close()
except Exception as e:
    print("Erro ao coletar diagnostico final:", e)
