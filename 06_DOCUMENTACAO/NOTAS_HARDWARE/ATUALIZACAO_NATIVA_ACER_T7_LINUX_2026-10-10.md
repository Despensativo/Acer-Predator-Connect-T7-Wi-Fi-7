# Atualização nativa Acer T7 pelo Linux ativo — 10/10/2026

**Atualização posterior no mesmo dia:** o teste sugerido ao fim deste relatório foi executado. BOOTCONFIG integral sem `fsbootargs` iniciou a stock v27 no estado `primaryboot=0`; o resultado está em `TESTE_BOOT_NATIVO_SLOT2_V27_2026-10-10.md` e no `CONSOLIDADO_DESCOBERTAS_T7_2026-10-10.md`. A recomendação final abaixo registra o estado **anterior** ao teste.

## Escopo e estado lido ao vivo

Esta análise é somente de leitura; nenhuma atualização ou gravação foi iniciada. O T7 respondeu por Telnet em `192.168.76.1`. `/proc/cmdline` mostrou `ubi.mtd=rootfs`, `/proc/mtd` mostrou `rootfs_1=mtd20` e `rootfs=mtd21`, e as duas BOOTCONFIG mostraram `rootfs/primaryboot=1`, `rootfs/upgradepartition=rootfs_1`, `age=3`. Não havia `/proc/upgrade_info/trybit` nem variável persistente `fsbootargs`; `bootcmd=bootipq` e `bootargs=console=ttyMSM0,115200n8`.

Os SHA-256 de `/lib/upgrade/platform.sh`, `/sbin/sysupgrade`, `/bin/falotupgrade.sh`, `/lib/functions/download_img.sh` e `/lib/functions/update_img.sh` no roteador coincidiram, respectivamente, com os arquivos em `_FORA DO GitHub/03_ARTEFATOS_SQUASHFS_BUILD/rootfs_extracted/`: `8cade9c82a7a4e1138217d218ac4c6733ffe57d9ac49d20f5055a6fc5a3e7f6b`, `57ec2413b68ba9547ff7630eba87a316edeed62e23a218232d9ccee589308154`, `7f77ce918e310599523f115cd6c70f549cac76c5043da5cd996b472be54f0dca`, `58376135dd7f012f75a4baa4d403f2d74a1dea17ed20e8d07f0b6670dff7207b` e `cc6ca1fe7a6134cd343b964404c1cde98a58cd81e4593043f6c93399956ff000`.

## Entrada pelo painel e pelo serviço online

O backend proprietário `libsod-platform.so` contém as cadeias `sysupgrade -T %s` e `/bin/falotupgrade.sh %s&` próximas das rotinas de atualização. O wrapper `/bin/falotupgrade.sh` executa `sleep 10` e depois `sysupgrade $1`. Isto identifica o caminho de validação/instalação de arquivo pelo backend, mas não foi observado um clique real em um botão do painel Acer nem capturado o HTTP correspondente.

A página LuCI `www/luci-static/resources/view/system/flash.js` envia o arquivo para `/tmp/firmware.bin`, solicita a validação, chama `sysupgrade --test` e, após confirmação, chama `sysupgrade` com as opções escolhidas. Essa é uma entrada distinta da interface Acer.

No caminho online, `/lib/functions/download_img.sh` verifica conectividade, chama `fota ipq check_version` e, quando aplicável, `fota ipq download`. `/lib/functions/update_img.sh` exige `/tmp/nand-4k-ipq5332-single.img` e `fota_force_ready=1`, depois chama `fota ipq install`. O binário `fota` contém a cadeia `sysupgrade `, mas a chamada interna exata não foi reconstruída nesta análise. Não se deve presumir que todo botão de atualização online percorra exatamente o wrapper de upload local.

## O que `sysupgrade` executa neste firmware

1. `/sbin/sysupgrade` usa `/usr/libexec/validate_firmware_image`, oferece backup das configurações por padrão (`SAVE_CONFIG=1`) e passa a etapa de gravação ao `ubus`/`upgraded`, que muda para um sistema temporário em RAM. A opção `-n` desabilita o backup. O teste `-T` não inicia a gravação, mas a função de validação da plataforma inclui um ramo de `reboot` se `dumpimage -c` falhar; não o classificar como ensaio sem qualquer efeito possível.
2. `/lib/upgrade/platform.sh` declara `mandatory_nand="ubi mibib"` neste build (`FLASH_MIBIB=1`), mas chama `image_has_mandatory_section $1 ${mandatory_nand}` sem aspas; a função lê somente `$2`. Assim, **na implementação atual, a checagem obrigatória efetiva examina apenas `ubi`**, apesar da intenção declarada de exigir também `mibib`. O script extrai as seções para `/tmp` com `dumpimage` e verifica o FIT com `dumpimage -c`. O FIT OEM v27 possui ambas as seções; aceitação efetiva pelo painel não foi testada agora.
3. Para a seção `ubi`, `do_flash_ubi` consulta a BOOTCONFIG selecionada por `age`. Em modo ordinário, muda em memória `rootfs/primaryboot` nas duas BOOTCONFIG, lê `upgradepartition` e executa `ubiformat` no MTD correspondente. Com o estado lido hoje, o destino previsto é `rootfs_1` (`mtd20`). `ubiformat` substitui o contêiner UBI inteiro do destino, inclusive `rootfs_data`; não conserva o overlay antigo integralmente.
4. O FIT OEM completo também traz seções de boot. O dispatcher grava `sbl1` em `0:SBL1` e `0:SBL1_1`; `tz` em `0:QSEE` e `0:QSEE_1`; `tme` em `0:TME` e `0:TME_1`; `devcfg`, `ddr/CDT` e `u-boot/APPSBL` seguem o caminho de partição de atualização quando há `upgradepartition`. `mibib` é gravada na partição compartilhada `0:MIBIB`. As seções `script` e `bootconfig*` do FIT são ignoradas pelo dispatcher Linux; BOOTCONFIG é exportada dos objetos `/proc/boot_info` e escrita posteriormente.
5. Depois do laço de seções, `platform_do_upgrade` grava as duas BOOTCONFIG em modo ordinário. Se houver backup de configurações, `platform_copy_config` tenta anexar o UBI de destino e copiar `/tmp/sysupgrade.tgz` para o novo `rootfs_data`. Por fim, `/lib/upgrade/do_stage2` força o reboot.

## Limites relevantes para a recuperação atual

- A atualização nativa tem lógica real de slot inativo; o FIT OEM via Web Recovery executa outro script, que nomeia `rootfs` e não `rootfs_1`.
- Um FIT de Web Recovery com `script` e `ubi` pode parecer válido ao validador Linux por causa da checagem obrigatória incompleta. Se o Linux o aceitar, o dispatcher **ignora o `script` de U-Boot**, processa a seção `ubi` pela lógica nativa e tenta trocar o boot. Portanto, não enviar os FITs candidatos de Web Recovery ao painel `192.168.76.1`; a aceitação efetiva de um arquivo específico continua não testada.
- A instalação completa pelo Linux também toca partições de boot, incluindo algumas cópias ativas/compartilhadas. Não é apenas uma nova gravação de `rootfs_1`.
- O laço `for sec ...; flash_section ${sec}` não interrompe explicitamente ao primeiro retorno não zero. `do_flash_ubi` não verifica leitura de volta dos volumes. A tela de progresso ou o reboot não comprovam integridade nem boot estável.
- Nos ensaios anteriores, a UBI stock v27 em `rootfs_1` teve `wifi_fw`, `kernel` e `ubi_rootfs` lidos de volta com hashes OEM, mas três tentativas de boot não trouxeram rede. Regravar os mesmos bytes pela interface nativa não é, por si, explicação para a falha.
- Os alternadores manuais usados antes definiram `fsbootargs` explicitamente. O `platform.sh` nativo não o faz; hoje essa variável está ausente no Slot 1 funcional. É uma diferença de procedimento a isolar, não uma causa demonstrada para o boot falho.
- `Scripts_Automacao/gravar_v27_stock_limpa_slot2.py` não substitui o caminho nativo: espera `rootfs=mtd20` e `rootfs_1=mtd21`, inverso do mapa lido hoje, e seus três arquivos de origem não estão presentes. `01_FIRMWARES_E_IMAGENS/Official_v27_Componentes/flash_engine.sh` também contém uma atribuição de `primaryboot` que não foi validada contra a lógica nativa. Não executar esses scripts sem correção e revisão.

## Recomendação

Manter o Slot 1 ativo. Para identificar a causa do Slot 2, a próxima comparação útil é **um teste controlado da seleção de boot no estilo nativo**, sem regravar a UBI já verificada e sem manter um `fsbootargs` manual, acompanhado de captura de `SYSTRACE` imediatamente após a tentativa. Preparar o BOOTCONFIG de destino e o alternador de retorno antes do ensaio; sem UART, a primeira exceção pode novamente se perder. Uma atualização completa pelo painel Acer deve ficar para quando houver evidência de que o caminho nativo completo é necessário, pois também grava componentes de boot e não oferece leitura de volta de cada volume antes de reiniciar.
