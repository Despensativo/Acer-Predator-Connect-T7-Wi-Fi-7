# Auditoria comparativa local: Predator Connect X7 101000050 × T7 101000027

Data: 2026-10-03. Escopo: pacotes oficiais fornecidos, examinados como dados; nenhuma gravação no HD externo ou em roteadores. **A comparação é entre modelos diferentes.** A frase “101000024 e 101000027” no pedido não corresponde aos dois alvos indicados. O T7 024 foi tratado em auditoria anterior, separada.

**Estado consolidado após o aprofundamento:** o código carregável do APPSBL não apresentou mudança de instruções; o kernel continua 5.4.213 com a mesma configuração `CONFIG_*`; a única mudança de `.text` demonstrada em `umac.ko` ajusta o limite inferior de um parâmetro associado a `min-rssi` de −90 para −120. O receptor web de CFG mantém as mesmas instruções depois de normalizar endereços de chamadas e linhas de log, e `sysupgrade -r` é idêntico. Isso torna a continuidade do mecanismo CFG uma inferência forte, mas **não comprova** que um CFG modificado seja aceito num X7 real. O usuário dispõe somente da ROM baixada do X7: não há CFG X7 nem aparelho X7 para validar persistência, serviços ou `/proc/mtd`. Os complementos das seções 9–18 prevalecem quando refinam conclusões preliminares das seções 4–8.

## 1. Origens, integridade e alcance da validação

| Estado | Origem verificada (arquivo regular `.img`) | Bytes | SHA-256 da origem e da cópia de trabalho |
|---|---|---:|---|
| Fato observado | `H:\FEITOS COM IA\acer-predator-fota-extractor\firmwares_oficiais\Acer_Predator_X7\nand-4k-ipq5332-single_101000050.img` | 58.259.744 | `b02e7b2e162df9f8016437209136e001833e52069502b22b38b3f0e33020e8ef` |
| Fato observado | `H:\FEITOS COM IA\Acer-Predator-Connect-T7\02_BACKUPS_E_DUMPS\MTD_Full_Dumps\Acer_Predator_Connect_T7\nand-4k-ipq5332-single_101000027.img` | 57.997.600 | `b18c54aabfbad9da22245748e393e63f8b56467e011fac3bdba021f8a91103cc` |

**Fato observado.** Antes da extração, C: tinha 140.991.610.880 bytes livres. As cópias e extrações foram feitas em `C:\Users\User\Documents\Codex\X7-vs-T7-101000050-vs-101000027\` e no filesystem interno do WSL Ubuntu. Nenhum erro de leitura/E/S foi observado. Os comprimentos declarados nos cabeçalhos FIT coincidem com os tamanhos dos arquivos. Em cada pacote, 22 hashes CRC32 dos componentes externos conferiram. No FIT interno de kernel X7, 15 CRC32 e 15 SHA-1 conferiram; a validação análoga do T7 consta da auditoria anterior. Isso verifica consistência dos contêineres lidos, **não** assinatura do fornecedor, proveniência, nem integridade da NAND física.

**Fato observado.** A identificação `file`, o cabeçalho FDT `d0 0d fe ed` e `dumpimage -l` mostram que ambos são pacotes OTA FIT, **não dumps completos de NAND**, apesar do nome da pasta. Os `AGENTS.md` aplicáveis do workspace foram consultados. Nenhum dado privado, chave ou identificador completo foi reproduzido neste relatório.

## 2. Geometria, organização e mapa

| Estrutura | X7 050 | T7 027 | Estado |
|---|---:|---:|---|
| FIT externo | 22 imagens | 22 imagens | Fato observado |
| XBL/SBL1, MIBIB, BOOTCONFIG ×2, QSEE, DEVCFG, TME, 12 CDT e `flash.scr` (índices 0–19) | hashes iguais | hashes iguais | Fato observado |
| APPSBL/U-Boot, índice 20 | 565.320 B | 565.320 B | hashes diferentes |
| UBI, índice 21 | 55.050.240 B | 54.788.096 B | X7 tem um PEB extra |
| UBI PEB / I/O mínimo / LEB | 262.144 / 4.096 / 253.952 B | iguais | Fato observado |
| UBI: layout / dados / desconhecidos | 2 / 208 / 0 PEB | 2 / 207 / 0 PEB | Fato observado no pacote |
| `wifi_fw` | 34 PEB, 8.554.496 B | iguais | **SHA-256 igual**: `5c05c0e0747c8f678178fcdf3631d272fc784c82d270e7ee60be72e8ceb1f9de` |
| `kernel` | 17 PEB; 4.239.100 B extraídos | 17 PEB; 4.237.480 B | FITs diferentes; 14 DTBs idênticos |
| `ubi_rootfs` | 157 PEB; 39.870.464 B | 156 PEB; 39.616.512 B | SquashFS diferente |
| `rootfs_data` | 0 PEB de conteúdo | 0 PEB de conteúdo | persistência real não incluída |

**Fato observado.** A MIBIB dos dois pacotes é byte a byte igual. O mapa lógico completo está em `logs/partition-map.tsv` da auditoria anterior: SBL1 `0x0`, MIBIB `0x300000`, APPSBL `0xf80000`, APPSBL_1 `0x1100000`, ART `0x1400000`, `rootfs` `0x1640000`, `rootfs_1` `0x10640000`, fim das partições em `0x1ffc0000`. Cada `rootfs` reserva `0xf000000` bytes; há `0x40000` de espaço lógico até 512 MiB. Esses offsets vêm da tabela de partições empacotada, não de leitura física do aparelho. O `flash.scr` idêntico referencia APPSBL e rootfs; a existência de partição secundária na tabela não demonstra que o pacote a usa automaticamente.

**Precisa confirmar.** O I/O mínimo UBI de 4 KiB e o nome `nand-4k` são compatíveis com página NAND de 4 KiB. Os FIT não incluem OOB, ECC, mapa de bad blocks, ART, ambiente U-Boot ou dados persistentes do aparelho; portanto não se pode distinguir efeitos físicos de bad blocks nem atestar saúde da flash. PEBs não utilizados e padding de imagens não são alterações funcionais.

## 3. Inventário extraído

**Fato observado.** Os dois volumes `wifi_fw` extraem o mesmo SquashFS: 91 arquivos e 2 diretórios, sem diferenças de conteúdo nem metadados no manifesto. Isso inclui os firmwares de rádio e a base regulatória **presentes no volume**, mas não prova que o mesmo firmware seja carregado em ambos os aparelhos.

**Fato observado.** O rootfs T7 tem 5.030 entradas de inventário; o X7, 5.058. Há 136 caminhos acrescentados, 108 removidos e 751 arquivos de mesmo caminho com conteúdo diferente; nenhum caminho comum teve apenas metadados diferentes no comparador. O SquashFS X7 extrai 4.331 arquivos, 254 diretórios, 473 symlinks e 1 dispositivo; o T7, 4.303 arquivos com os demais totais iguais. Arquivos web com nomes contendo hash representam muitos dos acréscimos/remoções e podem ser substituições de build, não recursos independentes. Manifestos com tipo, modo, tamanho e SHA-256 estão em `logs/manifest-x7-*.jsonl` e nos manifestos T7 da auditoria anterior.

**Fato observado.** O inventário opkg passa de 568 para 569 pacotes: entra `fibo_logtool`; não sai pacote. Vinte e seis campos `Version` mudam, sobretudo a revisão geral `r0+14315-60fc7c16ce` → `r0+14466-ea6c334be9` e pacotes relacionados a modem. O pacote `kmod-qca-wifi-unified-profile` passa de `5.4.213+g5e30b91-1` para `5.4.213+g5c5c304-1`; isso **não** altera a versão principal do kernel. Há centenas de `.control` alterados, em grande parte metadados de build; ver `logs/packages.txt`.

## 4. Mudanças significativas

| Estado | Componente e evidência precisa | Interpretação e impacto provável |
|---|---|---|
| **Fato observado** | `etc/rc.button/reset`, linhas 27–35 no X7: antes de `jffs2reset`, para `modem_datausage` e executa `flash_eraseall /dev/mtd22` e `/dev/mtd24`; o script do botão no T7 não contém essas linhas. Capturas de `/proc/mtd` de um T7 real identificam `mtd22` como `0:TRAFFIC` (6 MiB) e `mtd24` como `0:TRAFFIC_DAY` (3 MiB). Bibliotecas de ambos os pacotes já contêm os mesmos comandos no contexto textual de `system_factoryReset`/`factoryreset`. | **Inferência:** o X7 passou a limpar o histórico de tráfego também pelo botão físico de reset; a rotina de reset pela interface já parece ter esse caminho em ambos. Essas duas partições não são bootloader nem ART no T7 capturado. A enumeração de um X7 real ainda não foi lida. |
| **Fato observado** | `etc/config/firewall`: nova zona `lan1` com input/output/forward `ACCEPT`, encaminhamento `lan1`→`wan`, regras DNS/DHCP e encaminhamentos `lan`↔`lan1`. | **Inferência:** a topologia padrão do X7 prevê uma LAN adicional e comunicação entre LANs. **Precisa confirmar:** interfaces associadas em runtime e efeito sobre isolamento; não há prova de porta aberta na WAN. |
| **Fato observado** | `etc/lighttpd/lighttpdmqtt.conf`, linhas 266–315: blocos TLS `:8443` e `[::]:8443` ativos no X7, antes comentados no T7. `etc/init.d/lighttpd/lighttpd.init:55` inicia essa configuração. O PEM referenciado não está embutido no rootfs. | **Inferência:** o processo MQTT/web tentará escutar HTTPS na 8443 se iniciar e gerar/encontrar certificado. **Precisa confirmar:** sucesso do serviço, ACL/firewall e alcance a partir de LAN/WAN. |
| **Fato observado** | `lib/filter/faiot_initial_firewall.sh` cria cadeia IPv4/IPv6 `PARENTCTRL_ACCESS_FWD`; `lib/filter/faiot_firewall_cfg.sh` chama o novo `faiot_parentalCtlAccessRestriction.sh`. Este usa estado `TrandMicroPC`, MAC, horário e iptables para `ACCEPT`/`DROP` (linhas 5–33). | **Inferência:** foi acrescentado um mecanismo de restrição de acesso por dispositivo/horário. A grafia do estado foi preservada como no script. **Precisa confirmar:** interface, política padrão e interação com regras existentes. |
| **Fato observado** | `lib/filter/faiot_parentalCtl.sh`: as duas regras `PARENTALCTL_FWD` para URL/ipset deixam de incluir `-m time --timestart ... --timestop ... --weekdays ...`. | **Inferência:** quando essa função é chamada com a regra ativa, o bloqueio de URL deixa de depender diretamente do horário nessa cadeia; pode haver agendamento em outra camada. Merece teste de comportamento em bancada. |
| **Fato observado** | `lib/wifi/hostapd.sh` lê `isbasic`; quando verdadeiro, configura `beacon_prot=0` e `add_sha256=0`. `lib/functions/repacd-map.sh` acrescenta limpeza de VAPs/MLDs na desmontagem mesh. | **Inferência:** há ajuste de compatibilidade/segurança para SSID básico e manutenção de VAPs na malha. **Precisa confirmar:** condições de geração da configuração hostapd e repercussão em PMF/WPA no aparelho. |
| **Fato observado** | `lib/wifiMesh_TwoPack.sh` deixa de copiar arquivos `dhcp`, `firewall` e `network` ao tornar-se controlador. | **Inferência:** preserva configurações existentes nesses três arquivos durante essa transição; comportamento efetivo depende do fluxo de provisionamento. |
| **Fato observado** | `usr/bin/logtool`, `usr/bin/faiot_modemlog.sh`, `etc/config/datausage`, `ipqApnTable`, `qxdm_default.cfg`, perfis WAN `PA_wanconfig` e `PLAY_wanconfig` entram; cinco perfis de operadoras T7 saem. `lib/netifd/rmnet.script` muda a criação de rota IPv6 e evita `network_phy lan` se `logtool` estiver rodando. | **Inferência:** X7 amplia diagnóstico/gestão de modem e muda tratamento de WAN móvel. Perfis de operadora são dados específicos do modelo/mercado; não representam ganho universal para T7. |
| **Fato observado** | `lib/functions/silent-reboot.sh` retorna 3 quando `/tmp/model` é `X7`; `etc/init.d/log` muda buffer padrão 64→5120; `etc/init.d/mwan3` acrescenta `killall lock`. | **Inferência:** o X7 evita reboot silencioso por esse caminho, retém mais log e altera limpeza de lock do multi-WAN. Unidades/uso real do buffer dependem do consumidor da configuração. |
| **Fato observado** | `etc/config/acer_ota`: versão `1.120`→`1.163`, permissão `0775`→`0664`; `usr/bin/fota`, `usr/bin/modem_fota_tool` e `usr/sbin/modem_readd` têm hashes diferentes. `usr/bin/fota.sh` e `flash.scr` são iguais. | **Precisa confirmar:** sem símbolos/trechos de código suficientes, não há prova de mudança nas regras de assinatura, instalação por CFG, anti-rollback ou slot. A permissão remove bit de execução do arquivo de configuração, cujo conteúdo não é um programa. |
| **Fato observado** | `etc/opkg/keys/`: um arquivo de chave pública sai e outro entra. Conteúdo de chave omitido. | **Inferência:** confiança opkg foi atualizada; pode afetar instalação de pacotes de feeds antigos, não prova bloqueio de root, CFG ou imagens. |
| **Fato observado** | Interface `webapps/web/pub/dist/` passa de título T7 a X7 e `version.json` de `T7_WEB_1.01.000034` a `_WEB_1.02.000032`; há 64 arquivos JS no X7 e 53 no T7, sem SHA-256 de conteúdo idêntico entre eles. Não há source maps no pacote X7. | Há rebuild e diferenças de interface do modelo X7. **Precisa confirmar:** recursos específicos e fluxos de autenticação a partir de JS minificado/servidor, antes de atribuir funcionalidade ou falha. Mudança de hash não equivale a recurso novo. |
| **Fato observado** | FIT do kernel: Linux **5.4.213 em ambos**, GCC 7.5.0; strings de build T7 `r0+14315-60fc7c16ce`/11-03-2025 e X7 `r0+14466-ea6c334be9`/04-08-2026. Os 14 DTBs são byte a byte iguais. | Há kernel recompilado, sem migração para 5.15/6.18. **Precisa confirmar:** quais rotinas de kernel mudaram; 3.456.274 bytes diferentes no kernel descomprimido incluem efeitos de layout e não equivalem a esse número de alterações funcionais. |
| **Fato observado** | Dos 18 módulos `.ko` com hashes diferentes, 17 preservam bytes de `.text`, `.rodata`, `.data`, `.init.text` e `.modinfo` comparáveis. Em `umac.ko`, só três bytes de `.text` mudam, alterando a faixa aceita de um parâmetro relacionado à mensagem `min-rssi` de −90…−30 para −120…−30. | **Inferência:** há uma ampliação do limite configurável, sem prova de alteração do padrão, alcance ou desempenho Wi-Fi. Os 17 não comprovam driver mais recente em execução; diferenças em outras seções podem refletir build/linkedição. |

## 5. Boot, root por CFG, recuperação e OpenWrt

**Fato observado.** `flash.scr`, XBL/SBL1, MIBIB, BOOTCONFIG, QSEE, DEVCFG, TME e CDT são idênticos. APPSBL tem 565.320 B nos dois pacotes; seus 77 bytes alterados em 24 intervalos foram localizados em identificadores de build, timestamp gzip e campo de 32 B fora do segmento carregável. O gzip embutido descomprime para conteúdo idêntico. **Inferência forte:** este pacote não acrescenta lógica TFTP nem console de rede ao APPSBL. **Precisa confirmar:** significado do campo de 32 B, ambiente U-Boot gravado no aparelho e recuperação real. Se o U-Boot funcional da flash falhar, a presença de `tftpboot` no binário não garante TFTP, pois esse comando depende do próprio U-Boot rodando.

**Fato observado.** `etc/config/dropbear` e os DTBs não mostram mudança pertinente. O handler web de restore CFG preserva suas instruções após normalizar realocações e linhas de log; `sbin/sysupgrade` é idêntico e mantém `tar -C / -xzf` no caminho `-r`. O backend X7 acrescenta operações de perfis/APN ao redor do restore. **Inferência forte:** o mecanismo básico de restauração por CFG permaneceu. **Precisa confirmar:** aceitação de um CFG modificado, autenticação completa e resultado num X7 real; o usuário possui apenas a ROM, sem backup CFG X7. O utilitário T7 local tem efeitos colaterais específicos de slot e não deve ser aplicado diretamente ao X7. Nenhuma conclusão aqui autoriza flash cruzado, atualização isolada de U-Boot ou escrita em partição secundária.

**Inferência.** Para porte OpenWrt, o material reutilizável com evidência mais forte é o mapa MIBIB, os 14 DTBs idênticos e o `wifi_fw` idêntico; os ajustes de shell para malha/WAN podem servir como referência de comportamento. **Precisa confirmar:** licenças, dependências binárias, kernel ABI, art/calibração e funcionamento em Linux 6.18. Os módulos compilados para 5.4.213 não podem ser assumidos carregáveis em 6.18.

## 6. Diferenças de baixo nível sem função demonstrada

- **Fato observado:** X7 FIT/UBI possui exatamente mais um PEB de 256 KiB, atribuído a `ubi_rootfs`; datas FIT/SquashFS, sequência UBI, padding e tamanho comprimido mudam. Não há evidência de bad blocks no pacote.
- **Fato observado:** APPSBL tem 77 bytes diferentes em 24 intervalos, todos localizados em identificadores de build, timestamp gzip ou um campo de 32 B fora do único segmento `LOAD`; o payload gzip descomprimido é idêntico. O significado do campo externo segue desconhecido.
- **Fato observado:** `.control` opkg, 144 artefatos Samba e assets web com nomes de hash compõem grande parte dos 751 caminhos alterados. 55 de 212 ELF comparados têm `.text` diferente; várias bibliotecas Samba e `umac.ko` estão nesse grupo. Versão Samba `4.14.12` permanece, mas não se pode atribuir CVE ou ganho de segurança sem análise orientada.
- **Fato observado:** alguns executáveis ARM vêm sem tabela de seções ELF; seus hashes mudaram, mas o comparador de `.text` não consegue classificá-los. Não interpretar ausência de seção como igualdade de código.

## 7. Método, reprodutibilidade e limites

**Ferramentas e operações realizadas.** PowerShell `Get-Item`, `Get-Volume`, `Get-FileHash -Algorithm SHA256` identificou origens e espaço; `Copy-Item` para disco interno seguido de SHA-256 validou cópias. Ubuntu WSL `file` 5.46 identificou FIT/SquashFS/ELF. `dumpimage` U-Boot 2025.10 com `-l` e `-T flat_dt -p <índice> -o <arquivo>` listou e separou 22 componentes externos e 15 internos do kernel; `validate_fit.py` revalidou CRC32/SHA-1. `ubi-reader` 0.8.16 (`ubireader_display_info`, `ubireader_extract_images`) interpretou UBI e volumes; `unsquashfs` 4.7.5 com `-processors 1 -no-progress -no-xattrs` extraiu rootfs e wifi. Scripts Python locais `inventory.py`, `compare_manifests.py`, `compare_packages.py`, `compare_elf.py`, `text_diffs.py` e `binary_ranges.py` produziram logs e comparações. `file`, hashes e contagens de arquivos/volumes foram usados como validação cruzada. Os comandos não executaram arquivos extraídos. Logs de `dumpimage`, UBI, `unsquashfs`, inventários, diferenças e os scripts ficam na área C:; trabalho anterior T7 em `C:\Users\User\Documents\Codex\T7-audit-101000024-vs-101000027\`. Extrações nativas WSL ficam em `/root/x7-vs-t7-101000050-vs-101000027/x7/` e `/root/t7-audit-101000024-vs-101000027/027/`.

**Limitações.** A auditoria estrutural dos contêineres e dos arquivos extraídos foi concluída sem erro de leitura, mas a análise funcional **não é completa**: faltam flash física/OOB/ECC, partições persistentes, ambiente de boot, `/proc/mtd` capturado de um X7 real, descompilação dirigida de `fota`/interface web/`umac.ko`, e teste do fluxo CFG. Há `/proc/mtd` capturado de um T7 real, com `mtd22/24` identificados. A saída do comparador ELF não cobre executáveis sem seções. Não foi feita validação de assinatura criptográfica do fabricante. A análise é de pacotes de modelos distintos, não uma trajetória de atualização do mesmo dispositivo.

## 8. Principais achados e testes seguros seguintes

1. **Fato observado:** são X7 050 e T7 027, ambos OTA FIT, não dumps físicos NAND.
2. **Fato observado:** 20/22 componentes externos, 14 DTBs e todo `wifi_fw` são idênticos.
3. **Fato observado:** kernel continua 5.4.213 e tem a mesma configuração `CONFIG_*`; `umac.ko` amplia de −90 para −120 o limite inferior aceito de um parâmetro `min-rssi`. Não há ganho de alcance comprovado.
4. **Fato observado:** no T7 capturado, `mtd22/24` são áreas de estatísticas de tráfego, e ambos os pacotes contêm apagamento dessas áreas na rotina de reset da interface; o botão X7 acrescenta esse apagamento explicitamente.
5. **Fato observado:** firewall X7 inclui `lan1` e uma cadeia nova de controle parental; porta TLS 8443 foi configurada para serviço adicional.
6. **Fato observado:** entra `fibo_logtool` e muda lógica de modem/IPv6; não há ganho comprovado para T7 sem modem correspondente.
7. **Fato observado:** APPSBL não traz mudança de instruções carregáveis identificada nem novo console de rede; TFTP automático segue não demonstrado.
8. **Inferência forte:** a rota de restauração CFG foi preservada, mas root por CFG no X7 e compatibilidade com OpenWrt 6.18 seguem sem teste.

**Próximos testes somente leitura quando houver acesso ao X7:** obter um backup CFG do próprio X7 e conferir apenas estrutura/metadados do tar; capturar `/proc/mtd`, `fw_printenv` (consulta), versão, regras de firewall, processos, `ss -lnt` e tráfego de boot passivo. No T7 já funcional, as capturas de `/proc/mtd` existentes podem ser complementadas com ambiente de boot e regras efetivas. Nenhum desses testes pode ser concluído usando somente a ROM baixada. Qualquer escrita em flash ou tentativa de recuperação requer plano e autorização específicos.

## 9. Aprofundamento estático das dúvidas (mesma data)

Este complemento usa apenas as extrações internas já validadas. O script reproduzível `deep_dive.py` e os resultados `logs/deep-dive-summary.txt`, `logs/kernel-config.diff` e `logs/umac-section-diff.txt` foram guardados em C:.

### U-Boot e recuperação

**Fato observado.** Os 77 bytes diferentes do APPSBL distribuem-se em 24 intervalos. Trinta e dois bytes ficam em `0x1070–0x108f`, fora do único segmento ELF `LOAD` (`0x12000–0x8a048`), aparentemente um campo de hash. Todos os demais intervalos estão em textos de identificação/build: quatro cópias de `version:25.03.11` → `version:26.08.04`, `qca_oem-2262` → `qca_oem-4352`, revisão GCC/OpenWrt e string `U-Boot 2016.01` com data de compilação. Os 4 bytes em `0x79e94–0x79e97` são o timestamp no cabeçalho gzip embutido. O gzip descomprime para **65.488 bytes idênticos**, SHA-256 `06b05fb2521b79b34fd0ea666c5819a8dc7047900768032527fb01f77d7ac3bb` nos dois. O ponto de entrada ELF é idêntico (`0x4a400000`).

**Inferência forte, limitada ao APPSBL empacotado:** não foi encontrada alteração de instrução de U-Boot, DTB embutido ou lógica TFTP/console de rede; as diferenças localizadas são identificadores, timestamp gzip e campo binário fora de `LOAD`. **Precisa confirmar:** o significado/autenticidade do campo de 32 bytes, o ambiente U-Boot realmente gravado e o comportamento de recuperação do aparelho. Esta análise reduz o motivo para atualizar U-Boot do T7 usando o X7; não demonstra que o flash cruzado seja seguro.

**Fato observado adicional.** `strings` do APPSBL contém comandos genéricos `tftpboot`, `tftpput` e `bootp` em ambos os pacotes; não foi localizado marcador textual de `netconsole`/`ncip`. Isso demonstra disponibilidade de rotinas TFTP no binário, mas não acionamento automático de recuperação, endereço, arquivo esperado, nem console de rede configurado. O comportamento deve ser observado passivamente no boot real antes de propor uso de TFTP.

### Kernel e driver Wi-Fi

**Fato observado.** O kernel descomprimido contém, em `0x7810c8`, um gzip com a configuração Linux de 5.607 linhas. A comparação linha a linha encontrou **somente a string de revisão do compilador** diferente; todos os `CONFIG_*` e demais linhas são iguais. Não apareceu opção nova de kernel, driver ou debug neste pacote. O kernel binário continua diferente; parte expressiva dos bytes alterados se concentra em `0x3e0000–0x78ffff`, o que por si só não identifica rotina ou recurso novo.

**Fato observado.** Em `umac.ko` (5.808.628 B em ambos), a seção `.text` de 2.891.896 B tem **apenas três bytes diferentes**, nos offsets relativos `0x474e4`, `0x474e8` e `0x47508`, dentro da função simbolizada `wlan_set_param`. Eles alteram constantes imediatas observáveis de 90→120, 60→90 e 89→119; a unidade e o parâmetro exato ainda não foram identificados. `.rodata`, `.data` e `.modinfo` são iguais; `.rodata.str` e `.rodata.str1.4` diferem em milhares de bytes, potencialmente por caminhos/identificadores de build, sem semântica atribuída. **Precisa confirmar:** desassemblar o ramo específico e cruzar o identificador do parâmetro antes de dizer que houve melhoria de Wi-Fi ou mudança de timeout.

### FOTA e método de root via backup CFG

**Fato observado.** A documentação local `06_DOCUMENTACAO/PROCEDIMENTOS/02_DESBLOQUEIO_SSH_E_ROOT.md` registra que, no **T7 024 e 027**, o método usa a restauração web do backup `config.cfg` (tar.gz de configurações), com alterações em `rc.local` e contas. Essa documentação descreve teste no T7; não é validação do X7. Os arquivos de fábrica `etc/rc.local`, `etc/passwd`, `etc/shadow`, `etc/config/dropbear` e `etc/trconf/tr.conf` são byte a byte iguais entre os dois rootfs. Um crontab personalizado usado no procedimento não aparece no SquashFS de fábrica de nenhum dos dois.

**Fato observado.** O executável de atendimento web `usr/bin/faiotfcgi` muda de 201.115 para 205.211 bytes; preserva as strings de caminho `config.cfg`, `fcgi_api_do_restore_cfg`, `fcgi_api_restore_cfg` e `/tmp/upload_data_token`. Adiciona strings de backup APN (`apnconfig.cfg`, `apnbackup`), operações de mensagens de modem e `fcgi_api_fileGet`; remove strings relacionadas a `webDisEncode`/`decodeUri`. `libsod-platform.so` e `libtr_sodlib.so`, que também referenciam backup de configuração, têm código/binário diferente e novas strings de backup do sistema/APN. **Precisa confirmar:** se o handler antigo de CFG teve validação, extração, filtragem de caminhos ou verificação de token alterada. Só a permanência das strings não prova que um CFG modificado ainda seja aceito, e a ausência de strings não prova remoção de validação.

**Fato observado.** `usr/bin/fota` conserva 70.287 bytes de tamanho total, mas o segmento executável cresce de `0x102c0` para `0x1032c`, o ponto de entrada muda de `0x3fec` para `0x4010` e uma nova string `/etc/init.d/ipqcm restart &` aparece; as demais strings ASCII de 8 ou mais caracteres comparadas permanecem iguais. **Inferência:** há uma alteração de código ligada possivelmente ao reinício assíncrono do serviço de modem; o ponto de chamada e as condições ainda precisam ser localizados. Não há evidência textual nova de política de assinatura, anti-rollback ou bloqueio de CFG.

### Riscos ainda abertos

| Pergunta | Evidência obtida | O que falta para responder |
|---|---|---|
| CFG de root do T7 funcionaria no X7? | Handler e bibliotecas mudaram; marcadores de restore permanecem. | Comparar o fluxo ARM do handler, seus argumentos, validação e extração; idealmente testar apenas num X7 de bancada, com backup próprio e plano de recuperação. |
| O X7 trouxe TFTP/netconsole novo ao T7? | APPSBL carregável só muda identificadores e tempo gzip; payload embutido igual. | Leitura de ambiente/console real e captura passiva de tráfego de boot. O pacote não demonstra novo recurso. |
| O que o reset X7 apagaria no T7? | Duas capturas de `/proc/mtd` de T7 identificam `mtd22=0:TRAFFIC` e `mtd24=0:TRAFFIC_DAY`; MIBIB e DTBs empacotados são idênticos. Bibliotecas de ambos os pacotes já mencionam apagamento dessas áreas no reset. | Confirmar versão/estado do T7 alvo e obter `/proc/mtd` de X7 real. Não extrapolar a numeração para qualquer outro hardware ou firmware. |
| Há avanço de driver/kernel útil para OpenWrt 6.18? | Config Linux idêntica, firmware Wi-Fi idêntico, somente 3 bytes de `.text` diferentes em `umac.ko`. | Identificar parâmetro alterado e ABI/fontes disponíveis; estes binários 5.4.213 não são prova de porte para 6.18. |

## 10. Correção baseada em `/proc/mtd` real do T7

**Fato observado.** Duas capturas arquivadas do terminal de um Predator Connect T7 em `07_ARTEFATOS_BUILD_WSL/evidencias/` (`inventario-slot-telnet-20261003T014259Z.txt`, linhas 42–46, e `conferencia-slots-20261003T025209Z.txt`, linhas 31–35) contêm estas entradas de `/proc/mtd`:

| Dispositivo Linux no T7 capturado | Nome | Tamanho | Interpretação baseada no nome/uso |
|---|---|---:|---|
| `mtd22` | `0:TRAFFIC` | `0x00600000` = 6 MiB | estatísticas de tráfego |
| `mtd23` | `0:SYSTRACE` | `0x00080000` = 512 KiB | rastreamento de sistema; **não** é apagado pelas novas linhas |
| `mtd24` | `0:TRAFFIC_DAY` | `0x00300000` = 3 MiB | histórico diário de tráfego |

**Fato observado.** Nessa captura, bootloaders são `mtd14/15`, ART é `mtd18` e as imagens de sistema são `mtd20/21`. Logo, a avaliação anterior de que o reset X7 poderia apagar bootloader ou calibração **por atingir `mtd22/24` no T7 capturado era excessiva e foi corrigida**. O kernel em execução da captura se identifica como build de janeiro de 2025; a captura não comprova diretamente a enumeração de um T7 já atualizado para 027, embora MIBIB e 14 DTBs dos dois pacotes comparados sejam idênticos.

**Fato observado.** Em `usr/lib/libsod-platform.so` e `usr/lib/libtr_sodlib.so` dos **dois** pacotes, `strings -t x` localiza, em sequência, `system_factoryReset...`, `factoryreset`, parada de `modem_datausage` e os comandos `flash_eraseall /dev/mtd22` e `/dev/mtd24`. O executável `modem_datausage` de ambos também contém apagamento de `mtd22`; o `newsod` X7 o contém adicionalmente. Isso apoia a interpretação de que são áreas de contadores/dados de uso, cuja limpeza no reset pela interface já era prevista. A nova diferença do X7 é incluir os comandos no script `etc/rc.button/reset`, potencialmente alinhando o botão físico ao caminho de reset da interface.

**Inferência.** Para o T7 com essa enumeração, o impacto direto esperado do novo trecho do botão é perder histórico/contadores de tráfego durante reset de fábrica; não há sinal de apagamento de bootloader, ART ou slots por essas duas linhas. **Precisa confirmar:** `/proc/mtd` de um X7 real, se o caminho de reset pela interface chega a executar as strings identificadas nas bibliotecas, e se há uso privado não documentado dentro dessas duas partições. O risco de flash cruzado X7→T7 continua por outras incompatibilidades; ele não deve ser atribuído principalmente a `mtd22/24`.

## 11. Nova análise dirigida: limite numérico no driver e evidência CFG

**Fato observado.** Com Capstone 5.0.9 e pyelftools 0.32, os três bytes de `.text` alterados em `umac.ko` foram desassemblados dentro de `wlan_set_param`:

| Offset `.text` | T7 | X7 |
|---|---|---|
| `0x474e4` | `add r3, r2, #0x5a` | `add r3, r2, #0x78` |
| `0x474e8` | `cmp r3, #0x3c` | `cmp r3, #0x5a` |
| `0x47508` | `mvn r3, #0x59` | `mvn r3, #0x77` |

O ramo seguinte mantém `bhi` para erro e `strb r2` quando aceita o valor. **Inferência técnica direta do código:** para esse parâmetro, a faixa de inteiro aceita passa de **−90 a −30** para **−120 a −30**; o limite inferior informado no erro também muda de −90 para −120. **Precisa confirmar:** o nome/unidade do parâmetro e se o equipamento realmente envia valores nessa faixa. Uma faixa negativa sugere limiar de sinal, mas isso não basta para afirmar RSSI, potência, ganho ou melhora de alcance.

**Fato observado.** Uma nota local `06_DOCUMENTACAO/NOTAS_HARDWARE/MODEM_5G_FIBOCOM_X7.md`, linhas 79–86, afirma que o X7 poderia usar o mesmo desbloqueio por `.cfg`; ela não apresenta captura de teste, resultado de restore ou versão X7 validada. A documentação do procedimento T7, em contraste, marca teste em bancada nas versões 024 e 027. **Conclusão:** a nota X7 é uma hipótese/afirmação documental, não comprovação de que o X7 050 aceita o CFG modificado. A mudança em `faiotfcgi` e bibliotecas mantém essa pergunta aberta.

## 12. Restauração CFG, utilitário de desbloqueio e FOTA: análise ARM dirigida

**Método.** Capstone 5.0.9 desassemblou somente as regiões de código já extraídas; não houve execução dos binários. Em `libsod-platform.so`, a tabela dinâmica ELF, recuperada a partir dos cabeçalhos de programa, identificou endereços e tamanhos das funções exportadas. O script `compare_restore_handlers.py` e `logs/restore-handler-comparison.txt` preservam a comparação do CGI.

### Receptor web do CFG

**Fato observado.** A rotina do CGI associada a `fcgi_api_do_restore_cfg` tem 1.784 bytes de instruções nos dois pacotes (`0x15b78` no T7; `0x16440` no X7). Entre 446 palavras ARM, 390 são byte a byte iguais, 54 são chamadas `bl` realocadas ao **mesmo destino** e duas mudam só números de linha de log em +49; nenhuma outra instrução difere. A rotina de chamada `fcgi_api_restore_cfg` preserva fluxo e instruções, com a mesma realocação/log; uma chamada interna passa ao endereço realocado de um auxiliar de resposta. Os marcadores de `config.cfg`, do caminho temporário e do token de upload continuam presentes. **Inferência forte:** não foi detectado endurecimento novo no receptor web específico do CFG. Isso não prova que toda autenticação anterior ao handler ou toda validação posterior seja idêntica.

**Fato observado.** `sbin/sysupgrade` é byte a byte igual (SHA-256 `57ec2413b68ba9547ff7630eba87a316edeed62e23a218232d9ccee589308154`). Na biblioteca `libsod-platform.so`, a função exportada `systemConfigRestore` cresce de **308 B** (T7, `0x6e990`) para **476 B** (X7, `0x6f094`). Ambas preservam a formatação da checagem `tar -tzvf %s | grep etc | wc -l` e o comando de restauração `sysupgrade -q -r %s`. Depois disso, a versão X7 acrescenta operações de perfis/APN: consulta de índice de perfil, exclusão/commit de `profiles`, ajuste de `apn.apnapply.apnid` e `sync`. **Inferência:** a mudança do backend visa sincronizar perfil de operadora após restore, não foi localizada nova rejeição de um CFG por assinatura/modelo nesse trecho. O efeito preciso dos comandos adicionais depende do backup e do estado persistente.

**Fato observado.** A função exportada `systemConfigBackup` cresce de **220 B** (T7) para **592 B** (X7). Ambas chamam `sysupgrade -q -b %s`; antes do backup o X7 acrescenta operações de `apn.apnapply.apnid` e `profiles`. **Inferência:** um CFG gerado no X7 pode conter contexto APN adicional. Para qualquer teste futuro de restauração, a origem apropriada é o **backup do próprio X7**, preservado antes da alteração, não um CFG do T7.

### Risco no script local de desbloqueio

**Fato observado.** O utilitário local `04_SCRIPTS_E_FERRAMENTAS/Automacao_e_Unlock/unlock_only_ssh.py`, linhas 26–31 e 121–145, reconstrói o tar.gz incluindo apenas membros que `tarfile` classifica como arquivos regulares. Ele preserva parte dos metadados (modo, nomes de usuário/grupo e `mtime`), mas não copia explicitamente tipo dos outros membros nem UID/GID numéricos. **Precisa confirmar:** quais tipos/owners existem no backup X7 real; não há um `config.cfg` do X7 neste conjunto.

**Fato observado.** O mesmo script injeta no `rc.local` a criação de `/usr/sbin/boot-acer` (linhas 59–77), auxiliar que, **se executado manualmente**, escreve no BOOTCONFIG (`/dev/mtd3` e `/dev/mtd4`) para voltar ao slot identificado no texto como OEM v24. O `rc.local` cria esse auxiliar; não o chama automaticamente. **Conclusão prática:** mesmo que o X7 aceite um CFG modificado, **não usar esse script T7 sem revisão específica do X7**. A recomendação aqui decorre do código do script, não de falha observada no X7. Esta auditoria não executou o utilitário nem alterou CFG algum.

### Mudança localizada em FOTA de modem

**Fato observado.** No executável `usr/bin/fota`, após o caminho que remove um pacote temporário de OTA do modem e reinicia `at_ril`, o X7 acrescenta uma chamada ao mesmo auxiliar de execução com a string `/etc/init.d/ipqcm restart &` (`0xa45c–0xa464`); no T7 a sequência prossegue diretamente para espera e reinício/controle subsequente. **Inferência:** atualização de modem no X7 também reinicia o serviço `ipqcm` de forma assíncrona. Esta mudança localizada não altera, por si, o fluxo de atualização do IPQ, a verificação de imagem ou o método de CFG.

**Limite remanescente.** A equivalência do receptor CFG e a preservação de `sysupgrade -r` dão evidência estática mais forte de continuidade do fluxo, mas não constituem teste de root no X7 050. Autenticação web completa, scripts acionados pelo `sysupgrade`, compatibilidade de um backup X7 modificado, e estado persistente do aparelho ainda não foram validados em execução.

## 13. Verificação dirigida de restauração e serviço HTTPS

**Fato observado.** O `sbin/sysupgrade` idêntico entra no ramo `CONF_RESTORE` nas linhas 284–292 e executa `tar -C / -xzf "$CONF_RESTORE"`, retornando o status da extração. Não há verificação de assinatura nesse ramo do script. Os trechos desassemblados de `systemConfigRestore` nos dois firmwares preparam a checagem `tar -tzvf ... | grep etc | wc -l` e chamam `sysupgrade -q -r`; não apareceu uma checagem criptográfica nova no caminho identificado. **Inferência forte:** um backup X7 próprio, modificado de forma compatível com o formato aceito, provavelmente passa pelo mesmo mecanismo de restauração do T7. **Precisa confirmar:** autenticação/token no fluxo HTTP completo, conteúdo do CFG real do X7 e resultado num aparelho. Esta conclusão não recomenda aplicar o utilitário T7 sem revisão.

**Fato observado.** `etc/rc.local:18`, idêntico nos dois rootfs, chama `/etc/init.d/lighttpd/lighttpd.init start`; esse script inicia `lighttpd` com `lighttpdmqtt.conf`. A configuração X7 declara TLS em IPv4/IPv6 `:8443`, além da porta 8181; a T7 mantém o bloco 8443 comentado. O próprio `start()` verifica ou gera `/etc/ipq.com.pem` antes de iniciar os dois processos, de modo que a ausência do PEM no SquashFS, isoladamente, não impede a porta. Os symlinks `etc/rc.d/S100lighttpd.init` de ambos apontam para um caminho ausente, mas a chamada direta em `rc.local` contorna isso. A zona WAN no firewall padrão X7 tem `input REJECT`, e não foi encontrada regra textual específica abrindo 8443. **Inferência:** se o comando OpenSSL e a inicialização tiverem sucesso, o X7 provavelmente expõe 8443 à LAN; exposição pela WAN não foi demonstrada. **Precisa confirmar:** `ss -lnt`, regras efetivas, endereços de bind e resultado de conexão em um X7 ligado.

## 14. Interação de controle parental e ordem das cadeias

**Fato observado.** Em `lib/filter/faiot_initial_firewall.sh:48–60`, o X7 insere primeiro `PARENTALCTL_FWD` e depois `PARENTCTRL_ACCESS_FWD`, ambos com `iptables -I FORWARD` (e equivalentes IPv6). Como `-I` sem posição insere no início, a segunda cadeia fica **antes** da primeira no `FORWARD` produzido por esse script. `faiot_parentalCtl.sh:32–33` remove a restrição horária de suas regras de bloqueio por URL/ipset. O script novo `faiot_parentalCtlAccessRestriction.sh:20–25`, quando `TrandMicroPC=1` e a entrada está habilitada, instala uma regra com horário e alvo `ACCEPT` para o MAC, seguida de `ACCEPT` para destino `br+` e `DROP` para esse MAC.

**Inferência técnica:** se a ordem dessas cadeias continuar a mesma em runtime, um pacote de MAC com horário permitido recebe `ACCEPT` na cadeia de acesso e não chega à cadeia posterior de bloqueio de URL. Fora do horário, a nova cadeia pode permitir destino `br+` ou negar o restante. Isso pode ser uma escolha de política, mas a interação precisa de teste de dois casos (URL bloqueada dentro/fora do horário) e de captura somente leitura de `iptables-save`/`ip6tables-save`. Não chamar isso de vulnerabilidade comprovada nem afirmar exposição à WAN sem regras efetivas do aparelho.

## 15. Origem de `lan1` e alcance da nova zona

**Fato observado.** A zona `lan1` acrescentada ao firewall X7 referencia uma interface de mesmo nome. O gerador `lib/wifi/qcawificfg80211.sh` dos **dois** pacotes já emite seis configurações de `wifi-iface` com `option network lan1`, inclusive VAPs de malha com VLAN 20; `lib/functions/repacd-map.sh` também contém o tratamento `eth1.20` para `lan1` nos dois. Portanto, `lan1` não é um hardware novo introduzido pelo pacote X7. A diferença observada é a política de firewall que passa a declarar zona `lan1`, encaminhamento para WAN e regras de comunicação `lan`↔`lan1`.

**Inferência:** o X7 pode estar corrigindo ou ampliando conectividade de uma rede de malha/bridge que o código T7 já sabia criar. **Precisa confirmar:** se `lan1` é instanciada em cada modo de operação, se pertence a backhaul, SSID adicional ou porta física no aparelho, e se as regras amplas `ACCEPT` afetam isolamento desejado. Configurações de rede geradas/persistidas não constam integralmente destes SquashFS.

## 16. Ferramenta nova de diagnóstico do modem

**Fato observado.** O X7 acrescenta `usr/bin/faiot_modemlog.sh`, `usr/bin/logtool`, `etc/config/qxdm_default.cfg` e o pacote `fibo_logtool`. O script, lido como texto sem execução, verifica se o modelo em `/tmp/ipq_model` é `cpe`; fora disso, sai. Ele procura um endereço associado a `lan1`/`lan2` em `/tmp/online_table` e então inicia `logtool` com `/dev/mhi_diag` e a configuração QXDM. O comando contém uma dupla de credenciais embutida; **os valores não são reproduzidos aqui**. Antes disso o script sincroniza a configuração QXDM de fábrica e encerra eventual instância anterior de `logtool`.

**Inferência:** trata-se de coleta/transporte de diagnóstico do modem Fibocom para um cliente de rede selecionado, possivelmente para suporte. **Precisa confirmar:** quem invoca o script, protocolo/porta/controle de acesso do `logtool`, e se há transmissão efetiva num X7 em funcionamento. Não foi encontrada chamada automática a `faiot_modemlog.sh` nos scripts de inicialização e nos binários principais examinados por strings; portanto não há evidência de serviço de diagnóstico ativo por padrão. O teste seguro é inspecionar processos e conexões num X7 próprio, sem habilitar a ferramenta nem divulgar logs privados.

## 17. Modo de rede celular padrão

**Fato observado.** Em `etc/config/apn`, o campo `networkmode.mode` muda de `5` (T7 027) para `1` (X7 050), e entra `networkmode.version=1`; `connectmode.mode` continua `0`. O binário `at_rild` X7 lê explicitamente `apn.networkmode.mode` e contém uma mensagem de falha ao configurar o modo de rede; portanto o campo é consumido pelo caminho de modem. **Precisa confirmar:** o mapeamento exato dos valores `1` e `5` no firmware FM160/na camada da Acer. A busca por manual público específico da combinação FM160 + versão de comando não forneceu uma tabela primária verificável para esses dois valores; não atribuir “5G automático”, “LTE somente” ou qualquer outro significado por analogia com outro modem. No T7 sem modem instalado, o impacto real desse padrão provavelmente é nulo; isso é inferência de hardware, não teste de boot.

## 18. Metadados de um CFG original do T7

**Fato observado.** A leitura **somente de metadados tar**, sem extração de conteúdo, do arquivo T7 `config_v27_stock_original.cfg` encontrou 137 entradas: 135 arquivos regulares e 2 symlinks; todos os UID/GID numéricos de entrada são 0. Os symlinks são caminhos de configuração de Easy RSA e ksmbd, sem conteúdo privado reproduzido aqui. Como `unlock_only_ssh.py` aceita apenas `m.isfile()` ao reconstruir o tar, esse utilitário remove essas duas entradas do CFG gerado. O método foi registrado como funcional em bancada para T7, então a ausência delas não impediu aquele cenário específico; ela ainda é uma alteração silenciosa da cópia de segurança. **Precisa confirmar:** estrutura do backup X7 real e impacto de membros não regulares ou metadados diferentes nele. Um teste X7 deve começar com backup próprio preservado e comparação estrutural antes de qualquer restauração.

## 19. Ciclo de vida do listener TLS adicional

**Fato observado.** `etc/init.d/lighttpd/lighttpd.init` gera ou valida `/etc/ipq.com.pem` durante `start()` e, depois de iniciar o lighttpd principal, executa explicitamente um segundo `lighttpd -f /etc/lighttpd/lighttpdmqtt.conf` (linhas 29–56). Portanto, o certificado é previsto para ser criado em runtime. Em `restart()` (linhas 67–110), o script encerra processos `lighttpd` e inicia apenas a configuração principal `lighttpd.conf`; não repete a chamada de `lighttpdmqtt.conf`. O script é idêntico nos pacotes, mas só o X7 ativa TLS 8443 nessa configuração adicional.

**Inferência:** após um `restart` desse serviço, os listeners adicionais 8181/8443 podem deixar de existir até o próximo `start`/boot, salvo se outra rotina os reabrir. **Precisa confirmar:** comportamento real do `start-stop-daemon -K -x`, processos sobreviventes e listeners antes/depois do restart em X7 ligado. Esta é uma diferença operacional relevante para avaliar a porta 8443, não prova de indisponibilidade observada.

**Limite de material disponível.** O usuário confirmou possuir apenas a ROM baixada do X7, sem backup CFG gerado pelo aparelho e sem X7 ligado. Por isso não é possível comparar a estrutura do CFG X7, testar importação/root, consultar seu `/proc/mtd` ou observar serviços e firewall efetivos. Esses itens permanecem explicitamente como **Precisa confirmar**; não houve falha de leitura/extração dos pacotes analisados.
