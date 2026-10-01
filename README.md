<p align="center">
  <img src="assets/acer-predator-t7-banner.jpg" alt="Acer Predator Connect T7 Wi-Fi 7 Banner" width="100%">
</p>

# Acer Predator Connect T7 - Desbloqueio, Modo Access Point 2.5 Gbps & Wi-Fi 7

> **Resumo Executivo**: Documentação completa da transformação do roteador gamer **Acer Predator Connect T7** (Qualcomm IPQ5332 Wi-Fi 7) em um **Ponto de Acesso (AP) / Switch de 2.5 Gbps de altíssima performance**, sem duplo NAT, com desbloqueio permanente de terminal Root (SSH / Telnet), canais de rádio otimizados e backups de baixo nível para recuperação de desastre.

> **Keywords / SEO**: Acer Predator Connect T7, Wi-Fi 7 router unlock, Qualcomm IPQ5332, MLO 6GHz, AP Mode 2.5Gbps, root access dropbear, telnet unlock, unbrick predator t7, openwrt predator t7, double NAT fix, firmware dump MTD.

---

> [!IMPORTANT]
> ### ⚠️ Atenção sobre o Endereço IP do Roteador:
> * **IP Padrão de Fábrica (Stock Default):** **`192.168.76.1`** (Modo Roteador tradicional com servidor DHCP ativo na faixa `192.168.76.x`).
> * **IP Customizado deste Projeto (Lab / Modo AP):** **`192.168.73.2`** (Alterado manualmente pelo usuário para operar como Access Point / Bridge na mesma sub-rede do roteador mestre `192.168.73.1`, com DHCP desativado).
> * **Regra Prática:** Se o seu roteador está com as configurações de fábrica ou foi recém-resetado, utilize **`192.168.76.1`**. Se já aplicou o arquivo de backup para AP deste projeto, utilize **`192.168.73.2`**.

---

## 1. Dados e Credenciais da Rede

| Parâmetro | Padrão de Fábrica (Stock) | Configuração Ativa (Modo AP Lab) | Detalhes |
| :--- | :--- | :--- | :--- |
| **Endereço IP** | **`192.168.76.1`** | **`192.168.73.2`** | IP estático na rede local |
| **Máscara de Sub-rede** | `255.255.255.0` (`/24`) | `255.255.255.0` (`/24`) | Sub-rede alinhada ao roteador mestre |
| **Gateway / DNS** | `192.168.76.1` | `192.168.73.1` | Roteador Mestre (Cudy WR3000) |
| **Servidor DHCP** | **Ativado** (Pool 76.x) | **Desativado** | Evita duplo NAT; todos os IPs vêm do Mestre |
| **Porta WAN (2.5 Gbps)** | Roteamento NAT | Em Bridge com LAN | Tráfego de 2 Gbps flui sem gargalo |
| **Usuário do Painel Web** | `Admin` | `Admin` | Senha configurada pelo usuário |
| **Usuário Terminal (SSH / Telnet)**| *(Bloqueado de fábrica)* | `Admin` ou `root` | UID 0 (Superusuário completo) |
| **Acesso Telnet (Sem senha)** | Porta `23` | Porta `23` | `telnet 192.168.73.2` (ou `76.1`) |
| **Acesso SSH (Criptografado)** | Porta `22` | Porta `22` | `ssh -o HostKeyAlgorithms=+ssh-rsa Admin@192.168.73.2` (ou `76.1`) |

---

## 2. Configuração dos Rádios e Redes Wi-Fi

| Rádio | Frequência | SSID | Canal Travado | Largura | Potência | Finalidade |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`wifi0`** | 2.4 GHz | **`CASA_ARK`** | **1** | **`HT20` (20 MHz)** | 25 dBm | Máxima penetração de paredes e alcance (25m) |
| **`wifi0`** | 2.4 GHz | **`TV casa`** | **1** | **`HT20` (20 MHz)** | 25 dBm | Na bridge `lan` principal (espelhamento liberado) |
| **`wifi1`** | 5 GHz | **`CASA_ARK_5G`** | **36** | **`HT160` (160 MHz)** | 25 dBm | Mais de 1.5 a 2 Gbps sem risco de queda por radar DFS |
| **`wifi2`** | 6 GHz | **`CASA_ARK_6G`** | **37 (PSC)** | **`HT320` (320 MHz)** | 25 dBm | Wi-Fi 7 ultra-rápido no canal de varredura preferencial |
| **MLD** | 5G + 6G | **`CASA_ARK_7G`** | MLO Agregado | 160 + 320 MHz | 25 dBm | **Wi-Fi 7 Multi-Link Operation** ativo em hardware |

*As senhas das redes Wi-Fi podem ser mantidas ou customizadas livremente no painel web ou via terminal UCI (`uci set wireless.@wifi-iface[X].key='suasenha'`).*

---

## 3. Comandos Rápidos de Acesso

### Acesso Instantâneo via Telnet (Recomendado na LAN):
No Prompt de Comando ou PowerShell do Windows:
```powershell
# Se o roteador estiver com o IP padrão de fábrica:
telnet 192.168.76.1

# Se o roteador já estiver configurado como AP na rede deste lab:
telnet 192.168.73.2
```
*Você cai direto no terminal de superusuário (`/ #`) sem necessidade de senha.*

### Acesso via SSH:
```powershell
# Se o roteador estiver com o IP de fábrica:
ssh -o HostKeyAlgorithms=+ssh-rsa Admin@192.168.76.1

# Se o roteador já estiver configurado no modo AP:
ssh -o HostKeyAlgorithms=+ssh-rsa Admin@192.168.73.2
```
*(ou `ssh -o HostKeyAlgorithms=+ssh-rsa root@...`, utilizando a sua senha de Admin).*

---

## 4. Estrutura deste Repositório

```text
Acer-Predator-Connect-T7/
├── Backups_MTD/                                 # [CRÍTICO] Imagens brutas da memória Flash (Full Dump)
│   ├── backup_predator_t7_art.bin               # Calibração Wi-Fi 7 (Atheros Radio Test - 2 MB)
│   ├── backup_predator_t7_ubi_rootfs.bin        # Imagem bruta 1:1 do SquashFS de fábrica (38 MB)
│   ├── backup_predator_t7_wifi_fw_raw.bin       # Partição bruta do firmware Wi-Fi (8.16 MB)
│   ├── backup_predator_t7_kernel.bin            # Partição bruta do Kernel Linux 5.4 Qualcomm (4.04 MB)
│   ├── backup_predator_t7_qsee_tz.bin           # Qualcomm TrustZone / QSEE (3.5 MB)
│   ├── backup_predator_t7_uboot_appsbl.bin      # Bootloader U-Boot APPSBL principal (1.5 MB)
│   ├── backup_predator_t7_appsbl_1.bin          # Cópia secundária do U-Boot (1.5 MB)
│   ├── backup_predator_t7_sbl1.bin              # Bootloader primário Qualcomm SBL1 (1.5 MB)
│   ├── backup_predator_t7_ethphy_fw.bin         # Firmware da PHY Ethernet 2.5G (1 MB)
│   ├── backup_predator_t7_mibib.bin             # Tabela de partições do SoC (1 MB)
│   ├── backup_predator_t7_uboot_env.bin         # Variáveis de ambiente do U-Boot (512 KB)
│   ├── backup_predator_t7_devcfg.bin            # Device Config Qualcomm (512 KB)
│   └── backup_predator_t7_cdt.bin               # Platform Data CDT (512 KB)
│
├── Configuracoes_Roteador/                      # Arquivo .cfg pronto para restauração Web
│   └── config_ap_ssh_unlocked_template.cfg      # Template público ativo (AP + Wi-Fi 7 + SSH + Canais)
│
├── Engenharia_Reversa_OpenWrt/                  # [DEV] Kit de portabilidade para o OpenWrt Oficial
│   ├── acer_predator_t7.dts                     # Árvore de dispositivos (Device Tree) DESCOMPILADA (100 KB)
│   ├── acer_predator_t7.dtb                     # Binário original montado pelo kernel (/sys/firmware/fdt)
│   ├── kernel_modules_5.4.213.tar.gz            # Drivers proprietários compilados (PPE, NSS, ECM, Wi-Fi 7 - 8.3 MB)
│   ├── webapps_acer_oem.tar.gz                  # Binários e daemons da interface Acer, CGI e Killer QoS (3.4 MB)
│   ├── qualcomm_ini_and_sawf.tar.gz             # Tabelas INI de calibração Qualcomm e classes SAWF QoS (8 KB)
│   ├── etc_factory_tree.tar.gz                  # Árvore /etc/ de fábrica (scripts init.d, uci defaults - 435 KB)
│   ├── ipq5332_wifi_fw.tar.gz                   # Pacote de firmwares Wi-Fi 7 Qualcomm IPQ5332 (4.3 MB)
│   ├── gpio_table.txt                           # Tabela e mapa de pinos digitais GPIO
│   ├── board.json                               # Definição OpenWrt de modelo e portas de rede
│   ├── switch_config.txt                        # Configuração do switch gigabit integrado
│   ├── loaded_modules.txt                       # Módulos de kernel carregados (lsmod)
│   ├── network_interfaces.txt                   # Mapeamento completo de interfaces de rede
│   ├── README_PORT_OPENWRT.md                   # Guia passo a passo para criar o Target no OpenWrt
│   └── modem_5g_fibocom_x7/                     # [NOVO] Engenharia reversa do modem 5G Fibocom FM160 do X7
│       ├── bin/                                 # Binários RIL (at_rild, ipqcm, modem-monitor, etc.)
│       ├── config/                              # Configurações do modem, ril.json (/dev/mhi_at) e GPIOs
│       ├── init.d/                              # Scripts de serviço de telefonia e discagem celular
│       ├── kmod/                                # Drivers de kernel (rmnet_core.ko, rmnet_ctl.ko)
│       └── README.md                            # Documentação técnica detalhada do subsistema celular
│
├── Scripts_Automacao/                           # Utilitários Python
│   ├── apply_debloat.py                         # Limpeza cirúrgica de telemetria, FOTA e daemons não utilizados
│   ├── dump_full_firmware.py                    # Script de dump completo 1:1 de MTDs e diretórios do sistema
│   ├── unlock_only_ssh.py                       # Script para destravar SOMENTE SSH/Telnet em qualquer backup
│   ├── build_ssh_unlocked.py                    # Script que compilou a injeção do SSH e canais
│   └── test_router_access.py                    # Diagnóstico rápido de portas, temperatura e Wi-Fi
│
├── README.md                                    # Este documento
├── DESCOBERTAS_LUCI_DEBLOAT_E_ARQUITETURA.md    # [IMPORTANTE] LuCI nativo, fix de login, debloat e blueprint
├── COMO_EDITAR_CFG_E_LIBERAR_SSH.md             # Guia: como editar o .cfg e destravar apenas SSH/Telnet
├── GUIA_TECNICO_DESBLOQUEIO_E_AP.md             # Passo a passo da engenharia reversa e modificações
├── MAPA_HARDWARE_E_PARTICOES.md                 # Tabela MTD, Dual-Boot e parâmetros do U-Boot
└── RECUPERACAO_E_DESASTRE_UNBRICK.md            # Guia de recuperação de emergência (TFTP)
```

---

## 5. 📦 Boas Práticas de Download e Armazenamento (GitHub & Repositório)

Este repositório preserva imagens de calibração e partições MTD essenciais (`Backups_MTD/`). Para garantir downloads rápidos e respeitar as diretrizes da comunidade:

> [!TIP]
> ### ⚡ Dica para Clonagem Rápida:
> Para economizar tempo e largura de banda, recomenda-se realizar uma **clonagem rasa** (*shallow clone*), que baixa apenas a revisão atual dos arquivos sem todo o histórico de commits:
> ```bash
> git clone --depth 1 https://github.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7.git
> ```

> [!IMPORTANT]
> ### 🛡️ Diretrizes de Armazenamento e Limites do GitHub:
> * **Limite de Arquivo do Git:** O GitHub impõe um limite estrito de **100 MB** por arquivo individual no Git tradicional (com alertas a partir de 50 MB) e recomenda manter o repositório abaixo de **1 GB a 5 GB**.
> * **Publicação de Novos Dumps ou Imagens Compiladas:** Imagens completas de firmware (`.bin`, `.img`, `.iso`) ou pacotes compilados pesados **não devem ser commitados diretamente na árvore do Git**. Em vez disso, utilize a aba **[Releases](https://github.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/releases)** do repositório, que suporta gratuitamente arquivos de até **2 GB cada**, mantendo o repositório leve, ágil e dentro das diretrizes gratuitas do GitHub.

---

## 6. 🔗 Compatibilidade com o Acer Predator Connect X7 5G CPE (Irmão Gêmeo)

Conforme identificado em discussões de desenvolvedores no fórum oficial do OpenWrt, o roteador **Acer Predator Connect X7 5G CPE** compartilha **99% do mesmo hardware e código-fonte base** com o **Predator Connect T7**.

### 🔍 Evidências Forenses Comprovadas nos Dumps:
1. **Mesma Plataforma Base:** Ambos utilizam a arquitetura Qualcomm Immersive Home `IPQ5332/AP-MI01.6`, com kernel Linux 5.4.213, mesmo particionamento MTD e rádios Wi-Fi 7 BE11000.
2. **Código do Modem no T7:** No dump original da partição `rootfs` do T7, o binário `/usr/bin/at_rild` contém a rotina de detecção `AT+CGMI?` validando o fabricante `"Fibocom"` e a função interna dedicada `set_fm160_usb_lock`.
3. **Device Tree (DTS):** O Device Tree extraído do T7 (`acer_predator_t7.dts`) declara ativamente o barramento PCIe 0 (`pcie@20000000`) com o controlador MHI (`qcom,mhi@0`), aliases de rede `rmnet_mhi` e os pinos GPIO 33 (`mdm2ap`) e 34 (`ap2mdm`).
4. **Módulos Celulares Ativos:** O kernel carrega nativamente os módulos `rmnet_core.ko` e `rmnet_ctl.ko`.

### 📊 Comparativo Técnico: T7 vs. X7

| Componente | Predator Connect T7 | Predator Connect X7 5G CPE |
| :--- | :--- | :--- |
| **SoC Principal** | Qualcomm IPQ5332 (Quad-Core A53 @ 1.5 GHz) | Qualcomm IPQ5332 (Quad-Core A53 @ 1.5 GHz) |
| **Wi-Fi** | Tri-Band Wi-Fi 7 BE11000 (2.4G + 5G + 6G) | Tri-Band Wi-Fi 7 BE11000 (2.4G + 5G + 6G) |
| **Portas de Rede** | 1x 2.5 Gbps WAN + 2x 1 Gbps LAN | 1x 2.5 Gbps WAN + 2x 1 Gbps LAN |
| **Slot M.2 WWAN** | Desocupado na PCB | **Módulo Fibocom FM160 (Snapdragon X62 5G)** |
| **Slot Cartão SIM** | Ausente / Não soldado | Slot Nano-SIM / eSIM presente |
| **Estrutura de Backup** | `config.cfg` (tar.gz descompactado) | `config.cfg` (tar.gz descompactado) |

### 🚀 Desbloqueio de Root no X7:
Como a infraestrutura de firmware e backup Web é idêntica, **o script [`unlock_only_ssh.py`](Scripts_Automacao/unlock_only_ssh.py) funciona 1:1 no Predator Connect X7**, permitindo aos donos do X7:
* Obter acesso Root Shell (SSH / Telnet) sem abrir o roteador e sem soldar cabos UART.
* Conversar diretamente com o modem Fibocom FM160 via comandos AT na porta serial `/dev/mhi_at` (bloqueio de bandas 5G, ajuste de TTL / Mangle para planos ilimitados, telemetria de sinal).
* Realizar o dump preventivo das partições de calibração Wi-Fi (`0:ART`) e do sistema.

Para detalhes completos dos binários, GPIOs e scripts do modem 5G, consulte:
👉 **[Documentação da Engenharia Reversa do Modem 5G Fibocom FM160](Engenharia_Reversa_OpenWrt/modem_5g_fibocom_x7/README.md)**

