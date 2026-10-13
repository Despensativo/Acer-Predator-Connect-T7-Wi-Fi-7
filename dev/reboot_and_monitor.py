import time
import subprocess
import sys

ROUTER_IP = "192.168.76.1"

def run_cmd(cmd, timeout=10):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -2, "", str(e)

def is_pingable():
    code, _, _ = run_cmd(f"ping -c 1 -W 1000 {ROUTER_IP}", timeout=2)
    return code == 0

def is_ssh_ready():
    code, out, _ = run_cmd(f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@{ROUTER_IP} 'uptime'", timeout=4)
    return code == 0 and "load average" in out

def main():
    print("==================================================")
    print("      INICIANDO REBOOT MONITORADO DO PREDATOR T7   ")
    print("==================================================")
    
    # 1. Enviar comando reboot
    print(f"[*] Enviando 'sync && reboot' para {ROUTER_IP}...")
    run_cmd(f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@{ROUTER_IP} 'sync; reboot'", timeout=6)
    
    start_time = time.time()
    print("[*] Comando de reboot enviado. Aguardando o roteador reiniciar...")
    
    # 2. Esperar o roteador cair (desconectar)
    dropped = False
    for i in range(30):
        time.sleep(1)
        if not is_pingable():
            dropped = True
            elapsed = time.time() - start_time
            print(f"[+] Roteador desligou / reiniciando o SoC ({elapsed:.1f}s)")
            break
        print(f"    ... aguardando encerramento do sistema ({i+1}s)")
        
    if not dropped:
        print("[!] Aviso: O ping nao caiu durante a janela inicial. Prosseguindo...")

    # 3. Esperar o roteador responder ping novamente
    print("[*] Aguardando o kernel subir e responder ICMP ping...")
    rebooted = False
    while time.time() - start_time < 120:
        if is_pingable():
            rebooted = True
            elapsed = time.time() - start_time
            print(f"[+] Roteador respondeu ao ping ICMP! ({elapsed:.1f}s)")
            break
        time.sleep(1)

    if not rebooted:
        print("[X] Erro: Timeout aguardando ping do roteador.")
        sys.exit(1)

    # 4. Esperar o servico SSH (dropbear) e rede inicializarem
    print("[*] Aguardando o servico SSH (Dropbear) e rede estabilizarem...")
    ssh_ready = False
    while time.time() - start_time < 180:
        if is_ssh_ready():
            ssh_ready = True
            elapsed = time.time() - start_time
            print(f"[+] SSH disponivel e autenticado! Tempo total ate SSH: {elapsed:.1f}s")
            break
        time.sleep(2)

    if not ssh_ready:
        print("[X] Erro: Timeout aguardando SSH no roteador.")
        sys.exit(1)

    # 5. Esperar alguns segundos para os daemons (hostapd, SQM, pppoe) terminarem de subir
    print("[*] Aguardando 10 segundos para convergencia total dos daemons e Wi-Fi...")
    time.sleep(10)

    # 6. Auditoria pos-reboot completa
    print("\n==================================================")
    print("      AUDITORIA DE SAUDE POS-BOOT (PREDATOR T7)    ")
    print("==================================================")
    
    audit_cmd = """
echo "=== Uptime & Carga ==="
uptime

echo "=== Governadores de CPU ==="
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null | tr '\n' ' ' && echo ""

echo "=== Interface WAN PPPoE ==="
ifconfig pppoe-wan 2>/dev/null | grep -E "inet |UP |MTU" || echo "pppoe-wan offline"

echo "=== Interfaces Wi-Fi VAPs ==="
for dev in ath0 ath1 ath2; do
    if ifconfig $dev >/dev/null 2>&1; then
        echo -n "$dev: UP | "
        iwconfig $dev 2>/dev/null | grep -o 'ESSID:.*' || echo ""
    else
        echo "$dev: DOWN"
    fi
done

echo "=== DoH (https-dns-proxy) ==="
ps | grep -v grep | grep https-dns-proxy || echo "DoH nao esta rodando"

echo "=== Dnsmasq Cache ==="
ps | grep -v grep | grep dnsmasq || echo "dnsmasq nao esta rodando"

echo "=== WireGuard Kernel Module ==="
lsmod | grep wireguard || echo "wireguard nao carregado"

echo "=== SQM CAKE Config & Egress Qdisc ==="
tc -s qdisc show dev eth0 | grep -E "cake.*bandwidth" || echo "SQM cake nao ativo em eth0"

echo "=== Status ECM SFE (Bloqueio de Bypass para SQM) ==="
cat /sys/kernel/debug/ecm/front_end_ipv4_stop 2>/dev/null || echo "ECM debugfs indisponivel"
cat /sys/kernel/debug/ecm/front_end_ipv6_stop 2>/dev/null || echo "ECM debugfs indisponivel"

echo "=== Teste de Resolucao DNS no Roteador ==="
nslookup google.com 127.0.0.1 >/dev/null 2>&1 && echo "DNS 127.0.0.1: OK" || echo "DNS: FALHA"

echo "=== Teste de Conectividade Internet (Ping 1.1.1.1) ==="
ping -c 2 -W 1 1.1.1.1 >/dev/null 2>&1 && echo "WAN Ping: OK" || echo "WAN Ping: FALHA"
"""
    
    code, stdout, stderr = run_cmd(f"ssh -o StrictHostKeyChecking=no root@{ROUTER_IP} '{audit_cmd}'", timeout=20)
    print(stdout)
    if stderr:
        print("[STDERR]:", stderr)

    total_time = time.time() - start_time
    print(f"\n[+] Ciclo de reboot e monitoramento concluido com sucesso em {total_time:.1f}s!")

if __name__ == "__main__":
    main()
