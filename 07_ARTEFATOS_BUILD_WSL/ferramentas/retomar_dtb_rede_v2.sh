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
cd "$WORK/linux"
aarch64-openwrt-linux-musl-gcc -E -nostdinc -undef -D__DTS__ -x assembler-with-cpp -I arch/arm64/boot/dts -I include "$OWN/fontes/t7-diagnostico-net-v2.dts" -o "$OUT/t7-diagnostico.preprocessed.dts"
dtc -I dts -O dtb -o "$OUT/t7-diagnostico.dtb" "$OUT/t7-diagnostico.preprocessed.dts"
python3 "$OWN/ferramentas/empacotar_candidato.py" "$OUT"
cp "$OWN/identidade-net-v2.json" "$OUT/identidade-net-v2.json"
tar -czf "$OUT/fontes-kernel-isoladas.tar.gz" --exclude='*.o' --exclude='*.a' --exclude='*.cmd' --exclude='vmlinux' --exclude='Image' --exclude='System.map' -C "$WORK" linux
echo COMPILACAO_REDE_CONCLUIDA_SEM_HARDWARE
