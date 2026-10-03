#!/bin/sh
set -eu
reference='/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT/fontes/squashfs-qsdk-referencia-7267622a7417'
work=/home/builder/t7-squashfs-compat-20261002-v2
[ ! -e "$work" ] || { echo 'Scratch already exists; refusing overwrite'; exit 1; }
python3 - "$reference/squashfs4.2.tar.gz" <<'PY'
import sys,tarfile
with tarfile.open(sys.argv[1]) as t:
 for m in t.getmembers():
  p=m.name.split('/')
  if m.name.startswith('/') or '..' in p or p[0]!='squashfs4.2' or not (m.isfile() or m.isdir()):
   raise SystemExit('Unexpected archive member: '+m.name)
PY
mkdir "$work"
tar xzf "$reference/squashfs4.2.tar.gz" -C "$work"
cd "$work/squashfs4.2"
patch -p1 < "$reference/openwrt-v17.01.0-110-allow_static_liblzma.patch"
patch -p1 < "$reference/openwrt-v17.01.0-160.patch"
patch -p1 < "$reference/openwrt-v17.01.0-190-no_nonstatic_inline.patch"
make -C squashfs-tools -j2 GZIP_SUPPORT=1 COMP_DEFAULT=xz XZ_SUPPORT=1 LZMA_XZ_SUPPORT=1 XATTR_SUPPORT= LZMA_LIB=/home/builder/openwrt/staging_dir/host/lib/liblzma.a EXTRA_CFLAGS='-I/home/builder/openwrt/staging_dir/host/include -fcommon -std=gnu11 -include sys/sysmacros.h -Wno-error=incompatible-pointer-types' mksquashfs unsquashfs
