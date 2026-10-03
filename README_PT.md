<p align="center">
  <img src="assets/acer-predator-t7-banner.jpg" alt="Acer Predator Connect T7 Wi-Fi 7 Banner" width="100%">
</p>

<p align="center">
  <b>🌐 Idioma / Language:</b>
  <a href="README_PT.md"><b>🇧🇷 Português (Brasil)</b></a> |
  <a href="README.md">🇺🇸 English</a>
</p>

# Acer Predator Connect T7 — Desbloqueio Root, Modo AP 2.5 Gbps, Wi-Fi 7 & Arquitetura Dual-Boot

> **Status do Projeto (Outubro / 2026)**: Roteador operando em produção no **Slot 2 (`rootfs_1`)** com **Firmware Oficial v1.01.000027 (v27)**, interface **LuCI nativa na Porta 80**, aceleração de switch **Layer-2 a 2.5 Gbps puro**, **Wi-Fi 7 (320 MHz / 5.76 Gbps)** com Roaming 802.11k/v e debloat total de telemetrias. **Slot 1 (`rootfs`) mantido 100% intacto como salvaguarda anti-brick**.

> **Keywords / SEO**: Acer Predator Connect T7, Wi-Fi 7 router unlock, Qualcomm IPQ5332, MLO 6GHz, AP Mode 2.5Gbps, root access dropbear, telnet unlock, unbrick predator t7, openwrt predator t7, double NAT fix, dual-boot slot rollback, firmware dump MTD.

---

## ⚡ Sumário Rápido de Recursos Ativos

* 🛡️ **Dual-Boot A/B Seguro:** O Slot 1 (`mtd21` / v24) é uma reserva de fábrica intocável. Todas as customizações rodam no Slot 2 (`mtd20` / v27).
* 🔄 **Rollback em 1 Comando:** Se o Slot 2 apresentar qualquer falha, o comando `/usr/sbin/boot-acer` restaura o boot para o Slot 1 instantaneamente.
* 🌐 **LuCI Nativo na Porta 80:** Servidor web da Acer (`lighttpd`) desativado; LuCI (`uhttpd`) promovido a servidor principal.
* 🚀 **Switch 2.5 Gbps Puro (Modo AP):** Bypass de netfilter na ponte (`net.bridge.bridge-nf-call-iptables = 0`), eliminando drops de DHCP, mDNS, AirPlay e entregando throughput L2 de velocidade de fio.
* 📶 **Wi-Fi 7 Otimizado:** Rádio 6 GHz em 320 MHz (5.76 Gbps), Roaming Rápido 802.11k/v (BSS Transition + RRM) e DTIM=2.
* 🧹 **Debloat Severo:** Daemons celulares 5G inexistentes (`at_ril`, `modem_readd`), telemetrias pesadas (`monitord`, `sodd`, `cwmp`, `breakpad`) e Samba desativados, liberando **+50 MB de memória RAM**.
* 💾 **Central de Backup de 1 Clique:** Utilitário interativo `RESTAURAR_OU_BACKUP_T7.bat` para restauração e snapshot em segundos.

---

> [!IMPORTANT]
> ### ⚠️ Endereços IP, Credenciais e Regras de Senha:
> * **IP Padrão de Fábrica (Stock Default):** **`192.168.76.1`** (Modo Roteador tradicional com DHCP ativo na faixa `192.168.76.x`).
> * **IP em Modo AP de Alta Performance:** **`192.168.73.2`** (Opera como Switch L2 / AP na rede do roteador principal `192.168.73.1`, com DHCP desativado).
> * **🔐 Qual senha vai ficar após o desbloqueio?**
>   - **Se você usou seu próprio backup (`unlock_only_ssh.py`):** A senha do `Admin` e do `root` é **EXATAMENTE A MESMA** que você já usava para entrar na página da Acer! Suas redes Wi-Fi continuam 100% iguais.
>   - **Se você restaurou um backup de exemplo ou imagem do repositório:** A senha padrão de fábrica é **`admin0100`**.
>   - **Acesso de Emergência (Zero Risco de Trancar Fora):** O **Telnet na porta 23** (`telnet 192.168.76.1 23`) conecta direto ao shell `ash` como root **sem pedir senha**. Se esquecer sua senha, basta conectar via Telnet e digitar `passwd root`.
> * **Interface LuCI Web (Porta 80):** `http://192.168.76.1` (ou `73.2`) | Usuário: `root` ou `Admin`.
> * **Acesso SSH (Porta 22):** `ssh -o HostKeyAlgorithms=+ssh-rsa Admin@192.168.76.1` (ou `root@...`).

---

## 1. 🛡️ Arquitetura Dual-Boot A/B e Salvaguarda Anti-Brick

O Acer Predator Connect T7 possui uma memória flash SPI NAND de 1 GB com **particionamento duplo redundante (Slots A e B)** gerenciado pelo SoC Qualcomm IPQ5332.

```
       +-----------------------------------------------------------+
       |                  MEMÓRIA FLASH NAND (1 GB)                |
       +-----------------------------------------------------------+
                                     |
           +-------------------------+-------------------------+
           |                                                   |
     [SLOT 1 - A]                                        [SLOT 2 - B]
  Partição: mtd21 (rootfs)                           Partição: mtd20 (rootfs_1)
  Estado: INTATO / RESERVA DE FÁBRICA                Estado: ATIVO EM PRODUÇÃO
  Firmware: v1.01.000024 OEM                         Firmware: v1.01.000027 Otimizado
  Função: Salvaguarda Anti-Brick                     Função: LuCI Porta 80 + Wi-Fi 7 AP
```

### O que controla qual slot inicializa?
O U-Boot lê as partições **`mtd3` (`0:BOOTCONFIG`)** e **`mtd4` (`0:BOOTCONFIG1`)**. Dentro delas existe a variável binária `primaryboot`:
* `primaryboot = 1`: O roteador inicializa o Slot 1 (`mtd21`).
* `primaryboot = 2`: O roteador inicializa o Slot 2 (`mtd20`).

---

### 🚨 O que fazer se o Slot 2 for corrompido ou quebrar?

#### Cenário A: O roteador ainda responde via terminal (Telnet ou SSH)
Se você estiver no Slot 2 e quiser voltar para o Slot 1 de fábrica a qualquer momento:
1. Digite um único comando no terminal:
   ```sh
   /usr/sbin/boot-acer
   ```
2. O script regrava automaticamente `primaryboot = 1` nas partições `mtd3` e `mtd4`, sincroniza a memória flash e reinicia o roteador diretamente no **Slot 1 (OEM intacto)**.

*(Alternativa no Windows: basta rodar o script Python [`04_SCRIPTS_E_FERRAMENTAS/Automacao_e_Unlock/executar_chaveamento_slot1_recovery.py`](04_SCRIPTS_E_FERRAMENTAS/Automacao_e_Unlock/executar_chaveamento_slot1_recovery.py)).*

#### Cenário B: O Roteador NÃO Inicializa (Brick, Loop de Boot ou Sem Rede)
* **A Realidade da UART e do Watchdog:** Os pads de teste da UART na placa vêm cobertos de fábrica por máscara de solda preta (sem pinos nem estanho exposto), e o watchdog da Qualcomm muitas vezes congela se o kernel travar no início do init.
* **A Solução Definitiva de Hardware (Modo Failsafe Web no IP `192.168.1.1`):**
  1. Desligue a fonte da tomada.
  2. Pressione e mantenha o **botão físico WPS** pressionado na carcaça.
  3. Ligue a fonte mantendo o **WPS pressionado por 5 a 10 segundos** até os LEDs piscarem no padrão de recuperação.
  4. O U-Boot sobe uma **Página Web de Emergência no IP `http://192.168.1.1`**.
  5. Fixe o IP do seu PC em `192.168.1.66` (máscara `255.255.255.0`, gateway `192.168.1.1`).
  6. Acesse `http://192.168.1.1` pelo navegador e envie o arquivo `.itb` desejado:
     * **[`restaurar_slot1_acer.itb`](02_BACKUPS_E_DUMPS/Imagens_Recuperacao_WPS_Failsafe/restaurar_slot1_acer.itb):** Regrava a NAND e reinicia direto no **Slot 1 (OEM v24 de fábrica)**.
     * **[`chavear_slot2_acer.itb`](02_BACKUPS_E_DUMPS/Imagens_Recuperacao_WPS_Failsafe/chavear_slot2_acer.itb):** Regrava a NAND e reinicia no **Slot 2 (v27 LuCI)**.
  *O U-Boot descompacta o arquivo na memória RAM, regrava a partição `BOOTCONFIG` e reinicia no slot selecionado em menos de 1 minuto, sem cabos seriais e sem abrir o aparelho!*

#### Cenário C: Como reinstalar o Slot 2 do zero (Reflash Limpo)
Se o sistema de arquivos do Slot 2 for apagado ou danificado:
1. Inicialize no Slot 1.
2. Execute o script de gravação direta via rede:
   ```powershell
   python "04_SCRIPTS_E_FERRAMENTAS\Automacao_e_Unlock\gravar_v27_slot2.py"
   ```
3. Ele regrava a imagem oficial v27 na partição `mtd20`, define `primaryboot = 2` e reinicia no Slot 2 novo em folha!

---

## 2. 🚀 Configuração de Alta Performance (Modo Access Point 2.5 Gbps)

Para transformar o roteador em um ponto de acesso sem gargalos de rede:

| Parâmetro | Padrão Stock | Modo AP Otimizado | Benefício Técnico |
| :--- | :--- | :--- | :--- |
| **Porta WAN (2.5G)** | Roteamento NAT L3 | Integrada na `br-lan` | As 3 portas físicas viram um switch unificado de 2.5 Gbps |
| **Bypass de Netfilter** | `iptables = 1` | `sysctl net.bridge.bridge-nf-call-iptables=0` | Zero drops de DHCP/mDNS/AirPlay; comutação Layer-2 a velocidade de fio |
| **Servidor DHCP** | Ativo (Pool 76.x) | Desativado | Sem duplo NAT; IP distribuído pelo roteador mestre |
| **Cache DNS** | 150 registros | 10.000 registros (TTL min 300s) | Resposta de resolução DNS instantânea (0 ms) |
| **Tabela Conntrack**| 16.384 conexões | 65.536 conexões (timeout 7440s) | Estabilidade para centenas de conexões P2P e torrents |
| **TCP Fast Open** | Desativado | Ativado (`tcp_fastopen = 3`) | Aceleração de abertura de páginas web e APIs |
| **UPnP Gamer** | Básico | `miniupnpd` com NAT-PMP e IGDv1 | NAT Tipo 1 / Aberto automático no PS5, Xbox e PC |

---

## 3. 📶 Canais de Rádio e Ajustes Finos de Wi-Fi 7

| Rádio | Frequência | SSID | Canal / Largura | Taxa Física | Roaming / Recursos |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`wifi2`** | 6 GHz | **`CASA_ARK_7G`** | Auto / **`HT320` (320 MHz)** | **5.7648 Gb/s** | WPA3-SAE, PMF Obrigatório, 802.11k/v, DTIM=2 |
| **`wifi1`** | 5 GHz | **`CASA_ARK_5G`** | Auto / **`HT80` (80 MHz)** | **1.44 Gb/s** | 4 Antenas Beamforming (8.38 dBi), 802.11k/v, DTIM=2 |
| **`wifi0`** | 2.4 GHz | *(Opcional / IoT)* | Auto / `HT20` | 688 Mb/s | WPA2-PSK AES (Compatibilidade legada universal) |

> [!NOTE]
> **Sobre a Potência de Transmissão (dBm):** O rádio de 5 GHz já opera no teto físico de seus amplificadores (~27.3 dBm conduzido / ~35 dBm EIRP com beamforming). O rádio de 6 GHz é calibrado de fábrica sob a máscara regulatória internacional LPI (Low Power Indoor - 5 dBm/MHz). Tentar forçar dBm mais alto no software em canais de 320 MHz satura os amplificadores e gera distorção de constelação (EVM) no 4096-QAM, derrubando a velocidade real. A calibração de fábrica já entrega o limiar perfeito.

---

## 4. 💾 Central de Backup e Restauração em 1 Clique

Disponibilizamos um painel interativo no Windows para que você nunca perca suas configurações:

👉 **Execute no Windows:** `RESTAURAR_OU_BACKUP_T7.bat`

```text
===========================================================================
      CENTRAL DE BACKUP E RESTAURAÇÃO - ACER PREDATOR CONNECT T7
            Firmware v27 (Slot 2) - Wi-Fi 7 + LuCI Porta 80
===========================================================================

  [1] RESTAURAR VIA SCRIPT INTELIGENTE (Recomendado)
      - Reaplica Wi-Fi 7 (CASA_ARK_7G / 320MHz), 5GHz, Modo AP (192.168.73.2)
      - Desativa DHCP e integra portas em Switch L2 em 5 segundos

  [2] RESTAURAR CLONE COMPLETO DO OVERLAY (.tar.gz)
      - Restaura 100% da memoria Flash NAND (senhas, LuCI, sysctl, scripts)
      - Ideal se o roteador foi resetado pelo botao fisico Reset

  [3] GERAR NOVO BACKUP DO ROTEADOR PARA O COMPUTADOR
      - Baixa automaticamente o snapshot do Overlay e Sysupgrade atualizados

  [4] ABRIR PAINEL LUCI NO NAVEGADOR (http://192.168.73.2)

  [5] ABRIR TERMINAL TELNET NO ROTEADOR (root / admin0100)

  [0] SAIR
===========================================================================
```

Os backups gerados ficam salvos localmente na pasta:
📂 **[`02_BACKUPS_E_DUMPS/Backups_Configuracao_Pessoal/`](02_BACKUPS_E_DUMPS/Backups_Configuracao_Pessoal/)**

---

## 5. 📁 Estrutura Atualizada do Repositório

```text
Acer-Predator-Connect-T7/
├── INDEX.md                                     # [GROUND TRUTH] Mapa executivo e especificações críticas
├── CHANGELOG_BUILDS.md                          # Matriz consolidada de versões e status de testes
├── README.md                                    # Apresentação do projeto e guia mestre
├── RESTAURAR_OU_BACKUP_T7.bat                   # Central interativa de backup e restauração (Windows)
│
├── 01_FIRMWARES_E_IMAGENS/                      # Imagens de firmware e RootFS
│   ├── OpenWrt_Imagens/                         # Imagens FIT (.itb), sysupgrade e initramfs
│   └── Custom_SquashFS/                         # Imagens extraídas e modificadas de RootFS
│
├── 02_BACKUPS_E_DUMPS/                          # Imagens da Flash e snapshots de configuração
│   ├── Backups_Configuracao_Pessoal/            # Backups Overlay .tar.gz e runners .bat rápidos
│   ├── MTD_Full_Dumps/                          # Dumps 1:1 de fábrica (ART, APPSBL, Kernel, SBL)
│   └── Configuracoes_CFG/                       # Backups .cfg da interface OEM
│
├── 03_ENGENHARIA_REVERSA/                       # Análise técnica aprofundada
│   ├── DeviceTree_DTS/                          # DTS e DTB descompilados da placa
│   ├── Modulos_Kernel_QSDK/                     # Drivers de aceleração PPE, NSS, ECM (Linux 5.4)
│   ├── Modem_5G_Fibocom_X7/                     # Engenharia reversa dos binários celulares e RIL
│   ├── Homologacao_FCC/                         # Relatórios FCC e fotos forenses do circuito PCB
│   └── Desmontagem_U-Boot/                      # Scripts de análise estática do bootloader
│
├── 04_SCRIPTS_E_FERRAMENTAS/                    # Ferramental de Automação
│   ├── Automacao_e_Unlock/                      # Scripts mestre de otimização, debloat, AP e rollback
│   │   ├── otimizar_e_ativar_luci_slot2.py      # Suite global de debloat, LuCI porta 80 e kernel
│   │   ├── aplicar_configuracao_pessoal_ap_t7.py# Injetor declarativo do modo AP Wi-Fi 7
│   │   ├── restaurar_backup_pessoal.py          # Restaurador de snapshot do overlay em 10s
│   │   ├── gerar_backup_pessoal.py              # Extrator de backup automático para o PC
│   │   ├── executar_chaveamento_slot1_recovery.py# Forçador de boot de volta para o Slot 1
│   │   └── gravar_v27_slot2.py                  # Gravador de firmware limpo no Slot 2
│   ├── Diagnostico_de_Rede/                     # Scanners ARP, ouvintes DHCP e monitores de ping
│   └── Servidor_TFTP/                           # Utilitários TFTP para Windows
│
├── 05_COMPILADORES/                             # Ferramentas de compilação
│   └── SquashFS_QSDK_T7/                        # mksquashfs e unsquashfs (256k XZ)
│
├── 06_DOCUMENTACAO/                             # Documentação técnica em camadas
│   ├── PROCEDIMENTOS/                           # Guias operacionais passo a passo (00 a 08)
│   └── NOTAS_HARDWARE/                          # Análises de particionamento, FOTA e TrustZone
│
└── assets/                                      # Banners e diagramas do projeto
```

---

## 6. 🔗 Irmão Gêmeo: Compatibilidade com o Acer Predator Connect X7 5G CPE

O roteador **Acer Predator Connect X7 5G CPE** compartilha **99% do mesmo hardware e código-fonte base** com o **Predator Connect T7** (SoC Qualcomm IPQ5332, kernel 5.4.213, mesmo particionamento MTD e rádios Wi-Fi 7 BE11000). A única diferença física é que o X7 possui um modem Fibocom FM160 (Snapdragon X62 5G) instalado em um slot M.2 interno.

Os scripts de desbloqueio root ([`unlock_only_ssh.py`](04_SCRIPTS_E_FERRAMENTAS/Automacao_e_Unlock/unlock_only_ssh.py)) funcionam 1:1 no X7 sem modificação.

Para detalhes completos dos binários, pinagem GPIO e engenharia reversa do modem 5G, consulte:
👉 **[Documentação da Engenharia Reversa do Modem 5G Fibocom FM160](03_ENGENHARIA_REVERSA/Modem_5G_Fibocom_X7/README.md)**

---

<p align="center">
  <b>Desenvolvido pela Comunidade OpenWrt & Engenharia Reversa Independente</b><br>
  Licença MIT — Livre para modificação e aprimoramento.
</p>
