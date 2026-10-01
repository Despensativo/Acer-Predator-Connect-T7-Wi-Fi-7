import gzip
import tarfile
import io

src_path = r'C:\Users\User\Downloads\config.cfg'
out_path = r'C:\Users\User\Downloads\config_ap_turbinado.cfg'

with open(src_path, 'rb') as f:
    decompressed = gzip.decompress(f.read())

src_tar = tarfile.open(fileobj=io.BytesIO(decompressed), mode='r')

out_tar_bytes = io.BytesIO()
out_tar = tarfile.open(fileobj=out_tar_bytes, mode='w')

for member in src_tar.getmembers():
    if not member.isreg():
        out_tar.addfile(member)
        continue
        
    f = src_tar.extractfile(member)
    if f is None:
        out_tar.addfile(member)
        continue
    content = f.read()
    
    # 1. NETWORK: 2.5 Gbps port in LAN bridge, IP 192.168.73.2, Gateway 192.168.73.1, WAN disabled
    if member.name == 'etc/config/network':
        text = content.decode('utf-8')
        text = text.replace("option ifname 'eth1.1 eth1.2'", "option ifname 'eth0 eth1.1 eth1.2'")
        target_ip_block = "option ipaddr '192.168.73.2'\n\toption gateway '192.168.73.1'\n\tlist dns '192.168.73.1'\n\tlist dns '8.8.8.8'"
        text = text.replace("option ipaddr '192.168.76.1'", target_ip_block)
        target_wan_old = "config interface 'wan'\n\toption ifname 'eth0'\n\toption proto 'dhcp'"
        target_wan_new = "config interface 'wan'\n\toption disabled '1'"
        text = text.replace(target_wan_old, target_wan_new)
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('[+] Modified etc/config/network')
        
    # 2. DHCP: Disable DHCP server and IPv6 server/RA on LAN
    elif member.name == 'etc/config/dhcp':
        text = content.decode('utf-8')
        old_lan = "config dhcp 'lan'\n\toption interface 'lan'"
        new_lan = "config dhcp 'lan'\n\toption interface 'lan'\n\toption ignore '1'"
        text = text.replace(old_lan, new_lan)
        text = text.replace("option dhcpv6 'server'", "option dhcpv6 'disabled'")
        text = text.replace("option ra 'server'", "option ra 'disabled'")
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('[+] Modified etc/config/dhcp')
        
    # 3. HOSTS: Update management domain IP
    elif member.name == 'etc/hosts':
        text = content.decode('utf-8')
        text = text.replace('192.168.76.1', '192.168.73.2')
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('[+] Modified etc/hosts')
        
    # 4. WIRELESS: 160MHz on 5GHz, unblock DFS, txpower boost, 802.11v roaming, MLO enabled, PSC channel
    elif member.name == 'etc/config/wireless':
        text = content.decode('utf-8')
        
        # wifi0 (2.4 GHz): HT20 for 25m with walls, txpower 25 dBm
        old_wifi0 = "config wifi-device 'wifi0'\n\toption type 'qcawificfg80211'\n\toption channel 'auto'\n\toption hwmode '11beg'\n\toption disabled '0'\n\toption txpower '22'\n\toption htmode 'HT40'"
        new_wifi0 = "config wifi-device 'wifi0'\n\toption type 'qcawificfg80211'\n\toption channel 'auto'\n\toption hwmode '11beg'\n\toption disabled '0'\n\toption txpower '25'\n\toption htmode 'HT20'"
        text = text.replace(old_wifi0, new_wifi0)
        
        # wifi1 (5 GHz): HT160, blockdfslist '0', txpower 25 dBm
        old_wifi1 = "config wifi-device 'wifi1'\n\toption type 'qcawificfg80211'\n\toption channel 'auto'\n\toption hwmode '11bea'\n\toption disabled '0'\n\toption txpower '22'\n\toption htmode 'HT80'\n\toption blockdfslist '1'"
        new_wifi1 = "config wifi-device 'wifi1'\n\toption type 'qcawificfg80211'\n\toption channel 'auto'\n\toption hwmode '11bea'\n\toption disabled '0'\n\toption txpower '25'\n\toption htmode 'HT160'\n\toption blockdfslist '0'"
        text = text.replace(old_wifi1, new_wifi1)
        
        # wifi2 (6 GHz): PSC channel 37, psc '1', txpower 25 dBm
        old_wifi2 = "config wifi-device 'wifi2'\n\toption type 'qcawificfg80211'\n\toption channel 'auto'\n\toption hwmode '11bea'\n\toption disabled '0'\n\toption txpower '22'"
        new_wifi2 = "config wifi-device 'wifi2'\n\toption type 'qcawificfg80211'\n\toption channel '37'\n\toption psc '1'\n\toption hwmode '11bea'\n\toption disabled '0'\n\toption txpower '25'"
        text = text.replace(old_wifi2, new_wifi2)
        
        # Roaming 802.11v
        text = text.replace("option ssid 'CASA_ARK'\n", "option ssid 'CASA_ARK'\n\toption wnm '1'\n")
        text = text.replace("option ssid 'CASA_ARK_5G'\n", "option ssid 'CASA_ARK_5G'\n\toption wnm '1'\n")
        text = text.replace("option ssid 'CASA_ARK_6G'\n", "option ssid 'CASA_ARK_6G'\n\toption wnm '1'\n")
        
        # Replace ALL occurrences of T7_0W0J_MLO across all bands with CASA_ARK_7G
        text = text.replace("T7_0W0J_MLO", "CASA_ARK_7G")
        
        # Set all MLO passwords to Casa0100@ and unhide
        text = text.replace("option key 'f4ussvwT'\n\toption ieee80211w '2'\n\toption sae_password 'f4ussvwT'\n\toption sae '1'\n\toption mld 'mld0'\n\toption hidden '1'",
                            "option key 'Casa0100@'\n\toption ieee80211w '2'\n\toption sae_password 'Casa0100@'\n\toption sae '1'\n\toption mld 'mld0'\n\toption hidden '0'")
        
        # Enable all MLO interfaces (wifi0, wifi1, wifi2)
        # In wifi0 MLO:
        mlo_wifi0_old = "config wifi-iface\n\toption device 'wifi0'\n\toption network 'lan'\n\toption mode 'ap'\n\toption ssid 'CASA_ARK_7G'\n\toption encryption 'ccmp'\n\toption maxsta '64'\n\toption disabled '1'"
        mlo_wifi0_new = "config wifi-iface\n\toption device 'wifi0'\n\toption network 'lan'\n\toption mode 'ap'\n\toption ssid 'CASA_ARK_7G'\n\toption encryption 'ccmp'\n\toption maxsta '64'\n\toption disabled '0'"
        text = text.replace(mlo_wifi0_old, mlo_wifi0_new)
        
        # In wifi1 MLO:
        mlo_wifi1_old = "config wifi-iface\n\toption device 'wifi1'\n\toption network 'lan'\n\toption mode 'ap'\n\toption ssid 'CASA_ARK_7G'\n\toption encryption 'ccmp'\n\toption maxsta '64'\n\toption disabled '1'"
        mlo_wifi1_new = "config wifi-iface\n\toption device 'wifi1'\n\toption network 'lan'\n\toption mode 'ap'\n\toption ssid 'CASA_ARK_7G'\n\toption encryption 'ccmp'\n\toption maxsta '64'\n\toption disabled '0'"
        text = text.replace(mlo_wifi1_old, mlo_wifi1_new)
        
        # In wifi2 MLO:
        mlo_wifi2_old = "config wifi-iface\n\toption device 'wifi2'\n\toption network 'lan'\n\toption mode 'ap'\n\toption ssid 'CASA_ARK_7G'\n\toption en_6g_sec_comp '0'\n\toption encryption 'ccmp'\n\toption maxsta '64'\n\toption disabled '1'"
        mlo_wifi2_new = "config wifi-iface\n\toption device 'wifi2'\n\toption network 'lan'\n\toption mode 'ap'\n\toption ssid 'CASA_ARK_7G'\n\toption en_6g_sec_comp '0'\n\toption encryption 'ccmp'\n\toption maxsta '64'\n\toption disabled '0'"
        text = text.replace(mlo_wifi2_old, mlo_wifi2_new)
        
        # Move TV casa from guest to lan (so it receives 192.168.73.X and can be casted to from phones)
        old_tv = "config wifi-iface\n\toption device 'wifi0'\n\toption network 'guest'\n\toption mode 'ap'\n\toption encryption 'psk2+aes'\n\toption maxsta '64'\n\toption isguest '1'\n\toption rrm '1'\n\toption wps_state '2'\n\toption disabled '0'\n\toption ssid 'TV casa'"
        new_tv = "config wifi-iface\n\toption device 'wifi0'\n\toption network 'lan'\n\toption mode 'ap'\n\toption encryption 'psk2+aes'\n\toption maxsta '64'\n\toption isguest '0'\n\toption rrm '1'\n\toption wps_state '2'\n\toption disabled '0'\n\toption ssid 'TV casa'"
        text = text.replace(old_tv, new_tv)
        
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('[+] Modified etc/config/wireless (ALL MLO blocks set to CASA_ARK_7G, PSC=1, TV casa on LAN)')
        
    # 5. TRIPLEBAND: Enable MLO, set bands to 0 (5G+6G)
    elif member.name == 'etc/config/tripleband':
        text = content.decode('utf-8')
        text = text.replace("option mlo_enable '0'", "option mlo_enable '1'")
        # In Vue JS MLOBandLists: 0 is "5G+6G"!
        text = text.replace("option mlo_bands '0'", "option mlo_bands '0'")
        text = text.replace("option basic_ssid 'T7_0W0J'", "option basic_ssid 'CASA_ARK'")
        text = text.replace("option basic_key 'f4ussvwT'", "option basic_key 'Casa0100@'")
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('[+] Modified etc/config/tripleband (mlo_enable 1, mlo_bands 0 = 5G+6G)')
        
    # 6. WIFI_SSID_PWD: Align web interface state cache
    elif member.name == 'etc/config/wifi_ssid_pwd':
        text = "ssid2.4g:CASA_ARK\nssid5g:CASA_ARK_5G\nssid6g:CASA_ARK_6G\npasswd:Casa0100@\n"
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('[+] Modified etc/config/wifi_ssid_pwd')
        
    # 7. DROPBEAR: Enable SSH access on port 22
    elif member.name == 'etc/config/dropbear':
        text = content.decode('utf-8')
        text = text.replace("option enable\t\t'0'", "option enable\t\t'1'")
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('[+] Modified etc/config/dropbear (SSH enabled)')
        
    # 8. SKB RECYCLER: Increase packet buffers for 2 Gbps traffic
    elif member.name == 'etc/config/skb_recycler':
        text = content.decode('utf-8')
        text = text.replace("option max_skbs '1024'", "option max_skbs '2048'")
        text = text.replace("option max_spare_skbs '256'", "option max_spare_skbs '512'")
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('[+] Modified etc/config/skb_recycler (Packet buffer doubled)')
        
    # 9. RC.LOCAL: Explicitly start Dropbear SSH service on boot
    elif member.name == 'etc/rc.local':
        text = content.decode('utf-8')
        text = text.replace("exit 0", "/etc/init.d/dropbear enable\n/etc/init.d/dropbear start\nexit 0")
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('[+] Modified etc/rc.local (Dropbear enabled and started on boot)')
        
    else:
        out_tar.addfile(member, io.BytesIO(content))

out_tar.close()
src_tar.close()

# Gzip compress the new tar
compressed = gzip.compress(out_tar_bytes.getvalue())
with open(out_path, 'wb') as f:
    f.write(compressed)

print('SUCCESS! Rebuilt config_ap_turbinado.cfg 100% aligned! Size:', len(compressed))
