import telnetlib, time, socket

print("1. Conectando ao roteador para disparar o reboot...")
tn = telnetlib.Telnet('192.168.73.2', 23, timeout=5)
tn.read_until(b'login: ', 3)
tn.write(b'root\n')
tn.read_until(b'Password: ', 3)
tn.write(b'admin0100\n')
time.sleep(0.5)
tn.write(b'sync\n')
time.sleep(0.5)
print("2. Enviando comando reboot...")
tn.write(b'reboot\n')
time.sleep(1)
tn.close()
print("3. Reboot enviado! Aguardando o roteador reiniciar...")

time.sleep(15)

start_time = time.time()
connected_ip = None
connected_port = None

while time.time() - start_time < 90:
    for ip in ['192.168.73.2', '192.168.1.1']:
        for port in [23, 22, 80]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                s.connect((ip, port))
                connected_ip = ip
                connected_port = port
                s.close()
                break
            except:
                s.close()
        if connected_ip:
            break
    if connected_ip:
        break
    time.sleep(1)

if connected_ip:
    print(f"\n>>> Roteador online em {connected_ip}:{connected_port} apos {int(time.time() - start_time + 15)}s!")
    time.sleep(3)
    # Tenta conectar via telnet se disponivel
    try:
        tn2 = telnetlib.Telnet(connected_ip, 23, timeout=5)
        tn2.read_until(b'login: ', 4)
        tn2.write(b'root\n')
        tn2.read_until(b'Password: ', 4)
        tn2.write(b'admin0100\n')
        time.sleep(0.5)
        tn2.read_very_eager()
        
        tn2.write(b'cat /proc/cmdline\n')
        time.sleep(0.4)
        cmdline = tn2.read_very_eager().decode()
        
        tn2.write(b'cat /sys/class/ubi/ubi0/mtd_num\n')
        time.sleep(0.4)
        mtd_num = tn2.read_very_eager().decode()
        
        print("\n=== CMDLINE ===")
        print(cmdline)
        print("=== UBI0 MTD_NUM ===")
        print(mtd_num)
        tn2.close()
    except Exception as e:
        print("Nao foi possivel ler telnet imediatamente:", e)
else:
    print("\nRoteador nao respondeu apos 90s.")
