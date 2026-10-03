#!/usr/bin/env python3
"""Round-trip offline do backup SquashFS; nunca acessa o roteador."""
import hashlib,json,os,stat,struct,subprocess,sys,time
from pathlib import Path
BASE=Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
ORIGINAL=BASE.parent/'Backups_MTD/backup_predator_t7_ubi_rootfs.bin'
TOOL=Path('/home/builder/t7-squashfs-compat-20261002-v3/squashfs4.2/squashfs-tools')
STAMP=time.strftime('%Y%m%d-%H%M%S')
WORK=Path('/home/builder')/('t7-squashfs-roundtrip-'+STAMP)
OUT=BASE/'artefatos'/('squashfs-roundtrip-mtime-'+STAMP)
WORK.mkdir(); OUT.mkdir()
RESULT={'status':'running','router_tested':False,'original':str(ORIGINAL),'scratch':str(WORK),'output':str(OUT)}
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def run(label,args):
 log=OUT/(label+'.log')
 with open(log,'wb') as f:
  p=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,cwd=WORK)
 RESULT[label+'_exit']=p.returncode
 print(label+': exit '+str(p.returncode),flush=True)
 if p.returncode: raise RuntimeError(label+' failed; consult '+str(log))
def inventory(root):
 entries={}; groups={}; counts={}
 for here,dirs,files in os.walk(root,followlinks=False):
  for path in [Path(here)] + [Path(here)/n for n in files] + [Path(here)/n for n in dirs if (Path(here)/n).is_symlink()]:
   rel=str(path.relative_to(root)); s=path.lstat(); typ=stat.S_IFMT(s.st_mode)
   kind={stat.S_IFREG:'file',stat.S_IFDIR:'directory',stat.S_IFLNK:'symlink',stat.S_IFCHR:'char',stat.S_IFBLK:'block',stat.S_IFIFO:'fifo',stat.S_IFSOCK:'socket'}.get(typ,'unknown')
   data={'type':kind,'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid,'mtime':int(s.st_mtime)}
   if kind=='file':
    data.update(size=s.st_size,sha256=sha(path))
    groups.setdefault((s.st_dev,s.st_ino),[]).append(rel)
   elif kind=='symlink': data['target']=os.readlink(path)
   elif kind in ('char','block'): data['device']=[os.major(s.st_rdev),os.minor(s.st_rdev)]
   entries[rel]=data; counts[kind]=counts.get(kind,0)+1
 return entries,sorted(sorted(g) for g in groups.values() if len(g)>1),counts
def header(path):
 with open(path,'rb') as f: b=f.read(110)
 n=struct.unpack_from('<H',b,96)[0]&0x7fff
 return {'bytes_used':struct.unpack_from('<Q',b,40)[0],'compression':struct.unpack_from('<H',b,20)[0],'block_size':struct.unpack_from('<I',b,12)[0],'flags':struct.unpack_from('<H',b,24)[0],'options_hex':b[98:98+n].hex(),'file_bytes':path.stat().st_size}
try:
 RESULT['original_sha256_before']=sha(ORIGINAL)
 RESULT['extractor_sha256']=sha(TOOL/'unsquashfs')
 RESULT['builder_sha256']=sha(TOOL/'mksquashfs')
 RESULT['symlink_timestamp_fix']=True
 run('01-extract-original',[TOOL/'unsquashfs','-processors','1','-no-progress','-d',WORK/'source',ORIGINAL])
 original,links_a,counts_a=inventory(WORK/'source')
 image=OUT/'rootfs-rebuilt-offline.squashfs'
 run('02-rebuild',[TOOL/'mksquashfs',WORK/'source',image,'-noappend','-nopad','-no-progress','-b','256k','-comp','xz','-processors','2','-Xpreset','9','-Xlc','0','-Xlp','2','-Xpb','2','-Xfb','64','-Xdict-size','256k','-Xbcj','ia64,arm,armthumb'])
 run('03-extract-rebuilt',[TOOL/'unsquashfs','-processors','1','-no-progress','-d',WORK/'rebuilt',image])
 rebuilt,links_b,counts_b=inventory(WORK/'rebuilt')
 changed=[{'path':p,'fields':[k for k in set(original[p])|set(rebuilt[p]) if original[p].get(k)!=rebuilt[p].get(k)]} for p in sorted(original.keys()&rebuilt.keys()) if original[p]!=rebuilt[p]]
 RESULT.update(original_header=header(ORIGINAL),rebuilt_header=header(image),counts_original=counts_a,counts_rebuilt=counts_b,missing=sorted(original.keys()-rebuilt.keys()),extra=sorted(rebuilt.keys()-original.keys()),changed=changed,hardlink_groups_original=len(links_a),hardlink_groups_rebuilt=len(links_b),hardlinks_identical=links_a==links_b,rebuilt_sha256=sha(image))
 RESULT['original_sha256_after']=sha(ORIGINAL)
 RESULT['original_unchanged']=RESULT['original_sha256_before']==RESULT['original_sha256_after']
 RESULT['compressor_options_identical']=RESULT['original_header']['options_hex']==RESULT['rebuilt_header']['options_hex']
 RESULT['content_and_metadata_identical']=not RESULT['missing'] and not RESULT['extra'] and not changed and links_a==links_b
 capacity=39870464
 RESULT['reference_volume_capacity_bytes']=capacity
 RESULT['fits_reference_volume']=image.stat().st_size<=capacity
 RESULT['reference_volume_margin_bytes']=capacity-image.stat().st_size
 RESULT['status']='passed' if all(RESULT[k] for k in ('original_unchanged','compressor_options_identical','content_and_metadata_identical','fits_reference_volume')) else 'differences'
except Exception as e:
 RESULT['status']='failed'; RESULT['error']=str(e)
finally:
 (OUT/'resultado.json').write_text(json.dumps(RESULT,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({k:v for k,v in RESULT.items() if k != 'changed'} | {'changed_entries':len(RESULT.get('changed',[]))},indent=2,ensure_ascii=False),flush=True)
sys.exit(0 if RESULT['status']=='passed' else 1)
