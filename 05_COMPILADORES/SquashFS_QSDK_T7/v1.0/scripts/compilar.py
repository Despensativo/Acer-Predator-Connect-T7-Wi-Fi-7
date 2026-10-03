#!/usr/bin/env python3
"""Compila ferramentas locais em scratch novo; não instala nem acessa o roteador."""
import argparse,hashlib,json,subprocess,tarfile
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--work-dir',required=True,type=Path)
p.add_argument('--xz-prefix',type=Path,default=Path('/home/builder/openwrt/staging_dir/host'))
a=p.parse_args()
pkg=Path(__file__).resolve().parents[1]
m=json.loads((pkg/'manifesto.json').read_text())
for name,expected in m['inputs'].items():
 if hashlib.sha256((pkg/'fontes'/name).read_bytes()).hexdigest()!=expected: raise SystemExit('Input hash mismatch: '+name)
work=a.work_dir.resolve()
if work.exists(): raise SystemExit('Scratch exists; choose a new directory')
if str(work).startswith('/mnt/'): raise SystemExit('Use a Linux scratch outside /mnt; preserve Unix filesystem metadata')
lib=a.xz_prefix/'lib/liblzma.a'
if not lib.is_file() or not (a.xz_prefix/'include/lzma.h').is_file(): raise SystemExit('Missing liblzma.a or lzma.h; provide --xz-prefix')
if hashlib.sha256(lib.read_bytes()).hexdigest()!=m['liblzma_sha256']: raise SystemExit('liblzma differs from validated dependency')
work.mkdir(parents=True)
archive=pkg/'fontes/squashfs4.2.tar.gz'
with tarfile.open(archive) as t:
 for member in t.getmembers():
  bits=member.name.split('/')
  if member.name.startswith('/') or '..' in bits or bits[0]!='squashfs4.2' or not (member.isfile() or member.isdir()): raise SystemExit('Invalid archive member')
 t.extractall(work,filter='data')
source=work/'squashfs4.2'
with (work/'compilacao.log').open('wb') as log:
 for name in ('openwrt-v17.01.0-110-allow_static_liblzma.patch','openwrt-v17.01.0-160.patch','openwrt-v17.01.0-190-no_nonstatic_inline.patch','200-preservar-symlink-mtime.patch'):
  with (pkg/'fontes'/name).open('rb') as patch:
   subprocess.run(['patch','-p1','--batch'],cwd=source,stdin=patch,stdout=log,stderr=subprocess.STDOUT,check=True)
 flags='-I'+str(a.xz_prefix/'include')+' -fcommon -std=gnu11 -include sys/sysmacros.h -Wno-error=incompatible-pointer-types'
 subprocess.run(['make','-C',str(source/'squashfs-tools'),'-j2','GZIP_SUPPORT=1','COMP_DEFAULT=xz','XZ_SUPPORT=1','LZMA_XZ_SUPPORT=1','XATTR_SUPPORT=','LZMA_LIB='+str(lib),'EXTRA_CFLAGS='+flags,'mksquashfs','unsquashfs'],stdout=log,stderr=subprocess.STDOUT,check=True)
actual={n:hashlib.sha256((source/'squashfs-tools'/n).read_bytes()).hexdigest() for n in ('mksquashfs','unsquashfs')}
expected={'mksquashfs':m['binaries']['mksquashfs4-compat'],'unsquashfs':m['binaries']['unsquashfs4-compat-mtime']}
res={'work':str(work),'hashes':actual,'matches_validated_binaries':actual==expected}
(work/'resultado-compilacao.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
