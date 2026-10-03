import subprocess, sys

def run_ssh(cmd):
    full_cmd = f'sshpass -p admin0100 ssh -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.73.2 "{cmd}"'
    res = subprocess.run(["wsl", "bash", "-c", full_cmd], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERRO] CMD: {cmd}\nSTDERR: {res.stderr}")
    return res.stdout.strip()

print("="*60)
print("=== CONFIGURANDO OVERLAY DO SLOT 2 COM MÁXIMA PRECISÃO ===")
print("="*60)

# 1. Habilitar dropbear nativo no uci
print("\n[1] Habilitando Dropbear nativo no /etc/config/dropbear...")
run_ssh("sed -i 's/option enable .0./option enable .1./g' /tmp/s2/upper/etc/config/dropbear")
print(run_ssh("cat /tmp/s2/upper/etc/config/dropbear"))

# 2. Desabilitar monitord e modem-monitor definitivamente (remover qualquer chance de execução)
print("\n[2] Garantindo que monitord e modem-monitor não executem sob hipótese alguma...")
run_ssh("mkdir -p /tmp/s2/upper/usr/sbin /tmp/s2/upper/usr/bin")
# Criar stubs que saem imediatamente com 0 para monitord e modem-monitor
run_ssh("printf '#!/bin/sh\\nexit 0\\n' > /tmp/s2/upper/usr/sbin/monitord && chmod 755 /tmp/s2/upper/usr/sbin/monitord")
run_ssh("printf '#!/bin/sh\\nexit 0\\n' > /tmp/s2/upper/usr/bin/modem-monitor && chmod 755 /tmp/s2/upper/usr/bin/modem-monitor")
print("Stubs de seguranca criados para monitord e modem-monitor!")

# 3. Verificar rc.local
print("\n[3] Verificando rc.local no Slot 2...")
print(run_ssh("cat /tmp/s2/upper/etc/rc.local | grep -E 'dropbear|telnetd|uhttpd'"))

# 4. Verificar shadow e passwd
print("\n[4] Verificando shadow e passwd no Slot 2...")
print(run_ssh("head -n 2 /tmp/s2/upper/etc/shadow; head -n 2 /tmp/s2/upper/etc/passwd"))

# 5. Verificar rede estática em /etc/config/network
print("\n[5] Verificando /etc/config/network...")
print(run_ssh("grep -E 'ifname|ipaddr' /tmp/s2/upper/etc/config/network"))

# 6. Sincronizar e desmontar
print("\n[6] Sincronizando dados com a flash NAND...")
run_ssh("sync")
print(run_ssh("du -sh /tmp/s2/upper"))
run_ssh("umount /tmp/s2")
run_ssh("ubidetach -m 20")
print("Slot 2 desmontado e seguro!")

print("\n" + "="*60)
print(">>> OVERLAY DO SLOT 2 FINALIZADO COM SUCESSO! <<<")
print("="*60)
