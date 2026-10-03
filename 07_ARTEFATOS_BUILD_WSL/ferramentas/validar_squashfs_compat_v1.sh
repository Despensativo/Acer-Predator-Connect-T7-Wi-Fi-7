#!/bin/sh
set -eu
work=/home/builder/t7-squashfs-compat-20261002-v2
out='/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT/artefatos/squashfs-compat-20261002-v1'
tool="$work/squashfs4.2/squashfs-tools"
original='/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Backups_MTD/backup_predator_t7_ubi_rootfs.bin'
mkdir -p "$out"
[ ! -e "$work/version-only" ] || exit 1
"$tool/unsquashfs" -processors 1 -no-progress -d "$work/version-only" "$original" etc/version
cat "$work/version-only/etc/version"
mkdir "$work/synthetic"
printf 'Offline compatibility test only\n' > "$work/synthetic/test.txt"
"$tool/mksquashfs" "$work/synthetic" "$out/synthetic.squashfs" -noappend -nopad -b 256k -comp xz -processors 1 -Xpreset 9 -Xlc 0 -Xlp 2 -Xpb 2 -Xfb 64 -Xdict-size 256k -Xbcj ia64,arm,armthumb
"$tool/unsquashfs" -processors 1 -no-progress -d "$work/synthetic-check" "$out/synthetic.squashfs"
cmp "$work/synthetic/test.txt" "$work/synthetic-check/test.txt"
cp "$tool/mksquashfs" "$out/mksquashfs4-compat"
cp "$tool/unsquashfs" "$out/unsquashfs4-compat"
python3 - "$original" "$out/synthetic.squashfs" <<'PY'
import struct,sys,json,hashlib
items=[]
for name in sys.argv[1:]:
 with open(name,'rb') as f: b=f.read(110)
 size=struct.unpack_from('<H',b,96)[0]&0x7fff
 opts=b[98:98+size]
 items.append({'file':name,'option_size':size,'options_hex':opts.hex(),'decoded_dict_flags_bitopts_fb':list(struct.unpack('<IIHH',opts))})
assert items[0]['options_hex']==items[1]['options_hex'],items
print(json.dumps({'exact_compressor_options_match':True,'images':items},indent=2))
PY
