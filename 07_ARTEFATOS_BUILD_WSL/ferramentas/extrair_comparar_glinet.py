import concurrent.futures, datetime, difflib, hashlib, json, pathlib, urllib.request
BASE=pathlib.Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
LOCAL=pathlib.Path('/home/builder/openwrt')
SHA='2365932733ca8ec3b346621d9cec2eb3df3b2cf3'
OUT=BASE/'fontes'/('glinet-extraido-'+SHA[:12])
OUT.mkdir(exist_ok=True)
headers={'User-Agent':'T7-offline-source-audit'}
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=45) as r:return r.read()
tree=json.loads(fetch('https://api.github.com/repos/perceival/openwrt-flint3/git/trees/'+SHA+'?recursive=1'))
if tree.get('truncated'):raise RuntimeError('Tree truncated')
entries=[e for e in tree['tree'] if e['type']=='blob' and (e['path'].startswith('target/linux/qualcommbe/') or (e['path'].startswith('target/linux/generic/') and any(k in e['path'].lower() for k in ['5332','53xx','qpic','squashfs','scm'])))]
def get(e):
    rel=e['path']; dest=OUT/rel; url='https://raw.githubusercontent.com/perceival/openwrt-flint3/'+SHA+'/'+rel
    data=dest.read_bytes() if dest.exists() else fetch(url)
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if blob!=e['sha']:raise RuntimeError('Git blob mismatch '+rel)
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    loc=LOCAL/rel; state='missing_local'; diffname=None
    if loc.is_file():
        localdata=loc.read_bytes(); state='identical' if data==localdata else 'different'
        if state=='different' and b'\0' not in data and b'\0' not in localdata:
            diffname=rel+'.diff'; d=BASE/'evidencias'/'diff-glinet-20261002'/diffname;d.parent.mkdir(parents=True,exist_ok=True)
            d.write_text(''.join(difflib.unified_diff(localdata.decode('utf8',errors='replace').splitlines(True),data.decode('utf8',errors='replace').splitlines(True),fromfile='local/'+rel,tofile='glinet/'+rel)),encoding='utf8')
    return dict(path=rel,size=len(data),git_blob_sha1=blob,sha256=hashlib.sha256(data).hexdigest(),comparison=state,diff=diffname,url=url)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: records=list(pool.map(get,entries))
localonly=[p.relative_to(LOCAL).as_posix() for p in (LOCAL/'target/linux/qualcommbe').rglob('*') if p.is_file() and not (OUT/p.relative_to(LOCAL)).exists()]
result=dict(collected_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_commit=SHA,local_source=str(LOCAL),hardware_tested=False,executed_downloaded_code=False,files=records,local_only=localonly)
summary={s:sum(r['comparison']==s for r in records) for s in ['identical','different','missing_local']}
result['summary']=summary
(OUT/'proveniencia-comparacao.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps(dict(summary=summary,total_bytes=sum(r['size'] for r in records),local_only=len(localonly)),indent=2))
print('DIFFERENT')
for r in records:
    if r['comparison']=='different':print(r['path'])
print('MISSING_LOCAL_TARGET')
for r in records:
    if r['comparison']=='missing_local' and '/qualcommbe/' in r['path']:print(r['path'])