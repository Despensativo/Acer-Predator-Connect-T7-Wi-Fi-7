# Kernel e drivers stock da versão 1.01.000027 — Predator Connect T7

Análise local em 09/10/2026. Fonte primária: os três componentes em `01_FIRMWARES_E_IMAGENS/Official_v27_Componentes/`, extraídos da imagem em `01_FIRMWARES_E_IMAGENS/Stock_OEM_Recovery/nand-4k-ipq5332-single_101000027.img`. Inspeção somente leitura; nenhum comando foi enviado ao T7. Este documento descreve o pacote, sem presumir que todos os módulos estejam carregados no aparelho ou que o DTB examinado seja necessariamente o selecionado no boot atual.

## Identidade e integridade

| Arquivo | Conteúdo | Tamanho real | SHA-256 |
| --- | --- | ---: | --- |
| `kernel.bin` | FIT com kernel LZMA e 14 DTBs | 4.237.480 B | `818c3a986277e56bc224470342d20f010696c7f28a457145301c6afd864736ab` |
| `rootfs.squashfs` | SquashFS XZ, bloco de 256 KiB, 5.031 inodes | 39.582.514 B | `fb4c1611319749f17c0bcfb6ac6265697550eb39365aa52a9fd143aa02741348` |
| `wifi_fw.bin` | SquashFS XZ de firmware de rádio, 93 inodes | 8.553.552 B | `5c05c0e0747c8f678178fcdf3631d272fc784c82d270e7ee60be72e8ceb1f9de` |
| Imagem de atualização completa | FIT com script de gravação e outros componentes de boot | 57.997.600 B | `b18c54aabfbad9da22245748e393e63f8b56467e011fac3bdba021f8a91103cc` |

Alguns relatos anteriores usam 39.616.512 B para o RootFS e 8.554.496 B para o Wi-Fi. Esses valores são os tamanhos declarados nos volumes UBI; os arquivos SquashFS locais acima têm tamanhos reais menores. Não usar esses números como se fossem intercambiáveis na comparação byte a byte.

## Kernel

O nó FIT `kernel@1` declara `ARM OpenWrt Linux-5.4.213`, arquitetura `arm`, compressão `lzma`, carga e entrada `0x40008000`. O payload descomprimido mede 11.842.200 B e contém a cadeia de versão:

`Linux version 5.4.213 (faiot@build-server3) (gcc version 7.5.0 (OpenWrt GCC 7.5.0 r0+14315-60fc7c16ce)) #0 SMP PREEMPT Tue Mar 11 08:57:41 2025`

A configuração embarcada `IKCFG_ST` foi descomprimida e confirma `CONFIG_ARM=y`, `CONFIG_ARCH_IPQ5332=y`, `CONFIG_SMP=y`, `CONFIG_PREEMPT=y`, `CONFIG_MODULES=y`, `CONFIG_IKCONFIG_PROC=y`, `CONFIG_QCOM_SCM_32=y`, `CONFIG_QCOM_Q6V5_MPD=y`, `CONFIG_MTD_NAND_QCOM=y`, `CONFIG_MTD_UBI=y`, `CONFIG_UBIFS_FS=y` e `CONFIG_SQUASHFS_XZ=y`. `CONFIG_NET_SCH_CAKE=m`, `CONFIG_NF_FLOW_TABLE=m` e `CONFIG_USB_DWC3=m`. O RootFS se identifica como OpenWrt `19.07-SNAPSHOT`, target `ipq53xx/ipq53xx_32`, arquitetura de pacote `arm_cortex-a7_neon-vfpv4` e versão Acer `1.01.000027`.

O SoC contém núcleos Cortex-A53, mas este **Linux OEM é ARM de 32 bits**. Isso é confirmado tanto pelo FIT quanto pelo ELF ARMv7 dos módulos (`vermagic=5.4.213 SMP preempt mod_unload ARMv7 p2v8`). A existência de componentes de boot AArch64 não muda a arquitetura desse kernel.

O FIT inclui DTBs para várias placas. No `fdt@mi01.6`, o modelo é `Qualcomm Technologies, Inc. IPQ5332/AP-MI01.6`; aparecem `qcom,ess-switch-qca8386` via MDIO, `qcom,nss-ppe` e portas `qcom,nss-dp`. O mesmo DTB marca `wifi@c0000000` (`qcom,cnss-qca5332`) e `wifi2@f00000` (`qcom,cnss-qcn9224`) como `ok`, enquanto `wifi1` QCN9224 e `wifi3` QCN9160 estão `disabled`. Isso descreve **esse DTB**, não prova por si só quais nós o bootloader escolheu nem quais rádios inicializaram no T7 físico.

## Pilha de drivers no RootFS

O SquashFS oficial contém 328 arquivos `.ko` em `lib/modules/5.4.213/`. As peças mais relevantes para o T7 são:

| Subsistema | Módulos presentes | Papel inferido dos nomes, dependências e scripts |
| --- | --- | --- |
| Wi-Fi host | `ipq_cnss2`, `qdf`, `umac`, `qca_ol`, `wifi_3_0`, `qca_spectral`, `ath_pktlog` | Inicialização CNSS, framework QCA, controle de rádio, telemetria |
| Switch/Ethernet | `qca-ssdk`, `qca-nss-ppe`, `qca-nss-dp`, `phy-qca-uniphy`, `phy-qca-m31` | Switch/PHY, PPE e portas de rede |
| Aceleração | `ecm`, `ecm-wifi-plugin`, `qca-nss-sfe`, família `qca-nss-ppe-*` | Seleção e gestão de caminhos de aceleração e offload |
| Outros | `rmnet_core`, `rmnet_ctl`, `dwc3-qcom`, `usbcore` | Capacidades comuns da plataforma; presença não prova uso no T7 |

As dependências ELF mostram a sequência lógica: `qca-nss-dp` depende de `qca-nss-ppe` e `qca-ssdk`; `qca_ol` depende de `umac`, `qdf`, `ipq_cnss2`, `qca_spectral`, `mem_manager` e `cfg80211`; `wifi_3_0` depende de `umac`, `qca_ol`, `qdf`, `qca-nss-ppe-ds` e `qca-nss-ppe`. O arquivo oficial `lib/wifi/qca-wifi-modules` lista a ordem de carga da parte Wi-Fi. O serviço `etc/init.d/load_cnss2` insere `ipq_cnss2.ko` e inicia `cnssdaemon`. O serviço `qca-nss-ecm` seleciona frentes SFE/PPE conforme configuração. A mera existência de módulos para várias funções não significa que estejam ativos em todas as configurações.

Não há `ath12k.ko` na lista oficial de módulos. A pilha Wi-Fi stock examinada é a QCA/QSDK (`qca_ol`/`wifi_3_0`/CNSS); tratá-la como um conjunto de módulos `ath12k` upstream seria incorreto.

## Firmware Wi-Fi separado

O `wifi_fw.bin` **não é um módulo de kernel**: é um SquashFS montado pelo serviço `wifi_fw_mount` no caminho `/lib/firmware/IPQ5332/WIFI_FW`. Ele contém `q6_fw0.*`, `q6_fw1.*`, dados de placa `bdwlan*`, banco regulatório e diretório `qcn9224/` com `amss.bin`, `m3.bin` e variantes de calibração/região. O script cria links para os caminhos que CNSS e drivers usam. A seleção efetiva de arquivo de placa/região depende do hardware e da configuração em execução; a presença de variantes FCC/CE não determina qual está ativa.

Também há dados únicos do aparelho fora desses três arquivos, como ART/calibração. Copiar somente `wifi_fw.bin` para outra placa não reproduz a calibração individual.

## Implicações práticas

1. Reutilizar os `.ko` stock exige compatibilidade com o kernel 5.4.213 ARMv7 e os símbolos/dependências dessa construção. O `vermagic` observado impede tratá-los como módulos prontos para o kernel experimental 6.18 ARM64.
2. `kernel.bin`, `rootfs.squashfs` e `wifi_fw.bin` têm funções diferentes e devem permanecer identificados por hash durante qualquer análise ou comparação.
3. O arquivo `.img` completo contém um script de **gravação de flash** e outros estágios de boot; não é uma imagem para boot temporário. Sua inspeção não executou o script.
4. Para afirmar quais drivers e firmwares estão **carregados no aparelho**, faltam leituras atuais de `/proc/modules`, `dmesg`, `/proc/device-tree/model`, `/proc/cmdline`, pontos de montagem e interfaces/radios. A análise aqui comprova o conteúdo do pacote stock.

## Método de reprodução

- `fdtget` leu propriedades do FIT; um parser local dos tokens FDT extraiu `kernel@1.data`, descomprimido por LZMA, e a configuração entre `IKCFG_ST` e `IKCFG_ED` por gzip.
- `unsquashfs -lls` e `unsquashfs -cat` consultaram os dois SquashFS oficiais sem executar conteúdo. O hash de `qca_ol.ko` lido diretamente do SquashFS coincidiu com o exemplar extraído no projeto (`fa94a433ea195a519027767222124c2d7460e05272fd1c98fddcfd9769fa0b02`).
- `fdtget` e `dtc` inspecionaram apenas o `fdt@mi01.6` extraído em `/tmp`.
