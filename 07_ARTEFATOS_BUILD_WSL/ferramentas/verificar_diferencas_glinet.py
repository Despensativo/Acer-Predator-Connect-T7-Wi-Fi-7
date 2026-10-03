import difflib, hashlib, json, pathlib, re
BASE=pathlib.Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT');LOCAL=pathlib.Path('/home/builder/openwrt');OUT=BASE/'fontes/glinet-extraido-2365932733ca';BUILD=pathlib.Path('/home/builder/t7-chatgpt-work-20261002-v1/linux')
pp=OUT/'target/linux/qualcommbe/patches-6.18';lp=LOCAL/'target/linux/qualcommbe/patches-6.18'
def stem(p):return re.sub(r'^\d+[a-z]*-','',p.name)
local={stem(p):p for p in lp.glob('*.patch')}
renamed=[]
for r in pp.glob('*.patch'):
    if stem(r) in local and r.name!=local[stem(r)].name:
        l=local[stem(r)];same=r.read_bytes()==l.read_bytes()
        renamed.append(dict(remote=r.name,local=l.name,byte_identical=same))
        if not same:
            d=BASE/'evidencias/diff-glinet-20261002'/('renumerado-'+r.name+'.diff')
            d.write_text(''.join(difflib.unified_diff(l.read_text().splitlines(True),r.read_text().splitlines(True),fromfile='local/'+l.name,tofile='glinet/'+r.name)))
print('RENAMED_BY_NAME',json.dumps(renamed,indent=2))
checks=[('drivers/net/ethernet/qualcomm/ppe/ppe_port.c','XGMAC_MTL_TXQ_TSF'),('drivers/net/ethernet/qualcomm/ppe/ppe_config.c','ipq5332_ppe_sch_bm_config'),('drivers/net/ethernet/qualcomm/ppe/ppe_config.c','ipq5332_ppe_bm_group_config'),('drivers/firmware/qcom/qcom_scm.c','QCOM_SCM_PIL_PAS_INIT_IMAGE_V2'),('drivers/clk/qcom/gcc-ipq5332.c','gpll0_out_aux'),('drivers/clk/qcom/nsscc-ipq5332.c','GCC_NSSNOC_NSSCC_CLK'),('arch/arm64/boot/dts/qcom/ipq5332.dtsi','qpic_nand:')]
evidence=[]
for rel,needle in checks:
    p=BUILD/rel; lines=p.read_text().splitlines();matches=[dict(line=i,text=t) for i,t in enumerate(lines,1) if needle in t];evidence.append(dict(file=rel,needle=needle,matches=matches));print('CHECK',rel,needle,matches)
for rel,start,end in [('drivers/net/ethernet/qualcomm/ppe/edma_rx.c',485,552),('drivers/net/ethernet/qualcomm/ppe/edma_rx.c',150,178),('drivers/net/ethernet/qualcomm/ppe/edma_rx.c',330,355),('arch/arm64/boot/dts/qcom/ipq5332.dtsi',130,225),('drivers/clk/qcom/gcc-ipq5332.c',0,0)]:
    if not start:continue
    lines=(BUILD/rel).read_text().splitlines();excerpt=[dict(line=i,text=lines[i-1]) for i in range(start,min(end,len(lines))+1)];evidence.append(dict(file=rel,excerpt=excerpt));
    if 'edma_rx' in rel:
        print(rel,start,end)
        for x in excerpt:print(x['line'],x['text'])
(OUT/'verificacao-fontes-kernel-local.json').write_text(json.dumps(dict(renamed_by_name=renamed,checks=evidence,hardware_tested=False),indent=2)+'\n')