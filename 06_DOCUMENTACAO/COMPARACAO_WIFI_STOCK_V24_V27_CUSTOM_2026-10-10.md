# Comparação estática do Wi-Fi: stock v24, stock v27 e custom T7

**Atualização após o boot medido em 10/10:** a stock v27 iniciou o QCN9224 e os três rádios no estado `primaryboot=0`. Assim, a diferença de `qcn9224/regdb.bin` não é prova de incompatibilidade que impeça todo boot no hardware deste T7. Permanecem avisos de WMI/ACS e uma reinicialização inicial a investigar. Ver `NOTAS_HARDWARE/CONSOLIDADO_DESCOBERTAS_T7_2026-10-10.md`.

Data: 2026-10-10. Análise somente leitura das imagens locais; nenhum comando foi enviado ao roteador. Comparações de arquivo não demonstram qual arquivo o aparelho carregou durante um boot específico.

## Fontes verificadas

- v24: `_FORA DO GitHub/02_FIRMWARES_E_DUMPS_PESADOS/MTD_Full_Dumps/backup_predator_t7_ubi_rootfs.bin` (SquashFS, `/etc/version=1.01.000024`) e `backup_predator_t7_wifi_fw_raw.bin` no mesmo diretório.
- v27 stock: `01_FIRMWARES_E_IMAGENS/Stock_OEM_Recovery/rootfs_v27_stock_oem_38mb.squashfs` (`/etc/version=1.01.000027`) e `01_FIRMWARES_E_IMAGENS/Official_v27_Componentes/wifi_fw.bin`.
- custom de deploy: `_FORA DO GitHub/V27_CUSTOM_DEPLOY/rootfs.squashfs`, `kernel.bin` e `wifi_fw.bin`.

Cada arquivo `.ko` foi lido diretamente do SquashFS com `unsquashfs -cat`. A extração em massa no macOS produz colisões entre nomes que diferem apenas por maiúsculas/minúsculas; ela **não** foi usada para formar as conclusões abaixo. As seções ELF32 foram identificadas pelos cabeçalhos de seção, e seus bytes comparados individualmente.

## Drivers de kernel

As duas rootfs stock contêm os mesmos 328 nomes de módulos `.ko`. Apenas 18 têm SHA-256 diferente entre v24 e v27. Em nenhum dos 18 a seção `.text` mudou.

Doze módulos ligados à pilha Wi-Fi diferem **somente na seção `.note.gnu.build-id`**: `ath_pktlog`, `ipq_cnss2`, `mem_manager`, `monitor`, `qca_ol`, `qca_spectral`, `qdf`, `rawmode_sim`, `smart_antenna`, `telemetry_agent`, `umac` e `wifi_3_0`. Todas as outras seções, inclusive `.text`, `.rodata`, `.data` e `.modinfo`, são idênticas. Cada arquivo manteve o mesmo tamanho; a diferença foi de 19 ou 20 bytes do identificador.

| Módulo | SHA-256 v24 | SHA-256 v27/custom | Diferença de `.text` |
| --- | --- | --- | ---: |
| `ipq_cnss2.ko` | `e8a709ebd539911cfc52e9db1dae23c194995c2b7527c60fd5af1f1930ab8a10` | `5e9456f66622f98f3c9bac277f1e39df72deb66c41590cfb779199f1438c0ce8` | 0 bytes |
| `qca_ol.ko` | `7cd10958362b5b8efc254a5375c2c8958327eced0d2b9f6c0380c5c8f4810162` | `fa94a433ea195a519027767222124c2d7460e05272fd1c98fddcfd9769fa0b02` | 0 bytes |
| `umac.ko` | `c9ad8435b2f9f1404a9fd95e1236dbf246ff94a4029ac658fc190793b54e75c7` | `48fc2d90d20d16626917abfae484ba44364d3fe14843638c5c42d7d6949be91b` | 0 bytes |
| `wifi_3_0.ko` | `d6ea5816f9452a96fca9fcd803b6deba80a17c641de04d8eb62290ff5ca07a50` | `1b7c6ff79c359505f06b46596b052605c652ec1d19f143f98e36e3114ae43cfa` | 0 bytes |

Os outros seis módulos com hash diferente são `qca-nss-ppe-bridge-mgr`, `qca-nss-ppe-gretap`, `qca-nss-ppe-netlink`, `qca-nss-ppe-vlan`, `qca-nss-ppe-vxlanmgr` e `qca-ssdk`. A única seção modificada neles é `.rodata.str1.1`; a mudança é a string de data/hora de build. Portanto, os hashes novos não sustentam a afirmação de refinamentos de código para estabilidade de Wi-Fi 7/MLO.

Na rootfs custom de deploy há 324 dos 328 módulos da v27 stock. Todos os 324 comuns são idênticos byte a byte aos da stock v27. Os quatro ausentes (`ksmbd.ko`, `xt_DSCP.ko`, `xt_HL.ko`, `xt_TCPMSS.ko`) não são os drivers Wi-Fi citados. O `kernel.bin` custom é idêntico ao componente v27 (`SHA-256 818c3a986277e56bc224470342d20f010696c7f28a457145301c6afd864736ab`).

## Firmware do rádio e scripts

Os dois pacotes `wifi_fw` contêm 91 arquivos. Comparação de SHA-256 de cada arquivo: **90 iguais, 1 diferente**. O único diferente é `qcn9224/regdb.bin`:

| Origem | MD5 de `qcn9224/regdb.bin` | SHA-256 |
| --- | --- | --- |
| Backup v24 | `3875e820d1b8c5daf27ddc9091a22f68` | `ca3e192308a653975f07e9dfdc758f3e7f791bf15a2b2b8eb037edc8432e52ad` |
| v27 stock e custom | `a826729629d1e99b55e6d73002b8ecbd` | `8888abda3175f8f9550571e168f31c545031555461da7b1524955064a7cbfc04` |

O `wifi_fw.bin` da custom é idêntico ao componente stock v27 (`SHA-256 5c05c0e0747c8f678178fcdf3631d272fc784c82d270e7ee60be72e8ceb1f9de`). Assim, `amss_dualmac.bin`, `bdwlan_fcc.b1015`, o `regdb.bin` genérico na raiz do pacote e todos os demais arquivos do firmware têm o mesmo conteúdo nas duas gerações verificadas, exceto o `qcn9224/regdb.bin`.

Entre as rootfs stock v24/v27, os scripts `etc/init.d/wifi_fw_mount`, `etc/init.d/load_cnss2`, `lib/wifi/qcawificfg80211.sh`, `lib/wifi/qcawifi.sh`, `lib/wifiCountryCode.sh` e `lib/wifi/qca-wifi-modules` são idênticos. Em `etc/config/wifi_cert`, a mudança observada foi o suporte 6 GHz da entrada `RO` de `N` para `Y`; as entradas `US` e `BR` não mudaram.

## Interpretação e limite

A imagem custom contém configuração de país `US` para os três rádios em `/etc/config/wireless`. O script `04_SCRIPTS_E_FERRAMENTAS/aplicar_potencia_maxima_us.py` usa UCI e `cfg80211tool setCountry US`; ele não substitui `regdb.bin`. A custom herdou o `qcn9224/regdb.bin` da stock v27.

O crash `QCN9224_PCI1` em `Post-STM` é compatível com uma falha na inicialização do subsistema de rádio, mas o trecho de log apresentado não identifica uma rejeição explícita do banco regulatório. A diferença do `regdb.bin` é um candidato para teste controlado; a comparação estática não prova causalidade. Também é necessário verificar as cópias no overlay, os links efetivos e os hashes dos arquivos carregados durante o boot do Slot 2 antes de atribuir o crash ao pacote gravado.
