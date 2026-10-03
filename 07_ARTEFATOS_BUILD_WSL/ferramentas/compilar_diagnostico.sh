#!/bin/sh
set -eu
OWN='/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT'
SOURCE='/home/builder/openwrt/build_dir/target-aarch64_cortex-a53_musl/linux-qualcommbe_ipq53xx/linux-6.18.52'
WORK='/home/builder/t7-chatgpt-work-20261002-v1'
TC='/home/builder/openwrt/staging_dir/toolchain-aarch64_cortex-a53_gcc-14.4.0_musl'
OUT="$OWN/artefatos/t7-diag-20261002-v1"
export STAGING_DIR='/home/builder/openwrt/staging_dir'
export PATH="$TC/bin:/home/builder/openwrt/staging_dir/host/bin:$PATH"
export ARCH=arm64 CROSS_COMPILE=aarch64-openwrt-linux-musl-
export KBUILD_BUILD_TIMESTAMP='2026-10-02 12:00:00 UTC'
export KBUILD_BUILD_USER=chatgpt KBUILD_BUILD_HOST=offline
[ ! -e "$WORK" ] || { echo 'Scratch ja existe; nao sobrescrever'; exit 2; }
[ ! -e "$OUT" ] || { echo 'Artefatos ja existem; nao sobrescrever'; exit 2; }
mkdir -p "$WORK" "$OUT"
sha256sum "$SOURCE/.config" > "$OUT/config-original-antes.sha256"
cp "$SOURCE/.config" "$OUT/config-original.txt"
echo 'Copiando fonte para scratch Linux isolado (sem alterar original)'
rsync -a --exclude='*.o' --exclude='*.a' --exclude='*.ko' --exclude='*.cmd' --exclude='/vmlinux*' --exclude='/arch/arm64/boot/Image*' --exclude='.git' "$SOURCE/" "$WORK/linux/"
cd "$WORK/linux"
make mrproper
cp "$OUT/config-original.txt" .config
mkdir -p "$WORK/initramfs/dev" "$WORK/initramfs/proc" "$WORK/initramfs/sys" "$WORK/initramfs/tmp"
aarch64-openwrt-linux-musl-gcc -static -Os -Wall -Wextra -Werror "$OWN/fontes/diag_init.c" -o "$WORK/initramfs/init"
printf 'dir /dev 0755 0 0\ndir /proc 0755 0 0\ndir /sys 0755 0 0\ndir /tmp 1777 0 0\nfile /init %s/init 0755 0 0\nnod /dev/console 0600 0 0 c 5 1\n' "$WORK/initramfs" > "$WORK/initramfs.list"
C=scripts/config
for symbol in MTD MODULES DEVMEM NVMEM_SYSFS NVMEM_BLOCK NVMEM_QCOM_QFPROM NVMEM_QCOM_SEC_QFPROM MMC SCSI USB_STORAGE BLK_DEV_NVME PCI USB WLAN WIRELESS NETDEVICES SOUND DRM MEDIA_SUPPORT CPU_FREQ DEBUG_INFO DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT DEBUG_INFO_DWARF4 DEBUG_INFO_DWARF5 GCC_PLUGINS WERROR KPROBES FTRACE DEBUG_FS BPF_SYSCALL; do
    "$C" --disable "$symbol"
done
for symbol in NET BLK_DEV_INITRD DEVTMPFS PROC_FS SYSFS TMPFS PRINTK SERIAL_EARLYCON SERIAL_MSM SERIAL_MSM_CONSOLE QCOM_SCM IPQ_GCC_5332 PSTORE PSTORE_RAM PSTORE_CONSOLE DEBUG_INFO_NONE CMDLINE_FORCE WATCHDOG QCOM_WDT WATCHDOG_HANDLE_BOOT_ENABLED; do
    "$C" --enable "$symbol"
done
"$C" --set-str INITRAMFS_SOURCE "$WORK/initramfs.list"
"$C" --set-str LOCALVERSION '-t7-diag-20261002-v1'
"$C" --set-str CMDLINE 'console=ttyMSM0,115200n8 earlycon=msm_serial_dm,0x78af000 loglevel=8 ignore_loglevel panic=0 maxcpus=1 rdinit=/init'
"$C" --set-val INITRAMFS_ROOT_UID 0
"$C" --set-val INITRAMFS_ROOT_GID 0
make olddefconfig
cp .config "$OUT/kernel.config"
echo 'Compilando kernel novo e initramfs minimo'
make -j8 Image
cp arch/arm64/boot/Image "$OUT/Image"
cp vmlinux "$OUT/vmlinux"
cp System.map "$OUT/System.map"
cp "$WORK/initramfs/init" "$OUT/init"
cp "$WORK/initramfs.list" "$OUT/initramfs.list"
aarch64-openwrt-linux-musl-readelf -h -l "$OUT/init" > "$OUT/init-readelf.txt"
aarch64-openwrt-linux-musl-nm vmlinux | grep -E '(ramoops_probe|pstore_register|start_kernel|do_execve|serial_msm)' > "$OUT/simbolos-diagnostico.txt"
aarch64-openwrt-linux-musl-gcc -E -nostdinc -undef -D__DTS__ -x assembler-with-cpp -I arch/arm64/boot/dts -I include "$OWN/fontes/t7-diagnostico.dts" -o "$OUT/t7-diagnostico.preprocessed.dts"
dtc -I dts -O dtb -o "$OUT/t7-diagnostico.dtb" "$OUT/t7-diagnostico.preprocessed.dts"
python3 "$OWN/ferramentas/empacotar_candidato.py" "$OUT"
sha256sum "$SOURCE/.config" > "$OUT/config-original-depois.sha256"
cmp "$OUT/config-original-antes.sha256" "$OUT/config-original-depois.sha256"
tar -czf "$OUT/fontes-kernel-isoladas.tar.gz" --exclude='*.o' --exclude='*.a' --exclude='*.cmd' --exclude='vmlinux' --exclude='Image' --exclude='System.map' -C "$WORK" linux
echo 'COMPILACAO_CONCLUIDA_SEM_TESTE_HARDWARE'
