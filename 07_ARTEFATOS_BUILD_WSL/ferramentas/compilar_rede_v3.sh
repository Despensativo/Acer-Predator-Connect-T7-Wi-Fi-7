#!/bin/sh
set -eu
OWN='/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT'
WORK=/home/builder/t7-chatgpt-work-20261002-v3
OUT="$OWN/artefatos/t7-net-20261002-v3"
SOURCE=/home/builder/openwrt/build_dir/target-aarch64_cortex-a53_musl/linux-qualcommbe_ipq53xx/linux-6.18.52
TC=/home/builder/openwrt/staging_dir/toolchain-aarch64_cortex-a53_gcc-14.4.0_musl
export STAGING_DIR=/home/builder/openwrt/staging_dir
export PATH="$TC/bin:/home/builder/openwrt/staging_dir/host/bin:$PATH"
export ARCH=arm64 CROSS_COMPILE=aarch64-openwrt-linux-musl-
export KBUILD_BUILD_TIMESTAMP='2026-10-02 12:00:00 UTC'
export KBUILD_BUILD_USER=chatgpt KBUILD_BUILD_HOST=offline
[ -f "$OUT/patches-aplicados.json" ] || exit 2
[ ! -e "$OUT/Image" ] || { echo 'Already built; refusing overwrite'; exit 2; }
sha256sum "$SOURCE/.config" > "$OUT/config-original-antes.sha256"
mkdir -p "$WORK/initramfs-net"
aarch64-openwrt-linux-musl-gcc -static -Os -Wall -Wextra -Werror "$OWN/fontes/diag_init_net_v3.c" -o "$WORK/initramfs-net/init"
printf 'dir /dev 0755 0 0\ndir /proc 0755 0 0\ndir /sys 0755 0 0\ndir /tmp 1777 0 0\nfile /init %s/init 0755 0 0\nnod /dev/console 0600 0 0 c 5 1\n' "$WORK/initramfs-net" > "$WORK/initramfs-net.list"
cd "$WORK/linux"
make mrproper
cp "$OWN/artefatos/t7-net-20261002-v2/kernel.config" .config
for symbol in MTD MODULES DEVMEM NVMEM_SYSFS NVMEM_QCOM_QFPROM NVMEM_QCOM_SEC_QFPROM MMC SCSI PCI USB WLAN WIRELESS REMOTEPROC; do
 scripts/config --disable "$symbol"
done
scripts/config --set-str INITRAMFS_SOURCE "$WORK/initramfs-net.list"
scripts/config --set-str LOCALVERSION '-t7-net-20261002-v3'
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
aarch64-openwrt-linux-musl-gcc -E -nostdinc -undef -D__DTS__ -x assembler-with-cpp -I arch/arm64/boot/dts -I include "$OWN/fontes/t7-diagnostico-net-v3.dts" -o "$OUT/t7-diagnostico.preprocessed.dts"
dtc -I dts -O dtb -o "$OUT/t7-diagnostico.dtb" "$OUT/t7-diagnostico.preprocessed.dts"
python3 "$OWN/ferramentas/empacotar_candidato.py" "$OUT"
cp "$OWN/identidade-net-v3.json" "$OUT/identidade-net-v3.json"
python3 "$OWN/ferramentas/verificar_artefatos_rede_v3.py" "$OUT" "$OUT/initramfs.cpio"
sha256sum "$SOURCE/.config" > "$OUT/config-original-depois.sha256"
cmp "$OUT/config-original-antes.sha256" "$OUT/config-original-depois.sha256"
tar -czf "$OUT/fontes-kernel-isoladas.tar.gz" --exclude='*.o' --exclude='*.a' --exclude='*.cmd' --exclude='vmlinux' --exclude='Image' --exclude='System.map' -C "$WORK" linux
echo V3_BUILD_AND_OFFLINE_CHECKS_COMPLETE_NO_ROUTER_TEST
