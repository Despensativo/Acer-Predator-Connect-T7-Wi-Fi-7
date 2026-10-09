#!/usr/bin/env python3
"""
configurar_samba4_apple.py
Aplica a configuração otimizada do Samba 4 com suporte Apple macOS e iOS (vfs_fruit + xattr_tdb),
compartilhando /mnt/sda1 como 'disk' com permissões totais de leitura e escrita.
"""

import sys
import time
sys.path.insert(0, 'Scripts_Automacao')
from telnet_compat import Telnet

def run_cmd(tn, cmd, timeout=10):
    tn.write(cmd + '\n')
    t0 = time.time()
    buf = ''
    while time.time() - t0 < timeout:
        time.sleep(0.3)
        chunk = tn.read_very_eager().decode('utf-8', errors='ignore')
        buf += chunk
        if '/ #' in buf:
            break
    return buf

def main():
    print("=== Conectando ao roteador 192.168.76.1 via Telnet ===")
    tn = Telnet('192.168.76.1', 23)
    time.sleep(0.5)
    tn.read_very_eager()

    print("=== 1. Desativando menu LuCI do ksmbd (sem apagar arquivos) ===")
    out = run_cmd(tn, '''
if [ -f /usr/lib/lua/luci/controller/ksmbd.lua ]; then
    mv /usr/lib/lua/luci/controller/ksmbd.lua /usr/lib/lua/luci/controller/ksmbd.lua.disabled
fi
rm -rf /tmp/luci-indexcache* /tmp/luci-modulecache*
echo "KSMBD controller desativado no menu LuCI."
''')
    print(out)

    print("=== 2. Configurando /etc/samba/smb.conf.template ===")
    smb_template = """[global]
        netbios name = Predator-T7
        interfaces = |INTERFACES|
        server string = |DESCRIPTION|
        unix charset = |CHARSET|
        workgroup = |WORKGROUP|

        bind interfaces only = yes
        deadtime = 15
        enable core files = no
        security = user
        smb encrypt = off
        map to guest = Bad User
        null passwords = yes
        passdb backend = smbpasswd
        socket options = IPTOS_LOWDELAY TCP_NODELAY
        load printers = No
        printcap name = /dev/null
        disable spoolss = yes
        printing = bsd
        mdns name = mdns
        disable netbios = yes
        smb ports = 445
        veto files = /Thumbs.db/desktop.ini/
        delete veto files = yes

        # Apple / macOS / iOS Extensions (vfs_fruit + xattr_tdb para exFAT)
        ea support = yes
        vfs objects = catia fruit streams_xattr xattr_tdb
        fruit:aapl = yes
        fruit:model = Macmini
        fruit:metadata = stream
        fruit:veto_appledouble = no
        fruit:posix_rename = yes
        fruit:zero_file_id = yes
        fruit:wipe_intentionally_left_blank_rfork = yes
        fruit:delete_empty_adfiles = yes
"""
    # Grava o arquivo template no roteador
    tn.write("cat << 'EOF' > /etc/samba/smb.conf.template\n" + smb_template + "EOF\n")
    time.sleep(1)
    print(tn.read_very_eager().decode('utf-8', errors='ignore'))

    print("=== 3. Configurando /etc/config/samba4 ===")
    samba4_uci = """config samba
	option workgroup 'WORKGROUP'
	option charset 'UTF-8'
	option description 'Predator Connect T7'
	option interface 'lan'
	option macos '1'
	option disable_netbios '1'
	option disable_ad_dc '1'
	option disable_winbind '1'

config sambashare
	option name 'disk'
	option path '/mnt/sda1'
	option browseable 'yes'
	option read_only 'no'
	option guest_ok 'yes'
	option force_root '1'
	option create_mask '0777'
	option dir_mask '0777'
	option vfs_objects 'xattr_tdb'
"""
    tn.write("cat << 'EOF' > /etc/config/samba4\n" + samba4_uci + "EOF\n")
    time.sleep(1)
    print(tn.read_very_eager().decode('utf-8', errors='ignore'))

    print("=== 4. Definindo senha root Samba (root0100) ===")
    out = run_cmd(tn, '(echo "root0100"; echo "root0100") | smbpasswd -a -s root')
    print(out)

    print("=== 5. Atualizando Avahi Service mDNS ===")
    avahi_service = """<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">Predator Connect T7</name>
  <service>
    <type>_smb._tcp</type>
    <port>445</port>
  </service>
  <service>
    <type>_device-info._tcp</type>
    <port>0</port>
    <txt-record>model=Macmini</txt-record>
  </service>
</service-group>
"""
    tn.write("cat << 'EOF' > /etc/avahi/services/smb.service\n" + avahi_service + "EOF\n")
    time.sleep(1)
    print(tn.read_very_eager().decode('utf-8', errors='ignore'))

    print("=== 6. Ativando e reiniciando servicos ===")
    out = run_cmd(tn, '''
/etc/init.d/avahi-daemon restart
/etc/init.d/samba4 enable
/etc/init.d/samba4 restart
sleep 2
netstat -tulpn | grep 445
ps | grep smbd
''', timeout=15)
    print(out)

    print("=== 7. Verificando configuracao gerada (/var/etc/smb.conf) e testparm ===")
    out = run_cmd(tn, 'cat /var/etc/smb.conf\ntestparm -s /var/etc/smb.conf', timeout=10)
    print(out)

    tn.close()
    print("=== Configuracao do Samba 4 concluida com sucesso! ===")

if __name__ == '__main__':
    main()
