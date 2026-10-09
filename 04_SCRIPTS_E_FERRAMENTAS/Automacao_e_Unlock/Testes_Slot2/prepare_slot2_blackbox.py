import telnetlib, time, sys

print("="*65)
print("=== INSTALANDO A CAIXA-PRETA DE LOG NO SLOT 2 VIA TELNET ===")
print("="*65)

tn = telnetlib.Telnet('192.168.73.2', 23, timeout=10)
tn.read_until(b'login: ', 3)
tn.write(b'root\n')
tn.read_until(b'Password: ', 3)
tn.write(b'admin0100\n')
time.sleep(0.5)
tn.read_very_eager()

def run_cmd(c, wait=0.5):
    tn.write(c.encode('ascii') + b'\n')
    time.sleep(wait)
    out = b''
    while True:
        chunk = tn.read_very_eager()
        if not chunk:
            break
        out += chunk
        time.sleep(0.1)
    res = out.decode('latin1', errors='replace').strip()
    return res

# 1. Anexar e montar Slot 2
print("\n[1/5] Anexando mtd20 e montando /dev/ubi1_3 em /tmp/s2...")
print(run_cmd("grep -q /tmp/s2 /proc/mounts || { ubiattach -m 20 2>/dev/null; mkdir -p /tmp/s2; mount -t ubifs /dev/ubi1_3 /tmp/s2; }", 1.5))
print(run_cmd("ls -la /tmp/s2/upper/etc/rc.local", 0.5))

# 2. Injetar hook no /etc/rc.common do Slot 2
print("\n[2/5] Injetando rastreador de servicos em /etc/rc.common...")
run_cmd("cp -a /rom/etc/rc.common /tmp/s2/upper/etc/rc.common", 0.5)
# Inserir log no boot() e start()
run_cmd("sed -i '/start()/a \\t[ -w /ultimo_passo.log ] && echo \"[$(date +%T)] RC_START: $initscript\" >> /ultimo_passo.log && sync' /tmp/s2/upper/etc/rc.common", 0.5)
run_cmd("chmod 755 /tmp/s2/upper/etc/rc.common", 0.5)
print(run_cmd("grep -n 'ultimo_passo' /tmp/s2/upper/etc/rc.common", 0.5))

# 3. Injetar heartbeat no rc.local do Slot 2
print("\n[3/5] Injetando heartbeat de 1 segundo em /etc/rc.local...")
run_cmd("sed -i '/# [CAIXA-PRETA]/,+15d' /tmp/s2/upper/etc/rc.local", 0.5)
heartbeat = """(
  echo "[$(date +%T)] RC_LOCAL: Sistema atingiu rc.local com sucesso!" >> /ultimo_passo.log && sync
  while true; do
    UP=$(cut -d' ' -f1 /proc/uptime)
    MEM=$(grep MemFree /proc/meminfo | awk '{print $2}')
    echo "[$(date +%T)] VIVO | Uptime: ${UP}s | MemLivre: ${MEM}kB" >> /ultimo_passo.log
    sync
    sleep 1
  done
) &"""
run_cmd("sed -i '2i " + heartbeat.replace('\n', '\\n') + "' /tmp/s2/upper/etc/rc.local", 0.5)
run_cmd("chmod 755 /tmp/s2/upper/etc/rc.local", 0.5)
print(run_cmd("head -n 20 /tmp/s2/upper/etc/rc.local", 0.5))

# 4. Criar o arquivo inicial de log limpo
print("\n[4/5] Inicializando /ultimo_passo.log no Slot 2...")
run_cmd("printf '=== INICIO DO BOOT DO SLOT 2 ===\\n' > /tmp/s2/upper/ultimo_passo.log", 0.5)
run_cmd("chmod 666 /tmp/s2/upper/ultimo_passo.log", 0.5)
print(run_cmd("cat /tmp/s2/upper/ultimo_passo.log", 0.5))

# 5. Sincronizar e desmontar
print("\n[5/5] Sincronizando e desmontando Slot 2...")
run_cmd("sync", 1.0)
run_cmd("umount /tmp/s2", 1.0)
run_cmd("ubidetach -d 1 2>/dev/null", 0.5)
print(run_cmd("ls -la /dev/ubi*", 0.5))

tn.close()
print("\n" + "="*65)
print(">>> CAIXA-PRETA DO SLOT 2 PRONTA E ARMADA COM SUCESSO! <<<")
print("="*65)
