# mksquashfs compatível com as opções XZ Acer — 2026-10-02

## Conclusão

Foi compilado offline um mksquashfs/unsquashfs 4.2 com patches do OpenWrt v17.01.0. A ferramenta gerou um SquashFS sintético com os mesmos 12 bytes de opções XZ presentes no backup Acer. O unsquashfs compilado extraiu somente etc/version do original, com sucesso. Não foi obtido ou identificado o executável exato usado pela Acer: a procedência deste resultado é uma reconstrução pública compatível com o formato observado.

Nada foi enviado, instalado, gravado ou testado no roteador. Os backups e o RootFS de produção não foram modificados. Não foi remontado um RootFS completo.

## Fontes e procedência

- Referência Netgear RAX120v2 GPL: https://github.com/akm-04/rax120v2-fw-toolkit/tree/7267622a7417d7ebce3ae0a821e396e9f60e6026/tools/squashfs4
- A versão inicial da patch 160 desse pacote usa flags/bit_opts/fb/dict_size e NÃO corresponde ao layout Acer. Ela foi preservada apenas como referência.
- A revisão compatível vem do OpenWrt v17.01.0, commit ac733df99c78f54b4cf9a8710f70a506f73e66fc, patches 110, 160 e 190.
- Patch com a estrutura correspondente: https://github.com/openwrt/openwrt/blob/ac733df99c78f54b4cf9a8710f70a506f73e66fc/tools/squashfs4/patches/160-expose_lzma_xz_options.patch
- Explicação histórica do formato pelo mantenedor: https://lists.infradead.org/pipermail/lede-dev/2017-May/007747.html
- O tarball squashfs4.2.tar.gz foi obtido do pacote público de referência; seu hash está no manifesto. Não se atribui esse tarball diretamente à Acer.

## Layout efetivamente conferido

Bytes de opções do backup e da imagem sintética: `000004001c00090090004000`.

| Campo little-endian | Valor | Interpretação na revisão compilada |
| --- | --- | --- |
| dict_size, uint32 | 262144 | Dicionário 256 KiB |
| flags, uint32 | 0x0009001c | Preset 9; candidatos BCJ ia64, arm, armthumb |
| bit_opts, uint16 | 0x0090 | lc=0, lp=2, pb=2 |
| fb, uint16 | 64 | Nice length 64 |

O conjunto de filtros indica opções de tentativa do compressor; não significa que todos os blocos usam todos os filtros, nem permite deduzir a arquitetura do firmware.

A igualdade foi conferida por assert no script de validação. O conteúdo de teste foi extraído novamente e comparado com cmp.

## Compilação e validação

Scratch isolado: /home/builder/t7-squashfs-compat-20261002-v2. A tentativa inicial v1 e seus logs foram preservados. A compilação final usa GCC 15.2, liblzma estática já existente no ambiente OpenWrt, gzip/XZ/LZMA habilitados e XATTR desabilitado. Não houve instalação de pacotes nem instalação global dos binários.

Para código antigo compilar com o ambiente atual: -std=gnu11, -fcommon, inclusão de sys/sysmacros.h e -Wno-error=incompatible-pointer-types para os handlers antigos de sinais. Warnings permanecem nos logs. Os patches de formato não foram adaptados manualmente.

Hash SHA-256 da liblzma.a utilizada: ce6991de066a8966f3122990d92db53d9dc92e0cb04b22ebdc7b9ede55935cc9.

- Extração seletiva de etc/version: 1 arquivo, resultado 1.01.000024. Não foram extraídos arquivos de credenciais/configuração.
- Imagem sintética: 304 bytes, conteúdo inofensivo, bloco configurado em 256 KiB.
- Opções XZ: 12 bytes iguais ao original.
- Round-trip do conteúdo sintético: cmp passou.
- O -s antigo não imprime as opções detalhadas; sua saída isolada não é usada como prova da equivalência.

Comando usado SOMENTE na árvore sintética dentro do scratch:

```sh
mksquashfs synthetic synthetic.squashfs -noappend -nopad -b 256k -comp xz -processors 1 -Xpreset 9 -Xlc 0 -Xlp 2 -Xpb 2 -Xfb 64 -Xdict-size 256k -Xbcj ia64,arm,armthumb
```

Nesta revisão, o help anuncia -Xnice, mas o parser realmente reconhece -Xfb. O comando validado utiliza -Xfb.

## Artefatos

Diretório: artefatos/squashfs-compat-20261002-v1/

- mksquashfs4-compat: SHA-256 0b6341e0080f6f8f03ca6d06ce51e078da908f2b03d201f98035d33d86131ac6.
- unsquashfs4-compat: SHA-256 aa06b1c11dfa42e05694b98ad54f9bdd75ae6edb9f62e5458c3db2e5afa24d4c.
- synthetic.squashfs, COPYING, fontes-compiladas.tar.gz e proveniencia-validacao.json.
- Binários ELF x86-64 para o WSL/PC; não são programas ARM para instalar no roteador.
- Scripts próprios em ferramentas/compilar_squashfs_compat_v1.sh e validar_squashfs_compat_v1.sh.
- Logs completos em logs/squashfs-compat-*.

## Limites e próximo passo

O formato das opções e a leitura de um arquivo foram verificados. Isso não comprova identidade com o toolchain Acer, integridade de todos os arquivos do backup, compatibilidade de montagem pelo kernel OEM ou sucesso de boot.

A explicação anterior de “compressão proprietária devido à NAND 4K” não está demonstrada. Os bytes são reproduzíveis com patches públicos históricos do OpenWrt. O tamanho de página da NAND e a serialização das opções SquashFS são assuntos distintos.

Uma imagem completa futura deve ser criada em saída nova com -noappend, preservar permissões, links e nós especiais do RootFS, passar verificação de conteúdo, caber no volume UBI real e usar procedimento de gravação que confirme o volume pelo nome. A ferramenta compatível não corrige sozinha os diretórios duplicados da release anterior, o excesso de tamanho ou as pendências do boot ARM64.

Avisar o usuário antes de qualquer teste no aparelho. Esta etapa terminou na validação offline.
