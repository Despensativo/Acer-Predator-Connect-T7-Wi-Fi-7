from pathlib import Path
import shutil,json,hashlib
base=Path('/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT')
pkg=base/'COMPILADOR-OFICIAL-SQUASHFS-T7/v1.0'
if pkg.exists(): raise SystemExit('Package exists; refusing overwrite')
for d in ('bin','fontes','scripts','evidencias','documentacao'): (pkg/d).mkdir(parents=True,exist_ok=True)
ref=base/'fontes/squashfs-qsdk-referencia-7267622a7417'
for n in ('squashfs4.2.tar.gz','openwrt-v17.01.0-110-allow_static_liblzma.patch','openwrt-v17.01.0-160.patch','openwrt-v17.01.0-190-no_nonstatic_inline.patch'):
 shutil.copy2(ref/n,pkg/'fontes'/n)
shutil.copy2(base/'fontes/squashfs-preservar-symlink-mtime.patch',pkg/'fontes/200-preservar-symlink-mtime.patch')
art=base/'artefatos/squashfs-compat-mtime-20261002-v2'
for n in ('mksquashfs4-compat','unsquashfs4-compat-mtime'): shutil.copy2(art/n,pkg/'bin'/n)
shutil.copy2(art/'COPYING',pkg/'COPYING')
for n in ('CORRECAO-SYMLINK-MTIME-TESTE-2026-10-02.md','TESTE-SQUASHFS-COMPLETO-2026-10-02.md','MKSQUASHFS-COMPATIVEL-ACER-2026-10-02.md'):
 shutil.copy2(base/n,pkg/'documentacao'/n)
result=base/'artefatos/squashfs-roundtrip-mtime-20261002-212028'
for n in ('resultado.json','01-extract-original.log','02-rebuild.log','03-extract-rebuilt.log'): shutil.copy2(result/n,pkg/'evidencias'/n)
shutil.copy2(base/'logs/squashfs-symlink-mtime-compilacao.log',pkg/'evidencias/compilacao-validada.log')
def write(n,s): (pkg/n).write_text(s.strip()+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'version':'1.0','name':'Compilador oficial SquashFS T7 — referência interna do projeto','acer_official':False,'date':'2026-10-02','openwrt_commit':'ac733df99c78f54b4cf9a8710f70a506f73e66fc','netgear_reference_commit':'7267622a7417d7ebce3ae0a821e396e9f60e6026','compiler':'gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0','liblzma_sha256':'ce6991de066a8966f3122990d92db53d9dc92e0cb04b22ebdc7b9ede55935cc9','validated_original_sha256':'57d1427dad607e6f30373fff8c27681d6fc7d02c3276c0b3ef8aa45755f8e7d3','validated_image_sha256':'460995361d98b91a92455257cc6d039fccb17816daecb52f6a5fa87fc437b925','validated_image_bytes':39595654,'expected_options_hex':'000004001c00090090004000','router_tested':False,'inputs':{p.name:sha(p) for p in (pkg/'fontes').iterdir()},'binaries':{p.name:sha(p) for p in (pkg/'bin').iterdir()}}
write('manifesto.json',json.dumps(manifest,indent=2,ensure_ascii=False))
write('scripts/compilar.py',r'''
#!/usr/bin/env python3
"""Compila ferramentas locais em scratch novo; não instala nem acessa o roteador."""
import argparse,hashlib,json,subprocess,tarfile
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--work-dir',required=True,type=Path)
p.add_argument('--xz-prefix',type=Path,default=Path('/home/builder/openwrt/staging_dir/host'))
a=p.parse_args()
pkg=Path(__file__).resolve().parents[1]
m=json.loads((pkg/'manifesto.json').read_text())
for name,expected in m['inputs'].items():
 if hashlib.sha256((pkg/'fontes'/name).read_bytes()).hexdigest()!=expected: raise SystemExit('Input hash mismatch: '+name)
work=a.work_dir.resolve()
if work.exists(): raise SystemExit('Scratch exists; choose a new directory')
if str(work).startswith('/mnt/'): raise SystemExit('Use a Linux scratch outside /mnt; preserve Unix filesystem metadata')
lib=a.xz_prefix/'lib/liblzma.a'
if not lib.is_file() or not (a.xz_prefix/'include/lzma.h').is_file(): raise SystemExit('Missing liblzma.a or lzma.h; provide --xz-prefix')
if hashlib.sha256(lib.read_bytes()).hexdigest()!=m['liblzma_sha256']: raise SystemExit('liblzma differs from validated dependency')
work.mkdir(parents=True)
archive=pkg/'fontes/squashfs4.2.tar.gz'
with tarfile.open(archive) as t:
 for member in t.getmembers():
  bits=member.name.split('/')
  if member.name.startswith('/') or '..' in bits or bits[0]!='squashfs4.2' or not (member.isfile() or member.isdir()): raise SystemExit('Invalid archive member')
 t.extractall(work,filter='data')
source=work/'squashfs4.2'
with (work/'compilacao.log').open('wb') as log:
 for name in ('openwrt-v17.01.0-110-allow_static_liblzma.patch','openwrt-v17.01.0-160.patch','openwrt-v17.01.0-190-no_nonstatic_inline.patch','200-preservar-symlink-mtime.patch'):
  with (pkg/'fontes'/name).open('rb') as patch:
   subprocess.run(['patch','-p1','--batch'],cwd=source,stdin=patch,stdout=log,stderr=subprocess.STDOUT,check=True)
 flags='-I'+str(a.xz_prefix/'include')+' -fcommon -std=gnu11 -include sys/sysmacros.h -Wno-error=incompatible-pointer-types'
 subprocess.run(['make','-C',str(source/'squashfs-tools'),'-j2','GZIP_SUPPORT=1','COMP_DEFAULT=xz','XZ_SUPPORT=1','LZMA_XZ_SUPPORT=1','XATTR_SUPPORT=','LZMA_LIB='+str(lib),'EXTRA_CFLAGS='+flags,'mksquashfs','unsquashfs'],stdout=log,stderr=subprocess.STDOUT,check=True)
actual={n:hashlib.sha256((source/'squashfs-tools'/n).read_bytes()).hexdigest() for n in ('mksquashfs','unsquashfs')}
expected={'mksquashfs':m['binaries']['mksquashfs4-compat'],'unsquashfs':m['binaries']['unsquashfs4-compat-mtime']}
res={'work':str(work),'hashes':actual,'matches_validated_binaries':actual==expected}
(work/'resultado-compilacao.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
''')
validator=(base/'ferramentas/testar_roundtrip_squashfs_mtime.py').read_text()
start=validator.index('BASE=Path('); end=validator.index('WORK.mkdir(); OUT.mkdir()')
replacement="""import argparse
parser=argparse.ArgumentParser(description='Round-trip offline; usa diretórios novos e não grava no roteador')
parser.add_argument('--original',type=Path,required=True)
parser.add_argument('--scratch',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--tools',type=Path,required=True,help='Diretório Linux com mksquashfs e unsquashfs corrigido')
parser.add_argument('--capacity-bytes',type=int,default=39870464,help='Referência histórica; não consulta o roteador')
args=parser.parse_args()
ORIGINAL=args.original.resolve()
TOOL=args.tools.resolve()
WORK=args.scratch.resolve()
OUT=args.output.resolve()
if WORK.exists() or OUT.exists(): raise SystemExit('Use diretórios scratch e output novos')
if str(WORK).startswith('/mnt/'): raise SystemExit('Scratch deve estar no filesystem Linux, fora de /mnt')
if ORIGINAL.is_relative_to(WORK) or ORIGINAL.is_relative_to(OUT): raise SystemExit('Original deve ficar fora dos diretórios de saída')
"""
validator=validator[:start]+replacement+validator[end:]
validator=validator.replace('capacity=39870464','capacity=args.capacity_bytes')
write('scripts/testar_roundtrip.py',validator)
write('LEIA-PRIMEIRO.md',r'''
# Compilador oficial SquashFS T7 — versão 1.0

Este é o conjunto de ferramentas adotado como referência oficial INTERNA deste projeto para remontar o RootFS SquashFS Acer Predator Connect T7. É uma reconstrução compatível validada offline, não uma ferramenta publicada, certificada ou homologada pela Acer. Também não compila o kernel Linux: empacota e extrai o sistema de arquivos.

## Estado validado

Em 2026-10-02 foi realizado o round-trip completo do backup de fábrica: extração, remontagem e nova extração. Conteúdo SHA-256 de 4.303 arquivos, metadados de 254 diretórios, 473 links e um dispositivo foram iguais; zero entradas ausentes, extras ou diferentes. As datas dos links passaram após a correção local. Opções XZ idênticas: 000004001c00090090004000. A imagem resultante mede 39.595.654 bytes.

Nada foi testado ou gravado no roteador. A montagem pelo kernel OEM e o boot não estão comprovados.

## Organização

- bin/: ferramentas x86-64 Linux/WSL prontas, não executáveis Windows ou ARM.
- fontes/: SquashFS 4.2 e quatro patches aplicados, incluindo a correção de datas de symlinks.
- scripts/compilar.py: compilação em scratch Linux novo, sem instalação global.
- scripts/testar_roundtrip.py: verificação completa parametrizada, offline.
- evidencias/: resultado passado, logs e prova da recompilação do pacote.
- documentacao/: relatórios completos e históricos.
- manifesto.json: commits, hashes, procedência e identidade da versão.
- SHA256SUMS: integridade dos arquivos do pacote.
- PROCEDIMENTO.md: dependências, comandos e critérios de sucesso.
- PARA-OUTRA-IA.md: texto pronto para compartilhar contexto.
- COPYING: licença GPL do SquashFS; as alterações locais acompanham o código/patch.

A imagem de firmware e as árvores extraídas não estão incluídas neste pacote. O caminho da imagem validada permanece no projeto original, registrado no resultado e no procedimento. As versões anteriores foram preservadas.
''')
write('PROCEDIMENTO.md',r'''
# Procedimento canônico — SquashFS T7 v1.0

## Procedência

Base SquashFS 4.2 obtida do pacote público GPL de referência Netgear RAX120v2, commit 7267622a7417d7ebce3ae0a821e396e9f60e6026:
https://github.com/akm-04/rax120v2-fw-toolkit/tree/7267622a7417d7ebce3ae0a821e396e9f60e6026/tools/squashfs4

Patches 110 (liblzma estática), 160 (opções XZ de 12 bytes) e 190 (inline) do OpenWrt v17.01.0, commit ac733df99c78f54b4cf9a8710f70a506f73e66fc:
https://github.com/openwrt/openwrt/tree/ac733df99c78f54b4cf9a8710f70a506f73e66fc/tools/squashfs4/patches

Patch 200 é local: restaura o timestamp do inode no próprio link com utimensat/AT_SYMLINK_NOFOLLOW. Uma falha nessa operação encerra a extração com erro. Não altera os destinos dos links. A patch 160 antiga da referência Netgear tinha ordem de campos diferente e não foi utilizada.

## Dependências e integridade

Linux/WSL; Python 3.12+ para o compilador parametrizado; GCC, make, patch, libc e zlib de desenvolvimento; headers e biblioteca estática liblzma já existentes no ambiente OpenWrt. Nenhum pacote é instalado automaticamente.

Dependência validada: /home/builder/openwrt/staging_dir/host, com include/lzma.h e lib/liblzma.a. Hash exigido da liblzma.a: ce6991de066a8966f3122990d92db53d9dc92e0cb04b22ebdc7b9ede55935cc9. Essa dependência externa não está incluída no ZIP. O build recusa uma biblioteca diferente.

GCC validado: Ubuntu 15.2.0-16ubuntu1. As opções -std=gnu11, -fcommon, inclusão de sys/sysmacros.h e -Wno-error=incompatible-pointer-types permitem compilar o código antigo; os warnings permanecem registrados. O recipe é reproduzível, mas não se promete hash idêntico em outro compilador/ambiente. No ambiente atual a recompilação do pacote foi comparada aos binários validados.

No WSL, entre no diretório v1.0 do pacote e confira:

```sh
sha256sum -c SHA256SUMS
```

## Compilação isolada

Use diretório novo dentro do filesystem Linux. Não use ExFAT para fontes extraídas, symlinks, dispositivos ou scratch. Os artefatos finais em arquivos regulares podem ficar no disco externo.

```sh
python3 scripts/compilar.py \
  --work-dir /home/builder/t7-squashfs-build-NOVO \
  --xz-prefix /home/builder/openwrt/staging_dir/host
```

O script verifica hashes das entradas e biblioteca, extrai a base, aplica os quatro patches em ordem e compila somente mksquashfs/unsquashfs. Não substitui bin/ do pacote nem instala globalmente. Consulte compilacao.log e resultado-compilacao.json no scratch. O diretório deve não existir.

Para usar diretamente bin/, copie os dois arquivos para uma pasta Linux sua com os nomes mksquashfs e unsquashfs e dê permissão de execução. A cópia para filesystem Linux evita depender de permissões de execução do ExFAT.

## Teste completo offline

Após compilar, use o diretório de ferramentas gerado. Scratch e output devem ser novos. Execute como root para preservar donos e o nó de dispositivo original; isso não executa o firmware nem acessa o roteador.

```sh
python3 scripts/testar_roundtrip.py \
  --original '/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Backups_MTD/backup_predator_t7_ubi_rootfs.bin' \
  --tools /home/builder/t7-squashfs-build-NOVO/squashfs4.2/squashfs-tools \
  --scratch /home/builder/t7-squashfs-teste-NOVO \
  --output '/mnt/h/FEITOS COM IA/Acer-Predator-Connect-T7/Feito por ChatGPT/artefatos/teste-squashfs-NOVO' \
  --capacity-bytes 39870464
```

Critérios: resultado.json status passed; comandos exit 0; zero caminhos ausentes/adicionais/modificados; conteúdo e metadados iguais; opções XZ iguais; hash original antes/depois igual; tamanho dentro da referência fornecida. O teste preserva as árvores em scratch e grava os logs, resultado e imagem remontada em output.

A comparação usa mtime com resolução de segundos, a resolução SquashFS. Atime/ctime locais não são metadados de equivalência do backup. O backup validado não tem xattrs. O teste é para um backup confiável do projeto, não um analisador de arquivos arbitrários não confiáveis.

## Opções de empacotamento usadas

```sh
mksquashfs RAIZ_EXTRAIDA SAIDA_NOVA.squashfs \
  -noappend -nopad -no-progress -b 256k -comp xz -processors 2 \
  -Xpreset 9 -Xlc 0 -Xlp 2 -Xpb 2 -Xfb 64 \
  -Xdict-size 256k -Xbcj ia64,arm,armthumb
```

O parser dessa revisão aceita -Xfb; seu help antigo anuncia -Xnice incorretamente. Preserve -noappend e use saída nova para evitar duplicação de árvores. Não copie a raiz extraída para ExFAT, que perde metadados Unix.

Layout little-endian de 12 bytes: uint32 dict_size=262144, uint32 flags=0x0009001c, uint16 bit_opts=0x0090, uint16 fb=64. Não é evidência de compressão proprietária ligada ao tamanho de página NAND.

## Evidência e limites

A imagem validada está fora do pacote: Feito por ChatGPT/artefatos/squashfs-roundtrip-mtime-20261002-212028/rootfs-rebuilt-offline.squashfs. Hash 460995361d98b91a92455257cc6d039fccb17816daecb52f6a5fa87fc437b925; 39.595.654 bytes. A capacidade histórica é 39.870.464 bytes, margem 274.810. A capacidade atual do aparelho não foi consultada.

A imagem é uma remontagem do RootFS de fábrica, sem pacotes LuCI ou modificações adicionais. Não é imagem UBI/NAND completa, instalador ou kernel ARM64. Não está certificada para flash; montagem OEM, boot do Slot 2 e boot ARM64 não foram testados. Avisar o usuário antes de testar no aparelho. Não tratar este pacote como autorização para gravação, reboot ou alteração de ambiente U-Boot.
''')
write('PARA-OUTRA-IA.md',r'''
# Contexto para outra IA

Leia LEIA-PRIMEIRO.md, PROCEDIMENTO.md, manifesto.json e evidencias/resultado.json deste pacote antes de propor alterações.

Este é o “compilador oficial SquashFS T7” adotado como referência interna do projeto Acer Predator Connect T7/IPQ5332. A ferramenta não é oficial da Acer e não compila o kernel: são mksquashfs/unsquashfs 4.2 reconstruídos com patches públicos do OpenWrt e uma correção local de timestamps de symlinks.

Já foi comprovado offline: o backup de fábrica pode ser completamente extraído, remontado e extraído novamente com conteúdo e metadados comparados iguais, incluindo as datas dos 473 links. A imagem nova mede 39.595.654 bytes; as opções XZ de 12 bytes são idênticas ao original. O hash do backup original foi preservado. Logs, hashes e fontes estão disponíveis.

Não use o mksquashfs padrão do Ubuntu como substituto automático; confira o layout das opções XZ. Use a receita documentada, -noappend e saída nova. Preserve permissões, donos, symlinks e nós de dispositivo em filesystem Linux. Não remonte a árvore no ExFAT. As versões anteriores permanecem no projeto para rastreabilidade.

Não afirmar que o erro do unsquashfs padrão comprova “XZ proprietário para NAND 4K”. Não atribuir a falha de boot à TrustZone como fato: a última etapa executada no aparelho segue desconhecida. Este resultado não valida kernel ARM64, montagem OEM, boot do Slot 2 ou imagem de produção modificada. A imagem validada é do RootFS de fábrica remontado.

Continue preparando e verificando offline. Antes de qualquer teste no roteador, avise o usuário; este pacote não autoriza acessar, gravar, reiniciar ou mudar U-Boot. Identifique volume real e recuperação antes de propor teste no hardware. Diferencie fatos observados, inferências e itens ainda não comprovados.
''')
print(pkg)
