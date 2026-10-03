import telnetlib, time, socket

print("=== DISPARANDO REBOOT DO ROTEADOR ===")
tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
tn.read_until(b'login: ', 3)
tn.write(b'root\n')
tn.read_until(b'Password: ', 3)
tn.write(b'admin0100\n')
time.sleep(0.5)
tn.write(b'sync\n')
time.sleep(0.5)
print("Enviando comando reboot...")
tn.write(b'reboot\n')
time.sleep(1)
tn.close()
print("Reboot disparado com sucesso! Aguardando o roteador reiniciar...")

time.sleep(25)

start_time = time.time()
found = False

while time.time() - start_time < 90:
    for port in [23, 22, 80]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect(('192.168.73.2', port))
            print(f">>> SUCESSO! Conexao ativa em 192.168.73.2:{port} apos {int(time.time() - start_time + 25)}s!")
            found = True
            s.close()
            break
        except:
            s.close()
    if found:
        break
    time.sleep(1)

if found:
    print("Aguardando 4 segundos para os servicos finalizarem...")
    time.sleep(4)
    try:
        tn2 = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
        tn2.read_until(b'login: ', 5)
        tn2.write(b'root\n')
        tn2.read_until(b'Password: ', 5)
        tn2.write(b'admin0100\n')
        time.sleep(0.5)
        tn2.read_very_eager()
        
        tn2.write(b'cat /proc/cmdline\n')
        time.sleep(0.5)
        cmdline = tn2.read_very_eager().decode()
        
        tn2.write(b'cat /sys/class/ubi/ubi0/mtd_num\n')
        time.sleep(0.5)
        mtd_num = tn2.read_very_eager().decode()
        
        tn2.write(b'df -h\n')
        time.sleep(0.5)
        df = tn2.read_very_eager().decode()
        
        print("\n" + "="*60)
        print("=== RELATORIO DE BOOT ===")
        print("="*60)
        print("1. CMDLINE:")
        print(cmdline.strip())
        print("\n2. UBI0 MTD_NUM (21 = Slot 1, 20 = Slot 2):")
        print(mtd_num.strip())
        print("\n3. MOUNTS (df -h):")
        print(df.strip())
        print("="*60)
        tn2.close()
    except Exception as e:
        print("Erro ao coletar dados via Telnet:", e)
else:
    print("Roteador nao respondeu em 192.168.73.2 apos 90s.")
