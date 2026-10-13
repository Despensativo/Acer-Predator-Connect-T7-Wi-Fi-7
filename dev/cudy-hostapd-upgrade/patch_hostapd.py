with open('dev/cudy-hostapd-upgrade/hostapd.sh.patched', 'r') as f:
    content = f.read()

print('Original length of hostapd.sh.patched:', len(content))

# Replace hostapd-$ifname.conf with hostapd-$ifname$mld_link_id.conf
old_conf_write = '''	rm -f /var/run/hostapd-$ifname.conf
	cat > /var/run/hostapd-$ifname.conf <<EOF'''

new_conf_write = '''	rm -f /var/run/hostapd-$ifname$mld_link_id.conf
	cat > /var/run/hostapd-$ifname$mld_link_id.conf <<EOF'''

assert old_conf_write in content, 'old_conf_write not found'
content = content.replace(old_conf_write, new_conf_write, 1)

# Replace the echo >>
old_echo = '		echo ${hwmode:+hw_mode=${hwmode#11}} >> /var/run/hostapd-$ifname.conf'
new_echo = '		echo ${hwmode:+hw_mode=${hwmode#11}} >> /var/run/hostapd-$ifname$mld_link_id.conf'
assert old_echo in content, 'old_echo not found'
content = content.replace(old_echo, new_echo, 1)

# Replace the dbdc filename list
old_dbdc = '		echo -e "/var/run/hostapd-$ifname.conf \\c\\h" >> /tmp/hostapd_conf_filename'
new_dbdc = '		echo -e "/var/run/hostapd-$ifname$mld_link_id.conf \\c\\h" >> /tmp/hostapd_conf_filename'
assert old_dbdc in content, 'old_dbdc not found'
content = content.replace(old_dbdc, new_dbdc, 1)

# Replace the lock and wpa_cli call
old_attach = '''		if [ "$force_hostapd_attach" -eq 1  ]; then
			[ -f "/var/run/hostapd-$ifname.lock" ] &&
				rm /var/run/hostapd-$ifname.lock
			wpa_cli -g $WPAD_VARRUN/hostapd/global raw ADD bss_config=$ifname:/var/run/hostapd-$ifname.conf
			[ $? -eq 0 ] || return
			touch /var/run/hostapd-$ifname.lock'''

new_attach = '''		if [ "$force_hostapd_attach" -eq 1  ]; then
			[ -f "/var/run/hostapd-$ifname$mld_link_id.lock" ] &&
				rm /var/run/hostapd-$ifname$mld_link_id.lock
			wpa_cli -g $WPAD_VARRUN/hostapd/global raw ADD bss_config=$ifname:/var/run/hostapd-$ifname$mld_link_id.conf
			[ $? -eq 0 ] || return
			touch /var/run/hostapd-$ifname$mld_link_id.lock'''

assert old_attach in content, 'old_attach not found'
content = content.replace(old_attach, new_attach, 1)

with open('dev/cudy-hostapd-upgrade/hostapd.sh.patched', 'w') as f:
    f.write(content)

print('Updated hostapd.sh.patched successfully! New length:', len(content))
