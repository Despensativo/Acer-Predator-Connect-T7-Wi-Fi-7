# Acer Predator Connect T7 - Desbloqueio, Modo Access Point 2.5 Gbps & Wi-Fi 7

> **Resumo Executivo**: Documentação completa da transformação do roteador gamer **Acer Predator Connect T7** (Qualcomm IPQ5332 Wi-Fi 7) em um **Ponto de Acesso (AP) / Switch de 2.5 Gbps de altíssima performance**, sem duplo NAT, com desbloqueio permanente de terminal Root (SSH / Telnet), canais de rádio otimizados e backups de baixo nível para recuperação de desastre.

---

## 1. Dados e Credenciais da Rede

| Parâmetro | Configuração Ativa | Detalhes |
| :--- | :--- | :--- |
| **Endereço IP do Roteador** | `192.168.73.2` | IP estático na rede local |
| **Máscara de Sub-rede** | `255.255.255.0` (`/24`) | Sub-rede única com o roteador principal |
| **Gateway / DNS** | `192.168.73.1` | Roteador Mestre (Cudy WR3000) |
| **Servidor DHCP** | **Desativado** | Evita duplo NAT; todos os IPs vêm do Mestre |
| **Porta WAN (2.5 Gbps)** | Em Bridge com LAN | Tráfego de 2 Gbps flui sem gargalo |
| **Usuário do Painel Web** | `Admin` | Senha configurada pelo usuário |
| **Usuário Terminal (SSH / Telnet)** | `Admin` ou `root` | UID 0 (Superusuário completo) |
| **Acesso Telnet (Sem senha)** | Porta `23` | `telnet 192.168.73.2` |
| **Acesso SSH (Criptografado)** | Porta `22` | `ssh -o HostKeyAlgorithms=+ssh-rsa Admin@192.168.73.2` |

---

## 2. Configuração dos Rádios e Redes Wi-Fi

| Rádio | Frequência | SSID | Canal Travado | Largura | Potência | Finalidade |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`wifi0`** | 2.4 GHz | **`CASA_ARK`** | **1** | **`HT20` (20 MHz)** | 25 dBm | Máxima penetração de paredes e alcance (25m) |
| **`wifi0`** | 2.4 GHz | **`TV casa`** | **1** | **`HT20` (20 MHz)** | 25 dBm | Na bridge `lan` principal (espelhamento liberado) |
| **`wifi1`** | 5 GHz | **`CASA_ARK_5G`** | **36** | **`HT160` (160 MHz)** | 25 dBm | Mais de 1.5 a 2 Gbps sem risco de queda por radar DFS |
| **`wifi2`** | 6 GHz | **`CASA_ARK_6G`** | **37 (PSC)** | **`HT320` (320 MHz)** | 25 dBm | Wi-Fi 7 ultra-rápido no canal de varredura preferencial |
| **MLD** | 5G + 6G | **`CASA_ARK_7G`** | MLO Agregado | 160 + 320 MHz | 25 dBm | **Wi-Fi 7 Multi-Link Operation** ativo em hardware |

*Todas as redes utilizam a senha:* `Casa0100@`

---

## 3. Comandos Rápidos de Acesso

### Acesso Instantâneo via Telnet (Recomendado na LAN):
No Prompt de Comando ou PowerShell do Windows:
```powershell
telnet 192.168.73.2
```
*Você cai direto no terminal de superusuário (`/ #`) sem necessidade de senha.*

### Acesso via SSH:
```powershell
ssh -o HostKeyAlgorithms=+ssh-rsa Admin@192.168.73.2
```
*(ou `ssh -o HostKeyAlgorithms=+ssh-rsa root@192.168.73.2`, utilizando a sua senha de Admin).*

---

## 4. Estrutura deste Repositório

```text
Acer-Predator-Connect-T7/
├── Backups_MTD/                                 # [CRÍTICO] Imagens brutas da memória Flash
│   ├── backup_predator_t7_art.bin               # Calibração Wi-Fi 7 (Atheros Radio Test - 2 MB)
│   ├── backup_predator_t7_uboot_env.bin         # Variáveis do Bootloader U-Boot (512 KB)
│   ├── backup_predator_t7_ethphy_fw.bin         # Firmware do chip 2.5 Gbps Ethernet PHY (1 MB)
│   ├── backup_predator_t7_license.bin           # Licença e números de série do fabricante (256 KB)
│   ├── backup_predator_t7_devcfg.bin            # Configuração de dispositivo Qualcomm (512 KB)
│   └── backup_predator_t7_cdt.bin               # Tabela de dados de plataforma CDT (512 KB)
│
├── Configuracoes_Roteador/                      # Arquivo .cfg pronto para restauração Web
│   └── config_ap_ssh_unlocked_template.cfg      # Template público ativo (AP + Wi-Fi 7 + SSH + Canais)
│
├── Engenharia_Reversa_OpenWrt/                  # [DEV] Kit de portabilidade para o OpenWrt Oficial
│   ├── acer_predator_t7.dts                     # Árvore de dispositivos (Device Tree) DESCOMPILADA (97 KB)
│   ├── acer_predator_t7.dtb                     # Binário original montado pelo kernel (/sys/firmware/fdt)
│   ├── ipq5332_wifi_fw.tar.gz                   # Pacote de firmwares Wi-Fi 7 Qualcomm IPQ5332 (4.3 MB)
│   ├── gpio_table.txt                           # Tabela e mapa de pinos digitais GPIO
│   ├── board.json                               # Definição OpenWrt de modelo e portas de rede
│   ├── switch_config.txt                        # Configuração do switch gigabit integrado
│   ├── loaded_modules.txt                       # Módulos de kernel carregados (NSS, PPE, drivers)
│   └── README_PORT_OPENWRT.md                   # Guia passo a passo para criar o Target no OpenWrt
│
├── Scripts_Automacao/                           # Utilitários Python
│   ├── unlock_only_ssh.py                       # Script para destravar SOMENTE SSH/Telnet em qualquer backup
│   ├── build_ssh_unlocked.py                    # Script que compilou a injeção do SSH e canais
│   └── test_router_access.py                    # Diagnóstico rápido de portas, temperatura e Wi-Fi
│
├── README.md                                    # Este documento
├── COMO_EDITAR_CFG_E_LIBERAR_SSH.md             # Guia: como editar o .cfg e destravar apenas SSH/Telnet
├── GUIA_TECNICO_DESBLOQUEIO_E_AP.md             # Passo a passo da engenharia reversa e modificações
├── MAPA_HARDWARE_E_PARTICOES.md                 # Tabela MTD, Dual-Boot e parâmetros do U-Boot
└── RECUPERACAO_E_DESASTRE_UNBRICK.md            # Guia de recuperação de emergência (TFTP)
```
