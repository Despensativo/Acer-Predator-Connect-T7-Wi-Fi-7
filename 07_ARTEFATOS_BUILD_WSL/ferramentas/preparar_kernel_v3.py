from pathlib import Path
import json,subprocess,hashlib,uuid
base=Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
work=Path('/home/builder/t7-chatgpt-work-20261002-v3')
out=base/'artefatos/t7-net-20261002-v3'
if work.exists() or out.exists(): raise SystemExit('v3 already exists; refusing overwrite')
work.mkdir(); out.mkdir()
source=Path('/home/builder/t7-chatgpt-work-20261002-v1/linux')
subprocess.run(['rsync','-a','--exclude=*.o','--exclude=*.a','--exclude=*.ko','--exclude=*.cmd','--exclude=/vmlinux*','--exclude=/arch/arm64/boot/Image*','--exclude=.git',str(source)+'/',str(work/'linux')+'/'],check=True)
gl=base/'fontes/glinet-extraido-2365932733ca/target/linux/qualcommbe/patches-6.18'
patches=[next(gl.glob(prefix+'*')) for prefix in ['0371-net','0372-net','0374-net','0375-net','0376-net','0410-net']]
patches.append(base/'fontes/referencia-immortalwrt-20261002/0362-net-ethernet-qualcomm-ppe-fix-rx-dma-mapping-direction.patch')
records=[]
for p in patches:
 with p.open('rb') as f:
  r=subprocess.run(['patch','--dry-run','-p1','--batch','--fuzz=0'],cwd=work/'linux',stdin=f,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (out/(p.name+'.dryrun.log')).write_bytes(r.stdout)
 if r.returncode: raise SystemExit('Patch dryrun failed: '+p.name)
 with p.open('rb') as f:
  r=subprocess.run(['patch','-p1','--batch','--fuzz=0'],cwd=work/'linux',stdin=f,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (out/(p.name+'.apply.log')).write_bytes(r.stdout)
 if r.returncode: raise SystemExit('Patch apply failed: '+p.name)
 records.append({'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'applied_to_isolated_scratch':True})
(out/'patches-aplicados.json').write_text(json.dumps(records,indent=2)+'\n')
identity=json.loads((base/'identidade-net-v2.json').read_text())
identity.update(identity=uuid.uuid4().hex,build='t7-net-20261002-v3',hardware_ready=False)
(base/'identidade-net-v3.json').write_text(json.dumps(identity,indent=2)+'\n')
(base/'fontes/identidade-net-v3.h').write_text('#define T7_NET_ID "'+identity['identity']+'"\n')
for src,dst in [('fontes/diag_init_net_v2.c','fontes/diag_init_net_v3.c'),('fontes/t7-diagnostico-net-v2.dts','fontes/t7-diagnostico-net-v3.dts'),('ferramentas/coletar_rede_v2.py','ferramentas/coletar_rede_v3.py'),('ferramentas/verificar_identidade_rede_local.py','ferramentas/verificar_identidade_rede_v3_local.py'),('ferramentas/verificar_artefatos_rede_v2.py','ferramentas/verificar_artefatos_rede_v3.py')]:
 s=(base/src).read_text().replace('t7-net-20261002-v2','t7-net-20261002-v3').replace('identidade-net-v2','identidade-net-v3').replace('coletar_rede_v2','coletar_rede_v3')
 (base/dst).write_text(s)
print('v3 scratch prepared with',len(records),'patches, without fuzz')
