from pathlib import Path
import json,urllib.request,hashlib,concurrent.futures,re
root=Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
dest=root/'fontes/immortalwrt-qualcommax-auditoria-5233c153'
j=json.loads((dest/'inventario.json').read_text(encoding='utf-8-sig'))
assert not j['truncated']
patches=dest/'patches'; patches.mkdir(exist_ok=True)
def download(f):
 u='https://raw.githubusercontent.com/immortalwrt/immortalwrt/'+j['commit']+'/'+f['path']
 data=urllib.request.urlopen(u,timeout=45).read()
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==f['sha']
 p=patches/Path(f['path']).name; p.write_bytes(data)
 txt=data.decode(errors='replace')
 touched=re.findall(r'^\+\+\+ b/(.+)$',txt,re.M)
 return {'name':p.name,'sha256':hashlib.sha256(data).hexdigest(),'source_url':u,'files_touched':touched,'ipq5332_mentions':len(re.findall('ipq5332',txt,re.I)),'bytes':len(data)}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex: rows=list(ex.map(download,j['files']))
(dest/'proveniencia.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Downloaded and Git blob verified:',len(rows),'files;',sum(x['bytes'] for x in rows),'bytes')
for r in rows:
 if r['ipq5332_mentions']: print(r['name'], 'ipq5332=',r['ipq5332_mentions'])
