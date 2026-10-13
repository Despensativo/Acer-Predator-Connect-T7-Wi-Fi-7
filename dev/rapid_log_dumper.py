import socket
import time
import subprocess
import os
import sys

TARGET_IPS = ["192.168.76.1", "192.168.1.1", "192.168.73.1"]
PASSWORDS = ["root", "root0100", "admin", "Casa0100@"]
DUMP_DIR = "/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/dev/crash_dumps"
os.makedirs(DUMP_DIR, exist_ok=True)

def check_port(ip, port, timeout=0.2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        res = s.connect_ex((ip, port))
        s.close()
        return res == 0
    except Exception:
        return False

def dump_ssh(ip):
    timestamp = int(time.time())
    dump_file = os.path.join(DUMP_DIR, f"dump_{ip}_{timestamp}.txt")
    print(f"\n[!!!] PORTA 22 ABERTA EM {ip}! DISPARANDO CAPTURA INSTANTANEA...")
    
    dump_script = """
echo "=== UPTIME & CMDLINE ==="
uptime
cat /proc/cmdline
cat /sys/class/ubi/ubi0/mtd_num 2>/dev/null || true
cat /etc/openwrt_release 2>/dev/null || true

echo "=== U-BOOT ENV / BOOTCOUNT ==="
fw_printenv bootcount bootlimit boot_partition 2>/dev/null || true

echo "=== CRASH TRACE / PSTORE / MTD23 ==="
cat /sys/fs/pstore/* 2>/dev/null || true
strings /dev/mtd23 2>/dev/null | grep -E '^<[0-9]>\[ *(2[0-9]|3[0-2])\.' | head -n 80 || true

echo "=== DMESG HEAD (BOOT REASON) ==="
dmesg | head -n 60

echo "=== DMESG TAIL (CRASH ERRORS) ==="
dmesg | tail -n 80

echo "=== LOGREAD TAIL ==="
logread | tail -n 80 2>/dev/null || true
"""
    
    # 1. Tentar primeiro com chave SSH sem senha
    cmd = f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@{ip} '{dump_script}'"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
    if res.returncode == 0 and len(res.stdout) > 50:
        with open(dump_file, "w") as f:
            f.write(res.stdout)
        print(f"[SUCCESS] Dump completo salvo em: {dump_file}")
        print(res.stdout[:1500])
        return True
        
    # 2. Se falhar, tentar com sshpass
    for pwd in PASSWORDS:
        cmd = f"/opt/homebrew/bin/sshpass -p '{pwd}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@{ip} '{dump_script}'"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if res.returncode == 0 and len(res.stdout) > 50:
            with open(dump_file, "w") as f:
                f.write(res.stdout)
            print(f"[SUCCESS] Dump completo salvo com senha '{pwd}' em: {dump_file}")
            print(res.stdout[:1500])
            return True
            
    print(f"[!] Conexao SSH respondeu mas autenticacao falhou em {ip}.")
    return False

def dump_telnet(ip):
    timestamp = int(time.time())
    dump_file = os.path.join(DUMP_DIR, f"dump_telnet_{ip}_{timestamp}.txt")
    print(f"\n[!!!] PORTA 23 (TELNET) ABERTA EM {ip}! CAPTURANDO VIA TELNET...")
    
    # Script python rapido para telnet
    script = f"""
import telnetlib, time
try:
    tn = telnetlib.Telnet('{ip}', 23, timeout=3)
    tn.read_until(b'login:', timeout=2)
    tn.write(b'root\\n')
    tn.read_until(b'Password:', timeout=2)
    tn.write(b'root0100\\n')
    time.sleep(0.5)
    tn.write(b'cat /proc/cmdline; cat /sys/class/ubi/ubi0/mtd_num; dmesg | tail -n 60; strings /dev/mtd23 | head -n 40\\n')
    time.sleep(2)
    out = tn.read_very_eager().decode('latin1', errors='ignore')
    with open('{dump_file}', 'w') as f:
        f.write(out)
    print(out[:1000])
except Exception as e:
    print('Telnet err:', e)
"""
    subprocess.run(["/Users/user/.antigravity-tools-env/bin/python3", "-c", script], timeout=8)
    return True

def main():
    print("==================================================")
    print("      WATCHDOG RAPIDO DE CAPTURA DE LOG / CRASH    ")
    print("==================================================")
    print(f"[*] Monitorando alvos: {TARGET_IPS}")
    print("[*] Aguardando qualquer resposta de porta 22 (SSH) ou 23 (Telnet)...")
    
    start_time = time.time()
    last_print = 0
    while time.time() - start_time < 300: # 5 minutos
        now = int(time.time() - start_time)
        if now % 10 == 0 and now != last_print:
            last_print = now
            print(f"    ... monitorando ({now}s)")
            
        for ip in TARGET_IPS:
            if check_port(ip, 22, timeout=0.15):
                if dump_ssh(ip):
                    return
            if check_port(ip, 23, timeout=0.15):
                if dump_telnet(ip):
                    return
        time.sleep(0.2)
        
    print("[X] Timeout de monitoramento.")

if __name__ == "__main__":
    main()
