#!/usr/bin/env python3
import shutil,difflib
from pathlib import Path
base=Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
src=Path('/home/builder/t7-squashfs-compat-20261002-v2/squashfs4.2')
dst=Path('/home/builder/t7-squashfs-compat-20261002-v3/squashfs4.2')
if dst.parent.exists(): raise SystemExit('Scratch v3 already exists; refusing overwrite')
shutil.copytree(src,dst)
p=dst/'squashfs-tools/unsquashfs.c'
old=p.read_text()
new=old.replace('#include <sys/types.h>','#include <sys/types.h>\n#include <sys/stat.h>\n#include <fcntl.h>',1)
needle='\n\t\t\tsym_count ++;'
assert old.count(needle)==1
block='''
			/* Restore the timestamp stored in the SquashFS inode on the
			 * link itself, including dangling links. Never touch its target.
			 */
			{
				struct timespec times[2] = {
					{ .tv_sec = i->time, .tv_nsec = 0 },
					{ .tv_sec = i->time, .tv_nsec = 0 }
				};
				if(utimensat(AT_FDCWD, pathname, times,
						AT_SYMLINK_NOFOLLOW) == -1) {
					ERROR("create_inode: failed to restore symlink "
						"timestamp on %s: %s\\n", pathname,
						strerror(errno));
					exit(EXIT_FAILURE);
				}
			}
'''
new=new.replace(needle,'\n'+block+needle,1)
p.write_text(new)
patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/squashfs-tools/unsquashfs.c',tofile='b/squashfs-tools/unsquashfs.c'))
(base/'fontes/squashfs-preservar-symlink-mtime.patch').write_text(patch)
validator=(base/'ferramentas/testar_roundtrip_squashfs.py').read_text()
validator=validator.replace('t7-squashfs-compat-20261002-v2','t7-squashfs-compat-20261002-v3').replace("('squashfs-roundtrip-'+STAMP)","('squashfs-roundtrip-mtime-'+STAMP)")
validator=validator.replace("RESULT['original_sha256_before']=sha(ORIGINAL)","RESULT['original_sha256_before']=sha(ORIGINAL)\n RESULT['extractor_sha256']=sha(TOOL/'unsquashfs')\n RESULT['builder_sha256']=sha(TOOL/'mksquashfs')\n RESULT['symlink_timestamp_fix']=True")
(base/'ferramentas/testar_roundtrip_squashfs_mtime.py').write_text(validator)
print('Scratch v3, patch and new validator prepared')
