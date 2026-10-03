"""Gera candidato offline de retorno; não envia nem executa no roteador."""
from pathlib import Path
import json,hashlib,subprocess,re,struct,zlib,sys
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/"ferramentas"))
from verificar_artefatos_rede_v3 import fdt
def wsl(p):return "/mnt/h/"+str(p).replace(chr(92),"/").split(":/",1)[1]
def main():
 out=Path(json.loads((BASE/"retorno-slot1-atual.json").read_text())["folder"])
 manifest=json.loads((out/"backup-manifesto.json").read_text())
 for name in ("BOOTCONFIG","BOOTCONFIG1","APPSBLENV"):
  item=manifest["files"][name];blob=(out/item["file"]).read_bytes()
  assert len(blob)==item["bytes"] and hashlib.sha256(blob).hexdigest()==item["sha256"]
 assert manifest["files"]["bootconfigs_equal"]
 geometry=manifest["environment_crc_geometry"]
 assert geometry==[{"offset":0,"size":262144,"data_offset":4,"endian":"<"}]
 rawenv=(out/"APPSBLENV.bin").read_bytes()
 assert struct.unpack_from("<I",rawenv)[0]==(zlib.crc32(rawenv[4:262144])&0xffffffff)
 env=manifest["files"]["selected_environment"]
 assert env["bootcmd"]=="bootipq" and env["fsbootargs"] is None
 assert re.fullmatch(r"[A-Za-z0-9_=,.: /+-]+",env["bootargs"])
 blobs=[(out/"BOOTCONFIG.bin").read_bytes(),(out/"BOOTCONFIG1.bin").read_bytes()]
 assert all(len(x)==0x80000 and x[0x6c]==1 for x in blobs)
 guards=[]
 def g(command,label):
  guards.append((command,label));return "if "+command+"; then\necho T7_OK_"+label+"\nelse\necho T7_STOP_"+label+"\nexit 1\nfi\n"
 text="echo T7_RETURN_SLOT1_CANDIDATE\n"
 for idx,ptr in ((0,"0xAAAAAAAA"),(1,"0xBBBBBBBB")):
  text+=g("setenv filesize","CLEAR_SIZE_PRE"+str(idx))
  text+=g("imxtract 0x44000000 bc"+str(idx)+" 0x45000000","EXTRACT_PRE"+str(idx))
  text+=g("itest ${filesize} == 0x80000","SIZE_PRE"+str(idx))
  text+=g("cmp.b 0x45000000 "+ptr+" 0x80000","COMPARE_PRE"+str(idx))
 text+=g("nand device 0","NAND_DEVICE")
 for idx,ptr,offset in ((0,"0xAAAAAAAA","0x400000"),(1,"0xBBBBBBBB","0x480000")):
  text+=g("setenv filesize","CLEAR_SIZE_WRITE"+str(idx))
  text+=g("imxtract 0x44000000 bc"+str(idx)+" 0x45000000","EXTRACT_WRITE"+str(idx))
  text+=g("itest ${filesize} == 0x80000","SIZE_WRITE"+str(idx))
  text+=g("cmp.b 0x45000000 "+ptr+" 0x80000","COMPARE_WRITE"+str(idx))
  text+=g("nand erase "+offset+" 0x80000","ERASE"+str(idx))
  text+=g("nand write 0x45000000 "+offset+" 0x80000","WRITE"+str(idx))
  text+=g("nand read 0x45000000 "+offset+" 0x80000","READBACK"+str(idx))
  text+=g("cmp.b 0x45000000 "+ptr+" 0x80000","VERIFY"+str(idx))
 text+=g("setenv fsbootargs","ENV_ROOT")+g("setenv bootcmd bootipq","ENV_BOOTCMD")+g("setenv bootargs '"+env["bootargs"]+"'","ENV_BOOTARGS")+g("saveenv","ENV_SAVE")
 text+="echo T7_RETURN_VERIFIED\nreset\n"
 template=text
 def build(script):
  (out/"retorno-script.txt").write_text(script,encoding="utf8",newline="\n")
  its='/dts-v1/;\n/ { description = "Flash T7 guarded return to Slot 1"; #address-cells = <1>; images {\n'
  for name,file,typ in (("script","retorno-script.txt","script"),("bc0","BOOTCONFIG.bin","firmware"),("bc1","BOOTCONFIG1.bin","firmware")):
   its+=name+' { data = /incbin/("'+wsl(out/file)+'"); type = "'+typ+'"; compression = "none"; hash@1 { algo = "crc32"; }; };\n'
  its+='}; };\n';(out/"retorno.its").write_text(its,encoding="utf8",newline="\n")
  subprocess.run(["wsl.exe","-u","root","--","mkimage","-f",wsl(out/"retorno.its"),wsl(out/"retornar-slot1-CANDIDATO-NAO-ENVIAR.itb")],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  return (out/"retornar-slot1-CANDIDATO-NAO-ENVIAR.itb").read_bytes()
 first=build(template);first_nodes=fdt(first)
 pointers=[];seek=0
 for blob in blobs:
  pos=first.find(blob,seek);assert pos>=0;pointers.append(pos);seek=pos+len(blob)
 finaltext=template.replace("0xAAAAAAAA",f"0x{0x44000000+pointers[0]:08x}").replace("0xBBBBBBBB",f"0x{0x44000000+pointers[1]:08x}")
 final=build(finaltext);nodes=fdt(final)
 assert final[0x5c:0x60]==b"Flas" and len(template)==len(finaltext)
 for idx,blob in enumerate(blobs):assert final[pointers[idx]:pointers[idx]+len(blob)]==blob
 for name in ("script","bc0","bc1"):
  data=nodes["/images/"+name]["data"];h=nodes["/images/"+name+"/hash@1"];assert h["algo"]==b"crc32\0" and struct.pack(">I",zlib.crc32(data)&0xffffffff)==h["value"]
 assert nodes["/images/script"]["data"]==finaltext.encode()
 stub="C=0\nmock(){ C=$((C+1)); echo MOCK_CALL_$C:\"$*\"; [ $C -ne $FAIL_AT ]; }\n"
 for name in ("setenv","imxtract","itest","cmp.b","nand","saveenv","reset"):stub+=name+'(){ mock '+name+' "$@"; }\n'
 testpath=out/"teste-fluxo-simulado.sh"
 testpath.write_text(stub+finaltext,encoding="utf8",newline="\n")
 tests=[]
 for fail in range(len(guards)+1):
  proc=subprocess.run(["wsl.exe","-u","root","--","env","FAIL_AT="+str(fail),"bash",wsl(testpath)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  if fail==0:assert proc.returncode==0 and "reset" in proc.stdout and "T7_RETURN_VERIFIED" in proc.stdout, (proc.returncode,proc.stdout,proc.stderr)
  else:
   assert proc.returncode==1 and "T7_STOP_" in proc.stdout and not re.search(r"MOCK_CALL_\d+:reset",proc.stdout)
   calls=re.findall(r"MOCK_CALL_(\d+):",proc.stdout);assert int(calls[-1])==fail
  tests.append({"fail_at":fail,"passed":True,"simulated_only":True})
 report={"hardware_ready":False,"upload_authorized":False,"candidate":str(out/"retornar-slot1-CANDIDATO-NAO-ENVIAR.itb"),"bytes":len(final),"sha256":hashlib.sha256(final).hexdigest(),"payload_offsets":pointers,"backup_source":str(out/"backup-manifesto.json"),"offline_fit_checks_passed":True,"simulated_control_flow_tests":tests,"writes_if_executed":["BOOTCONFIG","BOOTCONFIG1","U-Boot selected environment"],"kernel_rootfs_written":False,"blockers":['BOOTCONFIG proc export differs from raw flash at offset 0x04 (2 vs 3); generation/selection semantics not verified',"HTTP source execution not confirmed by prior probe","RAM buffers and uploaded FIT retention not validated dynamically","imxtract filesize/cmp/nand semantics and bad-block behavior unverified on hardware","two BOOTCONFIG writes and saveenv not atomic","OEM handler may reset after a failed script; abort does not guarantee no reset"]}
 (out/"recuperacao-manifesto-PENDENTE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
 print("CANDIDATO",report["bytes"],report["sha256"],"TESTES_SIMULADOS",len(tests),"HARDWARE_READY",False)
if __name__=="__main__":main()
