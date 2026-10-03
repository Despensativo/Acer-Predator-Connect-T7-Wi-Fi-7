#!/bin/sh
set -eu
OWN='/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT'
WORK='/home/builder/t7-chatgpt-work-20261002-v1'
TC='/home/builder/openwrt/staging_dir/toolchain-aarch64_cortex-a53_gcc-14.4.0_musl'
OUT="$OWN/artefatos/t7-net-20261002-v2"
export STAGING_DIR='/home/builder/openwrt/staging_dir'
export PATH="$TC/bin:/home/builder/openwrt/staging_dir/host/bin:$PATH"
export ARCH=arm64 CROSS_COMPILE=aarch64-openwrt-linux-musl-
export KBUILD_BUILD_TIMESTAMP='2026-10-02 12:00:00 UTC'
export KBUILD_BUILD_USER=chatgpt KBUILD_BUILD_HOST=offline
[ -d "$WORK/linux" ] || { echo 'Scratch isolado ausente'; exit 2; }
[ ! -e "$OUT" ] || { echo 'Saida ja existe'; exit 2; }
mkdir -p "$OUT" "$WORK/initramfs-net"
cp "$OWN/artefatos/t7-diag-20261002-v1/kernel.config" "$WORK/linux/.config"
aarch64-openwrt-linux-musl-gcc -static -Os -Wall -Wextra -Werror "$OWN/fontes/diag_init_net_v2.c" -o "$WORK/initramfs-net/init"
printf 'dir /dev 0755 0 0\ndir /proc 0755 0 0\ndir /sys 0755 0 0\ndir /tmp 1777 0 0\nfile /init %s/init 0755 0 0\nnod /dev/console 0600 0 0 c 5 1\n' "$WORK/initramfs-net" > "$WORK/initramfs-net.list"
cd "$WORK/linux"
for symbol in NET INET NETDEVICES ETHERNET NET_VENDOR_QUALCOMM QCOM_PPE PCS_QCOM_IPQ9574 MDIO_IPQ4019 QCA808X_PHY PHYLIB PHYLINK OF_MDIO IPQ_NSSCC_5332 IPQ_GCC_5332 NETCONSOLE NET_POLL_CONTROLLER SYSCTL PROC_SYSCTL; do
 scripts/config --enable "$symbol"
done
for symbol in MTD MODULES DEVMEM NVMEM_SYSFS NVMEM_QCOM_QFPROM NVMEM_QCOM_SEC_QFPROM MMC SCSI PCI USB; do
 scripts/config --disable "$symbol"
done
scripts/config --set-str INITRAMFS_SOURCE "$WORK/initramfs-net.list"
scripts/config --set-str LOCALVERSION '-t7-net-20261002-v2'
scripts/config --set-str CMDLINE 'console=ttyMSM0,115200n8 earlycon=msm_serial_dm,0x78af000 loglevel=8 ignore_loglevel panic=0 maxcpus=1 rdinit=/init netconsole=6665@169.254.73.2/lan,6667@169.254.73.1/ff:ff:ff:ff:ff:ff'
make olddefconfig
cp .config "$OUT/kernel.config"
make -j8 Image
cp arch/arm64/boot/Image "$OUT/Image"
cp vmlinux System.map "$OUT/"
cp "$WORK/initramfs-net/init" "$OUT/init"
cp "$WORK/initramfs-net.list" "$OUT/initramfs.list"
cp usr/initramfs_data.cpio "$OUT/initramfs.cpio"
aarch64-openwrt-linux-musl-nm vmlinux | grep -E '(ramoops_probe|pstore_register|start_kernel|qcom_ppe_probe|init_netconsole)' > "$OUT/simbolos-diagnostico.txt"
aarch64-openwrt-linux-musl-readelf -h -l "$OUT/init" > "$OUT/init-readelf.txt"
aarch64-openwrt-linux-musl-gcc -E -nostdinc -undef -D__DTS__ -x assembler-with-cpp -I arch/arm64/boot/dts -I include "$OWN/fontes/t7-diagnostico-net-v2.dts" -o "$OUT/t7-diagnostico.preprocessed.dts"
dtc -I dts -O dtb -o "$OUT/t7-diagnostico.dtb" "$OUT/t7-diagnostico.preprocessed.dts"
python3 "$OWN/ferramentas/empacotar_candidato.py" "$OUT"
cp "$OWN/identidade-net-v2.json" "$OUT/identidade-net-v2.json"
tar -czf "$OUT/fontes-kernel-isoladas.tar.gz" --exclude='*.o' --exclude='*.a' --exclude='*.cmd' --exclude='vmlinux' --exclude='Image' --exclude='System.map' -C "$WORK" linux
echo COMPILACAO_REDE_CONCLUIDA_SEM_HARDWARE
