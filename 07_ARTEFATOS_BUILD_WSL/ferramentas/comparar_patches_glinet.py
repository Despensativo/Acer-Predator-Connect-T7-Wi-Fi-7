import collections, difflib, hashlib, json, pathlib, re, subprocess
BASE=pathlib.Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
LOCAL=pathlib.Path('/home/builder/openwrt'); OUT=BASE/'fontes/glinet-extraido-2365932733ca'
manifest=json.loads((OUT/'proveniencia-comparacao.json').read_text())
def patchid(p):
    lines=p.read_text(errors='replace').splitlines()
    payload=[]; active=False
    for line in lines:
        if line.startswith('--- a/') or line.startswith('--- /dev/null'):active=True
        if active and not line.startswith('@@') and not line.startswith('diff --git') and not line.startswith('index ') and line!='-- ':
            payload.append(line)
    return hashlib.sha256(('\n'.join(payload)).encode()).hexdigest() if payload else hashlib.sha256(p.read_bytes()).hexdigest()
localpatches=list((LOCAL/'target/linux/qualcommbe/patches-6.18').glob('*.patch'))
ids=collections.defaultdict(list)
for p in localpatches:
    key=patchid(p)
    if key:ids[key].append(p.relative_to(LOCAL).as_posix())
sem=[]
for r in manifest['files']:
    if r['path'].endswith('.patch') and '/qualcommbe/' in r['path']:
        pid=patchid(OUT/r['path']);same=ids.get(pid,[])
        sem.append(dict(remote=r['path'],normalized_payload_sha256=pid,local_equivalent=same,status='equivalent' if same else 'no_equivalent_normalized_payload'))
(OUT/'comparacao-patches-semantica.json').write_text(json.dumps(sem,indent=2)+'\n')
print('NORMALIZED_PAYLOAD_SUMMARY',dict(collections.Counter(r['status'] for r in sem)))
for r in sem:
    if r['local_equivalent'] and r['remote'] not in r['local_equivalent']:print('RENAMED',pathlib.Path(r['remote']).name,'=>',','.join(pathlib.Path(x).name for x in r['local_equivalent']))
print('LOCAL_ONLY',json.dumps(manifest['local_only'],indent=2))
acer=LOCAL/'target/linux/qualcommbe/dts/ipq5332-acer-predator-t7.dts'
for other in ['ipq5332-gl-be6500.dts','ipq5332-gl-be9300.dts']:
    d=''.join(difflib.unified_diff(acer.read_text().splitlines(True),(OUT/'target/linux/qualcommbe/dts'/other).read_text().splitlines(True),fromfile='acer/'+acer.name,tofile='glinet/'+other))
    (BASE/'evidencias'/'diff-glinet-20261002'/('acer-vs-'+other+'.diff')).write_text(d)