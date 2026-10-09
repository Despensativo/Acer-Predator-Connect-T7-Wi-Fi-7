import telnetlib
import time
import sys
import socket
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROUTER_IP = "192.168.73.2"

print("=" * 70)
print("VERIFICANDO E DISPARANDO BOOT DIRETO DO SLOT 2 VIA BOOTCMD")
print("=" * 70)

tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
tn.read_until(b"/ # ", timeout=4)

def run(cmd):
    tn.write(cmd.encode('ascii') + b'\n')
    time.sleep(0.4)
    out = tn.read_until(b"/ # ", timeout=10).decode('utf-8', errors='replace')
    lines = [l.strip() for l in out.strip().split('\n') if l.strip() and not l.startswith(cmd) and not l.startswith('/ #')]
    return '\n'.join(lines)

print("[*] Variáveis ativas:")
print(run("fw_printenv bootcmd"))
print(run("fw_printenv bootcmd_slot2"))

print("\n[*] Sincronizando flash e executando reboot...")
run("sync")
tn.write(b"reboot\n")
time.sleep(1)
tn.close()

print("\n[+] Reboot disparado! Aguardando o roteador processar e reiniciar no Slot 2...")

t0 = time.time()
slot2_online = False

for attempt in range(50):
    time.sleep(2)
    elapsed = int(time.time() - t0)
    for ip in ["192.168.73.2", "192.168.1.1"]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.6)
            res = s.connect_ex((ip, 23))
            s.close()
            if res == 0:
                print(f"\n[+] RESPOSTA DETECTADA em {ip}:23 (Telnet) aos {elapsed}s!")
                slot2_online = True
                break
        except:
            pass
    if slot2_online:
        break
    sys.stdout.write(f"\r[{elapsed:02d}s] Aguardando leitura UBI e inicializacao do kernel...")
    sys.stdout.flush()

if not slot2_online:
    print(f"\n[*] Testando se esta em modo Failsafe Web...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        res = s.connect_ex(("192.168.1.1", 80))
        s.close()
        if res == 0:
            print("[!] Roteador em U-Boot Web Failsafe (192.168.1.1:80).")
        else:
            print("[-] Sem resposta em 192.168.1.1:80.")
    except Exception as e:
        print(f"[-] Erro: {e}")
