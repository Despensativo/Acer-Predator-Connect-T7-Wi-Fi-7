import telnetlib
import time
import urllib.request
import json

ROUTER_IP = "192.168.73.2"

def main():
    print(f"[*] Verificando estado do roteador {ROUTER_IP} pos-reboot...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=3)
    time.sleep(0.5)

    commands = [
        "echo '=== UPTIME ==='; uptime",
        "echo '=== PROCESSOS PARASITAS (DEBLOAT) ==='; ps | grep -E 'monitord|sodd|modem_readd|fota' | grep -v grep || echo 'Nenhum processo parasita rodando (DEBLOAT PERSISTENTE OK)'",
        "echo '=== CRONTAB ==='; crontab -l",
        "echo '=== PROCESSOS WEB ATIVOS ==='; ps | grep -E 'uhttpd|lighttpd' | grep -v grep",
        "echo '=== CANAIS WI-FI ==='; uci show wireless.wifi0.channel; uci show wireless.wifi1.channel; uci show wireless.wifi2.channel"
    ]

    for c in commands:
        tn.write(c.encode("ascii") + b"\n")
        time.sleep(0.4)

    out = tn.read_very_eager().decode("utf-8", errors="ignore")
    print(out)
    tn.close()

    # Test HTTP on port 80 and port 8080
    res80 = urllib.request.urlopen(f"http://{ROUTER_IP}/", timeout=3).getcode()
    res8080 = urllib.request.urlopen(f"http://{ROUTER_IP}:8080/", timeout=3).getcode()
    print("=== TESTE DAS INTERFACES WEB ===")
    print(f"Porta 80   (Acer UI):       Status {res80} (OK)")
    print(f"Porta 8080 (LuCI OpenWrt):  Status {res8080} (OK)")

if __name__ == "__main__":
    main()
