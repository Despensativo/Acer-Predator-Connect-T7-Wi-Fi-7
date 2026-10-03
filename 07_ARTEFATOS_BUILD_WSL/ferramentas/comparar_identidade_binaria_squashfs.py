from pathlib import Path
import hashlib,json,struct,collections
base=Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
original=base.parent/'Backups_MTD/backup_predator_t7_ubi_rootfs.bin'
rebuilt=base/'artefatos/squashfs-roundtrip-mtime-20261002-212028/rootfs-rebuilt-offline.squashfs'
a=original.read_bytes(); b=rebuilt.read_bytes()
def hashes(x): return {'md5':hashlib.md5(x).hexdigest(),'sha256':hashlib.sha256(x).hexdigest()}
def fields(x):
 return {'magic':x[:4].hex(),'inodes':struct.unpack_from('<I',x,4)[0],'mkfs_time':struct.unpack_from('<I',x,8)[0],'block_size':struct.unpack_from('<I',x,12)[0],'fragments':struct.unpack_from('<I',x,16)[0],'compression':struct.unpack_from('<H',x,20)[0],'flags':struct.unpack_from('<H',x,24)[0],'bytes_used':struct.unpack_from('<Q',x,40)[0],'inode_table_start':struct.unpack_from('<Q',x,64)[0],'directory_table_start':struct.unpack_from('<Q',x,72)[0],'fragment_table_start':struct.unpack_from('<Q',x,80)[0],'options_hex':x[98:110].hex()}
fa=fields(a); fb=fields(b)
common=min(len(a),len(b)); differences=sum(x!=y for x,y in zip(a,b))
first=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),None)
data_first=next((i for i in range(110,common) if a[i]!=b[i]),None)
tail=a[fa['bytes_used']:]
normalized={}
for fill in (0,255):
 normalized[str(fill)]=hashes(b+bytes([fill])*(len(a)-len(b)))
evidence=json.loads((base/'artefatos/squashfs-roundtrip-mtime-20261002-212028/resultado.json').read_text())
assert evidence['status']=='passed'
assert evidence['original_sha256_after']==hashes(a)['sha256']
assert evidence['rebuilt_sha256']==hashes(b)['sha256']
reference='022605865983843c69395859b9ee7e64'
r={'original_file':str(original),'rebuilt_file':str(rebuilt),'user_reported_slot_md5':reference,'original_file_hashes':hashes(a),'rebuilt_file_hashes':hashes(b),'local_backup_matches_reported_slot_md5':hashlib.md5(a).hexdigest()==reference,'original_bytes':len(a),'rebuilt_bytes':len(b),'binary_identical':a==b,'different_bytes_in_common_span':differences,'first_difference_offset':first,'first_difference_after_options_offset':data_first,'original_header':fa,'rebuilt_header':fb,'header_differences':{k:{'original':fa[k],'rebuilt':fb[k]} for k in fa if fa[k]!=fb[k]},'original_payload_hashes':hashes(a[:fa['bytes_used']]),'rebuilt_payload_hashes':hashes(b[:fb['bytes_used']]),'original_tail_bytes':len(tail),'original_tail_byte_counts':dict(collections.Counter(tail)),'rebuilt_padded_to_original_length_hashes':normalized,'padding_only_explains_difference':any(h['md5']==hashlib.md5(a).hexdigest() for h in normalized.values()),'content_metadata_roundtrip_verified':True,'content_metadata_evidence':'artefatos/squashfs-roundtrip-mtime-20261002-212028/resultado.json','router_accessed':False}
p=base/'evidencias/comparacao-binaria-squashfs-20261002.json'
p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
