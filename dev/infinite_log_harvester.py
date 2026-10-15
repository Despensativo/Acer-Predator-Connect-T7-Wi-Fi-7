#!/usr/bin/env python3
import socket
import time
import os

ROUTER_IP = "192.168.76.1"
BIND_IP = "192.168.76.5"
LOG_DIR = "/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/dev/crash_dumps"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "infinite_live_stream.log")
AUDIT_FILE = os.path.join(LOG_DIR, "last_full_audit.log")

def log(msg):
    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def check_port(port, timeout=0.15):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((BIND_IP, 0))
        s.settimeout(timeout)
        res = s.connect_ex((ROUTER_IP, port))
        s.close()
        return res == 0
    except Exception:
        return False

def run_telnet_rescue_and_audit():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((BIND_IP, 0))
        s.settimeout(4.0)
        s.connect((ROUTER_IP, 23))
        time.sleep(0.3)
        
        # 1. Comandos de travamento critico
        lock_cmds = [
            "ubus call system watchdog '{\"stop\":false,\"frequency\":5}' 2>/dev/null",
            "sysctl -w kernel.panic=0 2>/dev/null",
            "echo 0 > /proc/sys/kernel/panic 2>/dev/null",
            "echo 0 > /proc/sys/kernel/panic_on_oops 2>/dev/null",
            "killall -9 watchdog monitord breakpad 2>/dev/null",
            "rm -f /etc/rc.d/S01predator_dev /etc/init.d/predator_dev 2>/dev/null",
            "uci -q set predator_dev.failsafe.enabled='0' && uci -q commit predator_dev 2>/dev/null",
            "echo 0 > /data/boot_fail_count 2>/dev/null",
            "sed -i 's/dp_mlo_reo_rings_map=.*/dp_mlo_reo_rings_map=0/' /ini/internal/QCN9224_i.ini /cfg/default/ini/internal/QCN9224_i.ini 2>/dev/null",
            "sync"
        ]
        
        for c in lock_cmds:
            s.sendall((c + "\n").encode('ascii'))
            time.sleep(0.15)
            
        log("[TELNET]: Travas de emergencia aplicadas!")
        
        # 2. Auditoria de diagnostico
        audit_cmds = [
            "echo '=== UPTIME & CARGA ==='",
            "uptime",
            "cat /proc/uptime",
            "echo '=== MTD ATIVO ==='",
            "cat /sys/class/ubi/ubi0/mtd_num 2>/dev/null",
            "echo '=== CMDLINE ==='",
            "cat /proc/cmdline",
            "echo '=== INTERFACES LINK ==='",
            "ip -br link show",
            "echo '=== STATUS WAN ==='",
            "ifstatus wan 2>/dev/null | grep -E '\"up\"|\"device\"|\"proto\"'",
            "echo '=== PROCESSOS ATIVOS ==='",
            "ps | grep -v ' \\[' | head -n 30",
            "echo '=== SYSTRACE MTD23 CRASH ==='",
            "strings /dev/mtd23 2>/dev/null | grep -E '(Fatal|Crash|panic|PC is at|Assertion failed|driver_state)' | tail -n 30",
            "echo '=== ULTIMAS 70 LINHAS DMESG ==='",
            "dmesg | tail -n 70",
            "echo '=== FIM DA AUDITORIA ==='"
        ]
        
        for c in audit_cmds:
            s.sendall((c + "\n").encode('ascii'))
            time.sleep(0.2)
            
        time.sleep(1.5)
        buf = b""
        s.settimeout(3.0)
        while True:
            try:
                chunk = s.recv(8192)
                if not chunk: break
                buf += chunk
                if b"=== FIM DA AUDITORIA ===" in chunk:
                    break
            except Exception:
                break
                
        out = buf.decode('latin1', errors='ignore')
        with open(AUDIT_FILE, "w") as f:
            f.write(out)
        log(f"[TELNET]: Auditoria completa gravada em {AUDIT_FILE} ({len(out)} bytes)")
        
        # Destaques importantes no log
        for line in out.splitlines():
            if any(k in line for k in ["UPTIME", "MTD", "ath0", "ath1", "ath2", "pppoe", "Assertion", "BUG", "panic", "Fatal", "Crash"]):
                log(f"  > {line.strip()}")
                
        # Mantem canal aberto com ping de keepalive e monitoramento de Wi-Fi
        log("[TELNET]: Mantendo canal aberto para sustentar o shell...")
        heartbeat_count = 0
        wifi_brought_up = False
        while True:
            time.sleep(5)
            heartbeat_count += 1
            s.sendall(b"cat /proc/uptime; ip -br link show | grep -E 'ath|wifi'\n")
            time.sleep(0.5)
            chunk = s.recv(4096).decode('latin1', errors='ignore')
            lines = [l.strip() for l in chunk.splitlines() if l.strip()]
            for l in lines:
                if "ath" in l:
                    log(f"  [WIFI STATUS]: {l}")
            
            # Se atingiu 40s de uptime e ath0 ainda nao subiu, dispara wifi up limpo
            if not wifi_brought_up and heartbeat_count >= 8:
                if not any("ath0" in l for l in lines):
                    log("[TELNET]: Uptime > 40s atingido e calibração a frio concluída. Subindo Wi-Fi limpo...")
                    s.sendall(b"/sbin/wifi up 2>/dev/null\n")
                    wifi_brought_up = True
            
            log(f"  [HEARTBEAT #{heartbeat_count}]: mantendo conexao ativa")
                
    except Exception as e:
        log(f"[TELNET EXCEPTION]: {e}")
        return False

def main():
    log("==========================================================")
    log("  INFINITE LOG HARVESTER & HARDWARE WATCHDOG ARRESTER V2  ")
    log("==========================================================")
    
    cycle = 0
    while True:
        cycle += 1
        if check_port(23):
            log(f"[CICLO {cycle}] Porta 23 (Telnet) DETECTADA! Iniciando resgate e extracao...")
            run_telnet_rescue_and_audit()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
