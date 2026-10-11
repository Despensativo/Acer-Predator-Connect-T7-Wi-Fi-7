# Arquitetura e Engenharia Reversa: Modem 5G Fibocom FM160 (Acer Predator Connect X7)

Este diretório contém os binários, scripts de inicialização, arquivos de configuração e módulos de kernel responsáveis pelo subsistema **5G WWAN** do **Acer Predator Connect X7 5G CPE**, extraídos diretamente da imagem de firmware original (`rootfs` / `QSDK`) compartilhada entre os roteadores **Acer Predator Connect T7** e **X7**.

---

## 📌 Contexto e Descoberta

Embora o **Predator Connect T7** seja comercializado como um roteador Wi-Fi 7 Mesh puro (sem modem celular), a Acer e sua fabricante ODM utilizaram **uma única árvore de código-fonte e o mesmo sistema operacional base** para ambos os dispositivos. 

Em fóruns de desenvolvedores (OpenWrt), confirmou-se que:
> *"O Acer X7 é 99% idêntico ao T7. A única diferença é a presença do modem WWAN Fibocom FM160 no slot M.2 da placa-mãe."*

A perícia forense realizada nos binários originais do T7 comprovou isso de forma definitiva:
* O executável `bin/at_rild` possui chamadas compiladas verificando o fabricante `Fibocom` e executando rotinas proprietárias como `set_fm160_usb_lock` e `AT+GTCELLINFO=1`.
* O Device Tree (`acer_predator_t7.dts`) declara ativamente a controladora PCIe 0 (`pcie@20000000`) com os canais MHI (`rmnet_mhi`), QRTR e GPIOs de controle celular.
* O kernel de fábrica já carrega os módulos de rede celular da Qualcomm (`rmnet_core.ko` e `rmnet_ctl.ko`).

---

## 🛠️ Especificações Técnicas do Modem

| Item | Especificação |
| :--- | :--- |
| **Módulo Celular** | Fibocom FM160 (Série Sub-6 GHz) |
| **SoC do Modem** | Qualcomm Snapdragon X62 5G Modem-RF System (3GPP Rel-16) |
| **Fator de Forma** | M.2 Key B (30x52 mm) |
| **Interface com Host** | PCIe Gen3 x1 via protocolo MHI (*Modem Host Interface*) |
| **Interface Serial AT** | `/dev/mhi_at` (115200 baud, 8N1) |
| **Interface de Dados** | `rmnet_mhi` (MHI IP_HW0) com aceleração por hardware |

---

## 🔌 Mapeamento de GPIOs e Barramento PCIe

Extraído do arquivo de configuração oficial `config/modem-monitor-ipq.conf` e validado contra a árvore de dispositivos do kernel (`DTS`):

| Função | Pino GPIO | Linha no DTS | Descrição |
| :--- | :--- | :--- | :--- |
| **Modem Power On / Reset** | **GPIO 30** | - | Liga/desliga e reseta o módulo M.2 |
| **Modem Status (`MDM2AP`)** | **GPIO 33** (`0x21`) | `mdm2ap-gpio = <0xA 0x21 0x0>` | Sinal de status do modem enviado para o processador IPQ5332 |
| **Host Status (`AP2MDM`)** | **GPIO 34** (`0x22`) | `ap2mdm-gpio = <0xA 0x22 0x0>` | Sinal de controle do processador IPQ5332 para o modem |
| **PCIe Endpoint** | `0000:01:00.0` | `/soc/pcie@20000000` | Barramento PCIe 0 dedicado ao slot M.2 |

---

## 📁 Estrutura dos Arquivos Extraídos

```
modem_5g_fibocom_x7/
├── bin/
│   ├── at_rild                 # Daemon RIL responsável pelo envio de comandos AT ao Fibocom FM160
│   ├── ipqcm                   # Discador celular de dados da Qualcomm (QMI/MHI Connection Manager)
│   ├── modem-monitor           # Watchdog de monitoramento do link PCIe, hotplug e recuperação de falhas
│   ├── modem_datausage         # Contador de consumo de dados móveis
│   ├── modem_fota_tool         # Ferramenta OEM para atualização de firmware (FOTA) do modem
│   ├── modem_readd             # Leitor de telemetria de sinal (RSRP, RSRQ, SINR, bandas ativas)
│   └── qmi_simple_ril          # Camada RIL simplificada via protocolo QMI
├── config/
│   ├── modem                   # Configuração UCI de discagem e conexão automática
│   ├── modem_datausage         # Configuração de limites e franquia de dados
│   ├── modem_info              # Estrutura UCI que armazena IMEI, IMSI, bandas 5G e estado do SIM
│   ├── modem-monitor-ipq.conf  # Configurações de timeout PCIe, ramdump e GPIOs do Snapdragon X62
│   └── ril.json                # Mapeamento da porta serial AT (/dev/mhi_at)
├── init.d/
│   ├── at_ril                  # Script de serviço do daemon AT RIL
│   ├── ipqcm                   # Script de inicialização do discador celular
│   ├── modem-monitor           # Script de monitoramento contínuo do hardware do modem
│   ├── modem_datausage         # Serviço de contagem de franquia
│   ├── modem_read_init         # Inicializador de telemetria (condicionado a dispositivos "cpe")
│   └── ril                     # Serviço RIL complementar
└── kmod/
    ├── rmnet_core.ko           # Driver de kernel para agregação e demultiplexação de pacotes de dados celular
    └── rmnet_ctl.ko            # Driver de controle de mensagens de rede celular Qualcomm
```

---

## 🚀 Desbloqueio e Modding no Acer Predator Connect X7

Por compartilhar a mesma base do T7, donos do **Acer Predator Connect X7** podem aplicar o mesmo método de Root Shell Unlock sem abrir o aparelho:

1. Fazer backup do arquivo `.cfg` pelo painel Web (`192.168.76.1`).
2. Executar o script `Scripts_Automacao/unlock_only_ssh.py config.cfg`.
3. Restaurar o arquivo `config_ssh_unlocked.cfg` pela interface Web da Acer.
4. Conectar via SSH: `ssh Admin@192.168.76.1`.

### Comandos AT Úteis via Terminal no X7:
Uma vez com acesso root no X7, é possível conversar diretamente com o módulo Fibocom através da interface serial:
```bash
# Acessar console interativo AT do Fibocom FM160:
microcom -t 5000 /dev/mhi_at

# Comandos de diagnóstico:
ATI                 # Exibe modelo e revisão de firmware do FM160
AT+CGMI             # Exibe fabricante (Fibocom)
AT+CPIN?            # Verifica status do cartão SIM
AT+GTCELLINFO?      # Exibe métricas detalhadas das células 4G/5G conectadas
AT+GTRAT?           # Exibe e permite travar modos de rede (ex: forçar apenas 5G SA)
```
