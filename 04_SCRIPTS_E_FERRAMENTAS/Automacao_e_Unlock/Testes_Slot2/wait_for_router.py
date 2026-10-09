import socket
import time
import sys

def probe(host="192.168.73.2", port=23, timeout=0.5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    res = s.connect_ex((host, port))
    s.close()
    return res == 0

print("Aguardando o roteador reiniciar e responder na porta 23 (Telnet)...")
start = time.time()
while time.time() - start < 120:
    elapsed = int(time.time() - start)
    if probe("192.168.73.2", 23):
        print(f"\n[SUCESSO] Roteador respondeu em {elapsed} segundos!")
        sys.exit(0)
    elif probe("192.168.1.1", 80):
        print(f"\n[AVISO] Roteador respondeu em 192.168.1.1 (Failsafe Web) em {elapsed}s!")
        sys.exit(0)
    elif probe("192.168.73.2", 80):
        print(f"\n[SUCESSO] Roteador respondeu na porta 80 Web em {elapsed}s!")
        sys.exit(0)
    sys.stdout.write(f"\rAguardando boot... ({elapsed}s)")
    sys.stdout.flush()
    time.sleep(2)

print("\nTimeout atingido após 120 segundos.")
