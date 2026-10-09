# Trilha de potência 6 GHz no kernel e nos drivers do T7

Data: 2026-10-09. Inspeção somente de leitura do T7 e dos binários da imagem Acer `1.01.000027`. O objetivo é identificar **o que significa o 15 dBm de `iw dev ath2 info`**; não houve escrita, reinício nem alteração de canal/potência no equipamento nesta análise.

## 1. O kernel em execução não é o `kernel.bin` local da v27

| Origem | Versão compilada | Tamanho da imagem FIT/volume | SHA-256 |
| --- | --- | ---: | --- |
| `Official_v27_Componentes/kernel.bin` | `5.4.213`, GCC OpenWrt `r0+14315-60fc7c16ce`, **11/03/2025** | 4.237.480 B | `818c3a986277e56bc224470342d20f010696c7f28a457145301c6afd864736ab` |
| `/dev/ubi0_1`, volume ativo `kernel` | `5.4.213`, GCC OpenWrt `r0+14311-9a354fd0ab`, **17/01/2025**, segundo `/proc/version` | 4.238.664 B (`Data bytes` em `ubinfo`) | `ff131c1aeb280dfc9022a4474330e55e19b82f504723021546c46ea4fb4963fb` |

O volume UBI ativo tem outro tamanho e hash. `uname -a` e `/proc/version` também identificam a compilação de janeiro. Portanto, **não é correto atribuir um comportamento observado do kernel ativo ao `kernel.bin` oficial de março sem esta ressalva**. A leitura não determina por que o volume ativo é diferente, nem qual processo o gravou. O Device Tree ativo informa `IPQ5332/AP-MI01.6`.

## 2. Módulos Wi-Fi efetivamente carregados

`/proc/modules` registra `cfg80211`, `ipq_cnss2`, `qdf`, `umac`, `qca_ol` e `wifi_3_0`. Os seis arquivos em `/lib/modules/5.4.213/` têm o **mesmo SHA-256** que os extraídos do `rootfs.squashfs` oficial. Assim, a análise estática abaixo é dos módulos que estão carregados, apesar da diferença do kernel base. São módulos ARMv7 para 5.4.213; este stack proprietário Qualcomm não é `ath12k`/`mac80211`.

## 3. De onde sai o número mostrado pelo `iw`

No `umac.ko`, `wlan_cfg80211_get_txpower` chama `ieee80211_ucfg_get_txpow`. Esta última lê um campo **com sinal, de 16 bits**, no nó da interface (`+564`) e divide o valor por dois antes de preencher a resposta em dBm. O `qca_ol.ko`, em `ol_ath_vap_iter_update_txpow`, escreve no **mesmo campo** e, quando ele muda, atualiza o beacon. Isto mostra que os 15 dBm informados por `iw dev ath2 info` são uma **leitura de estado mantido pelo driver host**, em unidades internas de meio dBm. Não é leitura direta do acoplador RF, nem demonstra sozinha potência total conduzida de um sinal EHT320 com várias cadeias.

Essa trilha também explica por que o `iw` pode oscilar durante uma reinicialização do firmware: anteriormente o `ath1` apareceu brevemente com 0 dBm e depois 23 dBm enquanto recuperava o serviço. O valor de `iw` precisa ser coletado depois de a interface e o firmware estabilizarem.

## 4. Caminhos de redução de potência que existem nos módulos

No `umac.ko` há `reg_get_6g_chan_ap_power`, `reg_get_6g_chan_psd_eirp_power`, `reg_get_max_txpower_for_6g_tpe`, `wlan_reg_psd_2_eirp` e `wlan_reg_eirp_2_psd`. A desmontagem de `reg_get_6g_chan_ap_power` confirma uma bifurcação: consulta `reg_is_6g_psd_power` e, quando aplicável, busca a potência PSD/EIRP por canal. Isso significa que a política de 6 GHz considera classe de AP e PSD; o simples máximo `30 dBm` mostrado por `iw phy` não é necessariamente a potência aceita para cada combinação de largura, modo e taxa.

No `qca_ol.ko`, `ol_ath_setTxPowerLimit` compara o pedido com um máximo interno e o limita antes de enviar um parâmetro ao pdev/firmware. O log ativo contém duas ocorrências de `Tx power value is greater than supported` e `max tx power 69, Limiting to default Max`. Este `69` é uma unidade interna do caminho de limite, **não 69 dBm**. O log não identifica qual comando anterior gerou os pedidos excessivos. Há ainda handlers e comandos `TPC` e tabela de potência (`ol_ath_pdev_tpc_config_event_handler`, `wmi_unified_send_set_tpc_power_cmd`, `wmi_unified_set_power_table_cmd_send`, `tgt_if_regulatory_set_tpc_power`). A potência efetiva por cadeia/taxa passa, portanto, por firmware e dados de placa além do valor UCI.

O `dmesg` confirma que, após reinicializações SSR, o CNSS carrega no QCN9224 `amss_dualmac.bin`, `regdb.bin`, `bdwlan.b1015` e `caldata_2.bin`. A variante ativa de `bdwlan.b1015` aponta para FCC, mas o conteúdo dessas tabelas e as decisões TPC em tempo de transmissão não foram decodificados nesta inspeção. Os SSRs observados interrompem ensaios de desempenho; o trecho analisado não separa reload solicitado de falha espontânea nem prova relação causal com os 15 dBm.

## 5. Atenção à unidade de `iw ... set txpower`

A [documentação do Linux Wireless](https://wireless.docs.kernel.org/en/latest/en/users/documentation/iw.html) diz que o argumento de `iw ... set txpower` é **mBm**: 22 dBm seriam 2200 mBm. A [API cfg80211 do kernel](https://www.kernel.org/doc/html/next/driver-api/80211/cfg80211.html) também especifica que o callback `set_tx_power` recebe mBm. Porém, no `umac.ko` desta build, `wlan_cfg80211_set_txpower` repassa o inteiro recebido diretamente a `ieee80211_ucfg_set_txpow`, que o multiplica por dois para a representação interna de meio dBm, **sem conversão visível por 100 nesse trecho**. O `cfg80211.ko` stock, no caminho legado WEXT, faz explicitamente `valor × 100` antes de chamar o callback. Isso é evidência de possível incompatibilidade de unidade no caminho nl80211 do driver Qualcomm; não é confirmação experimental do efeito de `iw fixed 22` ou `iw fixed 2200` no T7.

Por essa inconsistência e pelos logs de pedido acima do máximo, **não usar `iw fixed 2200` como receita para obter 22 dBm** nem interpretar a mensagem de sucesso do comando como potência RF aplicada. Um teste deste ponto exigiria instrumentação de entrada/saída do callback e medição de RF, em bancada contida, com registro de retorno, logs e recuperação do rádio. Nenhum teste mutável foi feito aqui.

### Diferença concreta entre o script Wi-Fi stock e o painel personalizado

Leitura posterior dos arquivos ativos mostrou que `/lib/wifi/qcawificfg80211.sh` aplica a opção UCI com `iw "$ifname" set txpower fixed "${txpower%%.*}"` (valor inteiro em dBm no caminho Qualcomm desta build). Já `/usr/libexec/rpcd/predator`, ao salvar um rádio no painel personalizado, grava o mesmo UCI mas, depois de `/sbin/wifi up`, executa `iw phy phy7 set txpower fixed "$((TX * 100))"` para `wifi2`, descartando o erro com `2>/dev/null || true`. O painel também obtém o valor inicial do menu da leitura de `iw`, e o botão Salvar envia o valor do menu. Portanto, os dois caminhos realmente fazem pedidos numéricos diferentes ao driver. Isso dá um motivo adicional para testar o pedido de 22 **somente pelo caminho UCI/stock**, sem apertar Salvar no painel e sem executar `iw` manualmente durante o ensaio.

## Conclusão sobre os 15 dBm

Ficou demonstrado **onde o 15 é lido no driver host**, que o stack tem seleção regulatória por PSD e TPC no firmware, e que o kernel base ativo difere do FIT oficial. **Ainda não foi demonstrado qual limite específico produz 15**: pode envolver o valor pedido, classe LPI/PSD, canal/largura, tabela de potência por taxa/cadeia, calibração ou estado após SSR. A distinção só pode ser fechada com os valores TPC/PSD efetivos do QCN9224 e medição RF por cadeia/modo. O laudo FCC de outra amostra não identifica automaticamente o valor do campo interno desta unidade.

### Leitura adicional do driver no T7

Numa consulta posterior, `cfg80211tool wifi2 g_reg_txpower` respondeu **30**, e `g_oper_reg_info` respondeu `chan=37`, `6135 MHz`, `320 MHz`, `country=US`, `opclass=137`; `g_ap_power_mode` respondeu **0**. Sem a enumeração exata desta build, o número 0 não é rotulado aqui como uma classe específica. `cfg80211tool wifi2 disp_tpc` retornou `-22` (`EINVAL`), sem tabela TPC. Assim, a ferramenta confirmou que o valor regulatório anunciado no rádio é 30, mas não revelou a redução efetiva por taxa/cadeia.

No mesmo período houve novos SSRs e `Target failed service 0x108`. O trecho examinado do log começa com desativação coordenada de `ath0/ath1/ath2`, seguida de desligamento dos processadores Wi-Fi; ele é compatível com uma rotina de reload/recovery e **não prova crash espontâneo do firmware**. Depois de uma recuperação, `iw dev` chegou a informar **50/63/30 dBm** nos três APs enquanto o UCI estava em **22/23/15**; em outra leitura, `iw dev ath0/ath1/ath2 info` informou **22/63/15**. Os 50 e 63 excedem os tetos anunciados e não representam potência RF plausível. Isto demonstra que a resposta `get_txpower` desta build pode refletir estado transitório/inconsistente do driver após SSR. O reaparecimento de 15 no `ath2` confirma apenas o valor reportado após essa recuperação; não valida que a potência conduzida seja 15 dBm.

### Fontes e reprodução

- Binários locais `Official_v27_Componentes/{kernel.bin,rootfs.squashfs}`; extração somente de leitura com `unsquashfs -cat`; inspeção ARM com `nm` e `llvm-objdump` dos seis `.ko`.
- T7: `/proc/version`, `uname -a`, `sha256sum /dev/ubi0_1`, `ubinfo -a`, `/proc/modules`, hashes de `/lib/modules/5.4.213/*.ko` e `dmesg` por Telnet somente de leitura.
- Sem alteração no roteador nesta análise. Os hashes e datas acima são um retrato da leitura de 2026-10-09.
