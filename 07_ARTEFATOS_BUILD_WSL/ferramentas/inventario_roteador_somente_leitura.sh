#!/bin/sh
# Inventário somente leitura. Não grava, não reinicia e não altera ambiente.
uname -a
printf '\nBOOTARGS_ROOT\n'
for item in $(cat /proc/cmdline); do
 case "$item" in ubi.mtd=*|root=*|rootfstype=*) printf '%s\n' "$item" ;; esac
done
printf '\nMTD_MAP\n'
cat /proc/mtd
printf '\nUBI_MAP_AND_VOLUMES\n'
for device in /sys/class/ubi/ubi[0-9]*; do
 [ -d "$device" ] || continue
 printf '%s\n' "$device"
 for field in mtd_num name type data_bytes reserved_ebs usable_eb_size; do
  [ -f "$device/$field" ] || continue
  printf '%s=' "$field"; cat "$device/$field"
 done
done
printf '\nROM_AND_OVERLAY_MOUNTS\n'
awk '$2=="/rom" || $2=="/overlay" {print $1,$2,$3,$4}' /proc/mounts
printf '\nUBOOT_SELECTED_KEYS_READONLY\n'
if command -v fw_printenv >/dev/null 2>&1; then
 for key in bootcmd bootdelay ipaddr serverip loadaddr fdt_high primaryboot; do
  fw_printenv "$key" 2>/dev/null || :
 done
fi
