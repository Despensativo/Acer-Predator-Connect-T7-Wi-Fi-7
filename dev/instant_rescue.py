import socket
import time
import subprocess
import sys

ROUTER_IP = "192.168.76.1"

def check_port(port, timeout=0.1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        res = s.connect_ex((ROUTER_IP, port))
        s.close()
        return res == 0
    except Exception:
        return False

def rescue_telnet():
    import telnetlib
    print(f"\n[!!!] TELNET DETECTADO EM {ROUTER_IP}:23! EXECUTANDO TRAVA DE RESGATE...")
    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=3)
        time.sleep(0.2)
        # Enviar comandos criticos para matar panic e travar wifi antes do crash
        payload = b"""
sysctl -w kernel.panic=0
echo 0 > /proc/sys/kernel/panic
echo 0 > /proc/sys/kernel/panic_on_oops
/etc/init.d/watchdog stop 2>/dev/null
killall -9 watchdog 2>/dev/null
/sbin/wifi down 2>/dev/null
killall -9 hostapd 2>/dev/null
uptime
cat /sys/class/ubi/ubi0/mtd_num
cat /proc/cmdline
"""
        tn.write(payload + b"\n")
        time.sleep(1)
        out = tn.read_very_eager().decode('latin1', errors='ignore')
        print("[+] RESGATE EXECUTADO! Resposta:")
        print(out)
        
        # Agora ler logs e configuracao do wireless
        print("\n[*] Lendo /etc/config/wireless e dmesg...")
        tn.write(b"cat /etc/config/wireless > /tmp/wireless.bak\n")
        tn.write(b"cat /etc/config/wireless | grep -E 'mlo|eht|device|channel|htmode'\n")
        time.sleep(1)
        res = tn.read_very_eager().decode('latin1', errors='ignore')
        print(res)
        
        tn.write(b"dmesg | grep -C 5 -i 'assertion'\n")
        time.sleep(1)
        res_dmesg = tn.read_very_eager().decode('latin1', errors='ignore')
        print(res_dmesg)
        
        # Manter conexao aberta para interagir
        print("\n[+] ROTEADOR TRAVADO EM MODO SEGURO (SEM REBOOT)! Telnet ativo.")
        return True
    except Exception as e:
        print(f"[X] Erro ao conectar via Telnet: {e}")
        return False

def rescue_ssh():
    print(f"\n[!!!] SSH DETECTADO EM {ROUTER_IP}:22! EXECUTANDO TRAVA DE RESGATE...")
    cmd = f"""ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@{ROUTER_IP} '
sysctl -w kernel.panic=0
echo 0 > /proc/sys/kernel/panic
/sbin/wifi down 2>/dev/null
uptime
cat /sys/class/ubi/ubi0/mtd_num
'"""
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
    if res.returncode == 0:
        print("[+] RESGATE SSH EXECUTADO!")
        print(res.stdout)
        return True
    return False

def main():
    print("==================================================")
    print("      WATCHDOG DE RESGATE INSTANTANEO (76.1)      ")
    print("==================================================")
    print(f"[*] Polling ultra-rapido a cada 50ms na porta 23 e 22 de {ROUTER_IP}...")
    
    start_time = time.time()
    while time.time() - start_time < 180:
        if check_port(23, timeout=0.08):
            if rescue_telnet():
                return
        if check_port(22, timeout=0.08):
            if rescue_ssh():
                return
        time.sleep(0.05)
        
    print("[X] Timeout de resgate.")

if __name__ == "__main__":
    main()
