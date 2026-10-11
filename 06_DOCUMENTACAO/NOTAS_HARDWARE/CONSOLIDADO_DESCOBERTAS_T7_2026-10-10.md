# T7: descobertas e testes de 10/10/2026

Este é o índice consolidado do trabalho de hoje. Ele separa **leitura no aparelho**, **análise estática das imagens** e **hipóteses ainda não isoladas**. Os relatórios especializados listados ao fim preservam comandos, hashes e limitações de cada ensaio.

## 1. Layout físico e nomes de boot

- A MIBIB das ROMs Acer v24/v27 descreve 25 partições físicas e sete cópias com sufixo `_1`. `BOOTCONFIG` e `BOOTCONFIG1` são duas cópias do **controle de boot**; não são os dois sistemas de arquivos. Há dois contêineres físicos de 240 MiB nos endereços `0x01640000` e `0x10640000`.
- O byte `0x6c` do BOOTCONFIG integral usado neste aparelho é o seletor `rootfs/primaryboot`: `1` e `0` escolheram boots diferentes. As duas imagens raw de 512 KiB verificadas diferem **somente nesse byte**. Os demais seletores (`APPSBL`, `CDT`, `DEVCFG`, `HLOS`, `WIFIFW`) são independentes; mudar o byte de `rootfs` não obriga todas as partições redundantes a trocar juntas.
- No boot com `primaryboot=0`, o Linux nomeou o endereço `0x01640000` como `rootfs` (`mtd20`) e o endereço `0x10640000` como `rootfs_1` (`mtd21`); `ubi0` anexou `mtd20`.
- No boot com `primaryboot=1`, os nomes lógicos se inverteram: `0x01640000` apareceu como `rootfs_1` (`mtd20`) e `0x10640000` como `rootfs` (`mtd21`); `ubi0` anexou `mtd21`. **Os endereços físicos não trocaram**, só os nomes apresentados ao Linux e a partição ativa. Portanto, o nome `rootfs` em `/proc/cmdline` é o nome lógico do sistema escolhido, não um identificador físico fixo.
- Esse resultado ao vivo corrige a simplificação em documentos anteriores que tratavam `rootfs_1`/`mtd20` ou o endereço `0x10640000` como sinônimos permanentes de “Slot 2”. Neste documento, “Slot 1/2” indica o estado `primaryboot=1/0`; para identificar fisicamente o sistema, registrar também o **endereço NAND** e `ubi0/mtd_num`.

## 2. Origem dos arquivos durante o boot

- No boot observado com `primaryboot=0`, há somente `ubi0`, anexado ao `mtd20`. Esse UBI tem os volumes `wifi_fw`, `kernel`, `ubi_rootfs` e `rootfs_data`.
- `/rom` é SquashFS em `/dev/mtdblock27` (`ubi_rootfs` do UBI ativo); `/overlay` é UBIFS em `/dev/ubi0_3` (`rootfs_data` do mesmo UBI); `/lib/firmware/IPQ5332/WIFI_FW` é SquashFS em `/dev/mtdblock25` (`wifi_fw` do mesmo UBI). `qcn9224/amss_dualmac.bin` e `qcn9224/regdb.bin` são links para esse ponto de montagem. Os módulos `.ko` disponíveis no rootfs vêm de `/rom`, salvo eventual substituição no overlay **do sistema ativo**.
- A outra partição de sistema não estava anexada como UBI no boot normal. Não foi visto mecanismo de leitura automática de módulos ou `wifi_fw` do contêiner inativo. Isso não exclui partições **externas** ao UBI: `ART`, bootloader, calibração e algumas cópias de configuração são compartilhadas ou têm seleção própria.
- Um marcador de texto pode testar a separação dos dois `rootfs_data`; não deve ser gravado em `kernel`, `wifi_fw`, `ubi_rootfs`, `APPSBL`, `CDT`, `ART` ou MIBIB. Para esses componentes, usar montagens, BOOTCONFIG e hashes de leitura, pois alterar seus bytes pode impedir o boot ou invalidar firmware/calibração.

## 3. ROM v24, v27 e gravação de atualização

- Os FITs completos Acer v24 e v27 têm o **mesmo script de gravação** e a mesma MIBIB. O script do Web Recovery nomeia dez destinos, incluindo `BOOTCONFIG`, `BOOTCONFIG1` e `rootfs`; não nomeia explicitamente `rootfs_1` nem as demais cópias `_1`. A resolução física de `rootfs` durante um upload real ainda requer leitura posterior ou UART.
- A atualização nativa iniciada no Linux segue outro caminho: `sysupgrade` consulta `upgradepartition`, formata o contêiner UBI de destino, escreve também seções de boot do FIT e depois atualiza as BOOTCONFIG. O backup de configurações é opcional; mesmo quando usado, não espelha integralmente o `rootfs_data` de um slot para o outro.
- A comparação estática das rootfs stock v24/v27 encontrou 328 nomes de módulos `.ko`; 18 arquivos têm hash diferente, mas os 12 módulos Wi-Fi com hash diferente mudaram somente em `.note.gnu.build-id`, não na seção executável `.text`. Entre 91 arquivos de `wifi_fw`, só `qcn9224/regdb.bin` difere. Essa diferença não prova incompatibilidade regulatória com a placa brasileira.

## 4. Recuperação v27 e seleção que funcionou

- A imagem UBI stock v27 foi gravada no contêiner então inativo com `ubiformat`. `wifi_fw`, `kernel` e `ubi_rootfs` foram lidos de volta com hashes idênticos aos componentes OEM. Três boots seguintes falharam: os seletores foram exportados de `/proc/boot_info` em arquivos de **336 bytes** e o ambiente recebeu manualmente `fsbootargs=ubi.mtd=rootfs_1`. Inicializar previamente `rootfs_data` e igualar o número de LEBs não resolveram essas tentativas. `SYSTRACE` registrou pânicos perto de 26 segundos, mas não preservou a primeira linha de todas as exceções; não se pode atribuir a causa somente ao `regdb.bin` ou ao QCN9224.
- O ensaio seguinte gravou em `BOOTCONFIG` e `BOOTCONFIG1` a imagem **integral de 512 KiB**, alterando apenas `0x6c` de `1` para `0`, conferiu o SHA-256 de ambas e **não** definiu `fsbootargs` nem gravou `APPSBLENV`/UBI. A stock `T7_BR_1.01.000027` iniciou com Ethernet, painel e os rádios 2,4/5/6 GHz. Houve uma queda/reboot inicial; depois o uptime cresceu sem novo reboot durante a janela observada. Assim, o boot do sistema v27 é possível neste hardware.
- O teste mudou **duas variáveis** frente às três falhas anteriores: tamanho/conteúdo persistido da BOOTCONFIG e presença de `fsbootargs`. O boot funcional apresentou `ubi.mtd=rootfs` mesmo no estado `primaryboot=0`, tornando `ubi.mtd=rootfs_1` manual uma hipótese de erro plausível, mas não isolada experimentalmente.
- No boot funcional, o log mostrou o QCN9224 subir e carregar `amss_dualmac.bin`/`regdb.bin`; também mostrou uma reinicialização do subsistema Wi-Fi, aviso `Target failed service 0x108` e falha de ACS. Não apareceu `Target hung at Post-STM` no trecho inspecionado. A causa do reboot inicial e a estabilidade por longo prazo permanecem abertas.
- Foram gerados offline dois FITs V2 com extensão `.bin`, um para cada seletor, usando BOOTCONFIG de 512 KiB e sem `setenv`/`saveenv`. Eles **não foram enviados ao U-Boot**; o usuário adiou esse teste. Os alternadores anteriores foram preservados.

## 5. Ensaio de marcadores de overlay

Foi escolhido o mesmo caminho não funcional `/root/T7_SLOT_IDENTIDADE.txt` nos dois sistemas, com conteúdo distinto para cada estado `primaryboot`. No boot com `primaryboot=0`, o arquivo `T7-20261010-SLOT2` foi escrito e lido de volta no overlay de `ubi0`/`mtd20` (SHA-256 `5eff51e303c62dbe4f114532b08574ea4f71ef44e14442accb70ff1e771f2dff`). Depois de selecionar `primaryboot=1` com as duas BOOTCONFIG integrais, o aparelho iniciou com `ubi0`/`mtd21`; o marcador do outro estado **não existia** nesse overlay. O arquivo `T7-20261010-SLOT1` foi então escrito nesse sistema e conferido no overlay (SHA-256 `6bd738a28c845fc1862f223f78245354a6c4c00abb5a3b2857ac638c9b1b4103`). Após nova seleção de `primaryboot=0`, `ubi0` voltou ao `mtd20` e o marcador original `T7-20261010-SLOT2` reapareceu com o **mesmo SHA-256**. Isso confirma a separação dos `rootfs_data` e a persistência do marcador do estado `0` após dois reboots. O marcador do estado `1` foi conferido antes de sair dele; não foi relido após esse último reboot. O ensaio não prova por si só qual cópia de cada partição de boot foi executada.

Os marcadores e o script de alternância usado pelo Linux estão em `04_SCRIPTS_E_FERRAMENTAS/Teste_Marcadores_Slots/`; os logs de rede estão em `_FORA DO GitHub/Backups_teste_marcadores_slots_2026-10-10/`. Não foram escritos marcadores nas demais partições físicas.

O aparelho terminou o ensaio em `primaryboot=0`, stock v27, `ubi0`/`mtd20`, com o marcador do estado `0` preservado, `fsbootargs` ausente e os três rádios `UP`. O monitor de rede viu quedas curtas de TCP no retorno; o uptime continuou crescendo acima de 250 segundos, logo essas observações **não demonstram** novo reboot.

Uma auditoria **somente de leitura** das outras cópias mostrou BOOTCONFIG com `APPSBL/CDT/DEVCFG=1` e `HLOS/WIFIFW/rootfs=0` no boot final. As cópias físicas `QSEE`/`QSEE_1` tinham o mesmo SHA-256 completo; `SBL1`, `DEVCFG`, `TME`, `CDT` e `APPSBL` tinham hashes diferentes entre as respectivas cópias. Isso prova que não são meros links e que o seletor de rootfs não iguala automaticamente todos os componentes. Hash diferente não informa sozinho qual cópia o processador executou; para isso, usar os seletores específicos e, quando necessário, UART. As leituras estão em `_FORA DO GitHub/Backups_teste_marcadores_slots_2026-10-10/auditoria_hashes_particoes_slot2.txt`.

## 6. Regra operacional para gravar um dos dois sistemas pelo Linux

Esta tabela vale para os **dois contêineres UBI de sistema no layout medido hoje**, não para partições compartilhadas de boot. Conferir `/proc/mtd`, o endereço no `dmesg`, `primaryboot` nas duas BOOTCONFIG e `/sys/class/ubi/ubi0/mtd_num` antes de cada operação; não usar apenas o nome `rootfs_1` como endereço físico permanente.

| Sistema físico a instalar | Boot de trabalho | Alvo inativo visto pelo Linux | Seleção após verificar a gravação |
| --- | --- | --- | --- |
| Endereço `0x10640000`, `mtd21`, estado final `primaryboot=1` | Iniciar com `primaryboot=0`, `ubi0` em `mtd20` | `rootfs_1` = `mtd21` | Gravar as duas BOOTCONFIG integrais com `rootfs/primaryboot=1`; conferir e reiniciar |
| Endereço `0x01640000`, `mtd20`, estado final `primaryboot=0` | Iniciar com `primaryboot=1`, `ubi0` em `mtd21` | `rootfs_1` = `mtd20` | Gravar as duas BOOTCONFIG integrais com `rootfs/primaryboot=0`; conferir e reiniciar |

Para substituir **o contêiner UBI inteiro** (`wifi_fw`, `kernel`, `ubi_rootfs`, `rootfs_data`), trabalhar a partir do sistema oposto, confirmar que o alvo está desmontado e desanexado, fazer backup e só então usar `ubiformat`. Para atualizar **volumes individuais**, anexar o UBI inativo separadamente, atualizar o volume sem montá-lo para escrita simultânea, verificar hashes e desanexar antes da comutação. A política de preservar ou limpar `rootfs_data` é uma decisão explícita, pois cada contêiner tem seu próprio overlay. Depois da verificação, alterar **ambas** BOOTCONFIG de 512 KiB, conferir leitura de volta, manter `fsbootargs` ausente como no boot funcional e reiniciar. O sistema que acaba de subir deverá aparecer como `rootfs`/`ubi0`, independentemente do endereço físico.

**Exceções:** escrever um arquivo normal no overlay ativo (como o marcador) não exige boot pelo outro sistema. Partições de boot/calibração fora do UBI não seguem automaticamente essa regra; o seletor `rootfs/primaryboot` não troca todas as demais cópias. O Web Recovery do U-Boot é outro ambiente e o script da ROM stock não foi validado como instalador alternado de ambos os contêineres; não transportar a regra de nomes MTD do Linux para o comando `flash` do U-Boot sem leitura física posterior.

## Relatórios de evidência

- `06_DOCUMENTACAO/NOTAS_HARDWARE/COMPARACAO_GRAVACAO_UBOOT_V24_V27_2026-10-10.md`: scripts FIT e MIBIB.
- `06_DOCUMENTACAO/NOTAS_HARDWARE/GRAVACOES_ROM_STOCK_E_MAPA_SLOT2_2026-10-10.md`: destinos nomeados pela ROM stock e mapa estático.
- `06_DOCUMENTACAO/NOTAS_HARDWARE/ATUALIZACAO_NATIVA_ACER_T7_LINUX_2026-10-10.md`: caminho do `sysupgrade` no Linux.
- `06_DOCUMENTACAO/NOTAS_HARDWARE/TESTE_RESTAURACAO_STOCK_V27_SLOT2_2026-10-10.md`: gravação da UBI e três boots falhos.
- `06_DOCUMENTACAO/NOTAS_HARDWARE/TESTE_BOOT_NATIVO_SLOT2_V27_2026-10-10.md`: boot funcional com BOOTCONFIG integral e sem `fsbootargs`.
- `06_DOCUMENTACAO/COMPARACAO_WIFI_STOCK_V24_V27_CUSTOM_2026-10-10.md`: comparação de módulos e pacote `wifi_fw`.
- `04_SCRIPTS_E_FERRAMENTAS/Alternador_Boot_T7_V2/README.md`: FITs V2 gerados offline e teste pelo Web Recovery adiado.
- `04_SCRIPTS_E_FERRAMENTAS/Teste_Marcadores_Slots/README.md`: sequência e resultado dos dois marcadores de overlay.
