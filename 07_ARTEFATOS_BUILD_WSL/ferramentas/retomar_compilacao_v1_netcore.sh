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
rsync -a --ignore-existing --exclude='*.o' --exclude='*.a' --exclude='*.ko' --exclude='*.cmd' --exclude='/vmlinux*' --exclude='/arch/arm64/boot/Image*' --exclude='.git' "$SOURCE/" "$WORK/linux/"
cd "$WORK/linux"
scripts/config --enable NET --disable NETDEVICES
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
