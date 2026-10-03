# Estudo Técnico e Arquitetural Completo: Acer Predator Connect T7
**FCC ID:** `HLZT7` | **Modelo:** Acer Predator Connect T7 (`T7`) | **Projeto ODM:** Guangyi / Arcadyan `FG18WIFI`  
**Data da Certificação FCC:** Julho de 2024 | **Laboratório de Testes:** BTL Inc. & PHOENIX TESTLAB GmbH  
**Documentação Base:** Arquivos Oficiais FCC (`EP-2311H013-1` e Relatórios Técnicos BTL)

---

## 1. Visão Geral do Hardware & ODM

O **Acer Predator Connect T7** é construído sobre a plataforma de referência Qualcomm Wi-Fi 7 Immersive Home Platform. A documentação técnica arquivada na FCC revela a identidade do ODM (Original Design Manufacturer) e os códigos de projeto industriais:

- **Código de Projeto ODM:** `FG18WIFI` (Guangyi / Arcadyan Technology)
- **Silk-Screen da Placa-Mãe (Motherboard):** `FG18_MB_PCB_V1.3 S2352`
- **Revisão de Hardware:** V1.3
- **Chassi / Enclosure:** Torre hexagonal com aletas térmicas verticais, dissipação passiva com chapa de alumínio fundido e antena array interna superior.

```
                      +------------------------------------------+
                      |       Sunnyway 8x PIFA Antenna Array     |
                      |     (2.4 GHz, 5 GHz, 6 GHz Wi-Fi 7)      |
                      +--------------------+---------------------+
                                           | I-PEX MHF4
             +-----------------------------+-----------------------------+
             |                                                           |
             v                                                           v
+---------------------------+                               +---------------------------+
|  Qualcomm IPQ5322 SoC     |                               |   Qualcomm QCN6274        |
|  - 4x Cortex-A53 @ 1.5GHz |<====== PCIe Gen3 x1 =========>|   - Wi-Fi 7 6 GHz Dedicado|
|  - NSS Acceleration Core  |        (pcie@18000000)        |   - 320 MHz (EHT320)      |
|  - 2.4 GHz & 5 GHz Radio  |                               |   - Até 5764 Mbps (2T2R)  |
+-------------+-------------+                               +---------------------------+
              |
      +-------+-------+--------------------+--------------------+
      |               |                    |                    |
      v               v                    v                    v
+-----------+   +-------------+    +---------------+    +-------------------+
|  1GB DDR4 |   | 512MB SPI   |    | Qualcomm PHY  |    | Qualcomm QCA8384  |
|  NANYA    |   | NAND Flash  |    | 2.5 Gbps WAN  |    | 4-Port Switch     |
| NT5AD512M |   | MX35UF4GE4AD|    | (Atheros PHY) |    | 2x Gigabit LAN    |
+-----------+   +-------------+    +---------------+    +-------------------+
```

---

## 2. Inventário Detalhado dos Circuitos Integrados (Chips)

Através da extração direta e análise fotográfica em alta definição dos 31 relatórios da FCC (`EP-2311H013-1`), todos os chips sob as blindagens de RF (RF Shields) foram identificados e confrontados com os dumps de memória do sistema:

### 2.1 Processador Central (SoC)
- **Marca/Modelo:** **Qualcomm IPQ5322 003**
- **Marcação Física no Die:** `IPQ-5322 / 003 / FK3225LV`
- **Arquitetura:** Quad-Core ARM Cortex-A53 (ARMv8-A, compatível com 32-bit e 64-bit) operando a até 1.5 GHz.
- **Processo Litográfico:** 14nm FinFET.
- **Recursos Integrados:**
  - Coprocessador de aceleração de rede NSS (Network Subsystem / NPU).
  - Controlador de memória DDR4 com barramento de 16/32 bits.
  - Bloco de rádio integrado para bandas 2.4 GHz e 5 GHz 802.11be (2x2).
  - Interface QSPI / SPI NAND dedicada para inicialização de alta velocidade.

### 2.2 Memória RAM
- **Marca/Modelo:** **NANYA NT5AD512M16A4-HR**
- **Capacidade:** 8 Gbit = **1.0 GB (1024 MB)** DDR4 SDRAM.
- **Velocidade:** DDR4-3200 (1600 MHz clock real, CL22).
- **Barramento:** 16-bit com interface direta de baixa latência ao IPQ5322.

### 2.3 Memória de Armazenamento Não-Volátil (Flash)
- **Marca/Modelo:** **Macronix (MXIC) MX35UF4GE4AD-Z4I**
- **Marcação Física:** `MXIC MX35UF / 4GE4AD-Z4I / 5N637100`
- **Capacidade:** 4 Gbit = **512 Megabytes (512 MB)**.
- **Tecnologia:** SPI NAND Flash de 1.8V (High-Speed Quad SPI).
- **Organização Interna:**
  - Tamanho da Página: 2048 bytes (+ 64 bytes OOB/Spare).
  - Tamanho do Bloco de Apagamento (Eraseblock): 128 KB (131.072 bytes).
  - ECC Interno (On-Die ECC): 4-bit ou 8-bit ECC por 512 bytes.
- **Distribuição de Partições MTD (Conforme extraído no dump):**
  - `rootfs` (Slot 1 Primário de Fábrica): 240 MB (`mtd21`)
  - `rootfs_1` (Slot 2 Secundário de Recuperação): 240 MB (`mtd23`)
  - Partições de Boot/Calibração (`0:SBL1`, `0:MIBIB`, `0:ART`, `0:BOOTCONFIG`): 32 MB combinados.

### 2.4 Controlador de Switch e Rede Física (Ethernet)
- **Marca/Modelo:** **Qualcomm QCA8384 000**
- **Marcação Física:** `QCA8384 / 000 / FE3035YJ`
- **Função:** Switch Ethernet Gigabit gerenciado de 4 portas com suporte a IEEE 802.1Q VLANs, QoS por hardware e controle de fluxo IEEE 802.3x.
- **Controlador PHY WAN Integrado:** Transceiver dedicado 2.5 Gbps (`ethernet-phy-id004d.d180` operando a 2500Base-X).
- **Transformadores de Isolamento (Magnetics):**
  - `FLY_CORE FC1504GY` (Semana 28 de 2023)
  - `FLY_CORE FC5433` (Semana 11 de 2023)

### 2.5 Transceiver Wi-Fi 7 de 6 GHz (Rádio Dedicado)
- **Marca/Modelo:** **Qualcomm QCN6274 001**
- **Marcação Física:** `QCN-6274 / 001 / JK303C48`
- **Interface de Barramento:** PCIe Gen3 x1 conectado à porta PCIe 1 do IPQ5322 (`pcie@18000000`).
- **Recursos Principais:**
  - Banda U-NII-5 até U-NII-8 (5925 MHz a 7125 MHz).
  - Suporte completo a canais ultra-largos de **320 MHz (`EHT320`)**.
  - Modulação 4096-QAM (4K-QAM).
  - Taxa física teórica de até **5764 Mbps** em configuração 2x2 MIMO.
  - Multi-Link Operation (MLO) suportando agregação e switching transparente simultâneo com as bandas de 2.4 GHz e 5 GHz.

---

## 3. Especificação do Sistema de Antenas (Sunnyway)

De acordo com o documento de especificação do fabricante de antenas (`Shanghai Sunnyway Communication Technology Co., Ltd.`, Projeto `FG18WIFI`), o Acer T7 possui um conjunto omnidirecional de **8 antenas PIFA internas** conectadas via micro-conectores I-PEX MHF4 de 50 ohms:

| Antena | Código Sunnyway | Faixa de Frequência | Ganho Máximo | Aplicação Primária |
| :--- | :--- | :--- | :--- | :--- |
| **ANT0** | `SH23227IB98-1` | 2.4 GHz / 5 GHz | 1.43 dBi (2.4G) / 5.38 dBi (5G) | Transmissão/Recepção MIMO Ch 0 |
| **ANT1** | `SH23227IB98-2` | 2.4 GHz / 5 GHz | 0.84 dBi (2.4G) / 4.06 dBi (5G) | Transmissão/Recepção MIMO Ch 1 |
| **ANT2** | `SH23227IB98-3` | 5 GHz High-Band | 4.80 dBi | Diversidade e Beamforming 5 GHz |
| **ANT3** | `SH23227IB98-4` | 5 GHz DFS / Radar | 4.50 dBi | Zero-Wait DFS e Scan de Frequência |
| **WIFI1**| `SH23227IB65-1` | 5925 – 7125 MHz | 3.23 dBi | Wi-Fi 7 6 GHz Transceiver Ch 0 |
| **WIFI2**| `SH23227IB65-2` | 5925 – 7125 MHz | 3.61 dBi | Wi-Fi 7 6 GHz Transceiver Ch 1 |
| **ANT7** | `SH23227IB98-5` | Bluetooth / IoT | 1.20 dBi | Coexistência BT/Thread/Zigbee |
| **ANT8** | `SH23227IB98-6` | Malha de Retorno | 3.10 dBi | Predator Mesh Dedicated Backhaul |

### Parâmetros de Potência Radiada e Homologação FCC
- **2.4 GHz (802.11b/g/n/ax/be):**
  - Ganho Direcional com Beamforming: **4.43 dBi**
  - Potência Máxima Conduzida: **25.55 dBm (358.9 mW)**
  - Taxa Máxima: 688 Mbps (EHT40)
- **5 GHz (802.11a/n/ac/ax/be):**
  - Ganho Direcional com Beamforming: **8.38 dBi**
  - Potência Máxima Conduzida: **27.32 dBm (539.5 mW)**
  - Taxa Máxima: 2882 Mbps (EHT160)
- **6 GHz Wi-Fi 7 (802.11ax/be - Low Power Indoor 6ID):**
  - Ganho Direcional com Beamforming: **6.61 dBi**
  - Potência Máxima Irradiada (EIRP): **28.67 dBm (736.2 mW)**
  - Taxa Máxima: 5764 Mbps (EHT320)
  - Canais 320 MHz Homologados: `31, 63, 95, 127, 159, 191`

---

## 4. Requisitos de Alimentação e Interfaces Externas

- **Fonte de Alimentação Externa:**
  - Modelo: `TPQ-229C120300UW01` / `TPQ-229C120300VW01`
  - Entrada: 100-240V AC ~ 50/60Hz 1.2A
  - Saída: **12.0V DC @ 3.0A (36 Watts)** com conector coaxial barrel plug central positivo.
- **Portas Traseiras:**
  - 1x Porta WAN 2.5 Gbps (RJ45 com detecção automática 100M/1G/2.5G).
  - 2x Portas LAN 1 Gbps (Porta 1 marcada como "Game Port" com priorização QoS).
  - 1x Porta USB Type-C (para diagnósticos / alimentação de acessórios).
  - 1x Botão WPS (`GPIO 35`).
  - 1x Botão Reset oculto (`GPIO 49`).

---

## 5. Mapeamento para o OpenWrt & Device Tree (DTS)

Com a certeza absoluta dos circuitos integrados fornecida pela FCC:

1. **Substituição do Nó de Flash (`&qspi`):**
   - Configurar o controlador QSPI para comunicar com a Macronix `MX35UF4GE4AD` em 1.8V, frequência de clock até 104 MHz e layout MTD de partições duplas de 240 MB (`rootfs` e `rootfs_1`).
2. **Nó do Switch Ethernet QCA8384:**
   - O driver correto a utilizar no kernel OpenWrt é o driver para a família `qca8386` (`compatible = "qcom,ess-switch-qca8386"`), com acesso via MDIO (`mdio-bus = <0xC>`), configurando a porta 0 para o CPU, porta 1 para LAN1 e porta 2 para LAN2.
3. **Driver Sem Fio (ath12k):**
   - O chip **QCN6274** utiliza o driver `ath12k` padrão do kernel Linux upstream, exigindo os firmwares `q6_fw3.mdt` e arquivos de calibração extraídos da partição `0:ART` (`board-2.bin`).
4. **Bootloader & Kernel Mode (32-bit ARMv7 vs 64-bit AArch64):**
   - O U-Boot OEM da Acer executa em modo 32-bit (`blx` para o kernel zImage a `0x44000000`). Para iniciar um kernel OpenWrt moderno de forma 100% nativa sem necessidade de substituir o U-Boot na flash, a imagem OpenWrt para o Slot 2 pode ser compilada como `armv7l` (32-bit) ou utilizar um boot wrapper pequeno para transicionar para AArch64.
