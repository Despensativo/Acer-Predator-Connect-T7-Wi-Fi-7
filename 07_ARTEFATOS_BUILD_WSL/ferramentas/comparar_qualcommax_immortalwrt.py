import re,hashlib,json,collections
from pathlib import Path
base=Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
remote=base/'fontes/immortalwrt-qualcommax-auditoria-5233c153'
local=Path('/home/builder/openwrt/target/linux/qualcommbe/patches-6.18')
gl=base/'fontes/glinet-extraido-2365932733ca/target/linux/qualcommbe/patches-6.18'
k=Path('/home/builder/t7-chatgpt-work-20261002-v1/linux')
def norm(p):
 lines=p.read_text(errors='replace').splitlines(); active=False; result=[]
 for line in lines:
  if line.startswith('--- a/') or line.startswith('--- /dev/null'): active=True
  if active and not line.startswith(('@@','diff --git','index ')) and line!='-- ': result.append(line)
 return hashlib.sha256('\n'.join(result).encode()).hexdigest()
indexes=[]
for directory in (local,gl):
 d=collections.defaultdict(list)
 for p in directory.glob('*.patch'): d[norm(p)].append(p.name)
 indexes.append(d)
rows=[]
for p in sorted((remote/'patches').glob('*.patch')):
 n=norm(p)
 rows.append({'patch':p.name,'local_exact_payload_matches':indexes[0].get(n,[]),'gl_exact_payload_matches':indexes[1].get(n,[])})
markers={
 'drivers/remoteproc/qcom_q6v5_wcss_sec.c':[],
 'drivers/remoteproc/qcom_q6v5_mpd.c':[],
 'drivers/of/fdt.c':['bootargs-find-1'],
 'drivers/firmware/psci/psci.c':['of_machine_is_compatible("qcom,ipq6018")'],
 'drivers/mtd/nand/raw/nand_ids.c':['TH58NYG3S0HBAI4'],
 'drivers/mtd/nand/raw/nand_base.c':['min(4, type->id_len)'],
 'drivers/mtd/nand/spi/core.c':['min(3, info->devid.len)'],
 'drivers/spi/spi-qpic-snand.c':['ECC strength requirement of'],
 'drivers/phy/qualcomm/phy-qcom-uniphy-pcie-usb3-28lp.c':[],
}
checks={}
for name,strings in markers.items():
 p=k/name; txt=p.read_text(errors='replace') if p.exists() else ''
 checks[name]={'exists':p.exists(),'markers':{s:s in txt for s in strings}}
r={'normalization':'SHA256 of diff payload ignoring hunk positions and mail header; not equivalence proof for nonmatches','patches':rows,'local_source_checks':checks}
(remote/'comparacao-local-gl.json').write_text(json.dumps(r,indent=2)+'\n')
print('Exact normalized payload match count:',sum(bool(r['local_exact_payload_matches']) for r in rows),'local;',sum(bool(r['gl_exact_payload_matches']) for r in rows),'GL; total',len(rows))
for r in rows:
 if r['patch'].startswith(('0140','0150','0151','0152','0153','0154','0155','0185','0188','0400','0401','0411','0412','0803','0805','0903','0911','095')):
  print(r['patch'], 'LOCAL='+','.join(r['local_exact_payload_matches']),'GL='+','.join(r['gl_exact_payload_matches']))
print(json.dumps(checks,indent=2))
