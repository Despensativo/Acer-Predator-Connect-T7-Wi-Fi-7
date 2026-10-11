# Slot 2: clonagem funciona e regravacao de imagem falha

Data: 2026-10-02. Auditoria offline; nenhum script existente executado e nenhum acesso ao roteador.

## Conclusao

Nao foi identificada nesta revisao uma verificacao criptografica que rejeite automaticamente qualquer alteracao do Slot 2. Existem validacoes de integridade e estrutura e diferencas concretas nos scripts/imagens que podem explicar a falha. O arquivo e o comando da ultima tentativa ainda nao foram identificados; nao atribuir causa definitiva.

SSH/LuCI desbloqueados nao equivalem a Secure Boot desativado. Modificar arquivos no overlay tambem nao equivale a modificar o FIT ou o SquashFS base. O sucesso da clonagem nao exclui verificacao de assinaturas em algum outro nivel.

## Fato observado: imagem maior que o volume documentado

Arquivo: Firmwares_Custom/openwrt_predator_t7_release_rootfs.bin.
Tamanho: 41.571.150 bytes.
Magic: hsqs. SquashFS 4.0, bloco 262.144 bytes.
Superbloco bytes_used: 41.571.150.
SHA-256: 47ada20de8f05739c240a84769d3c9099240b9d19a1b9489a4c3be8615993997.

O script corrigir_layout_e_restaurar_slot2.py, linha 37, solicita 39.870.464 bytes para ubi_rootfs.
Essa imagem excede o tamanho solicitado em 1.700.686 bytes.

O instalador instalar_openwrt_slot2_release.py usa o tamanho integral do arquivo e grava no volume existente; nao o redimensiona nessa rotina. Se esse layout ainda estiver no dispositivo, a imagem nao cabe. Isso nao e evidencia de anti-modificacao: e incompatibilidade de tamanho. O tamanho efetivo atual precisa ser confirmado em reserved_ebs e usable_eb_size.

## Fato observado: identidade UBI presumida

Varias rotinas fixam ubi1 como Slot 2 e usam ubiattach -m 20 com erro ignorado. A numeracao ubi0/ubi1 depende de anexacao, e primaryboot sozinho nao comprova a associacao atual.

restaurar_slot2_padrao.py alterna ubi1/ubi0 por primaryboot, mas essa regra ainda e uma presuncao. O mapeamento correto deve ser verificado pelo mtd_num em sysfs e cruzado com /proc/mtd, volumes e mounts. O alvo deve estar inativo, nao montado.

## Fato observado: sucesso anunciado sem validar retorno

restaurar_e_ativar_slot2_producao.py: run_cmd apenas recebe texto ate um prompt, sem extrair codigo de saida. O chamador imprime mensagens de sucesso depois, independentemente do resultado real.

instalar_openwrt_slot2_release.py inclui set -e no shell remoto, portanto uma falha do ubiupdatevol pode interromper a rotina. Isso nao substitui a coleta e verificacao do retorno pelo Python. Nao afirmar que todas as mensagens OK internas desse script sao emitidas apos uma falha: elas podem nao ser executadas por causa do set -e.

## Validacoes que podem existir sem serem bloqueio de modificacao

- UBI possui CRC em dados de volumes static; o caminho correto de atualizacao recalcula metadados e CRC. Falha ou interrupcao pode deixar marcador de atualizacao pendente, conforme codigo UBI.
- FIT pode conter hashes ou assinaturas; hashes de integridade nao equivalem a assinatura obrigatoria com chave OEM. Exigencia de assinatura no caminho exato precisa ser comprovada.
- UBI, FIT, SquashFS e dump NAND sao camadas/formats diferentes; nao sao intercambiaveis no destino de gravacao.
- BOOTCONFIG seleciona a origem de boot, enquanto fsbootargs orienta o kernel. Divergencia pode carregar kernel de um slot e apontar o rootfs para outro.
- Overlay de arquivos precisa ser restaurado respeitando sua estrutura. Um dump raw UBIFS nao deve ser tratado como tar, nem um tar como UBI.
- Ver somente 192.168.1.1/LuCI nao comprova falha de boot: configuracao restaurada pode manter outro IP ou servico desativado.

## Procedimento para separar as hipoteses, sem regravar

1. Identificar o arquivo e o script/comando exatos da tentativa que falhou.
2. Confirmar em leitura o Slot 1 atual, /proc/mtd, associacao UBI->MTD, volume IDs/nomes/tipos/tamanhos, upd_marker e mounts.
3. Comparar o payload logico do kernel e do SquashFS lido do Slot 2 com o arquivo enviado, usando tamanho correto e SHA-256.
4. Conferir BOOTCONFIG0/1 e argumentos efetivos de boot separadamente.
5. Verificar IP/interface/servicos antes de classificar ausencia de LuCI como ausencia de Linux.

Igualdade de dumps NAND raw nao e exigencia de igualdade dos payloads logicos: wear leveling e metadados podem mudar.

## Fontes

- Scripts_Automacao/corrigir_layout_e_restaurar_slot2.py:37.
- Scripts_Automacao/instalar_openwrt_slot2_release.py:54,98.
- Scripts_Automacao/restaurar_e_ativar_slot2_producao.py:51-55,105-106.
- Codigo Linux local: drivers/mtd/ubi/upd.c e drivers/mtd/ubi/eba.c, como referencia de mecanismo, nao como comprovacao do estado do firmware OEM.
- [Documentacao do Linux: UBI, UBIFS e MTD](https://docs.kernel.org/filesystems/ubifs.html).

Nenhuma imagem foi instalada, nenhum volume anexado e nenhuma configuracao do roteador foi alterada.
