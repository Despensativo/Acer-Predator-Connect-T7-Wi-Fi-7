#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
EXECUTOR DO TESTE CONTROLADO DO SLOT 2 (OPENWRT OTIMIZADO)
Acer Predator Connect T7 (IPQ5322 Wi-Fi 7 BE11000)
=============================================================================
"""

import sys
import io
import os
import time
import socket
import telnetlib
import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROUTER_IP = "192.168.73.2"

def main():
    print("=" * 70)
    print("🚀 INICIANDO TESTE DO SLOT 2 (OPENWRT COM FSBOOTARGS CORRIGIDO)")
    print(f"Alvo Telnet: {ROUTER_IP}")
    print("=" * 70)

    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=5)
    except Exception as e:
        print(f"[-] Erro ao conectar ao roteador: {e}")
        return 1

    time.sleep(0.3)
    tn.write(b"\n")
    time.sleep(0.3)
    tn.read_very_eager()

    # Atualizar boot-openwrt com fsbootargs
    print("[*] Gravando boot-openwrt com parâmetros de rootfs_1 no Slot 1...")
    boot_script = """cat << 'EOF' > /usr/sbin/boot-openwrt
#!/bin/sh
echo "=== Chaveando boot para SLOT 2 (OpenWrt Otimizado) ==="
fw_setenv fsbootargs 'ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs'
echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot
echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot
cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
mtd unlock /dev/mtd3 2>/dev/null
mtd unlock /dev/mtd4 2>/dev/null
mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
rm -f /tmp/bc0.bin /tmp/bc1.bin
sync
echo "[OK] Reiniciando no Slot 2..."
reboot
EOF
chmod +x /usr/sbin/boot-openwrt
"""
    tn.write(boot_script.encode("ascii"))
    time.sleep(0.5)

    print("[*] Acionando chaveamento e reinicialização...")
    tn.write(b"/usr/sbin/boot-openwrt\n")
    time.sleep(1.0)
    tn.close()

    print("[+] Comando enviado! Aguardando o roteador reiniciar...")
    print("\n" + "=" * 70)
    print("⏳ MONITORANDO RESPOSTA DA REDE...")
    print("   -> LAN Padrao: 192.168.1.1:80 (LuCI Web GUI)")
    print("   -> SSH:        192.168.1.1:22")
    print("   -> Telnet:     192.168.1.1:23")
    print("   -> WAN:        192.168.73.2")
    print("=" * 70)

    t0 = time.time()
    time.sleep(15)  # espera desligamento

    for attempt in range(60):
        time.sleep(2)
        elapsed = int(time.time() - t0)

        # Checar 192.168.1.1 (LAN)
        try:
            r = requests.get("http://192.168.1.1/", timeout=0.8)
            if r.status_code == 200:
                if "LuCI" in r.text or "openwrt" in r.text.lower() or "authorization" in r.text.lower():
                    print(f"\n\n[+] 🎉 SUCESSO TOTAL! OpenWrt LuCI ONLINE em 192.168.1.1 após {elapsed}s!")
                    return 0
                elif "FIRMWARE UPDATE" in r.text.upper():
                    print(f"\n[!] Detectado U-Boot Failsafe em 192.168.1.1 após {elapsed}s.")
                    return 2
        except Exception:
            pass

        # Checar SSH na LAN
        try:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex(("192.168.1.1", 22)) == 0:
                s.close()
                print(f"\n\n[+] 🎉 SUCESSO! SSH OpenWrt ONLINE em 192.168.1.1:22 após {elapsed}s!")
                return 0
            s.close()
        except Exception:
            pass

        # Checar Telnet na LAN
        try:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex(("192.168.1.1", 23)) == 0:
                s.close()
                print(f"\n\n[+] 🎉 SUCESSO! Telnet OpenWrt ONLINE em 192.168.1.1:23 após {elapsed}s!")
                return 0
            s.close()
        except Exception:
            pass

        # Checar se voltou para o Slot 1
        try:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex(("192.168.73.2", 23)) == 0:
                s.close()
                print(f"\n\n[*] Roteador respondeu em 192.168.73.2:23 (Slot 1 ou WAN) após {elapsed}s.")
                return 3
            s.close()
        except Exception:
            pass

        sys.stdout.write(f"\r[{elapsed:02d}s] Sondando subida do OpenWrt em 192.168.1.1...")
        sys.stdout.flush()

    print("\n[!] Tempo limite de monitoramento atingido.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
