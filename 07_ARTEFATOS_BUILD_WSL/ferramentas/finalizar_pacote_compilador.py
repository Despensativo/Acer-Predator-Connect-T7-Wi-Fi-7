from pathlib import Path
import hashlib,json,zipfile,ast
base=Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
pkg=base/'COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0'
for p in (pkg/'scripts').glob('*.py'): ast.parse(p.read_text())
r=json.loads((pkg/'evidencias/recompilacao-do-pacote.json').read_text())
assert r['matches_validated_binaries']
assert json.loads((pkg/'evidencias/resultado.json').read_text())['status']=='passed'
files=sorted(p for p in pkg.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
lines=[]
for p in files:
 lines.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(pkg).as_posix())
(pkg/'SHA256SUMS').write_text('\n'.join(lines)+'\n')
zip_path=pkg.parent/'compilador-oficial-squashfs-t7-v1.0.zip'
if zip_path.exists(): raise SystemExit('ZIP exists; refusing overwrite')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(pkg.rglob('*')):
  if p.is_file(): z.write(p,p.relative_to(pkg.parent).as_posix())
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 for p in pkg.rglob('*'):
  if p.is_file(): assert z.read(p.relative_to(pkg.parent).as_posix())==p.read_bytes()
h=hashlib.sha256(zip_path.read_bytes()).hexdigest()
(zip_path.parent/(zip_path.name+'.sha256')).write_text(h+'  '+zip_path.name+'\n')
(pkg.parent/'README.md').write_text('''# Compilador oficial SquashFS T7

Versão adotada como referência interna do projeto: **v1.0**.
Não é ferramenta homologada ou publicada pela Acer.

Comece por [LEIA-PRIMEIRO.md](v1.0/LEIA-PRIMEIRO.md).
Para outra IA, compartilhe [PARA-OUTRA-IA.md](v1.0/PARA-OUTRA-IA.md) ou o [pacote ZIP](compilador-oficial-squashfs-t7-v1.0.zip).

A recompilação do pacote produziu os mesmos hashes dos dois binários validados no teste completo. A integridade do pacote e do ZIP foi conferida. Nenhum teste no aparelho.
''')
print(json.dumps({'package_files':len(files)+1,'zip_bytes':zip_path.stat().st_size,'zip_sha256':h,'zip_contents_verified':True},indent=2))
