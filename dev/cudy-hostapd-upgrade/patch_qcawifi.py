import os

with open('dev/cudy-hostapd-upgrade/qcawificfg80211.sh.orig', 'r') as f:
    content = f.read()

print('Original length:', len(content))

# 1. Update create_mlo_config
idx = content.find('create_mlo_config()')
assert idx != -1, 'create_mlo_config() not found'
print('Found create_mlo_config at', idx)

# Find mlo_suppported
idx_mlo = content.find('mlo_suppported=', idx)
idx_end_mlo = content.find('\n', idx_mlo)
line_mlo = content[idx_mlo:idx_end_mlo]
print('Original mlo_suppported line:', line_mlo)

# Replace the grep check in create_mlo_config
new_mlo_check = 'mlo_suppported=$(cat /tmp/sysinfo/board_name 2>/dev/null | grep -c -E \'ipq9574|ipq5332|ap-mi01\')'
content = content[:idx_mlo] + new_mlo_check + content[idx_end_mlo:]

# Find case "$board_name" in
idx_case = content.find('case "$board_name" in', idx)
idx_next_case = content.find('\n', idx_case)
mlo_board_entry = '''
		ap-mi01*|*ap-mi01*|ap-al02-c4)
			cat > /ini/mlo_config.ini <<EOF
mlo_max_num_groups=1

[MLO_GROUP_0]
mlo_max_num_peers=256
mlo_num_chips=3
mlo_soc_chip_ids=0,1,2

[MLO_SOC_CHIP_0]
mlo_chip_idx=0
mlo_num_adj_chip=2
mlo_adj_chip_idx=1,2

[MLO_SOC_CHIP_1]
mlo_chip_idx=1
mlo_num_adj_chip=2
mlo_adj_chip_idx=2,0

[MLO_SOC_CHIP_2]
mlo_chip_idx=2
mlo_num_adj_chip=2
mlo_adj_chip_idx=0,1
EOF
			;;'''
content = content[:idx_next_case] + mlo_board_entry + content[idx_next_case:]

# 2. Add set_pci_ce_irq_affinity
affinity_func = r'''
set_pci_ce_irq_affinity() {
	echo "Configuring CE IRQ CPU affinities..." > /dev/console
	# SoC 2.4G Copy Engine IRQs (ce0..ce9) -> Core 2 (smp_affinity 4)
	local soc_ce_irqs=$(cat /proc/interrupts | grep -E '\<ce[0-9]+\>' | cut -d ':' -f 1 | tr -d ' ')
	for irq in $soc_ce_irqs; do
		[ -n "$irq" ] && echo 4 > /proc/irq/$irq/smp_affinity 2>/dev/null || true
	done

	# External PCIe 5G/6G QCN9224 Copy Engine IRQs (pci1_wlan_ce_*) -> Core 3 (smp_affinity 8)
	local pci_ce_irqs=$(cat /proc/interrupts | grep 'pci1_wlan_ce_' | cut -d ':' -f 1 | tr -d ' ')
	for irq in $pci_ce_irqs; do
		[ -n "$irq" ] && echo 8 > /proc/irq/$irq/smp_affinity 2>/dev/null || true
	done
}
'''

idx_load = content.find('load_qcawificfg80211()')
assert idx_load != -1, 'load_qcawificfg80211 not found'
content = content[:idx_load] + affinity_func + '\n' + content[idx_load:]

# Inside load_qcawificfg80211, find set_umac_reset_affinity
idx_umac = content.find('set_umac_reset_affinity', idx_load)
assert idx_umac != -1, 'set_umac_reset_affinity not found'
idx_end_umac = content.find('\n', idx_umac)
content = content[:idx_end_umac] + '\n\tset_pci_ce_irq_affinity' + content[idx_end_umac:]

# 3. Add reorder_ap_add
reorder_func = r'''
#reorder_ap_add mldX athX athY .. mldY athXX athYY..
reorder_ap_add()
{
    local i=3 #first interface name starts from $3
    local j
    local mld
    local mbss_tx_vdev_inx
    local arg="$1 $2"

    if [ -z "$gdevice" ]; then
        gdevice=$DEVICES
    fi

    while [ ${i} -le ${#} ]; do
        eval "mld=\${${i}}";
        check_if_mld=$(echo $mld | grep -c "mld")
        [ $check_if_mld != 1 ] && break;
        j=$((i+1))

        while [ ${j} -le ${#} ]; do
            eval "arg_ifname=\${${j}}";
            check_if_mld=$(echo $arg_ifname | grep -c mld)

            [ $check_if_mld = 1 ] && break;
            j=$((j+1));

            # Find the corresponding vif
            for device in $gdevice; do
                config_get disabled "$device" disabled
                [ "$disabled" = "1" ] && {
                    echo "'$device' is disabled"
                    continue
                }
                scan_qcawificfg80211 $device
                vifs=
                config_get vifs "$device" vifs

                for vap in $vifs; do
                   config_get virt_if_name "$vap" ifname
                   if [ "$virt_if_name" = "$arg_ifname" ]; then
                       var=$(cfg80211tool $virt_if_name g_mbss_tx_vdev 2>/dev/null || true)
                       mbss_tx_check=${var##*:}
                       if [ "$mbss_tx_check" = "1" ]; then
                           mbss_tx_vdev_inx="$mbss_tx_vdev_inx $((j-2)) $((j-1))";
                           arg="$arg $mld $arg_ifname"
                           break;
                       fi
                   fi
                done;
            done;
        done;
        i=$((j))
    done;

    i=3
    while [ ${i} -le ${#} ]; do
        match=0
        for inx in $mbss_tx_vdev_inx; do
            [ "$i" = "$inx" ] && {
                match=1
                break;
            }
        done
        [ $match = 1 ] && {
            i=$((i+1))
            continue
        }
        eval "var=\${${i}}";
        arg="$arg $var"
        i=$((i+1))
    done

    mlo_ap_add $arg
}
'''

idx_mlo = content.find('mlo() {')
assert idx_mlo != -1, 'mlo() not found'
content = content.replace('ap_add) mlo_ap_add $@;;', 'ap_add) reorder_ap_add $@;;', 1)

idx_mlo_ap_add = content.find('mlo_ap_add() {')
assert idx_mlo_ap_add != -1, 'mlo_ap_add() not found'
content = content[:idx_mlo_ap_add] + reorder_func + '\n' + content[idx_mlo_ap_add:]

# 4. ubus_remove_mld_bridge
ubus_bridge_func = r'''
ubus_remove_mld_bridge()
{
	local mld_name="$1"
	local vif_found=0

	for ldevice in $gdevice; do
		config_get vifs "$ldevice" vifs
		for vif in $vifs; do
			config_get ifmld "$vif" mld
			if [ "$ifmld" = "$mld_name" ]; then
				vif_found=1
				net_cfg="$(find_net_config "$vif")"
				json_init
				json_add_string "name" "$mld_name"
				json_close_object
				remove_device_val_str=$(json_dump)
				echo "remove $mld_name from br-$net_cfg" > /dev/console
				ubus call network.interface.$net_cfg remove_device "$remove_device_val_str" >/dev/null 2>&1 &
				break;
			fi
		done
	done

	if [ $vif_found -eq 0 ]; then
		ip link set dev $mld_name nomaster 2>/dev/null || true
	fi
}
'''

idx_rm_mld = content.find('remove_mld_bridge() {')
assert idx_rm_mld != -1, 'remove_mld_bridge() not found'
idx_rm_end = content.find('}\n\npre_qcawificfg80211()', idx_rm_mld)
assert idx_rm_end != -1, 'pre_qcawificfg80211 after remove_mld_bridge not found'

new_rm_mld = ubus_bridge_func + '''
remove_mld_bridge() {
	local mld_name="$1"
	mld_netdev=1
	for mld in ${MLD_DEVICES}; do
		local wlanmode="__ap"
		if [ $mld_netdev = 0 ]; then
			break;
		fi
		if [ -z "$mld_name" ]; then
			ubus_remove_mld_bridge $mld
		else
			if [ "$mld_name" = "$mld" ]; then
				ubus_remove_mld_bridge $mld
			fi
		fi
	done
}'''
content = content[:idx_rm_mld] + new_rm_mld + content[idx_rm_end+1:]

# 5. Call cca_threshold in post_qcawificfg80211()
cca_call = '''
	for device in $gdevice; do
		if [ -e /lib/wifi/cca_threshold.sh ]; then
			. /lib/wifi/cca_threshold.sh
			ipq5322_cca_threshold ${device}
		fi
	done'''

idx_post_wifi = content.find('post_qcawificfg80211() {')
assert idx_post_wifi != -1, 'post_qcawificfg80211 not found'
idx_post_end = content.find('}\n\nunicastflood_configcfg80211()', idx_post_wifi)
assert idx_post_end != -1, 'unicastflood after post_qcawificfg80211 not found'

content = content[:idx_post_end] + cca_call + '\n' + content[idx_post_end:]

with open('dev/cudy-hostapd-upgrade/qcawificfg80211.sh.patched', 'w') as f:
    f.write(content)

print('Done! Patched file size:', len(content))
