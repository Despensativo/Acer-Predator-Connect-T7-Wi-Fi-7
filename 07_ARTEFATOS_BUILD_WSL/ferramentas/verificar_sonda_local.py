from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from receber_sonda_uboot import validate_profile,validate_record
base=Path(__file__).resolve().parents[1]
files=list((base/'artefatos').glob('sonda-uboot-rede-*/sessao-sonda-PENDENTE.json'))
assert len(files)==1
p=json.loads(files[0].read_text()); header=validate_profile(p)
assert validate_record(header,header)['linux_execution_proven'] is False
for bad in (header[:-1],bytes(64),b'x'+header[1:]):
 try: validate_record(bad,header)
 except ValueError: pass
 else: raise AssertionError('Invalid checkpoint accepted')
assert p['hardware_ready'] is False
print('Sonda: 4 verificações passaram, somente memória; sem sockets ou hardware.')
