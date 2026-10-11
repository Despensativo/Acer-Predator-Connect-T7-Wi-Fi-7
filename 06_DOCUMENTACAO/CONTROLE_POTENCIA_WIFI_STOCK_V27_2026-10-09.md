# Onde a v27 controla a potência Wi-Fi do T7

Investigação em 09/10/2026. Leitura do pacote stock e do T7 em `192.168.76.1`; nenhum arquivo do roteador foi alterado. A potência em dBm indicada pelo software não substitui ensaio conduzido ou irradiado.

## Estado observado no aparelho

O sistema respondeu `T7_BR_1.01.000027`; o Device Tree em execução identifica `IPQ5332/AP-MI01.6`. Os três `wifi-device` UCI têm `country=BR`, `txpower=22`, canal automático e larguras `HT40`, `HT80`, `HT320`. No momento da leitura, `iw dev ath0/ath1/ath2 info` informou, respectivamente, **15/23/15 dBm** nos canais 1/44/33. Esses valores são leitura do driver da interface, não potência RF medida no conector nem EIRP. O descompasso com o UCI impede tratar `option txpower '22'` como uma potência física exata.

O Device Tree ativo tem `wifi@c0000000` (`qcom,cnss-qca5332`) e `wifi2@f00000` (`qcom,cnss-qcn9224`) ativos, e `wifi1@f00000` QCN9224 desabilitado. O pacote e o DT ativo **não sustentam** chamar o rádio de 6 GHz de QCN6432; o nome no arquivo do firmware também é `qcn9224`. O nó `wifi1` do DT não deve ser confundido automaticamente com o nome lógico UCI `wifi1`.

### Leitura posterior após configuração US feita pelo usuário

O T7 já estava com `country=US` e `txpower=24/26/22` em `wifi0/1/2` quando foi relido. O driver continuou informando **22/23/15 dBm**, respectivamente. Os canais/larguras ativos eram 6/HT20, 36/HT160 e 37/HT320 (centro de 6 GHz em 6105 MHz). O domínio de cada `phy` era `US`, e os links ativos de dados de placa `bdwlan.b16` (IPQ5332) e `bdwlan.b1015` (QCN9224) apontavam para as variantes **FCC**; `/lib/wifi_cert_2` e `/lib/wifi_cert_5` eram `2`, igual ao mapeamento US em `/etc/config/wifi_cert`. Portanto, o descompasso não é explicado por falta de gravação UCI, país ainda BR, tabela `wifiPowerTable` ou seleção da variante CE.

O `iw phy` anunciou teto de canal de **30 dBm** em 2437 MHz, **24 dBm** em 5180 MHz e **30 dBm** em 6135 MHz. O canal 36 com HT160 ocupa também U-NII-2A, onde 26 dBm conduzidos não cabem na regra FCC; o rádio informar 23 dBm é coerente com um limite abaixo do pedido, embora o valor exato dependa de outras reduções do driver. Em 2,4 e 6 GHz, os tetos regulatórios anunciados não explicam sozinhos 22 e 15 dBm. Não está provado se esses números de `iw` representam a potência total conduzida das duas cadeias; medição RF é necessária.

### Mapa de potência anunciado pelos canais no perfil US atual

| Banda e canais disponíveis no T7 | Teto anunciado por `iw phy` | Interpretação |
| --- | ---: | --- |
| 2,4 GHz, canais 1–11 | 30 dBm | Teto regulatório/driver por canal. O pedido UCI de 24 dBm e a leitura da interface de 22 dBm são inferiores. |
| 5 GHz, canais 36–64 | 24 dBm | Limite anunciado pelo firmware US inclusive em 36–48. Canais 52–64 requerem DFS. |
| 5 GHz, canais 100–144 | 24 dBm | Limite anunciado pelo firmware US; estes canais requerem DFS. |
| 5 GHz, canais 149–165 | 30 dBm | Teto anunciado; com ganho direcional de 8,38 dBi em beamforming, o cálculo FCC do próprio laudo reduz o máximo conduzido de 30 para 27,62 dBm. A saída real ainda depende da calibração. |
| 6 GHz, canais de 20 MHz listados pelo rádio | 30 dBm | Este número acompanha o limite LPI de EIRP e não autoriza 30 dBm conduzidos. Aplicam-se 30 dBm EIRP **e** 5 dBm/MHz, conforme largura, ganho e PSD real. |

Para referência matemática, supondo emissões uniformemente distribuídas e ganho direcional beamforming de **6,61 dBi**, a restrição de 5 dBm/MHz daria tetos **aproximados de potência total conduzida** de 11,4/14,4/17,4/20,4/23,4 dBm em 20/40/80/160/320 MHz, respectivamente, com o teto EIRP total de 30 dBm aplicado em 320 MHz. Esses números são apenas um cálculo de planejamento: a PSD de pico por 1 MHz, distribuição OFDM, taxa e calibração podem exigir valores menores; os laudos medem condições específicas. [47 CFR §15.407(a)(5)](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-E/section-15.407)

Em leitura posterior voltada a desempenho, `iw dev athX survey dump` não retornou dados de ocupação dos canais. O log registrou uma sequência de **SSR do firmware Wi-Fi**, seguida de `Target failed service 0x108`; o `ath1` voltou ao ar no canal 36/HT160. Durante a recuperação, `iw dev ath1 info` informou temporariamente 0 dBm e depois 23 dBm. Portanto, comparar velocidade apenas por potências solicitadas ou pela leitura transitória de `iw` seria inconclusivo. Não houve alteração de configuração nessa leitura.

### Por que 15 dBm reaparece no 6 GHz

Em nova leitura, o valor **configurado** em `wireless.wifi2.txpower` já era `15`, igual aos 15 dBm informados por `iw dev ath2 info` e `iwconfig ath2`. O arquivo `/etc/config/wireless` no overlay tinha sido regravado; a leitura anterior havia encontrado `22` no UCI e `15` no driver. Não foi possível atribuir essa gravação a um ator específico apenas pelo horário do arquivo.

Há um mecanismo concreto de regravação na interface personalizada `predator_wifi.js`: `/usr/libexec/rpcd/predator` constrói o campo `txpower` do rádio usando a leitura de `iw dev ath2 info`, que atualmente é `15`. A página seleciona esse valor no menu e o botão Salvar envia `txSelect.value` ao RPC `set_radio`; o RPC faz `uci set wireless.wifi2.txpower="$TX"`, `uci commit wireless` e aciona `/sbin/wifi up` em segundo plano. Em seguida, executa `iw phy phy7 set txpower fixed "$((TX * 100))"`, ocultando eventuais erros. Portanto, salvar a página enquanto ela exibe `15` pode persistir `15` no UCI, mesmo que antes o usuário tenha definido `22` por outro caminho. A própria página rotula `15 dBm` como “Máximo LPI Wi-Fi 7 @ 320 MHz”, afirmação que o laudo FCC de EHT320 a 6105 MHz **não sustenta**: ele mediu 22,06 dBm conduzidos/28,67 dBm EIRP na amostra de ensaio. O script local `aplicar_potencia_maxima_us.py` também passou a conter comandos `uci set` com 22/23/15, apesar de seu texto inicial ainda anunciar 24/26/22; executá-lo igualmente regravaria 15.

Esse mecanismo explica a **persistência do 15 configurado**, mas ainda não demonstra por que o driver reportava 15 quando o UCI estava em 22. O `iw phy phy7` anuncia 30 dBm para o canal 37, o domínio do `phy` é US, a variante FCC de `bdwlan.b1015` está ativa e a tabela `wifiPowerTable` não traz teto US. O valor de `iw` não comprova a potência total conduzida de um sinal EHT320; a causa remanescente pode estar em política de potência do firmware/calibração e precisa de teste controlado ou medição RF.

Uma inspeção posterior do kernel e dos módulos trouxe evidência adicional em `TRILHA_KERNEL_DRIVER_POTENCIA_6GHZ_V27_2026-10-09.md`: `cfg80211tool wifi2 g_reg_txpower` retornou 30, enquanto o `iw` oscilou após SSR e chegou a informar 50/63/30 dBm nos APs, valores incompatíveis com os tetos anunciados. Portanto, a leitura de `iw` desta instalação não pode ser usada isoladamente nem para diagnosticar um limite fixo de 15 dBm nem para validar aumento de potência.

## Locais de configuração, em ordem de utilidade

| Camada | Caminho / mecanismo | Uso real |
| --- | --- | --- |
| Configuração persistente da instalação atual | `/etc/config/wireless`, seções `wifi0`, `wifi1`, `wifi2`: `country` e `txpower` | Valor desejado para cada rádio; `uci commit wireless` persiste no overlay do slot atual. O país deve corresponder ao local de operação. |
| Teto adicional da rotina QSDK | `/lib/wifiPowerTable`, campos `max_txpower_2g/5g/6g` da linha do país | `qcawificfg80211.sh` lê este arquivo e reduz o valor solicitado se ultrapassar o teto. É um teto simples por banda, não por canal/largura/taxa. |
| Cópia de gestão | `/etc/config/wifiPowerTable` e rotina `/lib/wifiPowerTableCheck.sh` | A rotina pode copiar uma tabela recebida em `/tmp/wifiPowerTable` para os dois caminhos e recarregar o Wi-Fi. Editar só uma cópia não garante persistência funcional. |
| Padrões de uma nova imagem | `/lib/wifi/qcawificfg80211.sh` dentro do `rootfs.squashfs` | Gera `wireless` quando ainda não existe, com `txpower 22` em ramificações examinadas. Uma imagem nova não substitui automaticamente o arquivo já persistido no overlay. |
| Driver e microcódigo | `qca_ol`/`wifi_3_0`, `wifi_fw.bin`, `bdwlan*`, banco regulatório, ART | Calibração e limites internos variam por canal, largura, taxa, cadeia e placa. Não há um único campo seguro que represente 24/26/22 dBm exatos em todas as condições. |

O **RootFS stock** não contém `/etc/config/wireless` pronto; ele é gerado. A pasta local `rootfs_extracted` contém uma cópia **modificada**, com `US` e 24/26/22; não usá-la como prova do conteúdo de fábrica. No T7 atual, ambas as tabelas `wifiPowerTable` têm apenas uma entrada `CN` sem valores máximos, portanto não fornecem teto `BR`. Seus hashes e versões diferem, embora ambas tenham os mesmos campos vazios.

## Interpretação dos números FCC

O laudo [BTL-FCCP-4-2311H013 R02 para HLZT7, 6 GHz](https://fccid.io/HLZT7/Test-Report/BTL-FCCP-4-2311H013-R02-UNLL5-8-1-7449468.pdf) registra **22,06 dBm conduzidos e 28,67 dBm EIRP no ensaio EHT320 a 6105 MHz**. O mesmo quadro dá **30 dBm EIRP como limite**, portanto o resultado medido está **1,33 dB abaixo** do limite, não exatamente no teto. O ganho direcional de **6,61 dBi** é uma conta de **3,61 dBi de antena + 3 dB de beamforming**, e não o ganho físico de uma única antena. Em outras larguras e canais, o laudo apresenta resultados diferentes. A amostra foi identificada como *engineering sample* com software `QSPR v5.14.00227.1`, não como firmware Acer v27.

Além do EIRP total, a regra LPI exige limite de **densidade espectral**: [47 CFR §15.407(a)(5)](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-E/section-15.407) e [Anatel, item 11.7.1](https://informacoes.anatel.gov.br/legislacao/component/content/article/96-atos-de-certificacao-de-produtos/2017/1139-ato-14448) indicam 30 dBm EIRP e 5 dBm/MHz para ponto de acesso indoor. Por isso um valor conduzido medido em EHT320 não deve ser travado como valor universal em EHT20/40/80/160.

Os laudos originais mostram que **25,55 dBm** é o máximo conduzido não beamforming em **802.11n HT40, 2,4 GHz** ([BTL-FCCP-1-2311H013 R01](https://fccid.io/HLZT7/Test-Report/BTL-FCCP-1-2311H013-R01-WLAN2-4G-1-7449471.pdf)). **27,32 dBm** é o máximo não beamforming em **802.11be EHT40, banda U-NII-3 de 5 GHz** ([BTL-FCCP-2-2311H013 R02](https://fccid.io/HLZT7/Test-Report/BTL-FCCP-2-2311H013-R02-RLAN1-4-1-7449507.pdf)). Nesse segundo laudo, os máximos das bandas U-NII-2A e U-NII-2C foram cerca de **22 dBm**, e o limite FCC nessas bandas é 250 mW ou menos conforme a largura. Assim, `26 dBm` não é alvo válido para qualquer canal de 5 GHz. Os dois laudos também usaram *engineering sample* e `QSPR v5.14.00227.1`. Os números medidos não definem limite térmico do FEM nem garantem estabilidade na v27.

## Perfil candidato para ensaio US em bancada de RF isolada

| Rádio | Canal/largura de ensaio | Alvo UCI | Condição a verificar |
| --- | --- | ---: | --- |
| `wifi0`, 2,4 GHz | Canal 6, HT40 | 24 dBm | Confirmar canal secundário, PSD e potência conduzida nas duas cadeias. |
| `wifi1`, 5 GHz | Canal 149, HT40 | 26 dBm | Canal U-NII-3 sem DFS; o máximo de 27,32 dBm do laudo é EHT40 nessa banda. Validar modulação, EIRP/PSD e leitura RF. |
| `wifi2`, 6 GHz | Canal primário 37, HT320 | 22 dBm | Comparar com o ensaio EHT320 de 6105 MHz; medir EIRP e PSD. Manter operação LPI indoor e conferir posição do canal primário/centro após iniciar o rádio. |

Esse perfil fixa apenas os **pedidos ao driver** para condições de ensaio repetíveis. O `country=US` deve ser usado somente em bancada RF contida/realizada nos EUA, conforme a situação de operação; no Brasil, a radiação normal deve obedecer à homologação e às regras locais. Para comprovar enquadramento FCC, medir potência conduzida por cadeia, EIRP, PSD, emissões fora da faixa e variações de taxa/modo com instrumentos calibrados. Um valor `txpower` em UCI ou `iw` não é essa comprovação. O limite de 6 GHz depende especialmente de largura: 22 dBm conduzidos mais 6,61 dBi representam aproximadamente 28,61 dBm EIRP no cenário beamforming citado, mas a PSD pode impedir o mesmo valor em canais mais estreitos.

## Consequência para uma gravação precisa

Para um **limite desejado persistente**, a primeira camada é `country=BR` e `txpower` nas três seções UCI do aparelho/overlay. Se a política for impor teto adicional, a tabela efetivamente lida em `/lib/wifiPowerTable` precisaria de uma entrada `BR` coerente e de controle sobre a rotina que a atualiza. Isso ainda é um **pedido ao driver**; a potência real, EIRP e PSD exigem medição RF por combinação de banda, canal, largura, modo e cadeias.

O script local `04_SCRIPTS_E_FERRAMENTAS/aplicar_potencia_maxima_us.py` **não é uma implementação precisa desses limites**: força país `US`, escreve tetos de `30` dBm (acima dos três valores desejados), agora grava UCI 22/23/15 e chama `iw ... fixed 22/23/15`. O `iw help` declara que esse comando recebe **mBm** (centésimos de dBm), enquanto os valores UCI são dados em dBm. Uma inspeção posterior do módulo stock `umac.ko` encontrou uma inconsistência: o callback Qualcomm repassa esse inteiro sem divisão por 100 e o multiplica por dois para uma representação interna de meio dBm. Assim, **nem `iw fixed 22`, nem `iw fixed 2200` devem ser usados como receita comprovada nesta build**; veja `TRILHA_KERNEL_DRIVER_POTENCIA_6GHZ_V27_2026-10-09.md`. O script não registra retorno/erro dessa chamada nem mede RF; não executá-lo novamente como forma de impor potência física exata.

Não modificar ART, arquivos `bdwlan*`, `regdb.bin`, `wifi_fw.bin` ou kernel apenas para obter aqueles três números: essas camadas contêm calibração e política por modo/canal, e mexer nelas requer identificação física e validação em bancada.
