# Validação da rootfs_v2 no Slot 2 antes da imagem final

Estado deste plano em 10/10/2026: **preparação e auditoria local concluídas; nenhuma gravação no T7 foi feita por este procedimento**. O último estado do aparelho documentado no ensaio de marcadores foi `primaryboot=0`, stock v27 ativa em `ubi0`/`mtd20` (endereço `0x01640000`). Confirmar novamente no aparelho antes de qualquer escrita: o estado pode ter mudado. Nesta inspeção, a rede respondeu nas portas 22, 23 e 80, mas o SSH apresentou uma chave de host diferente da conhecida no Mac; por isso, não foi usada uma sessão SSH para afirmar o estado atual.

## Fonte e escopo das mudanças

- Base stock v27: `_FORA DO GitHub/NAO TA ROLANDO/rootfs_v27_stock_oem_38mb.squashfs`, SHA-256 `fb4c1611319749f17c0bcfb6ac6265697550eb39365aa52a9fd143aa02741348`.
- Árvore editável: `_FORA DO GitHub/03_ARTEFATOS_SQUASHFS_BUILD/rootfs_v2/stock_v27_case_sensitive.sparsebundle`, diretório `rootfs` no volume APFS sensível a maiúsculas/minúsculas.
- Candidata **de ensaio**: `rootfs_v2_candidate_512k_redes_contas.squashfs`, 38.912.000 bytes, SHA-256 `4241b4ea2d199cac979e5e19c0a9a0479353a5b9812b1cac8da3e532b3fe3c2b`. É menor que o arquivo de referência OEM de 39.616.512 bytes, mas usa bloco SquashFS de 512 KiB, enquanto a stock usa 256 KiB. Essa diferença ainda precisa de boot real.
- O manifesto `rootfs_v2/manifest.json` é a lista de inclusão. A auditoria local de hoje releu no SquashFS os 11 caminhos únicos com hash em `applied_changes`; todos bateram com a árvore editável e o manifesto. O arquivo `etc/config/wireless` **não** foi incluído: o hook `etc/init.d/t7-wireless-v2` manda o gerador OEM criá-lo no primeiro boot e aplica potências, SSIDs e credenciais solicitados. `wifiPowerTable`, o JavaScript Wi-Fi anterior e `qcawificfg80211.sh` anterior são apenas referências, marcadas `applied_to_rootfs=false`.
- O backup pessoal é um conjunto de configurações, não uma rootfs inteira. Não restaurar o TAR completo sobre a v27 nem importar tudo de `reference/` automaticamente. Kernel, `wifi_fw`, drivers, ART e CDT ficam stock v27 neste ensaio.

## Fase 1 — ensaio das alterações no Slot 2 ativo

1. Confirmar `primaryboot`, `/proc/mtd`, `/sys/class/ubi/ubi0/mtd_num`, versão, montagens de `/rom`, `/overlay` e firmware Wi-Fi. Identificar o endereço físico, não só o nome `rootfs`.
2. Fazer backup privado do overlay ativo e dos arquivos que serão substituídos, com hashes. Manter retorno por cabo e alternador de Slot 1 disponível. Verificar a chave de host antes de uma sessão SSH com escrita.
3. Aplicar **somente a lista de inclusão** do manifesto ao overlay do Slot 2, em grupos reversíveis: primeiro LuCI/uhttpd/rpcd e redirecionamento web; depois contas e Dropbear; por último o hook Wi-Fi. Preservar permissões e links. O hook precisa de ensaio específico: seu marcador de conclusão não pode existir antes do teste, e o wireless atual deve ser salvo para reversão.
4. Verificar configuração UCI, início dos serviços, login `root` e `admin`, painel web, redes 2,4/5/6 GHz, associação real de clientes, conectividade cabeada, logs e ausência de reboot inesperado. Conferir os valores **efetivos** de potência/canal, não só os pedidos em `/etc/config/wireless`.

Esta fase valida comportamento dos arquivos, mas **não** valida o boot do SquashFS candidato. O overlay pode esconder arquivos da imagem de base.

## Fase 2 — boot da candidata SquashFS no Slot 2

1. Com a configuração do overlay aprovada, selecionar o Slot 1 por BOOTCONFIG integral de 512 KiB, sem `fsbootargs` manual. Após reiniciar, confirmar que `ubi0` está em `mtd21`/`0x10640000` e que o alvo inativo físico do Slot 2 é `mtd20`/`0x01640000`. Se os endereços não coincidirem, parar.
2. Anexar o UBI inativo como outro dispositivo (`ubi1` somente se o número for confirmado), listar os quatro volumes por **nome** e capacidade e salvar `ubi_rootfs` e `rootfs_data` do Slot 2. Registrar os hashes de `wifi_fw` e `kernel` stock v27. Não sobrescrever estes dois volumes nem qualquer partição externa ao UBI.
3. Confirmar que `ubi_rootfs` do alvo não está montado. Gravar a candidata de ensaio apenas nesse volume com `ubiupdatevol`; ler de volta a quantidade exata de bytes e comparar SHA-256. Para que `/etc/config`, `/etc/shadow` e `/www` da nova imagem não sejam encobertos por cópias antigas, preparar um `rootfs_data` limpo **após o backup**, ou remover de forma auditada apenas os caminhos conflitantes. Registrar qual opção foi usada.
4. Desanexar o UBI inativo. Selecionar o Slot 2 com as duas BOOTCONFIG integrais, conferir ambas por leitura de volta e reiniciar. Manter `fsbootargs` ausente.
5. No boot, confirmar endereço físico `mtd20`, `/rom` e os hashes dos arquivos da candidata vistos pelo Linux; conferir que nenhum overlay os está mascarando. Repetir os testes funcionais da fase 1 e acompanhar uptime, `dmesg`, `logread`, SSR de Wi-Fi, painel, Ethernet e clientes reais. Se falhar, retornar ao Slot 1 pelo alternador preservado e recolher os logs; não rotular a imagem como final.

## Fase 3 — congelar e empacotar a imagem final

Depois do boot e dos testes funcionais aprovados, incorporar à árvore editável **somente** correções observadas no ensaio, atualizar o manifesto e reconstruir o SquashFS com os **mesmos parâmetros que realmente deram boot**. Verificar extração integral, tamanho/capacidade do volume, hashes, permissões, links, ausência de metadados `._*` e leitura de volta após gravação. Guardar a candidata de ensaio e a stock intactas.

O resultado final deve ter dois níveis identificados: `ubi_rootfs` (SquashFS validado) e, se for necessária instalação por painel/Web Recovery, um firmware `.bin` FIT montado **separadamente** com o kernel e `wifi_fw` stock v27 e o UBI correto. O `.bin` depende do caminho escolhido: a atualização nativa pelo Linux alterna para o sistema inativo e também pode gravar partições de boot; o Web Recovery usa script e nomes de partição do U-Boot, cujo destino físico em uma gravação real ainda precisa ser conferido. Não chamar um FIT não testado de instalador definitivo nem reaproveitar um alternador como ROM completa.

Critério de conclusão: imagem final e hash registrados, leitura de volta dos volumes, boot repetível no Slot 2, serviços/contas/redes funcionais e retorno ao Slot 1 ainda disponível.
