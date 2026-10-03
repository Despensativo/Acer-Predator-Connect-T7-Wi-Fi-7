with open('wifi_fw_mount_stock.sh', 'r', encoding='latin1') as f:
    content = f.read()

# 1. In mount_wifi_fw:
old_start = """mount_wifi_fw (){
	local emmc_part=""
	local nand_part=""
	local nor_part=""
	local primaryboot=""
	local part_name="0:WIFIFW"
	local ubi_part_name="rootfs\""""

new_start = """mount_wifi_fw (){
	local emmc_part=""
	local nand_part=""
	local nor_part=""
	local primaryboot=""
	local part_name="0:WIFIFW"
	local ubi_part_name="rootfs"
	if grep -q "rootfs_1" /proc/cmdline; then
		ubi_part_name="rootfs_1"
	fi"""

content = content.replace(old_start, new_start, 1)

old_attach = """	elif [ -n "$nand_part" ]; then
                if [ -n "$wifi_on_rootfs" ]; then
                       local PART=$(grep -w  "rootfs" /proc/mtd | awk -F: '{print $1}')
                else
                       local PART=$(grep -w  "WIFIFW" /proc/mtd | awk -F: '{print $1}')
                fi
		ubiattach -p /dev/$PART
		sync"""

new_attach = """	elif [ -n "$nand_part" ]; then
                if [ -n "$wifi_on_rootfs" ]; then
                       local PART=$(grep -w  "$ubi_part_name" /proc/mtd | awk -F: '{print $1}')
                else
                       local PART=$(grep -w  "WIFIFW" /proc/mtd | awk -F: '{print $1}')
                fi
		if ! grep -q "wifi_fw" /proc/mtd; then
			[ -n "$PART" ] && ubiattach -p /dev/$PART 2>/dev/null
			sync
		fi"""

content = content.replace(old_attach, new_attach, 1)

# 2. In mount_adsp_fw:
old_adsp = """	elif [ -n "$nand_part" ]; then
		local PART=$(grep -w  "rootfs" /proc/mtd | awk -F: '{print $1}')
		ubiattach -p /dev/$PART
		sync
		local ubi_part=$(find_mtd_part adsp_fw 2> /dev/null)"""

new_adsp = """	elif [ -n "$nand_part" ]; then
		local adsp_root="rootfs"
		grep -q "rootfs_1" /proc/cmdline && adsp_root="rootfs_1"
		local PART=$(grep -w "$adsp_root" /proc/mtd | awk -F: '{print $1}')
		if ! grep -q "adsp_fw" /proc/mtd; then
			[ -n "$PART" ] && ubiattach -p /dev/$PART 2>/dev/null
			sync
		fi
		local ubi_part=$(find_mtd_part adsp_fw 2> /dev/null)"""

content = content.replace(old_adsp, new_adsp, 1)

# 3. In mount_bt_fw:
old_bt = """	elif [ -n "$nand_part" ]; then
		PART=$(grep -w  "rootfs" /proc/mtd | awk -F: '{print $1}')
		ubiattach -p /dev/$PART
		sync
		ubi_part=$(find_mtd_part bt_fw 2> /dev/null)"""

new_bt = """	elif [ -n "$nand_part" ]; then
		local bt_root="rootfs"
		grep -q "rootfs_1" /proc/cmdline && bt_root="rootfs_1"
		PART=$(grep -w "$bt_root" /proc/mtd | awk -F: '{print $1}')
		if ! grep -q "bt_fw" /proc/mtd; then
			[ -n "$PART" ] && ubiattach -p /dev/$PART 2>/dev/null
			sync
		fi
		ubi_part=$(find_mtd_part bt_fw 2> /dev/null)"""

content = content.replace(old_bt, new_bt, 1)

# 4. In umount:
content = content.replace('/bin/mount -t squashfs $ubi_part', '/bin/mount -t squashfs ${ubi_part%% *}')

with open('wifi_fw_mount.patched', 'w', encoding='latin1', newline='\n') as f:
    f.write(content)

print("wifi_fw_mount.patched successfully generated with all 3 fixes!")
