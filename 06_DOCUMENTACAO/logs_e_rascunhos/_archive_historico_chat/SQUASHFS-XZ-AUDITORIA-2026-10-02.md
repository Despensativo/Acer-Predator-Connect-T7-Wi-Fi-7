# Auditoria da hipotese de compressao SquashFS proprietaria

Data: 2026-10-02. Somente leitura dos arquivos originais, ferramentas e fontes. Nenhuma imagem gerada/alterada e nenhum teste no roteador.

## Conclusao

O erro do unsquashfs foi reproduzido no backup OEM. Ele corresponde a incompatibilidade do leitor de opcoes com o tamanho do bloco armazenado: 12 bytes no OEM contra 8 bytes esperados pela estrutura da ferramenta consultada. Isso nao demonstra um algoritmo XZ proprietario ligado a NAND de 4 KiB.

A afirmacao de que a imagem modificada possui um bloco de opcoes padrao rejeitado pelo kernel nao corresponde ao arquivo local examinado: nele, o flag SQUASHFS_COMP_OPT esta desativado e o bloco de opcoes nao esta presente.

Nao foi comprovado kernel panic, rejeicao pelo kernel OEM 5.4.213, patch Qualcomm especifico de XZ nem origem exata do formato estendido.

## Fatos binarios

| Campo | Backup OEM | Release modificada |
| --- | ---: | ---: |
| compression_id | 4 (XZ) | 4 (XZ) |
| SquashFS | 4.0 | 4.0 |
| block_size | 262144 | 262144 |
| bytes_used | 39589954 | 41571150 |
| flags | 0x6c0 | 0x2c0 |
| flag de opcoes | presente | ausente |
| tamanho do bloco de opcoes | 12 | sem bloco |
| primeira palavra do bloco OEM | 262144 | nao aplicavel |
| entradas no topo | 19 | 38 |

Opcoes OEM: 000004001c00090090004000. Nao interpretar os demais campos automaticamente como o layout de 8 bytes: isso misturaria formatos.

O dicionario indicado pela primeira palavra e 256 KiB, igual ao tamanho de bloco e um valor comum/potencia de dois. A pagina NAND 4 KiB nao foi identificada como causa desse formato.

## Verificacao por ferramentas padrao

unsquashfs -s mostrou o aviso no OEM, mas reconheceu o superbloco. A leitura padrao via unsquashfs -cat de etc/version teve codigo de saida 0 nas duas imagens e retornou 1.01.000024.

Isso comprova leitura de um arquivo e suas estruturas necessarias; nao e verificacao integral de todos os blocos nem teste de montagem pelo kernel OEM.

A fonte local xz_wrapper.c do squashfs-tools 4.7.5 compara o tamanho do bloco exatamente com sizeof(struct comp_opts), que e 8. Com 12, o caminho de exibicao das opcoes anuncia o erro.

A fonte publica do Linux v5.4 aceita len >= 8 no caminho padrao e usa defaults quando nao ha bloco de opcoes. Isso demonstra que o texto apresentado nao descreve uma regra universal do Linux. O comportamento da variante OEM precisa de fonte/analise propria ou log real.

Opcoes estendidas de XZ existem em ferramentas relacionadas ao OpenWrt. Isso torna plausivel um formato legado/estendido, mas nao identifica por si so a estrutura OEM exata.

## Outro defeito observado: append/duplicacao

A release tem pares bin/bin_1, etc/etc_1, init/init_1, lib/lib_1, usr/usr_1, www/www_1 e outros. O original nao possui essas copias de topo.

Inodes: 5031 no original e 10041 na release.

O comando em Scripts_Automacao/build_full_openwrt_release.py:156 nao usa -noappend e a rotina nao remove o arquivo de saida existente. O mksquashfs pode acrescentar a nova arvore ao filesystem existente; os pares observados sao fortemente consistentes com esse comportamento.

Consequencias possiveis:
- inflar a imagem e ultrapassar o volume;
- colocar alteracoes em etc_1/usr_1, enquanto o boot continua usando etc/usr;
- preservar dados de uma geracao anterior que se pretendia substituir.

Nao foi determinada qual geracao de cada arquivo ficou em cada arvore. Isso exige comparacao dirigida.

## Relacao com a falha do Slot 2

A release ainda tem 41.571.150 bytes contra os 39.870.464 solicitados pelo script de recriacao do volume. Se esse tamanho permanece no aparelho, o excesso de 1.700.686 bytes impede acomodar a imagem.

A compatibilidade SquashFS merece verificacao, mas esta auditoria nao transforma o aviso de uma ferramenta em prova de kernel panic. O excesso de tamanho e a duplicacao ja fornecem defeitos concretos a corrigir na geracao, antes de investigar uma trava criptografica.

Para futura geracao: usar destino novo dentro da pasta propria, impedir append, preservar a arvore e atributos corretamente, validar tamanho e conteudo. Nao contornar o aviso alterando bytes do arquivo original.

## Evidencias

- [Manifesto de metadados, leituras e listagens](evidencias/squashfs-xz-20261002.json)
- [Auditor somente leitura](ferramentas/auditar_squashfs_xz.py)
- [Auditoria anterior de tamanho/gravacao](SLOT2-CLONAGEM-VS-IMAGEM-2026-10-02.md)
- [Squashfs-tools: leitor XZ padrao](https://github.com/plougher/squashfs-tools/blob/master/squashfs-tools/xz_wrapper.c)
- [Squashfs-tools: opcoes estendidas OpenWrt](https://github.com/plougher/squashfs-tools/blob/master/squashfs-tools/xz_wrapper_extended.c)
- [Linux v5.4: XZ no SquashFS](https://github.com/torvalds/linux/blob/v5.4/fs/squashfs/xz_wrapper.c)
