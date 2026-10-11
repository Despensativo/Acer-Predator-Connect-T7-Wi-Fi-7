# Gravações da ROM stock v24/v27 e mapa do Slot 2

**Atualização após os boots medidos em 10/10:** a tabela MIBIB abaixo mantém endereços físicos fixos, mas os **nomes MTD apresentados ao Linux trocaram de lugar** conforme `rootfs/primaryboot`. Não usar `rootfs_1`, `mtd20` ou `0x10640000` isoladamente como sinônimo permanente de “Slot 2”. Ver `CONSOLIDADO_DESCOBERTAS_T7_2026-10-10.md`.

Data: 10/10/2026. Fonte: scripts FIT e MIBIB extraídos das imagens Acer v24/v27 locais. As duas imagens usam o mesmo script de gravação (SHA-256 `b8e54d3e6c31aa108e140aa18852f6c89e5739784c4f1108b42d02ee125c82ad`) e a mesma MIBIB. Esta análise de gravação é estática; o relato de teste do alternador Slot 1 está no `04_SCRIPTS_E_FERRAMENTAS/Alternador_Boot_T7/README.md`.

## Tudo o que o script da ROM completa grava

O script primeiro valida `soc_hw_version`/`machid`, inicializa NAND, extrai MIBIB para RAM e chama `mibib_reload`. Essas etapas não são, por si, gravações persistentes. Em seguida, executa `xtract_n_flash` para **10 destinos** nesta ordem:

| Ordem | Partição física de destino | Conteúdo enviado | Slot/grupo |
| ---: | --- | --- | --- |
| 1 | `0:SBL1` | Primeira etapa de boot | Cópia sem `_1` |
| 2 | `0:MIBIB` | Tabela de partições | Compartilhada |
| 3 | `0:BOOTCONFIG` | Controle de seleção de boot | Cópia de controle 0 |
| 4 | `0:BOOTCONFIG1` | Mesmo payload de controle | Cópia de controle 1 |
| 5 | `0:QSEE` | Firmware de segurança | Cópia sem `_1` |
| 6 | `0:DEVCFG` | Configuração do dispositivo | Cópia sem `_1` |
| 7 | `0:TME` | Firmware TME | Cópia sem `_1` |
| 8 | `0:CDT` | Uma das 12 variantes de tabela DDR, escolhida pelo `machid` | Cópia sem `_1` |
| 9 | `0:APPSBL` | U-Boot/APPSBL | Cópia sem `_1` |
| 10 | `rootfs` | Imagem UBI com `wifi_fw`, `kernel`, `ubi_rootfs` e metadados de `rootfs_data` | Slot 1 |

O script **não manda gravar** `0:SBL1_1`, `0:QSEE_1`, `0:DEVCFG_1`, `0:TME_1`, `0:CDT_1`, `0:APPSBL_1` nem `rootfs_1`. Também não nomeia `0:APPSBLENV`, `0:ETHPHYFW`, `0:TRAINING`, `0:ART`, `0:LICENSE`, `0:TRAFFIC`, `0:SYSTRACE` ou `0:TRAFFIC_DAY`. A seleção de boot pode mudar porque as duas BOOTCONFIG são regravadas, mesmo sem gravação de `rootfs_1`.

O alternador de boot criado neste projeto é **outro FIT**, com outro script: grava `0:BOOTCONFIG` e `0:BOOTCONFIG1`; depois `saveenv` grava o ambiente persistente do U-Boot (`0:APPSBLENV`). Não grava a ROM stock, o kernel nem qualquer `rootfs`.

## Quantas partições há no Slot 2?

A MIBIB traz **25 partições físicas no total**. Há **7 partições físicas com sufixo `_1`** associadas a cópias secundárias; `BOOTCONFIG1` é a segunda cópia do controle de boot, não o sistema do Slot 2.

| Partição secundária | Endereço NAND | Tamanho reservado |
| --- | ---: | ---: |
| `0:SBL1_1` | `0x00180000` | 1,5 MiB |
| `0:QSEE_1` | `0x00880000` | 3,5 MiB |
| `0:DEVCFG_1` | `0x00C80000` | 0,5 MiB |
| `0:TME_1` | `0x00D80000` | 0,5 MiB |
| `0:CDT_1` | `0x00E80000` | 0,5 MiB |
| `0:APPSBL_1` | `0x01100000` | 1,5 MiB |
| `rootfs_1` | `0x10640000` | 240 MiB |

Para o Linux do Slot 2, a partição que contém o sistema é **uma só: `rootfs_1`** (historicamente `/dev/mtd20`). Dentro dela há **4 volumes UBI nomeados**: `wifi_fw`, `kernel`, `ubi_rootfs` e `rootfs_data`, mais o volume interno de layout UBI. A ROM stock v24/v27 inclui esses quatro volumes em sua imagem UBI, mas a grava em `rootfs` do Slot 1; ela não atualiza `rootfs_1` automaticamente.
