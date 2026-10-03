import telnetlib
import time
import socket

ROUTER_IP = "192.168.73.2"

print("[*] Conectando para verificar / enviar reboot...")
try:
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
    tn.read_until(b"/ # ", timeout=3)
    tn.write(b"sync && reboot\n")
    time.sleep(1)
    tn.close()
    print("[+] Comando reboot enviado!")
except Exception as e:
    print(f"[-] Aviso (pode já estar reiniciando): {e}")

print("[*] Aguardando o roteador reiniciar no Slot 2...")
t0 = time.time()
time.sleep(15)

online = False
for i in range(50):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        res = s.connect_ex((ROUTER_IP, 23))
        s.close()
        if res == 0:
            print(f"\n[+] ROTEADOR ONLINE APOS {int(time.time() - t0)} SEGUNDOS!")
            online = True
            break
    except Exception:
        pass
    print(".", end="", flush=True)
    time.sleep(2)

if online:
    time.sleep(3)
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
    tn.read_until(b"/ # ", timeout=4)
    
    def send(cmd):
        tn.write(cmd.encode() + b"\n")
        time.sleep(0.4)
        return tn.read_until(b"/ # ", timeout=4).decode(errors="ignore")

    print("\n" + "=" * 60)
    print("[*] STATUS DO BOOTCONFIG:")
    print(send("cat /proc/boot_info/bootconfig0/rootfs/primaryboot").strip())
    
    print("\n[*] SISTEMA DE ARQUIVOS E OVERLAY:")
    print(send("df -h").strip())

    print("\n[*] UBI ATIVO E PARTIÇÃO MTD:")
    print(send("dmesg | grep -i 'attached mtd' || dmesg | grep -i 'ubi' | head -n 5").strip())
    
    print("\n[*] INTERFACES DE REDE:")
    print(send("ifconfig -s").strip())

    tn.close()
else:
    print("\n[-] Timeout aguardando retorno de rede.")
