"""Backup somente leitura; nÃ£o executa comandos de seleÃ§Ã£o ou escrita no roteador."""
from pathlib import Path
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)
import telnetlib,re,base64,json,hashlib,datetime,struct,zlib
BASE=Path(__file__).resolve().parents[1]
def main():
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
 out=BASE/"artefatos"/("retorno-slot1-"+stamp);out.mkdir(exist_ok=False)
 results={}
 with telnetlib.Telnet("192.168.73.2",23,timeout=5) as t:
  i,_,_=t.expect([br"(?i)login:\s*$",br"(?m)[#$] ?$"],5)
  if i!=1:raise SystemExit("Shell nÃ£o confirmado; nenhuma credencial ou alteraÃ§Ã£o enviada")
  for label,cmd,expected in [("BOOTCONFIG","dd if=/dev/mtd3 bs=65536 count=8 2>/dev/null",524288),("BOOTCONFIG1","dd if=/dev/mtd4 bs=65536 count=8 2>/dev/null",524288),("APPSBLENV","dd if=/dev/mtd13 bs=65536 count=8 2>/dev/null",524288),("export-bootconfig0","cat /proc/boot_info/bootconfig0/getbinary_bootconfig",None),("export-bootconfig1","cat /proc/boot_info/bootconfig1/getbinary_bootconfig",None)]:
   start="T7_BEGIN_"+label;end="T7_END_"+label
   command="printf " + repr(chr(10)+start+chr(10)) + "; " + cmd + " | base64; printf " + repr(chr(10)+end+chr(10)) + chr(10)
   t.write(command.encode())
   i,_,data=t.expect([("(?m)^"+re.escape(end)+r"\r*\n").encode()],40)
   if i<0:raise RuntimeError("Backup incompleto: "+label)
   clean=data.replace(b"\r",b"")
   match=re.search(("(?m)^"+re.escape(start)+r"\n([A-Za-z0-9+/=\n]+)\n"+re.escape(end)+"$").encode(),clean)
   if not match:raise RuntimeError("Envelope invÃ¡lido: "+label)
   blob=base64.b64decode(match.group(1),validate=False)
   if expected is not None and len(blob)!=expected:raise RuntimeError("Comprimento divergente: "+label)
   if not blob or len(blob)>1048576:raise RuntimeError("Comprimento invÃ¡lido")
   p=out/(label+".bin");p.write_bytes(blob)
   results[label]={"file":p.name,"bytes":len(blob),"sha256":hashlib.sha256(blob).hexdigest()}
   print(label,len(blob),results[label]["sha256"],flush=True)
  t.write(b"exit\n")
 for name in ("BOOTCONFIG","BOOTCONFIG1","export-bootconfig0","export-bootconfig1"):
  b=(out/results[name]["file"]).read_bytes()
  if b[:4]!=bytes.fromhex("a0a1a2a3") or len(b)<=0x6c or b[0x6c]!=1:raise RuntimeError("Backup nÃ£o representa seleÃ§Ã£o original esperada")
 results["bootconfigs_equal"]=(out/"BOOTCONFIG.bin").read_bytes()==(out/"BOOTCONFIG1.bin").read_bytes()
 env=(out/"APPSBLENV.bin").read_bytes();selected={}
 for key in (b"bootcmd",b"bootargs",b"fsbootargs",b"ipaddr",b"serverip"):
  token=key+b"=";pos=env.find(token);selected[key.decode()]=None if pos<0 else env[pos+len(token):env.index(0,pos)].decode("ascii")
 results["selected_environment"]=selected
 geometry=[{"offset":0,"size":262144,"data_offset":4,"endian":"<"}]
 if struct.unpack_from("<I",env)[0]!=(zlib.crc32(env[4:262144])&0xffffffff):raise RuntimeError("CRC do ambiente diverge da geometria confirmada")
 report={"environment_crc_geometry":geometry,"read_only":True,"host":"192.168.73.2","files":results,"upload_authorized":False,"hardware_ready":False,"boot_selection_changed":False}
 (out/"backup-manifesto.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (BASE/"retorno-slot1-atual.json").write_text(json.dumps({"folder":str(out)},indent=2)+"\n",encoding="utf8")
 print("BACKUP_COMPLETO",out,flush=True)
if __name__=="__main__":main()
