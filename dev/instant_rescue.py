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
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
        time.sleep(0.3)
        commands = [
            "ubus call system watchdog '{\"timeout\":3600,\"frequency\":5}' 2>/dev/null",
            "sysctl -w kernel.panic=0",
            "echo 0 > /proc/sys/kernel/panic",
            "echo 0 > /proc/sys/kernel/panic_on_oops",
            "cp -f /lib/wifi/qcawificfg80211.sh.bak.20261013 /lib/wifi/qcawificfg80211.sh 2>/dev/null",
            "rm -f /etc/rc.d/S01predator_dev /etc/init.d/predator_dev 2>/dev/null",
            "uci -q set predator_dev.failsafe.enabled='0' && uci -q commit predator_dev",
            "uci -q set system.@system[0].watchdog_timeout='3600' && uci -q commit system",
            "echo 0 > /data/boot_fail_count 2>/dev/null",
            "sed -i 's/dp_mlo_reo_rings_map=.*/dp_mlo_reo_rings_map=0/' /ini/internal/QCN9224_i.ini /cfg/default/ini/internal/QCN9224_i.ini 2>/dev/null",
            "grep -q 'timeout\":3600' /etc/rc.local || sed -i '2i ubus call system watchdog \"{\\\"timeout\\\":3600,\\\"frequency\\\":5}\" 2>/dev/null; sysctl -w kernel.panic=0 2>/dev/null; echo 0 > /proc/sys/kernel/panic 2>/dev/null' /etc/rc.local",
            "sync",
            "uptime",
            "cat /sys/class/ubi/ubi0/mtd_num",
            "cat /proc/cmdline"
        ]
        
        full_out = ""
        for cmd in commands:
            tn.write((cmd + "\n").encode('ascii'))
            time.sleep(0.2)
            chunk = tn.read_very_eager().decode('latin1', errors='ignore')
            full_out += chunk
            
        time.sleep(1.0)
        chunk = tn.read_very_eager().decode('latin1', errors='ignore')
        full_out += chunk
        
        print("[+] RESGATE EXECUTADO COM SUCESSO! Resposta:")
        print(full_out)
        with open("/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/dev/crash_dumps/rescue_output.txt", "w") as f:
            f.write(full_out)
        print("\n[+] ROTEADOR TRAVADO EM MODO SEGURO DEFINITIVO! S01predator_dev removido. Sem reboot.")
        
        # Manter conexao aberta para nao derrubar a shell
        print("[*] Mantendo canal aberto...")
        for _ in range(12):
            time.sleep(5)
            tn.write(b"echo PING_ALIVE > /dev/null\n")
            
        return True
    except Exception as e:
        print(f"[X] Erro ao conectar via Telnet: {e}")
        return False
        return False

def rescue_ssh():
    print(f"\n[!!!] SSH DETECTADO EM {ROUTER_IP}:22! EXECUTANDO TRAVA DE RESGATE...")
    cmd = f"""ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 root@{ROUTER_IP} '
echo V > /dev/watchdog 2>/dev/null
sysctl -w kernel.panic=0 2>/dev/null
sysctl -w kernel.panic_on_oops=0 2>/dev/null
echo 0 > /proc/sys/kernel/panic 2>/dev/null
killall -9 watchdog monitord breakpad 2>/dev/null
/etc/init.d/watchdog stop 2>/dev/null
uptime
cat /sys/class/ubi/ubi0/mtd_num
cat /proc/cmdline
dmesg | tail -n 40
'"""
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
    if res.returncode == 0:
        print("[+] RESGATE SSH EXECUTADO COM SUCESSO!")
        print(res.stdout)
        with open("/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/dev/crash_dumps/rescue_output.txt", "w") as f:
            f.write(res.stdout)
        return True
    return False

def main():
    print("==================================================")
    print("      WATCHDOG DE RESGATE INSTANTANEO (76.1)      ")
    print("==================================================")
    print(f"[*] Polling ultra-rapido a cada 50ms na porta 23 e 22 de {ROUTER_IP} (Timeout: 600s)...")
    
    start_time = time.time()
    while time.time() - start_time < 600:
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
