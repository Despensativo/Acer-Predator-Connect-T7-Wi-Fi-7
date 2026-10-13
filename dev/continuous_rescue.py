import socket
import time
import sys

ROUTER_IP = "192.168.76.1"

def main():
    print("==================================================")
    print("      RESGATE CONTINUO COM SESSAO PERSISTENTE     ")
    print("==================================================")
    print(f"[*] Aguardando porta 23 em {ROUTER_IP}...")
    
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            if s.connect_ex((ROUTER_IP, 23)) == 0:
                s.settimeout(10.0)
                print("\n[+] CONECTADO AO TELNET! Enviando payload de desarmamento de watchdog...")
                
                # Desarmar watchdog de hardware e panics
                commands = [
                    "echo V > /dev/watchdog",
                    "sysctl -w kernel.panic=0",
                    "sysctl -w kernel.panic_on_oops=0",
                    "echo 0 > /proc/sys/kernel/panic",
                    "killall -9 watchdog monitord breakpad",
                    "/etc/init.d/watchdog stop",
                    "uptime",
                    "cat /proc/cmdline",
                    "cat /sys/class/ubi/ubi0/mtd_num",
                    "dmesg | grep -C 5 -i 'assertion'",
                    "cat /etc/config/wireless | head -n 50",
                    "ps | grep -iE 'wifi|hostapd|cnss'"
                ]
                
                for cmd in commands:
                    s.sendall((cmd + "\n").encode('ascii'))
                    time.sleep(0.3)
                    
                # Ler todas as respostas
                time.sleep(2)
                buf = b""
                s.settimeout(2.0)
                while True:
                    try:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        buf += chunk
                    except socket.timeout:
                        break
                        
                out = buf.decode('latin1', errors='ignore')
                print("\n=== SAIDA DO ROTEADOR ===")
                print(out)
                
                # Salvar em arquivo
                with open("/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/dev/crash_dumps/rescue_output.txt", "w") as f:
                    f.write(out)
                print("[+] Salvo em dev/crash_dumps/rescue_output.txt")
                
                # Manter conexao viva
                print("[*] Mantendo conexao Telnet aberta com keep-alive...")
                while True:
                    s.sendall(b"uptime\n")
                    time.sleep(5)
                    data = s.recv(1024).decode('latin1', errors='ignore')
                    print(f"Keepalive: {data.strip()}")
            s.close()
        except KeyboardInterrupt:
            print("Interrompido pelo usuario.")
            break
        except Exception as e:
            # print(".", end="", flush=True)
            pass
        time.sleep(0.1)

if __name__ == "__main__":
    main()
