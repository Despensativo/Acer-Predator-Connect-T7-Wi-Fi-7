import gzip
import tarfile
import io
import os

src_path = r'C:\Users\User\Downloads\config.cfg'
out_path = r'C:\Users\User\Downloads\config_ap_2_5g.cfg'

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
    
    if member.name == 'etc/config/network':
        text = content.decode('utf-8')
        # 1. Add eth0 (2.5G port) to lan bridge alongside eth1.1 and eth1.2
        text = text.replace("option ifname 'eth1.1 eth1.2'", "option ifname 'eth0 eth1.1 eth1.2'")
        
        # 2. Set static IP to 192.168.73.2, gateway to master router 192.168.73.1
        target_ip_block = "option ipaddr '192.168.73.2'\n\toption gateway '192.168.73.1'\n\tlist dns '192.168.73.1'\n\tlist dns '8.8.8.8'"
        text = text.replace("option ipaddr '192.168.76.1'", target_ip_block)
        
        # 3. Disable the dedicated wan interface since eth0 is now in the lan bridge
        target_wan_old = "config interface 'wan'\n\toption ifname 'eth0'\n\toption proto 'dhcp'"
        target_wan_new = "config interface 'wan'\n\toption disabled '1'"
        text = text.replace(target_wan_old, target_wan_new)
        
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('Updated etc/config/network')
        
    elif member.name == 'etc/config/dhcp':
        text = content.decode('utf-8')
        # Disable DHCP server on lan interface
        old_lan = "config dhcp 'lan'\n\toption interface 'lan'"
        new_lan = "config dhcp 'lan'\n\toption interface 'lan'\n\toption ignore '1'"
        text = text.replace(old_lan, new_lan)
        text = text.replace("option dhcpv6 'server'", "option dhcpv6 'disabled'")
        text = text.replace("option ra 'server'", "option ra 'disabled'")
        
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('Updated etc/config/dhcp')
        
    elif member.name == 'etc/hosts':
        text = content.decode('utf-8')
        text = text.replace('192.168.76.1', '192.168.73.2')
        new_content = text.encode('utf-8')
        member.size = len(new_content)
        out_tar.addfile(member, io.BytesIO(new_content))
        print('Updated etc/hosts')
        
    else:
        out_tar.addfile(member, io.BytesIO(content))

out_tar.close()
src_tar.close()

# Gzip compress the new tar
compressed = gzip.compress(out_tar_bytes.getvalue())
with open(out_path, 'wb') as f:
    f.write(compressed)

print('Generated config_ap_2_5g.cfg successfully! Size:', len(compressed))
