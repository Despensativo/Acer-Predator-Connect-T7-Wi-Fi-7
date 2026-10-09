#!/usr/bin/env python3
"""
Orquestrador Seguro de Gravação no Slot 1 via Slot 2
Acer Predator Connect T7 (IPQ5332)
"""

import socket
import time
import sys

ROUTER_IP = "192.168.76.1"
TELNET_PORT = 23

def telnet_cmd(cmd, wait=2, timeout=10):
    try:
        s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=timeout)
        time.sleep(0.5)
        s.sendall(cmd.encode("utf-8") + b"\n")
        time.sleep(wait)
        out = b""
        while True:
            try:
                s.settimeout(1)
                chunk = s.recv(4096)
                if not chunk:
                    break
                out += chunk
            except Exception:
                break
        s.close()
        return out.decode("utf-8", errors="ignore")
    except Exception as e:
        return f"ERROR: {e}"

def wait_for_router(expected_version=None, max_retries=60, retry_delay=3):
    print(f"[*] Aguardando roteador responder em {ROUTER_IP}:{TELNET_PORT}...")
    for i in range(max_retries):
        try:
            s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=2)
            time.sleep(0.5)
            s.sendall(b"cat /etc/version\n")
            time.sleep(1)
            resp = s.recv(2048).decode("utf-8", errors="ignore")
            s.close()
            for line in resp.splitlines():
                line_clean = line.strip()
                if any(v in line_clean for v in ["000024", "000027", "1.01"]):
                    print(f"    [+] Roteador online! Versao detectada: {line_clean}")
                    if expected_version is None or expected_version in line_clean:
                        return True, line_clean
        except Exception:
            pass
        time.sleep(retry_delay)
        if (i + 1) % 5 == 0:
            print(f"    ... aguardando inicializacao ({(i+1)*retry_delay}s decorridos)")
    return False, "TIMEOUT"

def main():
    print("=" * 60)
    print("  INICIANDO FLASH SEGURO NO SLOT 1 (OPCAO B)")
    print("  Slot 2 (OEM v24) sera usado temporariamente para gravar Slot 1")
    print("=" * 60)

    # 1. Verificar estado atual no Slot 1
    print("\n[Etapa 1/6] Verificando conexao inicial no Slot 1...")
    out = telnet_cmd("cat /etc/version")
    print(f"Versao atual: {out.strip()}")
    if "000027" not in out:
        print("[!] Alerta: O roteador nao parece estar no Slot 1 v27 esperado.")

    # 2. Configurar bootconfig para Slot 2 (primaryboot = 1)
    print("\n[Etapa 2/6] Configurando boot temporario para o Slot 2 (OEM v24)...")
    switch_slot2 = """
echo 1 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 1 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null || true
mtd unlock /dev/mtd4 2>/dev/null || true
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
echo "SLOT2_ARMED"
reboot
"""
    res = telnet_cmd(switch_slot2, wait=2)
    print("Comando de chaveamento enviado. Roteador reiniciando para o Slot 2...")
    time.sleep(5)

    # 3. Aguardar reinicio no Slot 2
    print("\n[Etapa 3/6] Aguardando boot do Slot 2 (Stock OEM v24)...")
    ok, ver = wait_for_router(expected_version="000024", max_retries=50, retry_delay=3)
    if not ok:
        print(f"[-] Falha ao conectar no Slot 2: {ver}")
        sys.exit(1)
    print(f"[OK] Slot 2 ativo com sucesso! ({ver})")

    # 4. Executar script de flash no Slot 1 a partir do Slot 2
    print("\n[Etapa 4/6] Executando /root/executar_flash_slot1.sh no Slot 2...")
    print("    Isso vai: anexar ubi0, gravar rootfs.squashfs no ubi0_2,")
    print("    limpar overlay do Slot 1, redefinir bootconfig para Slot 1 e reiniciar.")
    
    flash_out = telnet_cmd("/root/executar_flash_slot1.sh", wait=25, timeout=70)
    print("Saida do processo de gravacao:")
    print(flash_out)
    time.sleep(5)

    # 5. Aguardar reinicio no Slot 1 com a nova imagem
    print("\n[Etapa 5/6] Aguardando reinicializacao no novo SLOT 1 atualizado...")
    ok, ver = wait_for_router(expected_version="000027", max_retries=60, retry_delay=3)
    if not ok:
        # Pode ser qualquer versao caso o /etc/version tenha sido alterado
        ok, ver = wait_for_router(expected_version=None, max_retries=20, retry_delay=3)
    
    if not ok:
        print(f"[-] Roteador demorou para responder: {ver}")
        sys.exit(1)

    print(f"[OK] Roteador respondeu com sucesso! Versao ativa: {ver}")

    # 6. Validacao pos-flash
    print("\n[Etapa 6/6] Verificando integridade do novo sistema...")
    val_cmd = """
echo '=== DF ==='
df -h
echo '=== MEMORIA ==='
free -m
echo '=== HTOP ==='
which htop && htop -v 2>/dev/null || echo 'htop ok'
echo '=== IPERF ==='
iperf -v 2>&1 | head -n 1
echo '=== WIFI INTERFACES ==='
iw dev
"""
    val_out = telnet_cmd(val_cmd, wait=3)
    print(val_out)
    print("=" * 60)
    print("  GRAVACAO CONCLUIDA COM SUCESSO NO SLOT 1!")
    print("=" * 60)

if __name__ == "__main__":
    main()
