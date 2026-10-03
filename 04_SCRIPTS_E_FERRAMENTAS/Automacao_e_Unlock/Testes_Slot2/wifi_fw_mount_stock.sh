#!/bin/sh /etc/rc.common
#
# Copyright (c) 2017-2019 The Linux Foundation. All rights reserved.
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

START=00
STOP=95

create_soft_link()
{
	if [ -e /sys/firmware/devicetree/base/AUTO_MOUNT ]; then
		cp -f $*
	elif [ ! -e /sys/firmware/devicetree/base/AUTO_MOUNT ]; then
		ln -s $*
	fi
}

mount_wifi_fw (){
	local emmc_part=""
	local nand_part=""
	local nor_part=""
	local primaryboot=""
	local part_name="0:WIFIFW"
	local ubi_part_name="rootfs"
	local arch=""
	local wifi_on_rootfs=""
	local hw=""
	local board_name
	local fwfolder="/lib/firmware"

	[ -f /tmp/sysinfo/board_name ] && {
		board_name=ap$(cat /tmp/sysinfo/board_name | awk -F 'ap' '{print$2}')
	}

	[ -e /sys/firmware/devicetree/base/AUTO_MOUNT ] && {
		case $board_name in
			ap-mp*)
				fwfolder="/lib/firmware/wifi"
				mkdir -p $fwfolder
			;;
		esac
	}

	if mount | grep -q WIFI_FW; then
		return 0
	fi

	arch=$1
	case "$arch" in
		"IPQ8074")
			hw="hw2.0"
	;;
		"IPQ6018")
			hw="hw1.0"
	;;
		*)
			hw="hw1.0"
	;;
	esac

	local age0=$(cat /proc/boot_info/bootconfig0/age)
	local age1=$(cat /proc/boot_info/bootconfig1/age)
	local bootname="bootconfig1"

	#Try mode
	if [ -e /proc/upgrade_info/trybit ]; then
		if [ -e /proc/upgrade_info/trymode_inprogress ]; then
			if [ $age0 -le $age1 ]; then
				bootname="bootconfig0"
			else
				bootname="bootconfig1"
			fi
		else
			if [ $age1 -ge $age0 ]; then
				bootname="bootconfig1"
			else
				bootname="bootconfig0"
			fi
		fi
	fi

	primaryboot=$(cat /proc/boot_info/$bootname/$part_name/primaryboot)
	if [ $primaryboot -eq 1 ]; then
		part_name="0:WIFIFW_1"
	fi
	if [[ "$arch" == "IPQ6018" ]] || [[ "$arch" == "IPQ5018" ]] || [[ "$arch" == "IPQ9574" ]] || [[ "$arch" == "IPQ5332" ]]; then
		wifi_on_rootfs="1"
	fi

	emmc_part=$(find_mmc_part $part_name 2> /dev/null)
	nor_part=$(cat /proc/mtd | grep -w "WIFIFW" | awk '{print $1}' | sed 's/:$//')
	local nor_flash=`find /sys/bus/spi/devices/*/mtd -name ${nor_part}`
	if [ -n "$wifi_on_rootfs" ]; then
		nand_part=$(find_mtd_part $ubi_part_name 2> /dev/null)
		if [ -n "$nand_part" ]; then
			emmc_part=""
		fi
	else
		nand_part=$(find_mtd_part $part_name 2> /dev/null)
	fi

	mkdir -p /lib/firmware/$arch/WIFI_FW
	if [ -n "$emmc_part" ]; then
		/bin/mount -t squashfs $emmc_part /lib/firmware/$arch/WIFI_FW > /dev/console 2>&1
		if [ $? -eq 0 ]; then
			cp /rom/lib/firmware/$arch/WIFI_FW/*.* /lib/firmware/$arch/WIFI_FW/
		fi
	elif [ -n "$nor_flash" ]; then
		local nor_mtd_part=$(find_mtd_part $part_name 2> /dev/null)
		if [ -n "$nor_mtd_part" ]; then
			/bin/mount -t squashfs $nor_mtd_part /lib/firmware/$arch/WIFI_FW > /dev/console 2>&1
		fi
	elif [ -n "$nand_part" ]; then
                if [ -n "$wifi_on_rootfs" ]; then
                       local PART=$(grep -w  "rootfs" /proc/mtd | awk -F: '{print $1}')
                else
                       local PART=$(grep -w  "WIFIFW" /proc/mtd | awk -F: '{print $1}')
                fi
		ubiattach -p /dev/$PART
		sync
		local ubi_part=$(find_mtd_part wifi_fw 2> /dev/null)
		if [ -n "$ubi_part" ]; then
			/bin/mount -t squashfs $ubi_part /lib/firmware/$arch/WIFI_FW > /dev/console 2>&1
			if [ $? -ne 0 ]; then
				echo "WIFI FW mount failed, retry after 1 sec" > /dev/console 2>&1
				sleep 1
				/bin/mount -t squashfs $ubi_part /lib/firmware/$arch/WIFI_FW > /dev/console 2>&1
				if [ $? -ne 0 ]; then
					echo "CRITICAL:WIFI FW mount failed, after 1 sec retry" > /dev/console 2>&1
					echo $(cat /proc/mtd) > /dev/console 2>&1
					return -1
				fi
			fi
		fi
	fi
	if [ -f /lib/firmware/$arch/WIFI_FW/q6_fw.mdt ] || ([ -f /lib/firmware/$arch/WIFI_FW/q6_fw0.mdt ] && [ -f /lib/firmware/$arch/WIFI_FW/q6_fw1.mdt ]); then
		echo " WIFI FW mount is successful" > /dev/console 2>&1
	fi

	if [ -d /lib/firmware/$arch/WIFI_FW/qcn9000 ]; then
		cd  $fwfolder && mkdir -p qcn9000 && mkdir -p /vendor/firmware/qcn9000
		cd qcn9000 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9000/*.* .
		cd /vendor/firmware/qcn9000 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9000/Data.msc .
		mkdir -p /lib/firmware/qcn9000 && cd /lib/firmware/qcn9000 && create_soft_link /lib/firmware/$arch/WIFI_FW/qcn9000/qdss* .
	fi

	if [ -d /lib/firmware/$arch/WIFI_FW/qcn9224 ]; then
		cd  $fwfolder && mkdir -p qcn9224 && mkdir -p /vendor/firmware/qcn9224
		cd qcn9224 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9224/*.* .
		local wifi_cert_5=$(cat /lib/wifi_cert_5)
		if [ ! -e "/lib/firmware/qcn9224/bdwlan.b1015" ] || [ ! -s "/lib/firmware/qcn9224/bdwlan.b1015" ]; then
			if [ $wifi_cert_5 -eq 0 ]; then
				echo "*****************/lib/firmware/qcn9224/bdwlan.b1015 file content is empty, relink bdwlan_default.b1015" > /dev/console 2>&1
				ln -fs /lib/firmware/IPQ5332/WIFI_FW/qcn9224/bdwlan_default.b1015 /lib/firmware/qcn9224/bdwlan.b1015
			elif [ $wifi_cert_5 -eq 1 ]; then
				echo "*****************/lib/firmware/qcn9224/bdwlan.b1015 file content is empty, relink bdwlan_ce.b1015" > /dev/console 2>&1
				ln -fs /lib/firmware/IPQ5332/WIFI_FW/qcn9224/bdwlan_ce.b1015 /lib/firmware/qcn9224/bdwlan.b1015
			else
				echo "*****************/lib/firmware/qcn9224/bdwlan.b1015 file content is empty, relink bdwlan_fcc.b1015" > /dev/console 2>&1
				ln -fs /lib/firmware/IPQ5332/WIFI_FW/qcn9224/bdwlan_fcc.b1015 /lib/firmware/qcn9224/bdwlan.b1015
			fi
		fi
		if [ -e "/etc/config/wireless" ] && [ -s "/etc/config/wireless" ]; then
			local country=$(uci get wireless.wifi2.country)
			if [ -n "$country" ]; then
				local wifi_cert5_completed=$(cat /etc/config/wifi_cert | grep $country | awk '{print $3}')
				echo "*****************Wireless configuration already existed, current country code is $country, wifi_cert5_completed:$wifi_cert5_completed, wifi_cert_5:$wifi_cert_5" > /dev/console 2>&1
				if [ $wifi_cert5_completed -ne $wifi_cert_5 ]; then
					echo $wifi_cert5_completed > /lib/wifi_cert_5
					if [ $wifi_cert5_completed -eq 0 ]; then
						echo "*****************/lib/firmware/qcn9224/bdwlan.b1015 file has not been updated, relink bdwlan_default.b1015" > /dev/console 2>&1
						ln -fs /lib/firmware/IPQ5332/WIFI_FW/qcn9224/bdwlan_default.b1015 /lib/firmware/qcn9224/bdwlan.b1015
					elif [ $wifi_cert5_completed -eq 1 ]; then
						echo "*****************/lib/firmware/qcn9224/bdwlan.b1015 file has not been updated, relink bdwlan_ce.b1015" > /dev/console 2>&1
						ln -fs /lib/firmware/IPQ5332/WIFI_FW/qcn9224/bdwlan_ce.b1015 /lib/firmware/qcn9224/bdwlan.b1015
					else
						echo "*****************/lib/firmware/qcn9224/bdwlan.b1015 file has not been updated, relink bdwlan_fcc.b1015" > /dev/console 2>&1
						ln -fs /lib/firmware/IPQ5332/WIFI_FW/qcn9224/bdwlan_fcc.b1015 /lib/firmware/qcn9224/bdwlan.b1015
					fi
				fi
			fi
		else
			local region=$(customer_nv r region)
			if [ -n "$region" ]; then
				local wifi_cert5_completed=$(cat /etc/config/wifi_cert | grep $region | awk '{print $3}')
				echo "*****************Wireless configuration already existed, current country code is $region, wifi_cert5_completed:$wifi_cert5_completed, wifi_cert_5:$wifi_cert_5" > /dev/console 2>&1
				if [ $wifi_cert5_completed -ne $wifi_cert_5 ]; then
					echo $wifi_cert5_completed > /lib/wifi_cert_5
					if [ $wifi_cert5_completed -eq 0 ]; then
						echo "*****************/lib/firmware/qcn9224/bdwlan.b1015 file has not been updated, relink bdwlan_default.b1015" > /dev/console 2>&1
						ln -fs /lib/firmware/IPQ5332/WIFI_FW/qcn9224/bdwlan_default.b1015 /lib/firmware/qcn9224/bdwlan.b1015
					elif [ $wifi_cert5_completed -eq 1 ]; then
						echo "*****************/lib/firmware/qcn9224/bdwlan.b1015 file has not been updated, relink bdwlan_ce.b1015" > /dev/console 2>&1
						ln -fs /lib/firmware/IPQ5332/WIFI_FW/qcn9224/bdwlan_ce.b1015 /lib/firmware/qcn9224/bdwlan.b1015
					else
						echo "*****************/lib/firmware/qcn9224/bdwlan.b1015 file has not been updated, relink bdwlan_fcc.b1015" > /dev/console 2>&1
						ln -fs /lib/firmware/IPQ5332/WIFI_FW/qcn9224/bdwlan_fcc.b1015 /lib/firmware/qcn9224/bdwlan.b1015
					fi
				fi
			fi
		fi
		cd /vendor/firmware/qcn9224 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9224/Data.msc .
		ln -s /lib/firmware/$arch/WIFI_FW/qcn9224/Data_dualmac.msc .
		mkdir -p /lib/firmware/qcn9224 && cd /lib/firmware/qcn9224 && create_soft_link /lib/firmware/$arch/WIFI_FW/qcn9224/qdss* .
	fi

	if [ -d /lib/firmware/$arch/WIFI_FW/qcn9100 ]; then
		cd $fwfolder && mkdir -p qcn9100 && mkdir -p /vendor/firmware/qcn9100
		cd qcn9100 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9100/*.* . && ln -s /lib/firmware/$arch/WIFI_FW/q6_fw.* .
		cd /vendor/firmware/qcn9100 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9100/Data.msc .
		mkdir -p /lib/firmware/qcn9100 && cd /lib/firmware/qcn9100 && create_soft_link /lib/firmware/$arch/WIFI_FW/qcn9100/qdss* .
	fi

	if [ -d /lib/firmware/$arch/WIFI_FW/qcn6122 ]; then
		cd $fwfolder && mkdir -p qcn6122 && mkdir -p /vendor/firmware/qcn6122
		cd qcn6122 && ln -s /lib/firmware/$arch/WIFI_FW/qcn6122/*.* . && ln -s /lib/firmware/$arch/WIFI_FW/q6_fw.* .
		cd /vendor/firmware/qcn6122 && ln -s /lib/firmware/$arch/WIFI_FW/qcn6122/Data.msc .
		mkdir -p /lib/firmware/qcn6122 && cd /lib/firmware/qcn6122 && create_soft_link /lib/firmware/$arch/WIFI_FW/qcn6122/qdss* .
	elif [ -d /lib/firmware/$arch/WIFI_FW/qcn9100 ]; then
		cd $fwfolder && mkdir -p qcn6122 && mkdir -p /vendor/firmware/qcn6122
		cd qcn6122 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9100/*.* . && ln -s /lib/firmware/$arch/WIFI_FW/q6_fw.* .
		cd /vendor/firmware/qcn6122 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9100/Data.msc .
		mkdir -p /lib/firmware/qcn6122 && cd /lib/firmware/qcn6122 && create_soft_link /lib/firmware/$arch/WIFI_FW/qcn9100/qdss* .
	fi

	if [ -d /lib/firmware/$arch/WIFI_FW/qcn9160 ]; then
		cd $fwfolder && mkdir -p qcn9160 && mkdir -p /vendor/firmware/qcn9160
		cd qcn9160 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9160/*.* . && ln -s /lib/firmware/$arch/WIFI_FW/q6_fw.* .
		cd /vendor/firmware/qcn9160 && ln -s /lib/firmware/$arch/WIFI_FW/qcn9160/Data.msc .
		mkdir -p /lib/firmware/qcn9160 && cd /lib/firmware/qcn9160 && create_soft_link /lib/firmware/$arch/WIFI_FW/qcn9160/qdss* .
	fi

	mkdir -p $fwfolder/$arch
	cd  $fwfolder/$arch && ln -s /lib/firmware/$arch/WIFI_FW/*.* .
	local wifi_cert_2=$(cat /lib/wifi_cert_2)
	if [ ! -e "/lib/firmware/IPQ5332/bdwlan.b16" ] || [ ! -s "/lib/firmware/IPQ5332/bdwlan.b16" ]; then
		if [ $wifi_cert_2 -eq 0 ]; then
			echo "*****************/lib/firmware/IPQ5332/bdwlan.b16 file content is empty, relink bdwlan_default.b16" > /dev/console 2>&1
			ln -fs /lib/firmware/IPQ5332/WIFI_FW/bdwlan_default.b16 /lib/firmware/IPQ5332/bdwlan.b16
		elif [ $wifi_cert_2 -eq 1 ]; then
			echo "*****************/lib/firmware/IPQ5332/bdwlan.b16 file content is empty, relink bdwlan_ce.b16" > /dev/console 2>&1
			ln -fs /lib/firmware/IPQ5332/WIFI_FW/bdwlan_ce.b16 /lib/firmware/IPQ5332/bdwlan.b16
		else
			echo "*****************/lib/firmware/IPQ5332/bdwlan.b16 file content is empty, relink bdwlan_fcc.b16" > /dev/console 2>&1
			ln -fs /lib/firmware/IPQ5332/WIFI_FW/bdwlan_fcc.b16 /lib/firmware/IPQ5332/bdwlan.b16
		fi
	fi
	if [ -e "/etc/config/wireless" ] && [ -s "/etc/config/wireless" ]; then
		local country=$(uci get wireless.wifi2.country)
		if [ -n "$country" ]; then
			local wifi_cert2_completed=$(cat /etc/config/wifi_cert | grep $country | awk '{print $2}')
			echo "*****************Wireless configuration already existed, current country code is $country, wifi_cert2_completed:$wifi_cert2_completed, wifi_cert_2:$wifi_cert_2" > /dev/console 2>&1
			if [ $wifi_cert2_completed -ne $wifi_cert_2 ]; then
				echo $wifi_cert2_completed > /lib/wifi_cert_2
				if [ $wifi_cert2_completed -eq 0 ]; then
					echo "*****************/lib/firmware/IPQ5332/bdwlan.b16 file has not been updated, relink bdwlan_default.b16" > /dev/console 2>&1
					ln -fs /lib/firmware/IPQ5332/WIFI_FW/bdwlan_default.b16 /lib/firmware/IPQ5332/bdwlan.b16
				elif [ $wifi_cert2_completed -eq 1 ]; then
					echo "*****************/lib/firmware/IPQ5332/bdwlan.b16 file has not been updated, relink bdwlan_ce.b16" > /dev/console 2>&1
					ln -fs /lib/firmware/IPQ5332/WIFI_FW/bdwlan_ce.b16 /lib/firmware/IPQ5332/bdwlan.b16
				else
					echo "*****************/lib/firmware/IPQ5332/bdwlan.b16 file has not been updated, relink bdwlan_fcc.b16" > /dev/console 2>&1
					ln -fs /lib/firmware/IPQ5332/WIFI_FW/bdwlan_fcc.b16 /lib/firmware/IPQ5332/bdwlan.b16
				fi
			fi
		fi
	else
		local region=$(customer_nv r region)
		if [ -n "$region" ]; then
			local wifi_cert2_completed=$(cat /etc/config/wifi_cert | grep $region | awk '{print $2}')
			echo "*****************Wireless configuration already existed, current country code is $region, wifi_cert2_completed:$wifi_cert2_completed, wifi_cert_2:$wifi_cert_2" > /dev/console 2>&1
			if [ $wifi_cert2_completed -ne $wifi_cert_2 ]; then
				echo $wifi_cert2_completed > /lib/wifi_cert_2
				if [ $wifi_cert2_completed -eq 0 ]; then
					echo "*****************/lib/firmware/IPQ5332/bdwlan.b16 file has not been updated, relink bdwlan_default.b16" > /dev/console 2>&1
					ln -fs /lib/firmware/IPQ5332/WIFI_FW/bdwlan_default.b16 /lib/firmware/IPQ5332/bdwlan.b16
				elif [ $wifi_cert2_completed -eq 1 ]; then
					echo "*****************/lib/firmware/IPQ5332/bdwlan.b16 file has not been updated, relink bdwlan_ce.b16" > /dev/console 2>&1
					ln -fs /lib/firmware/IPQ5332/WIFI_FW/bdwlan_ce.b16 /lib/firmware/IPQ5332/bdwlan.b16
				else
					echo "*****************/lib/firmware/IPQ5332/bdwlan.b16 file has not been updated, relink bdwlan_fcc.b16" > /dev/console 2>&1
					ln -fs /lib/firmware/IPQ5332/WIFI_FW/bdwlan_fcc.b16 /lib/firmware/IPQ5332/bdwlan.b16
				fi
			fi
		fi
	fi
	cd  /lib/firmware/$arch && create_soft_link /lib/firmware/$arch/WIFI_FW/qdss* .

	if [ -e /sys/firmware/devicetree/base/MP_512 ] || [ -e /sys/firmware/devicetree/base/MP_256 ]; then
		#qcn9224 INI file would have all QCN9224 RDP's info, so first priority for qcn9224 file if it exists
		if [ -f /lib/firmware/$arch/WIFI_FW/qcn9224/firmware_rdp_feature_512P.ini ]; then
			cd /lib/firmware
			create_soft_link /lib/firmware/$arch/WIFI_FW/qcn9224/firmware_rdp_feature_512P.ini .
		elif [ -f /lib/firmware/$arch/WIFI_FW/firmware_rdp_feature_512P.ini ]; then
			cd /lib/firmware
			create_soft_link /lib/firmware/$arch/WIFI_FW/firmware_rdp_feature_512P.ini .
		elif [ -f /lib/firmware/$arch/WIFI_FW/qcn9000/firmware_rdp_feature_512P.ini ]; then
			cd /lib/firmware
			create_soft_link /lib/firmware/$arch/WIFI_FW/qcn9000/firmware_rdp_feature_512P.ini .
		fi
	else
		#qcn9224 INI file would have all QCN9224 RDP's info, so first priority for qcn9224 file if it exists
		if [ -f /lib/firmware/$arch/WIFI_FW/qcn9224/firmware_rdp_feature.ini ]; then
			cd /lib/firmware
			create_soft_link /lib/firmware/$arch/WIFI_FW/qcn9224/firmware_rdp_feature.ini .
		elif [ -f /lib/firmware/$arch/WIFI_FW/firmware_rdp_feature.ini ]; then
			cd /lib/firmware
			create_soft_link /lib/firmware/$arch/WIFI_FW/firmware_rdp_feature.ini .
		elif [ -f /lib/firmware/$arch/WIFI_FW/qcn9000/firmware_rdp_feature.ini ]; then
			cd /lib/firmware
			create_soft_link /lib/firmware/$arch/WIFI_FW/qcn9000/firmware_rdp_feature.ini .
		fi
	fi

	. /lib/read_caldata_to_fs.sh
	do_load_ipq4019_board_bin

	if [ -e /lib/firmware/$arch/WIFI_FW/board-2.bin ]; then

		case "$arch" in
			IPQ5332)
				mkdir -p /lib/firmware/ath12k/$arch/$hw
				cd /lib/firmware/ath12k/$arch/$hw/
				;;
			*)
				mkdir -p /lib/firmware/ath11k/$arch/$hw
				cd /lib/firmware/ath11k/$arch/$hw/
				;;
		esac
		ln -s /lib/firmware/$arch/WIFI_FW/board-2.bin .
		ln -s /tmp/$arch/caldata.bin .
		ln -s /lib/firmware/$arch/qdss_trace_config.bin .
	fi

	if [ -d /lib/firmware/$arch/WIFI_FW/qcn9000 ]; then
		if [ -e /lib/firmware/$arch/WIFI_FW/qcn9000/board-2.bin ]; then
			mkdir -p /lib/firmware/ath11k/QCN9074/hw1.0/
			cd /lib/firmware/ath11k/QCN9074/hw1.0/
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9000/board-2.bin .
			ln -s /tmp/qcn9000/caldata*.bin .
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9000/m3.bin .
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9000/amss.bin .
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9000/qdss_trace_config.bin .
		fi
	fi

	if [ -d /lib/firmware/$arch/WIFI_FW/qcn9100 ]; then
		if [ -e /lib/firmware/$arch/WIFI_FW/qcn9100/board-2.bin ]; then
			mkdir -p /lib/firmware/ath11k/qcn9100/hw1.0/
			cd /lib/firmware/ath11k/qcn9100/hw1.0/
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9100/board-2.bin .
			ln -s /lib/firmware/qcn9100/caldata*.bin .
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9100/qdss_trace_config.bin .
		fi
	fi

	if [ -d /lib/firmware/$arch/WIFI_FW/qcn6122 ]; then
		if [ -e /lib/firmware/$arch/WIFI_FW/qcn6122/board-2.bin ]; then
			mkdir -p /lib/firmware/ath11k/qcn6122/hw1.0/
			cd /lib/firmware/ath11k/qcn6122/hw1.0/
			ln -s /lib/firmware/$arch/WIFI_FW/qcn6122/board-2.bin .
			ln -s /lib/firmware/qcn6122/caldata*.bin .
			ln -s /lib/firmware/$arch/WIFI_FW/qcn6122/qdss_trace_config.bin .
		fi
	elif [ -d /lib/firmware/$arch/WIFI_FW/qcn9100 ]; then
		if [ -e /lib/firmware/$arch/WIFI_FW/qcn9100/board-2.bin ]; then
			mkdir -p /lib/firmware/ath11k/qcn6122/hw1.0/
			cd /lib/firmware/ath11k/qcn6122/hw1.0/
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9100/board-2.bin .
			ln -s /lib/firmware/qcn9100/caldata*.bin .
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9100/qdss_trace_config.bin .
		fi
	elif [ -d /lib/firmware/$arch/WIFI_FW/qcn9224 ]; then
		if [ -e /lib/firmware/$arch/WIFI_FW/qcn9224/board-2.bin ]; then
			mkdir -p /lib/firmware/ath12k/QCN92XX/hw1.0/
			cd /lib/firmware/ath12k/QCN92XX/hw1.0/
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9224/m3.bin .
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9224/amss.bin .
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9224/amss_dualmac.bin .
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9224/board-2.bin .
			if [ -e /lib/firmware/$arch/WIFI_FW/qcn9224/regdb.bin ]; then
				ln -s /lib/firmware/$arch/WIFI_FW/qcn9224/regdb.bin .
			fi
			ln -s /lib/firmware/$arch/WIFI_FW/qcn9224/qdss_trace_config.bin .
			case $board_name in
				ap-al02-c4)
					#caldata_2.bin --> PCI1 2.4 GHz
					if [ -e /lib/firmware/qcn9224/caldata_2.bin ]; then
						ln -s /lib/firmware/qcn9224/caldata_2.bin cal-pci-0002:01:00.0.bin
					fi

					#caldata_3.bin --> PCI2 6 GHz
					if [ -e /lib/firmware/qcn9224/caldata_3.bin ]; then
						ln -s /lib/firmware/qcn9224/caldata_3.bin cal-pci-0003:01:00.0.bin
					fi

					#caldata_4.bin --> PCI3 5 GHz
					if [ -e /lib/firmware/qcn9224/caldata_4.bin ]; then
						ln -s /lib/firmware/qcn9224/caldata_4.bin cal-pci-0004:01:00.0.bin
					fi
				;;
				ap-al02-c6)
					#caldata_3.bin --> PCI2 6 GHz
					if [ -e /lib/firmware/qcn9224/caldata_3.bin ]; then
						ln -s /lib/firmware/qcn9224/caldata_3.bin cal-pci-0003:01:00.0.bin
					fi

					#caldata_4.bin --> PCI3 5 GHz
					if [ -e /lib/firmware/qcn9224/caldata_4.bin ]; then
						ln -s /lib/firmware/qcn9224/caldata_4.bin cal-pci-0004:01:00.0.bin
					fi
				;;
				*)
					#No sym links
				;;
			esac
		fi
	fi

	mkdir -p /vendor/firmware/$arch
	cd /vendor/firmware/$arch && ln -s /lib/firmware/$arch/WIFI_FW/Data.msc .
}

mount_adsp_fw (){
	local emmc_part=""
	local nand_part=""
	local nor_part=""
	local ubi_part_name="rootfs"
	local part_name="0:ADSPFW"
	local arch=""

	if mount | grep -q ADSP_FW; then
		return 0
	fi

	arch=$1
	emmc_part=$(find_mmc_part $part_name 2> /dev/null)
	nor_part=$(cat /proc/mtd | grep ADSPFW | awk '{print $1}' | sed 's/:$//')
	local nor_flash=`find /sys/bus/spi/devices/*/mtd -name ${nor_part}`
	nand_part=$(find_mtd_part $ubi_part_name 2> /dev/null)
	mkdir -p /lib/firmware/$arch/ADSP_FW

	if [ -n "$emmc_part" ]; then
		/bin/mount -t squashfs $emmc_part /lib/firmware/$arch/ADSP_FW > /dev/console 2>&1
		[ -f /rom/lib/firmware/$arch/ADSP_FW/q6_fw.mdt ] && cp /rom/lib/firmware/$arch/ADSP_FW/*.* /lib/firmware/$arch/ADSP_FW/
	elif [ -n "$nor_flash" ]; then
		local nor_mtd_part=$(find_mtd_part $part_name 2> /dev/null)
		if [ -n "$nor_mtd_part" ]; then
			/bin/mount -t squashfs $nor_mtd_part /lib/firmware/$arch/ADSP_FW > /dev/console 2>&1
		fi
	elif [ -n "$nand_part" ]; then
		local PART=$(grep -w  "rootfs" /proc/mtd | awk -F: '{print $1}')
		ubiattach -p /dev/$PART
		sync
		local ubi_part=$(find_mtd_part adsp_fw 2> /dev/null)
		if [ -n "$ubi_part" ]; then
			/bin/mount -t squashfs $ubi_part /lib/firmware/$arch/ADSP_FW > /dev/console 2>&1
		fi
	fi

	if [ -f /lib/firmware/$arch/ADSP_FW/image/adsp.mdt ]; then
		echo " ADSP FW mount is successful" > /dev/console 2>&1
	fi

	cd  /lib/firmware/$arch &&  ln -s ADSP_FW/image/*.* .
	[ -d /lib/firmware/$arch/ADSP_FW/dspso ] && ln -s /lib/firmware/$arch/ADSP_FW/dspso /dsp
}

mount_bt_fw (){
	local emmc_part=""
	local nand_part=""
	local nor_part=""
	local ubi_part_name="rootfs"
	local part_name="0:BTFW"
	local arch=""
	local nor_flash=""
	local nor_mtd_part=""
	local PART=""
	local ubi_part=""

	if mount | grep -q BT_FW; then
		return 0;
	fi

	arch=$1
	emmc_part=$(find_mmc_part $part_name 2> /dev/null)
	nor_part=$(cat /proc/mtd | grep BTFW | awk '{print $1}' | sed 's/:$//')
	nor_flash=`find /sys/bus/spi/devices/*/mtd -name ${nor_part}`
	nand_part=$(find_mtd_part $ubi_part_name 2> /dev/null)

	mkdir -p /lib/firmware/$arch/BT_FW

	if [ -n "$emmc_part" ]; then
		/bin/mount -t squashfs $emmc_part /lib/firmware/$arch/BT_FW > /dev/console 2>&1
		[ -f /rom/lib/firmware/$arch/BT_FW/bt_fw.mdt ] && cp /rom/lib/firmware/$arch/BT_FW/*.* /lib/firmware/$arch/BT_FW/
	elif [ -n "$nor_flash" ]; then
		nor_mtd_part=$(find_mtd_part $part_name 2> /dev/null)
		/bin/mount -t squashfs $nor_mtd_part /lib/firmware/$arch/BT_FW > /dev/console 2>&1
	elif [ -n "$nand_part" ]; then
		PART=$(grep -w  "rootfs" /proc/mtd | awk -F: '{print $1}')
		ubiattach -p /dev/$PART
		sync
		ubi_part=$(find_mtd_part bt_fw 2> /dev/null)
		/bin/mount -t squashfs $ubi_part /lib/firmware/$arch/BT_FW > /dev/console 2>&1
	fi

	if [ -f /lib/firmware/$arch/BT_FW/image/bt_fw_patch.mdt ]; then
		echo "BT FW mount is successful" > /dev/console 2>&1
		mkdir /tmp/BT_FW &&  cp -r /lib/firmware/$arch/BT_FW/image/ /tmp/BT_FW
		umount /lib/firmware/$arch/BT_FW
	else
		echo "BT FW mount is failed" > /dev/console 2>&1
	fi

	cd /lib/firmware/$arch && ln -s /tmp/BT_FW/image/*.* .
}

boot() {
 . /lib/functions/system.sh
	local platform=$(grep -o "IPQ.*" /proc/device-tree/model | awk -F/ '{print $1}')
	local board=$(grep -o "IPQ.*" /proc/device-tree/model | awk -F/ '{print $2}')

	if [ "$platform" == "IPQ807x" ]; then
		mount_wifi_fw "IPQ8074"
	elif [ "$platform" == "IPQ8074" ]; then
		mount_wifi_fw "IPQ8074"
	elif [ "$platform" == "IPQ9574" ]; then
		mount_wifi_fw "IPQ9574"
	elif [ "$platform" == "IPQ6018" ]; then
		mount_wifi_fw "IPQ6018"
		case "$board" in
			AP-CP01*)
				mount_adsp_fw "IPQ6018"
				;;
		esac
	elif [ "$platform" == "IPQ5018" ]; then
		mount_bt_fw "IPQ5018"
		mount_wifi_fw "IPQ5018"
	elif [ "$platform" == "IPQ5332" ]; then
		mount_wifi_fw "IPQ5332"
	else
		echo "\nInvalid Target"
	fi
}

stop_wifi_fw() {
	local emmc_part=""
	local nand_part=""
	local nor_part=""
	local primaryboot=""
	local part_name="0:WIFIFW"
	local wifi_on_rootfs=""
	local nor_flash=""
	arch=$1

	if [[ "$arch" == "IPQ6018" ]] || [[ "$arch" == "IPQ5018" ]]; then
		part_name="rootfs"
		wifi_on_rootfs="1"
	fi

	local age0=$(cat /proc/boot_info/bootconfig0/age)
	local age1=$(cat /proc/boot_info/bootconfig1/age)
	local bootname="bootconfig1"

	#Try mode
	if [ -e /proc/upgrade_info/trybit ]; then
		if [ $age1 -ge $age0 ]; then
			bootname="bootconfig1"
		else
			bootname="bootconfig0"
		fi
	fi

	primaryboot=$(cat /proc/boot_info/$bootname/$part_name/primaryboot)
	if [ $primaryboot -eq 1 ]; then
		part_name="${part_name}_1"
	fi

	emmc_part=$(find_mmc_part $part_name 2> /dev/null)
	nor_part=$(cat /proc/mtd | grep -w "WIFIFW" | awk '{print $1}' | sed 's/:$//')
	if [ -n "$nor_part" ]; then
		nor_flash=`find /sys/bus/spi/devices/*/mtd -name ${nor_part}`
	fi
	nand_part=$(find_mtd_part $part_name 2> /dev/null)
	if [ -n "$emmc_part" ]; then
		umount /lib/firmware/$arch/WIFI_FW
	elif [ -n "$nor_flash" ]; then
		local nor_mtd_part=$(find_mtd_part $part_name 2> /dev/null)
		umount /lib/firmware/$arch/WIFI_FW
	elif [ -n "$nand_part" ]; then
		umount /lib/firmware/$arch/WIFI_FW
		if [ -z "$wifi_on_rootfs" ]; then
			local PART=$(grep -w  "WIFIFW" /proc/mtd | awk -F: '{print $1}')
			ubidetach -f -p  /dev/$PART
			sync
		fi
	fi
}

stop_adsp_fw() {
	local emmc_part=""
	local nand_part=""
	local nor_part=""
	local part_name="0:ADSPFW"
	arch=$1

	emmc_part=$(find_mmc_part $part_name 2> /dev/null)
	nor_part=$(cat /proc/mtd | grep ADSPFW | awk '{print $1}' | sed 's/:$//')
	local nor_flash=`find /sys/bus/spi/devices/*/mtd -name ${nor_part}`
	nand_part=$(find_mtd_part rootfs 2> /dev/null)
	if [ -n "$emmc_part" ]; then
		umount /lib/firmware/$arch/ADSP_FW
	elif [ -n "$nor_flash" ]; then
		local nor_mtd_part=$(find_mtd_part $part_name 2> /dev/null)
		umount /lib/firmware/$arch/ADSP_FW
	elif [ -n "$nand_part" ]; then
		umount /lib/firmware/$arch/ADSP_FW
	fi
}

stop_bt_fw() {
	local emmc_part=""
	local nand_part=""
	local nor_part=""
	local part_name="0:BTFW"
	local nor_mtd_part=""
	local nor_flash=""
	arch=$1

	emmc_part=$(find_mmc_part $part_name 2> /dev/null)
	nor_part=$(cat /proc/mtd | grep BTFW | awk '{print $1}' | sed 's/:$//')
	nor_flash=`find /sys/bus/spi/devices/*/mtd -name ${nor_part}`
	nand_part=$(find_mtd_part rootfs 2> /dev/null)
	if [ -n "$emmc_part" ]; then
		umount /lib/firmware/$arch/BT_FW
	elif [ -n "$nor_flash" ]; then
		nor_mtd_part=$(find_mtd_part $part_name 2> /dev/null)
		umount /lib/firmware/$arch/BT_FW
	elif [ -n "$nand_part" ]; then
		umount /lib/firmware/$arch/BT_FW
	fi
}

stop() {
	local platform=$(grep -o "IPQ.*" /proc/device-tree/model | awk -F/ '{print $1}')
	local board=$(grep -o "IPQ.*" /proc/device-tree/model | awk -F/ '{print $2}')

	if [ "$platform" == "IPQ807x" ]; then
		stop_wifi_fw "IPQ8074"
	elif [ "$platform" == "IPQ8074" ]; then
		stop_wifi_fw "IPQ8074"
	elif [ "$platform" == "IPQ9574" ]; then
		stop_wifi_fw "IPQ9574"
	elif [ "$platform" == "IPQ6018" ]; then
		stop_wifi_fw "IPQ6018"
		case "$board" in
			AP-CP01*)
				stop_adsp_fw "IPQ6018"
				;;
		esac
	elif [ "$platform" == "IPQ5018" ]; then
		stop_wifi_fw "IPQ5018"
		stop_bt_fw "IPQ5018"
	elif [ "$platform" == "IPQ5332" ]; then
		stop_wifi_fw "IPQ5332"
	else
		echo "\nInvalid Target"
		return 0
	fi
	return 0
}
