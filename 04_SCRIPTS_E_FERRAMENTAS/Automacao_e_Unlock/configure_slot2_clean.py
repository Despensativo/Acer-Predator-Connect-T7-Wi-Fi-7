#!/usr/bin/env python3
"""
Configura e Debloata o Slot 2 Diretamente pelo Overlay
Acer Predator Connect T7
"""

import telnetlib
import time

ROUTER_IP = "192.168.73.2"

def main():
    print(f"[*] Conectando em {ROUTER_IP} via Telnet...")
    tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
    tn.read_until(b"/ # ", timeout=5)

    cmds = [
        # Garantir montado
        "mkdir -p /mnt/slot2; mount -t ubifs /dev/ubi1_3 /mnt/slot2 2>/dev/null || true",
        
        # 1. Crontabs
        "sed -i '/silent-reboot/d' /mnt/slot2/upper/etc/crontabs/* 2>/dev/null",
        "sed -i '/download_img/d' /mnt/slot2/upper/etc/crontabs/* 2>/dev/null",
        "sed -i '/update_img/d' /mnt/slot2/upper/etc/crontabs/* 2>/dev/null",
        
        # 2. Desativar daemons no boot apagando links no rc.d
        "rm -f /mnt/slot2/upper/etc/rc.d/S*modem* /mnt/slot2/upper/etc/rc.d/S*ril*",
        "rm -f /mnt/slot2/upper/etc/rc.d/S*monitord* /mnt/slot2/upper/etc/rc.d/S*sodd*",
        "rm -f /mnt/slot2/upper/etc/rc.d/S*cwmp* /mnt/slot2/upper/etc/rc.d/S*mqtt*",
        "rm -f /mnt/slot2/upper/etc/rc.d/S*breakpad*",
        
        # 3. Desativar modem_readd do rc.local
        "sed -i 's|^modem_readd &|# modem_readd desativado|g' /mnt/slot2/upper/etc/rc.local 2>/dev/null",
        
        # 4. Hostname
        "sed -i 's/Acer-Predator/Predator-Slot2/g' /mnt/slot2/upper/etc/config/system 2>/dev/null",
        
        # 5. Criar Banner personalizado
        "cat << 'EOF' > /mnt/slot2/upper/etc/banner",
        "   _______                     ________        __",
        "  |       |.-----.-----.-----.|  |  |  |.----.|  |_",
        "  |   -   ||  _  |  -__|     ||  |  |  ||   _||   _|",
        "  |_______||   __|_____|__|__||________||__|  |____|",
        "           |__| W I R E L E S S   F R E E D O M",
        " -----------------------------------------------------",
        "  Acer Predator Connect T7 - SLOT 2 (OpenWrt Otimizado)",
        "  IPQ5322 Quad-Core @ 1.5GHz | Wi-Fi 7 Tri-Band (BE11000)",
        "  LuCI Web: http://192.168.73.2:8080/ | Shell: Telnet/SSH",
        " -----------------------------------------------------",
        "EOF",
        
        # 6. Copiar scripts de dual-boot
        "mkdir -p /mnt/slot2/upper/usr/sbin",
        "cp -f /usr/sbin/boot-acer /usr/sbin/boot-openwrt /mnt/slot2/upper/usr/sbin/ 2>/dev/null",
        "chmod +x /mnt/slot2/upper/usr/sbin/boot-* 2>/dev/null",
        
        # 7. Sync e Umount
        "sync",
        "umount /mnt/slot2",
        "echo DEBLOAT_SLOT2_PRONTO"
    ]

    for cmd in cmds:
        tn.write(cmd.encode("ascii") + b"\n")
        time.sleep(0.2)

    out = tn.read_until(b"DEBLOAT_SLOT2_PRONTO", timeout=15).decode("utf-8", errors="ignore")
    print(out)
    tn.close()
    print("[*] Configuração do Slot 2 concluída com sucesso!")

if __name__ == "__main__":
    main()
