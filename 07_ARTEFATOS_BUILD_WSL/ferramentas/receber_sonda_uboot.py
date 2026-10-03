"""Receptor de sonda U-Boot. Sem upload HTTP, RRQ, boot ou escrita no roteador."""
import argparse,hashlib,ipaddress,json,socket,struct,time,uuid
from pathlib import Path
from tftp_restrito import read_request,receive_record,error
BASE=Path(__file__).resolve().parents[1]
def validate_profile(p):
 blob=(BASE/p['launcher']['path']).read_bytes()
 if len(blob)!=p['launcher']['bytes'] or hashlib.sha256(blob).hexdigest()!=p['launcher']['sha256']: raise ValueError('Launcher hash/size mismatch')
 if blob[0x5c:0x60]!=b'Flas' or blob[:64].hex()!=p['expected_header_hex']: raise ValueError('OEM marker/header mismatch')
 if p['mode']!='upload_buffer_readback_only' or not p['no_bootm'] or not p['no_kernel_download'] or not p['no_saveenv']: raise ValueError('Wrong probe mode')
 return blob[:64]
def validate_record(record,expected):
 if len(record)!=64 or record!=expected: raise ValueError('Returned upload header mismatch')
 return {'probe_execution_evidence':True,'linux_execution_proven':False,'returned_bytes':64}
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--manifesto',type=Path,required=True)
 parser.add_argument('--executar',action='store_true')
 a=parser.parse_args(); p=json.loads(a.manifesto.read_text(encoding='utf-8-sig'))
 expected=validate_profile(p)
 if not a.executar: print('Sonda conferida offline. Nenhum socket aberto.'); return
 if not p.get('hardware_ready') or not p.get('current_slot_verified') or not p.get('adapter_link_verified') or not p.get('recovery_confirmed'): raise SystemExit('PENDENTE: slot, enlace e recuperação não confirmados; não iniciar teste')
 local=str(ipaddress.IPv4Address(p['server_ip'])); router=str(ipaddress.IPv4Address(p['router_ip']))
 folder=BASE/'sessoes-sonda'/uuid.uuid4().hex; folder.mkdir(parents=True)
 print('Recebendo somente WRQ da sonda revisada; nenhum upload ou comando remoto é enviado.')
 with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as listener:
  listener.bind((local,69)); listener.settimeout(1); end=time.monotonic()+300
  while time.monotonic()<end:
   try: packet,peer=listener.recvfrom(2048)
   except socket.timeout: continue
   if peer[0]!=router: continue
   with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as transfer:
    transfer.bind((local,0)); transfer.settimeout(0.5)
    try:
     opcode,name=read_request(packet)
     if opcode!=2 or name!=p['filename']: raise ValueError('Only the expected probe WRQ is allowed')
     record=receive_record(transfer,peer); result=validate_record(record,expected)
     (folder/'header-returned.bin').write_bytes(record)
     (folder/'resultado.json').write_text(json.dumps(result|{'session':p['session_id'],'peer':peer,'pc_time':time.time()},indent=2)+'\n')
     ack=struct.pack('!HH',4,1); transfer.sendto(ack,peer)
     linger=time.monotonic()+2
     while time.monotonic()<linger:
      try: duplicate,sender=transfer.recvfrom(2048)
      except socket.timeout: continue
      if sender==peer and duplicate==struct.pack('!HH',3,1)+record: transfer.sendto(ack,peer)
     print('SONDA_CONFIRMADA: source/tftpput chegaram ao PC; execução Linux não comprovada.')
     return
    except (ValueError,TimeoutError,OSError) as exc:
     error(transfer,peer,0,'Probe rejected')
     (folder/'erro.json').write_text(json.dumps({'error':str(exc)})+'\n')
 print('SEM_SONDA: não conclui falha ARM64; Linux não foi iniciado neste ensaio.')
if __name__=='__main__': main()
