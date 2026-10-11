# Conferência atual do Slot 2 — 2026-10-02

## Conclusão

O Slot 2 já contém kernel, RootFS e firmware Wi-Fi idênticos aos volumes funcionais do Slot 1, pelos hashes SHA-256. Tabela de volumes coerente com a referência funcional. Overlay sem blocos UBI associados. Não há necessidade demonstrada de restaurar/regravar esses conteúdos ou esvaziar novamente o overlay.

Isso valida conteúdo e metadados observados, não o boot do Slot 2. Não foi alterada seleção de boot nem enviado reboot. Estado e configuração de boot precisam ser considerados antes de um teste separado; não concluir que o Slot 2 está operacional apenas pelos hashes.

## Estado do aparelho

Sistema normal responde em 192.168.73.2. Linux 5.4.213 ARM32. Bootargs ubi.mtd=rootfs. mtd21=rootfs, ubi0/mtd_num=21 e overlay /dev/ubi0_3 confirmam Slot 1 ativo. mtd20=rootfs_1 corresponde ao Slot 2 e não estava anexado ao UBI. bootcmd=bootipq; fsbootargs/primaryboot não retornaram valor. Ambiente persistente lido informa ipaddr=192.168.10.1 e serverip=192.168.10.10; isso não é leitura do ambiente volátil do Failsafe.

## Método somente leitura

Lidos os cabeçalhos VID dos 960 blocos físicos da mtd20 por dd, sem ubiattach. Identificadas duas cópias de layout nos PEBs 651/652, sequências 3922/3923, com registros equivalentes, CRCs corretos e update_marker=0. Nenhuma leitura curta. Os volumes de sistema tinham mapeamento lógico contínuo, sem duplicatas e copy_flag=0; hashes obtidos em fluxo pela ordem lógica dos PEBs, pulando os cabeçalhos físicos e limitando ao comprimento do volume. Não baixados arquivos de configuração ou payloads completos para o PC.

Volume | Tipo | LEBs reservados | Conteúdo comparado
--- | --- | --- | ---
wifi_fw | static | 44 | 8.554.496 bytes
kernel | static | 25 | 4.238.664 bytes
ubi_rootfs | dynamic | 157 | 39.870.464 bytes
rootfs_data | dynamic | 690 | Nenhum VID associado ao volume 3

A ausência de VID para volume 3 em toda a varredura é compatível com volume esvaziado, sem filesystem persistente alocado. Isso não prova como ele foi esvaziado, nem antecipa o resultado da primeira montagem.

## Hashes SHA-256 iguais nos dois slots

- wifi_fw: 835763cc96fe2d798e5ba9ca9ff14c1cd82fab18848a9cf0bf1f514e320dac7b
- kernel: ff131c1aeb280dfc9022a4474330e55e19b82f504723021546c46ea4fb4963fb
- ubi_rootfs: 57d1427dad607e6f30373fff8c27681d6fc7d02c3276c0b3ef8aa45755f8e7d3

## Evidências

- evidencias/conferencia-slots-20261003T025209Z.txt.
- evidencias/slot2-varredura-metadados-20261003T025436Z.json.
- evidencias/comparacao-hashes-slots-20261003T025604Z.txt.
- evidencias/resultado-conferencia-slot2-atual.json.

Nenhuma partição escrita, formatação, anexação/montagem UBI, alteração de ambiente ou reinício foi realizado nesta conferência.
