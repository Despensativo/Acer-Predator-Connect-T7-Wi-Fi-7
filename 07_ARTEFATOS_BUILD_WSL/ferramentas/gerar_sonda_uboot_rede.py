"""Gera apenas prova de comunicação OEM; não faz upload, download de kernel ou bootm."""
from pathlib import Path
import json,hashlib,subprocess,uuid
base=Path(__file__).resolve().parents[1]
session=uuid.uuid4().hex
out=base/'artefatos'/('sonda-uboot-rede-'+session)
out.mkdir(exist_ok=False)
name='t7-probe-'+session+'.bin'
script='\n'.join(['echo T7_NETWORK_PROBE_ONLY','setenv ipaddr 192.168.1.1','setenv serverip 192.168.1.5',f'if tftpput 0x44000000 0x40 {name}; then','echo T7_CHECKPOINT_SENT','else','echo T7_CHECKPOINT_FAILED','fi','exit 0'])+'\n'
(out/'script.txt').write_text(script)
its='''/dts-v1/;
/ {
 description = "Flash T7 network probe";
 #address-cells = <1>;
 images { script {
  description = "Read upload buffer; no kernel boot or persistent commands";
  data = /incbin/("script.txt");
  type = "script"; arch = "arm"; os = "linux"; compression = "none";
  hash@1 { algo = "crc32"; };
 }; };
};
'''
(out/'sonda.its').write_text(its)
subprocess.run(['mkimage','-f','sonda.its','sonda.itb.PENDING'],cwd=out,check=True)
b=(out/'sonda.itb.PENDING').read_bytes()
assert b[0x5c:0x60]==b'Flas'
# Preserve the size of the previously inspected OEM script launcher; not a new claim of hardware acceptance.
b+=bytes(max(0,33582-len(b)))
assert len(b)==33582
(out/'sonda.itb.PENDING').write_bytes(b)
profile={'status':'offline_probe_pending_hardware_preflight','hardware_ready':False,'session_id':session,'mode':'upload_buffer_readback_only','server_ip':'192.168.1.5','router_ip':'192.168.1.1','current_service_ip_reported':'192.168.73.2','current_slot_verified':False,'adapter_link_verified':False,'filename':name,'expected_header_hex':b[:64].hex(),'launcher':{'path':str((out/'sonda.itb.PENDING').relative_to(base)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'oem_marker_offset':'0x5c','oem_marker':'Flas'},'no_kernel_download':True,'no_bootm':True,'no_saveenv':True,'script_returns_to_oem_handler':True,'warning':'OEM handler may reset after source returns; current slot and recovery must be confirmed before test','validated_static_memory_read':'0x44000000 first 64 bytes of existing HTTP upload buffer; no new fixed scratch address'}
(out/'sessao-sonda-PENDENTE.json').write_text(json.dumps(profile,indent=2)+'\n')
print('Offline probe generated:',out)
