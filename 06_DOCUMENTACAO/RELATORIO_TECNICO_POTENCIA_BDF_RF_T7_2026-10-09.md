# Relatório Técnico Completo: Análise de Potência Wi-Fi, BDF FCC, Drivers e Física de RF do Acer Predator Connect T7

**Data:** 09/10/2026  
**Dispositivo:** Acer Predator Connect T7 (`T7_BR_1.01.000027`)  
**Plataforma de Hardware:** Qualcomm IPQ5332 (AP-MI01.6) + QCN9224 (Waikiki / Wi-Fi 7)  
**Kernel:** Linux 5.4.213 (OpenWrt QSDK / ARMv7 32-bit)  
**Escopo:** Diagnóstico forense completo, engenharia reversa de binários e scripts de boot, decodificação Tri-Band de BDFs e Caldata, física de RF, sensores térmicos e guia de telemetria.

---

## 1. Sumário Executivo

Durante os testes de rádio no canal 37 com largura de 320 MHz em 6 GHz (`ath2`), observou-se que o comando `iw dev ath2 info` reportava invariavelmente **15 dBm**, mesmo quando o UCI estava configurado para 22 dBm. Além disso, a execução de `cfg80211tool wifi2 disp_tpc 1` retornava erro `-22` (`EINVAL`), sem exibir tabelas.

Esta investigação realizou a engenharia reversa estática dos módulos de kernel stock (`qca_ol.ko`, `umac.ko`, `wifi_3_0.ko`), dos scripts de inicialização do sistema (`wifi_fw_mount`, `qcawificfg80211.sh`), dissecou os binários de dados de calibração de placa (`bdwlan_fcc.b1015`, `bdwlan_ce.b1015`, `bdwlan_default.b1015`, `bdwlan_fcc.b16`, `caldata_2.bin` e `caldata.bin`) e levantou a física de RF do arranjo MIMO do equipamento.

### Conclusões Principais:
1. **O rádio NÃO está defeituoso nem "capado" por bug de configuração:** O valor de 15 dBm está **gravado de forma estática (hardcoded)** na BDF FCC (`bdwlan_fcc.b1015`) para modulações ultra-densas (1024-QAM / 4096-QAM nos MCS 10 a 13) em 320 MHz e na tabela de conformidade regulatória CTL da FCC.
2. **O comando `iw` reporta potência escalar por cadeia individual:** Ele não reflete a potência irradiada total. Com o arranjo **MIMO 2x2 (+3,0 dB)** e o ganho direcional com **Beamforming (+6,61 dBi)**, a potência conduzida combinada é de **18 dBm (63 mW)** e a potência efetiva irradiada no ar é de **24,61 dBm EIRP (~290 mW)**.
3. **O erro `-22` de `disp_tpc` é um bug de retorno no driver stock:** O comando WMI é enviado ao firmware Q6, mas a função do driver não zera a variável de retorno (`r9`), e o evento assíncrono de resposta é descartado silenciosamente porque o callback de debug não é registrado em compilações comerciais de produção da Acer.
4. **Calibração Única de Silício e Cristal Oscilador (XO Trim):** A partição ART armazena ajustes de bancada de fábrica cruciais, como a compensação do cristal oscilador (`0x61` vs `0x21` padrão) para eliminar drift de partes por milhão (ppm) no canal de 320 MHz, garantindo a sustentação de 4096-QAM.
5. **Mapeamento Regulatório Automático por País:** O sistema operacional possui o banco de dados `/etc/config/wifi_cert` que comuta automaticamente entre três BDFs de 6 GHz (`FCC`, `CE` e `DEFAULT`), impondo perfis drásticos de potência de acordo com o país configurado.

---

## 2. Engenharia Reversa dos Módulos de Kernel Stock

### 2.1. Por que `cfg80211tool wifi2 disp_tpc 1` retornou `-22`?
A desmontagem ARMv7 de `qca_ol.ko` revelou o fluxo exato:
* `cfg80211tool` envia subcomando vendor com parâmetro `0x200a` (`disp_tpc`).
* `ol_ath_ucfg_setparam` entra no case `0x200a` (offset `0x0ad0`) e chama `wmi_unified_pdev_get_tpc_config_cmd_send(wmi_handle, 1)`.
* O comando WMI TLV (`WMI_PDEV_GET_TPC_CONFIG_CMDID`) **é despachado ao firmware** via `wifi_3_0.ko`.
* **O Bug:** O registrador `r9` foi inicializado na entrada com `mvn r9, #21` (`-22` / `-EINVAL`). Após despachar o comando, o código salta para a saída sem zerar `r9`. O driver sempre devolve `-EINVAL` ao espaço de usuário.

### 2.2. Por que nada apareceu no `dmesg`?
* O firmware Q6 calcula o TPC e responde com o evento WMI `0x22` (`WMI_PDEV_TPC_CONFIG_EVENTID`).
* O manipulador `ol_ath_pdev_tpc_config_event_handler` (offset `0x7a4c`, 36 bytes) faz:
  ```arm
  7a4c: ldr  r3, [r0, #0x198]
  7a50: ldr  r3, [r3, #0x68]    @ Ponteiro do callback de debug
  7a54: cmp  r3, #0
  7a58: beq  7a6c               @ Se for NULL, encerra imediatamente!
  7a5c: push {r4, lr}
  7a60: blx  r3
  ```
* Em builds comerciais de produção da Acer, o ponteiro `[r3, #0x68]` é mantido em `NULL`. O evento com todos os dados é descartado sem gerar logs.

### 2.3. De onde sai a leitura de `iw dev ath2 info`?
* No `umac.ko`, `wlan_cfg80211_get_txpower` chama `ieee80211_ucfg_get_txpow`, que lê um inteiro de 16 bits no offset `+564` da interface e divide por 2 (unidade interna de meio dBm: 30 / 2 = 15 dBm).
* Esse número representa a potência de referência da menor taxa/teto da cadeia individual mantida no estado do host.

---

## 3. Decodificação Forense da BDF e Caldata (QCN9224 / Waikiki)

Foi desenvolvido o script [`04_SCRIPTS_E_FERRAMENTAS/decodificar_bdf_caldata_6ghz.py`](file:///Volumes/--400GB--/FEITOS%20COM%20IA/Acer-Predator-Connect-T7/04_SCRIPTS_E_FERRAMENTAS/decodificar_bdf_caldata_6ghz.py), pioneiro na decodificação do payload interno do QCN9224.

### 3.1. Comparação Forense: `bdwlan_fcc.b1015` vs `caldata_2.bin`
* **Tamanho BDF FCC:** 161.792 bytes
* **Tamanho Caldata 2:** 184.320 bytes (extraído da partição ART `0:ART`, offset `skip=362496`)
* **Diferenças Mapeadas:** Exatamente 25 blocos calibrados individualmente em hardware.

### 3.2. A Tabela Conformance Test Limits (CTL) da FCC (Offset `0x1bf70`)
* **Na Caldata individual:** O hardware foi medido e calibrado na fábrica com suporte de até **21,0 dBm** (`[14.0, 14.5, 15.0, 15.5, 16.0, 18.0, 19.0, 21.0] dBm`).
* **Na BDF FCC (`bdwlan_fcc.b1015`):** **126 de 144 entradas (87,5%) foram deliberadamente travadas no byte `0x3c` (15,0 dBm)**, com recuos de borda para 14,5 e 14,0 dBm.
* **Conclusão:** A BDF FCC sobrepõe a calibração de bancada e crava o teto legal de emissão LPI em 15,0 dBm.

### 3.3. Rate Power Table em 320 MHz (Offset `0xd4b8`)
As unidades na BDF usam quartos de dBm ($0{,}25\text{ dBm}$). Na alocação 320-1 (Centro 6105 MHz, abrangendo o canal primário 37):

```text
Cadeia 0 (Linha 18): MCS0=16.5 | MCS1=16.0 | MCS2-5=15.0 | MCS6-11=18.5 | MCS12-13=17.5 dBm
Cadeia 1 (Linha 44): MCS0-3=18.5 | MCS4-7=17.5 | MCS8=16.5 | MCS9=16.0 | MCS10-13=15.0 dBm
```

Para as taxas mais densas de Wi-Fi 7 (**1024-QAM e 4096-QAM nos MCS 10 a 13**), a Cadeia 1 está travada em **15,0 dBm** para não ultrapassar a distorção máxima permitida de EVM (-38 dB a -40 dB).

### 3.4. Arquitetura Dual-MAC Descoberta no QCN9224
A extração forense revelou que o chip QCN9224 possui tabelas completas para **ambas as bandas de alta frequência**:
* **Faixa 5 GHz (Offset `0xfa3c`, 18 pontos):** `[5180, 5200, 5220, 5240, 5260, ..., 5825 MHz]`.
* **Faixa 6 GHz (Offset `0x1e234`, 18 pontos):** `[5955, 6015, 6085, 6135, ..., 7115 MHz]`.
Isso confirma a capacidade de hardware Dual-MAC do firmware `amss_dualmac.bin`, permitindo agregação MLO direta dentro do rádio.

### 3.5. Calibração do Cristal Oscilador (XO Trim / Offset `0x0232`)
Um dos dados mais críticos descobertos na engenharia reversa do silício:
* **BDF Genérica Padrão:** `0x21` (33 passos de capacitância).
* **Caldata Deste Aparelho Físico:** **`0x61`** (97 passos de capacitância) + `0x08`.
* **Impacto no Funcionamento:** O cristal oscilador de quartzo sofre desvios naturais de fabricação em partes por milhão (ppm). Em canais de 320 MHz, qualquer desvio de ppm distorce a fase das milhares de subportadoras ortogonais (OFDMA) e destrói os pontos de constelação do 4096-QAM. O caldata armazena a capacitância de carga exata calibrada na máquina de teste para anular o drift a zero ppm.

### 3.6. Sensores TSSI (Power Detector Direcional / CLPC)
* **Cadeia 0 (Offset `0xb806`):** Offsets de medição `[+0.3, -0.3, -0.5, +0.2, -0.3, -0.8, -0.9, -0.9, -0.5, -0.9, -1.3, -1.1] dB`.
* **Cadeia 1 (Offset `0x19fba`):** Offsets de medição `[+0.3, -0.8, -0.7, -0.5, -0.4, -0.3, -0.1, +0.2, +0.3] dB`.
* **Função:** Sensores integrados aos amplificadores Skyworks medem em tempo real a potência em Watts enviada para a antena e alimentam o Closed-Loop Power Control (CLPC) do firmware.

### 3.7. Calibração Individual do Silício de Fábrica (ATE Offsets)
* **Cadeia 0 (Offset `0xb7e4`):** Offsets reais de **-0,3 a -1,4 dB** (`[-7, -14, -5, -3, -8, -5, 0, 0, -4, -7, -7, -11]`).
* **Cadeia 1 (Offset `0x19f98`):** Offsets reais de **-0,3 a -1,2 dB** (`[-12, -5, -12, -7, -9, -9, 0, 0, -8, -6, -7, -6]`).
* **Front-End Skyworks 6 GHz:** Cadeia 0 = **`'777777'`** (Offset `0xb827`) | Cadeia 1 = **`'899999'`** (Offset `0x19fdb`).

---

## 4. Comparativo Tri-Regional de BDFs: FCC vs CE vs DEFAULT

O firmware da Acer embute três variantes completas de dados de placa para o rádio QCN9224:

| Parâmetro | `bdwlan_fcc.b1015` | `bdwlan_ce.b1015` | `bdwlan_default.b1015` |
| :--- | :---: | :---: | :---: |
| **Domínio Regulatório** | `0x4bb6` (FCC / Anatel) | `0x4fb2` (ETSI / Europa) | `0x4bb6` (Resto do Mundo) |
| **Teto 20 MHz (Ch 1)** | **20,0 dBm** | **12,0 dBm** (Restrito) | **20,0 dBm** |
| **Teto 320 MHz C0** | **18,5 dBm** (MCS6-11) | **11,5 dBm** (Flat todas taxas) | **18,5 dBm** |
| **Teto 320 MHz C1 (4096-QAM)** | **15,0 dBm** | **15,0 dBm** | **15,0 dBm** |
| **Teto LPI PSD Backoff** | 15,0 dBm | 13,5 dBm | **21,0 dBm** (MCS6-7) |
| **Perfil Operacional** | Alta Potência EUA/BR | Limite Rígido 200 mW EIRP | Genérico Internacional |

---

## 5. Arquitetura de Seleção de BDF e Banco de Dados `wifi_cert`

Durante o boot do roteador, o script `/etc/init.d/wifi_fw_mount` executa a seleção dinâmica:
1. Lê `uci get wireless.wifi2.country` (ou NVRAM `customer_nv r region`).
2. Consulta o banco de dados oficial em `/etc/config/wifi_cert` (206 países mapeados).
3. Cria symlinks dinâmicos em `/lib/firmware/qcn9224/bdwlan.b1015`:
   * Código `0`: `bdwlan_default.b1015`
   * Código `1`: `bdwlan_ce.b1015`
   * Código `2`: `bdwlan_fcc.b1015`

### Exemplos do Banco `wifi_cert`:
* **Brasil (`BR`):** `2 2 Y` $\rightarrow$ 2.4G = FCC (`b16`), 5G = FCC (`b16`), 6G = FCC (`bdwlan_fcc.b1015`).
* **Estados Unidos (`US`):** `2 2 Y` $\rightarrow$ 2.4G = FCC, 5G = FCC, 6G = FCC.
* **Alemanha / Reino Unido (`DE` / `GB`):** `0 1 Y` $\rightarrow$ 5G = CE, 6G = CE (`bdwlan_ce.b1015` - potência cortada).
* **Chile (`CL`):** `2 2 Y(0)` $\rightarrow$ 2.4G = FCC, 5G = FCC, 6G = DEFAULT (`bdwlan_default.b1015`).

---

## 6. Decodificação do SoC Interno IPQ5332 (2.4 GHz e 5 GHz)

O rádio onboard do SoC IPQ5332 gerencia as interfaces `wifi0` (2.4 GHz) e `wifi1` (5 GHz):
* **BDF:** `/lib/firmware/IPQ5332/bdwlan_fcc.b16` (63.488 bytes) | RegDomain: `0xbc3e` | Board ID: `0x5b34`.
* **Caldata:** `/lib/firmware/IPQ5332/caldata.bin` (extraído da partição ART `0:ART`, offset `skip=4096`).
* **Matriz de Potência 2.4 GHz (Offset `0xb8d0` - `0xba00`):**
  * MCS 0 a 3: **19,0 dBm** por cadeia (**22,0 dBm MIMO 2x2 conducted**).
  * MCS 4 a 7: **17,0 dBm** por cadeia (**20,0 dBm MIMO 2x2 conducted**).
  * MCS 8 a 11 (Wi-Fi 6): **14,0 dBm** por cadeia (**17,0 dBm MIMO 2x2 conducted**).
* **Calibração de Fábrica:** Apenas 36 bytes diferem da BDF genérica, localizados nos offsets `0xae54` (correções de ganho de até -2,1 dB) e `0xbaea` (sensores de temperatura e acopladores).

---

## 7. Física e Matemática de RF do Sistema

### 7.1. Conversão Logarítmica: dBm para Miliwatts
$$\text{Potência (mW)} = 10^{\left(\frac{\text{dBm}}{10}\right)}$$

* **A Regra dos 3 dB:** A cada $+3\text{ dB}$, a potência física em mW **dobra**. A cada $-3\text{ dB}$, ela **corta pela metade**.
* **A Regra dos 10 dB:** A cada $+10\text{ dB}$, a potência física multiplica por 10. A cada $-10\text{ dB}$, divide por 10.

### 7.2. Soma Física MIMO 2x2
O T7 opera com duas portas físicas simultâneas:
1. Cadeia 0: $15\text{ dBm} = 31{,}62\text{ mW}$
2. Cadeia 1: $15\text{ dBm} = 31{,}62\text{ mW}$
3. Potência Conduzida Total: $31{,}62 + 31{,}62 = 63{,}24\text{ mW}$
4. Em dBm: $10 \log_{10}(63{,}24) = \mathbf{18{,}0\text{ dBm}}$ ($15 + 3\text{ dB}$).

### 7.3. Potência Efetiva Irradiada (EIRP)
Com o ganho passivo das antenas ($+3{,}61\text{ dBi}$) e a formação de feixe direcional TxBF ($+3{,}0\text{ dB}$):
$$\text{EIRP Total} = 18{,}0\text{ dBm (conduzido)} + 6{,}61\text{ dBi (direcional)} = \mathbf{24{,}61\text{ dBm}} \approx \mathbf{289\text{ mW}}$$

O sinal no ar é quase **10 vezes mais forte** do que os aparentes "32 mW" de uma leitura unifilar.

---

## 8. Matriz Completa de Faixas, Canais, Larguras e Modos

### 8.1. Rádio 6 GHz (`wifi2` - Qualcomm QCN9224)
* **Antenas:** MIMO 2x2 | Ganho Direcional com Beamforming: **$+6{,}61\text{ dBi}$**
* **Canais PSC Primários:** 37, 53, 69, 85, 101, 117, 133, 149, 165, 181, 197, 213

| Largura | Canal Exemplo | UCI (`txpower`) | Leitura `iw` | Conduzido 2x2 | EIRP Real | Teto BDF | Perfil Recomendado |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **320 MHz** | Canal 37 | **`15`** | **15,0 dBm** | **18,0 dBm (63 mW)** | **24,6 dBm (290 mW)** | **15,0 dBm** | Velocidade Extrema (3-4 Gbps no cômodo). |
| **160 MHz** | Canal 37 | **`16`** | **16,0 dBm** | **19,0 dBm (80 mW)** | **25,6 dBm (365 mW)** | **16,0 dBm** | Melhor Equilíbrio (+3 dB SNR p/ paredes). |
| **80 MHz** | Canal 37 | **`17`** | **17,5 dBm** | **20,5 dBm (112 mW)** | **27,1 dBm (515 mW)** | **17,5 dBm** | Cobertura Ampla (+6 dB SNR p/ casa toda). |
| **40 MHz** | Canal 37 | **`18`** | **18,5 dBm** | **21,5 dBm (141 mW)** | **28,1 dBm (650 mW)** | **18,5 dBm** | Longo alcance em 6 GHz. |
| **20 MHz** | Canal 37 | **`20`** | **20,0 dBm** | **23,0 dBm (200 mW)** | **29,6 dBm (915 mW)** | **20,0 dBm** | Borda de sinal / link crítico. |
| **Qualquer** | Qualquer | **`13`** | **13,0 dBm** | **16,0 dBm (40 mW)** | **22,6 dBm (182 mW)** | Livre | Eco 1 (-35% aquecimento QCN9224). |
| **Qualquer** | Qualquer | **`10`** | **10,0 dBm** | **13,0 dBm (20 mW)** | **19,6 dBm (91 mW)** | Livre | Eco 2 (Apenas mesmo ambiente). |

---

### 8.2. Rádio 5 GHz (`wifi1` - Qualcomm IPQ5332)
* **Antenas:** MIMO 2x2 | Ganho Direcional com TxBF: **$+7{,}38\text{ dBi}$** (Canais baixos) / **$+8{,}38\text{ dBi}$** (Canais altos)

| Faixa / Canais | Largura | UCI (`txpower`) | Leitura `iw` | Conduzido 2x2 | EIRP Real | Situação Legal |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **U-NII-1 & 2A** (36–64) | **HT160** | **`23`** | **23,0 dBm** | **26,0 dBm (400 mW)** | **33,4 dBm (2.180 mW)** | Teto FCC 24 dBm cond. |
| **U-NII-1** (36–48) | **HT80** | **`23`** | **23,0 dBm** | **26,0 dBm (400 mW)** | **33,4 dBm (2.180 mW)** | Sem DFS / Seguro |
| **U-NII-2C** (100–144) | **HT80/160** | **`23`** | **23,0 dBm** | **26,0 dBm (400 mW)** | **33,4 dBm (2.180 mW)** | Requer DFS (Pausas por radar) |
| **U-NII-3** (149–165) | **HT80** | **`26`** | **26,0 dBm** | **29,0 dBm (794 mW)** | **37,4 dBm (5.495 mW)** | **Teto Máximo sem DFS** |
| **Qualquer** | Qualquer | **`18`** | **18,0 dBm** | **21,0 dBm (126 mW)** | **28,4 dBm (692 mW)** | Modo Intermediário |
| **Qualquer** | Qualquer | **`12`** | **12,0 dBm** | **15,0 dBm (32 mW)** | **22,4 dBm (174 mW)** | Modo Econômico |

---

### 8.3. Rádio 2,4 GHz (`wifi0` - Qualcomm IPQ5332)
* **Antenas:** MIMO 2x2 | Ganho Direcional: **$+6{,}50\text{ dBi}$** | Canais: 1 a 11

| Largura | UCI (`txpower`) | Leitura `iw` | Conduzido 2x2 | EIRP Real | Observação |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **HT20** | **`22`** | **22,0 dBm** | **25,0 dBm (316 mW)** | **28,5 dBm (708 mW)** | Padrão Recomendado (Canais 1, 6 ou 11). |
| **HT20** | **`24`** | **24,0 dBm** | **27,0 dBm (501 mW)** | **30,5 dBm (1.122 mW)** | Teto Máximo US. |
| **HT40** | **`22`** | **22,0 dBm** | **25,0 dBm (316 mW)** | **28,5 dBm (708 mW)** | Maior velocidade em 2,4G. |
| **Qualquer** | **`17`** | **17,0 dBm** | **20,0 dBm (100 mW)** | **23,5 dBm (224 mW)** | Menor interferência com vizinhos. |
| **Qualquer** | **`10`** | **10,0 dBm** | **13,0 dBm (20 mW)** | **16,5 dBm (45 mW)** | Modo Econômico IoT. |

---

## 9. Telemetria Térmica e MLO em Tempo Real no Kernel (`sysfs`)

A engenharia reversa do módulo `qca_ol.ko` revelou uma interface completa de sensores expostos diretamente no subsistema de rede do Linux (`/sys/class/net/`):

### 9.1. Temperatura Real dos Chips em Graus Celsius
```bash
cat /sys/class/net/wifi0/temp   # Temperatura do silício IPQ5332 (2.4 GHz)
cat /sys/class/net/wifi1/temp   # Temperatura do silício IPQ5332 (5 GHz)
cat /sys/class/net/wifi2/temp   # Temperatura do rádio QCN9224 (6 GHz)
```

### 9.2. Níveis de Throttle e Proteção Térmica do QCN9224
* **Nível de Mitigação (`thlvl`):**
  ```bash
  cat /sys/class/net/wifi2/thlvl
  ```
  `0` = Normal | `1` = Nível Leve | `2` = Moderado | `3` = Crítico.
* **Recuo de Ciclo de Trabalho (`offpercent`):**
  ```bash
  cat /sys/class/net/wifi2/offpercent
  ```
  Mostra a porcentagem de tempo em que a transmissão é desligada para resfriar os amplificadores Skyworks.
* **Máscaras Ativas de Antena:**
  ```bash
  cat /sys/class/net/wifi2/txchains   # Retorna 3 (binário 11 = ambas antenas transmitindo)
  cat /sys/class/net/wifi2/rxchains   # Retorna 3 (binário 11 = ambas antenas recebendo)
  ```
* **Mapeamento de PHY do MLO:**
  ```bash
  cat /sys/class/net/wifi2/mldphy_name   # Retorna mld-phy0 ou mld-phy1
  ```

---

## 10. Comandos Ocultos de Driver Wi-Fi 7 / EHT no `cfg80211tool`

O binário `/usr/sbin/cfg80211tool` aceita comandos de baixo nível diretamente no driver Qualcomm:

### 10.1. Beamforming e Formação de Feixe EHT
```bash
# Ativar Beamformer e Beamformee EHT explícitos
cfg80211tool ath2 set_eht_su_bfmr 1
cfg80211tool ath2 set_eht_su_bfme 1

# Ajustar intervalo de sondagem matricial de feixe (sounding interval em ms)
cfg80211tool wifi2 txbf_snd_int 100
```

### 10.2. Otimizações de Latência e Imunidade a Ruído RF
```bash
# Modo de ultra-baixa latência para jogos (Qualcomm Gaming Mode)
cfg80211tool wifi2 low_latency_mode 1

# Imunidade Adaptativa a Ruído (Adaptive Noise Immunity)
cfg80211tool wifi2 ani_enable 1

# Preamble Puncturing estrito em caso de interferência
cfg80211tool wifi2 dfs_punctureEn 1
cfg80211tool wifi2 puncture_strict 1
```

### 10.3. Consulta de Região e Domínio Regulatório no Silício
```bash
cfg80211tool wifi2 getRegdomain
cfg80211tool wifi2 g_ap_power_mode   # 0 = LPI (Low Power Indoor), 1 = SP (Standard Power)
cfg80211tool wifi2 g_reg_txpower     # Teto regulatório anunciado no rádio
```

---

## 11. Script Utilitário: Telemetria Completa de RF e Temperatura

Para consultar todos os dados reais em uma única chamada no terminal do roteador, foi concebido o comando `/usr/bin/potencia-real`:

```bash
#!/bin/sh
echo "=================================================================="
echo "    PREDATOR CONNECT T7 - TELEMETRIA DE RF E TEMPERATURA"
echo "=================================================================="

for i in 0 1 2; do
    phy="wifi$i"
    vap="ath$i"
    
    if [ ! -d "/sys/class/net/$phy" ]; then
        continue
    fi
    
    temp=$(cat /sys/class/net/$phy/temp 2>/dev/null || echo "N/A")
    txc=$(cat /sys/class/net/$phy/txchains 2>/dev/null || echo "N/A")
    tx_iw=$(iw dev $vap info 2>/dev/null | grep txpower | awk '{print $2}')
    
    case "$i" in
        0) nome="2.4 GHz (IPQ5332)" ; gain="3.50 dBi" ;;
        1) nome="5.0 GHz (IPQ5332)" ; gain="5.38 dBi" ;;
        2) nome="6.0 GHz (QCN9224)" ; gain="3.61 dBi" ;;
    esac
    
    echo "[$nome]"
    echo "  - Temperatura do Silício:  ${temp}°C"
    echo "  - Antenas Transmitindo:    Cadeias ativas (mask: $txc)"
    echo "  - Potência por Antena:     ${tx_iw} dBm"
    if [ -n "$tx_iw" ]; then
        pwr_cond=$(awk "BEGIN {print $tx_iw + 3.01}")
        echo "  - Potência Conduzida 2x2:  ${pwr_cond} dBm (MIMO soma +3 dB)"
    fi
    echo "  - Ganho da Antena:         $gain (+3 dB TxBF)"
    echo "------------------------------------------------------------------"
done
```

---

## 12. Configurações Recomendadas no Terminal

### Perfil 1: "Velocidade Extrema Wi-Fi 7" (320 MHz em 6 GHz)
```bash
uci set wireless.wifi0.channel='6'
uci set wireless.wifi0.htmode='HT20'
uci set wireless.wifi0.txpower='22'

uci set wireless.wifi1.channel='149'
uci set wireless.wifi1.htmode='HT80'
uci set wireless.wifi1.txpower='26'

uci set wireless.wifi2.channel='37'
uci set wireless.wifi2.htmode='HT320'
uci set wireless.wifi2.txpower='15'

uci commit wireless
/sbin/wifi up
```

### Perfil 2: "Equilíbrio e Maior Penetração de Paredes" (160 MHz em 6 GHz)
```bash
uci set wireless.wifi0.channel='6'
uci set wireless.wifi0.htmode='HT20'
uci set wireless.wifi0.txpower='22'

uci set wireless.wifi1.channel='149'
uci set wireless.wifi1.htmode='HT80'
uci set wireless.wifi1.txpower='26'

uci set wireless.wifi2.channel='37'
uci set wireless.wifi2.htmode='HT160'
uci set wireless.wifi2.txpower='16'

uci commit wireless
/sbin/wifi up
```

---

## 13. Arquivos e Scripts Gerados nesta Auditoria

1. [`04_SCRIPTS_E_FERRAMENTAS/decodificar_bdf_caldata_6ghz.py`](file:///Volumes/--400GB--/FEITOS%20COM%20IA/Acer-Predator-Connect-T7/04_SCRIPTS_E_FERRAMENTAS/decodificar_bdf_caldata_6ghz.py): Decodificador forense Tri-Band de tabelas de potência, CTL, caldata individual, XO Trim e matriz regulatória para QCN9224 e IPQ5332.
2. [`06_DOCUMENTACAO/TRILHA_KERNEL_DRIVER_POTENCIA_6GHZ_V27_2026-10-09.md`](file:///Volumes/--400GB--/FEITOS%20COM%20IA/Acer-Predator-Connect-T7/06_DOCUMENTACAO/TRILHA_KERNEL_DRIVER_POTENCIA_6GHZ_V27_2026-10-09.md): Análise a nível de código dos módulos `umac.ko`, `qca_ol.ko` e `wifi_3_0.ko`.
3. [`06_DOCUMENTACAO/CONTROLE_POTENCIA_WIFI_STOCK_V27_2026-10-09.md`](file:///Volumes/--400GB--/FEITOS%20COM%20IA/Acer-Predator-Connect-T7/06_DOCUMENTACAO/CONTROLE_POTENCIA_WIFI_STOCK_V27_2026-10-09.md): Inspeção de laudos FCC oficiais e limites regulatórios.
