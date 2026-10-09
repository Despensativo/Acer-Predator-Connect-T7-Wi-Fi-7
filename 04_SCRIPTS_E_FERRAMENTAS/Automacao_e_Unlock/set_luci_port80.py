#!/usr/bin/env python3
"""
Desativa lighttpd (Acer Web) e coloca LuCI (uhttpd) na porta 80 e 443 padrao
Acer Predator Connect T7 - Slot 2
"""

import telnetlib
import time

ROUTER_IP = "192.168.73.2"

def main():
    print(f"[*] Conectando em {ROUTER_IP} via Telnet...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
    tn.read_until(b"/ # ", timeout=5)

    cmds = [
        # 1. Parar e desativar lighttpd
        "/etc/init.d/lighttpd.init stop 2>/dev/null",
        "/etc/init.d/lighttpd.init disable 2>/dev/null",
        "killall -9 lighttpd 2>/dev/null",
        
        # 2. Parar uhttpd antigo
        "killall -9 uhttpd 2>/dev/null",
        
        # 3. Corrigir o script de inicializacao /etc/init.d/uhttpd sabotado pela Acer
        "sed -i 's/#config_load uhttpd/config_load uhttpd/' /etc/init.d/uhttpd",
        "sed -i 's/#config_foreach start_instance uhttpd/config_foreach start_instance uhttpd/' /etc/init.d/uhttpd",
        
        # 4. Configurar uhttpd na porta 80 padrao
        "uci -q delete uhttpd.main.listen_http",
        "uci add_list uhttpd.main.listen_http='0.0.0.0:80'",
        "uci add_list uhttpd.main.listen_http='[::]:80'",
        "uci commit uhttpd",
        
        # 5. Habilitar e iniciar uhttpd
        "/etc/init.d/uhttpd enable",
        "/etc/init.d/uhttpd start",
        
        # 6. Salvar alteracoes no overlay
        "sync",
        "echo '[+] CONFIGURACAO CONCLUIDA'"
    ]

    for c in cmds:
        tn.write(c.encode("ascii") + b"\n")
        time.sleep(0.3)

    out = tn.read_until(b"[+] CONFIGURACAO CONCLUIDA", timeout=10).decode("utf-8", errors="ignore")
    print(out)
    
    # Checar portas ativas
    tn.write(b"netstat -ltn | grep 80; ps | grep uhttpd\n")
    time.sleep(1.0)
    res = tn.read_very_eager().decode("utf-8", errors="ignore")
    print("\n--- STATUS DAS PORTAS E PROCESSOS ---")
    print(res)
    
    tn.close()

if __name__ == "__main__":
    main()
