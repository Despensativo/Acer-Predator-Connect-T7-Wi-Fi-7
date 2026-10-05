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
* 📶 **Wi-Fi 7 Turbo & Acelerações de Protocolo:** Rádio 6 GHz em 320 MHz (5.76 Gbps) com Preamble Puncturing (anti-interferência), Target Wake Time (TWT - economia de bateria em celulares), BSS Coloring, Beamforming 4x4, OFDMA e Roaming Rápido 802.11k/v/r (<50ms).
* ⚖️ **Calibração Multicore RPS (4 CPUs):** Filas de pacotes da porta 2.5 Gbps distribuídas em paralelo pelos 4 núcleos do SoC Qualcomm IPQ5332 com buffers TCP expandidos para 8 MB.
* ⚡ **Parallel Turbo DNS (All-Servers):** Resolução DNS em paralelo no dnsmasq para respostas instantâneas (0 ms).
* 🧹 **Debloat Severo:** Daemons celulares 5G inexistentes (`at_ril`, `modem_readd`), telemetrias pesadas (`monitord`, `sodd`, `cwmp`, `breakpad`) e Samba desativados, liberando **+50 MB de memória RAM**.
* 💾 **Central de Backup de 1 Clique:** Utilitário interativo `RESTAURAR_OU_BACKUP_T7.bat` para restauração e snapshot em segundos.

---

> [!IMPORTANT]
> ### ⚠️ Endereços IP, Credenciais e a Regra de Ouro de Senhas:
> * **IP Padrão de Fábrica (Stock Default):** **`192.168.76.1`** (Modo Roteador tradicional com DHCP ativo na faixa `192.168.76.x`).
> * **IP em Modo AP de Alta Performance:** **`192.168.73.2`** (Opera como Switch L2 / AP na rede do roteador principal `192.168.73.1`, com DHCP desativado).
> * **🔑 Credenciais Padrão Unificadas:**
>   - **Usuário:** **`root`** (ou **`Admin`**)
>   - **Senha:** **`root`**
>   - **Interface LuCI Web (Porta 80):** `http://192.168.76.1` (ou `73.2`) | Usuário: `root` | Senha: `root`
>   - **Acesso SSH (Porta 22):** `ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.76.1` (Senha: `root`)
>   - **Acesso de Emergência (Zero Risco de Trancar Fora):** O **Telnet na porta 23** (`telnet 192.168.76.1 23`) conecta direto ao shell `ash` como root **sem pedir senha**.
> * **🛡️ Regra de Ouro ao Alterar Senhas:**
>   - **JAMAIS apague ou renomeie os usuários `root` ou `Admin`.** Ambos compartilham UID 0. Tarefas agendadas do cron e daemons da Acer dependem de `Admin`, enquanto o OpenWrt/LuCI espera `root`.
>   - **Se você for alterar a senha pelo terminal, atualize SEMPRE OS DOIS usuários para mantê-los sincronizados:**
>     ```sh
>     passwd root
>     passwd Admin
>     ```

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

## 4. 🚀 Assistente Interativo Universal & One-Liner PowerShell (Windows, macOS e Linux)

Para garantir que qualquer pessoa consiga operar o roteador sem erros — mesmo em um computador recém-formatado —, disponibilizamos um assistente inteligente com **triagem guiada de root, gerador automático de `.cfg` e Pre-Flight Check**:

### ⚡ Método Mais Rápido (1 Linha no Windows — Sem Baixar Nada Manualmente):
Abra o **PowerShell** no Windows e cole o comando oficial:
```powershell
irm https://raw.githubusercontent.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/main/iniciar.ps1 | iex
```

### Outras Formas de Executar (Se já clonou ou baixou o repositório):
* **No Windows:** Dê duplo clique em **`EXECUTAR_T7.bat`** (ou execute `.\iniciar.ps1` no PowerShell).  
  *(Totalmente compatível com "Executar como Administrador" sem perder os caminhos).*
* **No macOS e Linux:** Abra o terminal na pasta e execute:
  ```bash
  sh executar_t7.sh
  ```

---

### 🧭 Como Funciona a Triagem do Assistente:

1. **Seleção de Idioma:** Escolha Inglês (padrão ao apertar ENTER) ou Português (Brasil).
2. **Sonda Automática:** O script localiza o IP do roteador e inspeciona se as portas Web (80), Telnet (23) e SSH (22) estão abertas.
3. **Pergunta de Triagem Inicial:**
   > *"Você já possui acesso ROOT / SSH liberado no roteador?"*
   * **Se responder NÃO (Roteador travado de fábrica):**
     - O assistente gera o arquivo **`config_desbloqueio_t7.cfg`** direto na sua **Área de Trabalho**.
     - Abre seu navegador automaticamente na tela de restauração do painel da Acer.
     - Explica onde clicar para enviar o backup e ativar o root em 1 minuto.
     - Monitora ativamente a reinicialização e confirma quando a porta Telnet abrir com sucesso!
   * **Se responder SIM (Já desbloqueado):**
     - Confere o ambiente Python 3.14 (se faltar, instala silenciosamente via WinGet em 1 clique).
     - Abre a **Central de Gerenciamento** com Pre-Flight Check, gravação do Slot 2, ativação do LuCI, Dual-Boot e Hardening.

---

## 5. 🔒 Hardening Pós-Instalação: Como Desativar o Telnet

O **Telnet (porta 23)** vem ativado no desbloqueio para garantir que qualquer computador (mesmo sem chaves SSH cadastradas) consiga se comunicar com o roteador sem erros de autenticação ou certificados. Ele opera **estritamente na rede local (LAN)** e é 100% bloqueado na WAN pelo firewall.

Se após concluir sua instalação e testar o LuCI você desejar desativar o Telnet para manter apenas conexões SSH criptografadas:
* **No terminal do roteador:** digite apenas:
  ```sh
  desativar-telnet
  ```
  *(Para reativar no futuro caso precise rodar automações, basta digitar: `ativar-telnet`)*.
* **Pelo computador:** execute a opção [5] no launcher ou rode:
  ```bash
  python Scripts_Automacao/gerenciar_telnet.py desativar
  ```

---

## 6. 🔗 Protocolo de Pesquisa e Termos de Teste: Acer Predator Connect X7 (5G CPE)

O **Acer Predator Connect X7** possui arquitetura muito similar ao T7, porém conta com um modem celular 5G (Qualcomm Snapdragon X62) em slot interno e firmware oficial `v50`.

> [!WARNING]
> **TRAVA ANTI-BRICK ATIVA:** As imagens da versão 27 (`v27`) contidas neste repositório são **EXCLUSIVAS do Predator Connect T7**. A gravação direta dessas imagens no X7 causará **BRICK**. Por essa razão, a gravação no X7 está bloqueada no código.

### Como Colaborar com os Testes do X7:
1. **Diagnóstico Seguro:** Execute a opção `[7] Area de Pesquisa e Diagnostico do Modelo X7` no launcher (`python Scripts_Automacao/diagnostico_x7.py`) para gerar um relatório somente-leitura do seu aparelho.
2. **Envio do Backup (.cfg):** O usuário com X7 precisará compartilhar seu arquivo de backup `.cfg` original para auditoria dos serviços do modem.
3. **Disposição para Testes em Bancada:** Testes em hardware híbrido exigem acompanhamento cauteloso.
4. **Alta Recuperabilidade:** Assim como no T7, o X7 utiliza particionamento redundante Dual-Boot A/B. **Desde que a Partição 1 (Slot 1 original) NÃO seja sobrescrita ou forçada após obter o root, a chance de recuperação e chaveamento seguro de volta para o sistema original é altíssima!**

---

<p align="center">
  <b>Desenvolvido pela Comunidade OpenWrt & Engenharia Reversa Independente</b><br>
  Licença MIT — Livre para modificação e aprimoramento.
</p>
