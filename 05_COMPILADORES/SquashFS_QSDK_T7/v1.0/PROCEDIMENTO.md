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
