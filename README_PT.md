<p align="center">
  <img src="assets/acer-predator-t7-banner.jpg" alt="Acer Predator Connect T7 Wi-Fi 7 Banner" width="100%">
</p>

<p align="center">
  <b>🌐 Idioma / Language:</b>
  <a href="README_PT.md"><b>🇧🇷 Português (Brasil)</b></a> |
  <a href="README.md">🇺🇸 English</a>
</p>

# Acer Predator Connect T7 — Desbloqueio Root, LuCI Nativo, Wi-Fi 7 & Arquitetura Dual-Boot

> **Status do Projeto (Outubro / 2026)**: Roteador operando em produção no **Slot 2 (`rootfs_1`)** com **Firmware Oficial v1.01.000027 (v27)**, interface **LuCI nativa na Porta 80**, **Wi-Fi 7 (320 MHz / 5.76 Gbps)** com Roaming 802.11k/v e debloat total de telemetrias. **Slot 1 (`rootfs`) e U-Boot mantidos 100% intactos de fábrica como salvaguarda anti-brick definitiva**.

> **Keywords / SEO**: Acer Predator Connect T7, Wi-Fi 7 router unlock, Qualcomm IPQ5332, MLO 6GHz, root access dropbear, telnet unlock, unbrick predator t7, openwrt predator t7, dual-boot slot rollback, firmware dump MTD.

> ⚠️ **AVISO CRÍTICO**: **NÃO** execute os scripts de automação ou o processo de otimização conectado via rede Wi-Fi. Modificar interfaces de rede durante o processo derrubará sua conexão no meio da operação, o que pode corromper a instalação. **Utilize sempre um cabo de rede (Ethernet) durante todo o uso da central.**

---

## ⚡ INSTALAÇÃO RÁPIDA (AMBIENTE HOMOLOGADO & TESTADO)

> [!IMPORTANT]
> ### 💻 AMBIENTE RECOMENDADO: WINDOWS + POWERSHELL
> Todo o ecossistema de automação, injeção de arquivos `.cfg`, detecção de portas e gravação de memória flash foi **exaustivamente testado, validado e homologado no ambiente Windows com PowerShell**.  
> Para garantir **100% de sucesso e zero risco de falhas**, utilize um computador com Windows conectado via cabo de rede diretamente ao roteador.

### 🚀 Método Oficial (1 Linha no PowerShell — Sem Baixar Nada Manualmente):
Abra o **PowerShell** no seu Windows (como Usuário ou Administrador) e cole o comando oficial abaixo:

```powershell
irm https://raw.githubusercontent.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/main/iniciar.ps1 | iex
```

#### 📦 O que este comando faz automaticamente:
1. **Configura o Ambiente:** Baixa e organiza as ferramentas na pasta `Desktop\Acer-Predator-Connect-T7`.
2. **Garante o Python 3.14:** Detecta se o Python está presente; se não estiver, instala de forma silenciosa via WinGet e configura o `PATH` do sistema.
3. **Diagnóstico em Tempo Real:** Escaneia a rede, encontra o IP do seu Predator T7 e verifica se as portas Web (80), Telnet (23) e SSH (22) estão ativas.
4. **Fluxo Inteligente:**
   * **Se o roteador estiver travado de fábrica:** Gera na sua Área de Trabalho o arquivo de desbloqueio `.cfg`, abre a página de restauração no navegador e aguarda a reinicialização.
   * **Se o roteador já estiver liberado:** Abre direto a **Central de Gerenciamento Interativa** para gravação do Slot 2, ativação do LuCI, chaveamento de boot ou gerenciamento de Telnet.
5. **Geração Automática de Logs (`LOG_PREDATOR_T7.txt`):** Todas as etapas, verificações de portas e comandos executados são gravados em tempo real no arquivo `Desktop\LOG_PREDATOR_T7.txt`. Se você encontrar qualquer erro ou comportamento inesperado, basta compartilhar esse arquivo para suporte imediato!

---

### 📂 Alternativa Offline (Caso já tenha clonado ou baixado o repositório):
Se você já baixou o arquivo `.zip` ou clonou o repositório para o seu computador:
* **No Windows:** Dê duplo clique diretamente no arquivo **`EXECUTAR_T7.bat`** (ou execute `.\iniciar.ps1` no PowerShell).  
  *(Totalmente compatível com "Executar como Administrador" sem perder pastas ou caminhos).*

---

## 🔑 Endereços IP, Credenciais Unificadas e Redes Wi-Fi

As credenciais do ecossistema são **100% unificadas** entre o backup de desbloqueio `.cfg` (Slot 1) e a **ROM OpenWrt Custom** (Slot 2):

| Parâmetro | Configuração Padrão (.cfg Desbloqueio & ROM Custom Slot 2) |
| :--- | :--- |
| **Endereço IP LAN** | **`192.168.76.1`** (Padrão Oficial) |
| **Interface Web (Porta 80)** | **`http://192.168.76.1/`** (LuCI Nativo no Slot 2 / OEM Web no Slot 1) |
| **Usuário Web / SSH** | **`root`** (ou **`Admin`** na Web OEM) |
| **Senha do Sistema / Root** | **`root0100`** (Senha única unificada para Web, SSH e Telnet) |
| **Porta SSH (Terminal)** | Porta **`22`** (Dropbear ativo) |
| **Porta Telnet (Resgate)** | Porta **`23`** (Shell root direto para automações) |
| **Rede Wi-Fi 2.4 GHz** | **`PREDATOR T7_2.4GHz`** / **`Predator_T7_2.4G`** |
| **Rede Wi-Fi 5 GHz** | **`PREDATOR T7_5GHz`** / **`Predator_T7_5G`** |
| **Rede Wi-Fi 6 GHz (Wi-Fi 7)** | **`PREDATOR T7_6GHz`** / **`Predator_T7_6G`** (WPA3-SAE) |
| **Senha Wi-Fi (Todas as Bandas)** | **`123456789`** (Padrão para 2.4G, 5G e 6G) |

> [!TIP]
> **Arquivo Informativo do Backup:**  
> As instruções completas e credenciais do arquivo de desbloqueio `.cfg` estão descritas em:  
> [`02_BACKUPS_E_DUMPS/Configuracoes_CFG/INFORMACOES_DO_BACKUP_CFG.txt`](02_BACKUPS_E_DUMPS/Configuracoes_CFG/INFORMACOES_DO_BACKUP_CFG.txt)

> [!WARNING]
> ### 🛡️ A Regra de Ouro de Usuários e Senhas
> **JAMAIS delete ou renomeie as contas `root` ou `Admin`.**  
> Ambas compartilham o mesmo UID 0 no Linux. O LuCI e ferramentas OpenWrt esperam o usuário `root`, enquanto rotinas de cron e binários originais da Qualcomm/Acer dependem do usuário `Admin`.  
> Caso decida trocar sua senha pelo terminal, atualize **sempre ambos os usuários** para mantê-los sincronizados:
> ```sh
> passwd root
> passwd Admin
> ```

---

## ⚡ Sumário de Recursos do Projeto

* 🛡️ **Dual-Boot A/B com Salvaguarda de Fábrica:** O Slot 1 (`mtd21` / firmware OEM original que veio no aparelho) e o **U-Boot** são mantidos **100% intactos de fábrica**. Todas as customizações e gravações rodam no Slot 2 (`mtd20` / v27).
* 🔄 **Rollback Instantâneo em 1 Comando:** Se o Slot 2 apresentar qualquer inconsistência, rodar `/usr/sbin/boot-acer` restaura o boot para o Slot 1 de fábrica em segundos.
* 🌐 **LuCI Nativo na Porta 80:** O servidor proprietário da Acer (`lighttpd`) é desativado e o LuCI (`uhttpd`) assume a porta 80 por padrão, com redirecionamento automático de rotas legadas (`/pub/dist/index.html` -> LuCI).
* 📶 **Wi-Fi 7 Turbo Calibrado:** Rádio 6 GHz em 320 MHz de largura (5.76 Gbps) com *Preamble Puncturing*, *Target Wake Time* (TWT para economia de bateria móvel), *BSS Coloring*, Beamforming 4x4, OFDMA e Roaming Rápido 802.11k/v/r (<50ms).
* ⚖️ **Calibração Multicore RPS (4 CPUs):** Distribuição do tráfego das portas de rede entre todos os 4 núcleos do processador Qualcomm IPQ5332 com buffers TCP otimizados.
* 🧹 **Debloat do Sistema:** Desativação de processos celulares desnecessários do modelo X7 (`at_ril`, `modem_readd`), telemetrias pesadas da OEM (`monitord`, `sodd`, `cwmp`, `breakpad`) e Samba, liberando **mais de 50 MB de memória RAM**.
* 📋 **Log de Diagnóstico Automático em Tempo Real:** O toolkit grava continuamente o arquivo `Desktop\LOG_PREDATOR_T7.txt` com o histórico detalhado de todas as operações, facilitando o diagnóstico e suporte em caso de dúvidas.

---

## 1. 🛡️ Arquitetura Dual-Boot A/B e Proteção Anti-Brick

O Acer Predator Connect T7 conta com 1 GB de memória Flash SPI NAND estruturada em particionamento redundante gerenciado pelo SoC Qualcomm IPQ5332:

```
       +-----------------------------------------------------------+
       |                  MEMÓRIA FLASH NAND (1 GB)                |
       +-----------------------------------------------------------+
                                     |
           +-------------------------+-------------------------+
           |                                                   |
     [SLOT 1 - A]                                        [SLOT 2 - B]
  Partição: mtd21 (rootfs)                           Partição: mtd20 (rootfs_1)
  Estado: INTACTO / RESERVA OEM                      Estado: ATIVO EM PRODUÇÃO
  Firmware: Versão Nativa do seu Aparelho             Firmware: v1.01.000027 Otimizado
            (ex: v24, v26 ou v27 - varia por lote)
  Função: Salvaguarda Anti-Brick de Fábrica           Função: LuCI Porta 80 + Wi-Fi 7
  U-Boot: 100% Intacto de Fábrica                    U-Boot: 100% Intacto de Fábrica
```

### O que define qual slot inicializa?
O U-Boot faz a leitura das partições `mtd3` (`0:BOOTCONFIG`) e `mtd4` (`0:BOOTCONFIG1`), onde fica armazenada a variável `primaryboot`:
* **`primaryboot = 1`:** Inicializa o **Slot 1** (Firmware de fábrica OEM protegido).
* **`primaryboot = 2` (ou `0`):** Inicializa o **Slot 2** (OpenWrt v27 com LuCI).

---

### 🚨 O que fazer se o Slot 2 apresentar problemas?

#### Cenário A: O roteador ainda responde via terminal (Telnet ou SSH)
Basta digitar um único comando no terminal:
```sh
/usr/sbin/boot-acer
```
O roteador grava `primaryboot = 1` em ambas as partições de boot e reinicia de volta no **Slot 1 oficial intacto**.

*(Alternativa no Windows: basta rodar a opção [2] de chaveamento no launcher).*

#### Cenário B: Recuperação de Emergência de Hardware (WPS Failsafe no IP `192.168.1.1`)
Como o **U-Boot permanece 100% intacto de fábrica**, o modo de recuperação por hardware está sempre disponível:
1. Desconecte a fonte de energia.
2. Mantenha pressionado o **botão físico WPS** na carcaça.
3. Conecte a fonte mantendo o **WPS pressionado por 5 a 10 segundos** até os LEDs começarem a piscar no modo recovery.
4. O U-Boot inicializa uma **Página Web de Emergência no IP `http://192.168.1.1`**.
5. Configure a placa de rede do seu PC com o IP estático `192.168.1.66` (máscara `255.255.255.0`, gateway `192.168.1.1`).
6. Abra `http://192.168.1.1` no navegador e faça o upload do arquivo de recuperação correspondente:
   * **`restaurar_slot1_acer.itb`:** Restaura o boot para o **Slot 1 (Firmware OEM nativo de fábrica do seu roteador)**.
   * **`chavear_slot2_acer.itb`:** Restaura o boot para o **Slot 2 (LuCI v27)**.

#### Cenário C: Regravação Limpa do Slot 2 a partir do Slot 1
Caso queira reinstalar o Slot 2 do zero com partição limpa:
1. Inicialize no Slot 1.
2. No menu da Central de Gerenciamento, selecione a opção **`[1] Gravar ROM OpenWrt Custom + Root no Slot 2`**.
3. O script transfere a ROM Custom v27 via HTTP local, valida os hashes MD5, grava os volumes e formata o overlay limpo com 147 MB livres.

---

## 2. 📶 Canais de Rádio e Ajustes de Wi-Fi 7

| Rádio | Frequência | Largura / Canal | Taxa de Link | Recursos & Roaming |
| :--- | :--- | :--- | :--- | :--- |
| **`wifi2`** | 6 GHz | **HT320 (320 MHz)** / Auto | **5.7648 Gb/s** | WPA3-SAE, PMF Obrigatório, 802.11k/v, DTIM=2, TWT, Puncturing |
| **`wifi1`** | 5 GHz | **HT80 (80 MHz)** / Auto | **1.44 Gb/s** | 4 Antenas Beamforming (8.38 dBi), 802.11k/v, DTIM=2 |
| **`wifi0`** | 2.4 GHz | `HT20` / Auto | 688 Mb/s | WPA2-PSK AES (Compatibilidade legada e dispositivos IoT) |

> [!NOTE]
> **Calibração de Potência de Transmissão (dBm):** O rádio de 5 GHz já opera no limite físico de projeto de seus amplificadores (~27.3 dBm conduzido / ~35 dBm EIRP). O rádio de 6 GHz é calibrado de fábrica sob a máscara internacional LPI (Low Power Indoor - 5 dBm/MHz). Forçar potência superior por software em canais de 320 MHz satura os front-ends e causa degradação de modulação (EVM) em 4096-QAM, reduzindo a taxa de transferência. Os valores de fábrica entregam o equilíbrio matemático ideal de alcance e estabilidade.

---

## 3. 🔒 Hardening de Segurança: Gerenciamento do Telnet

A porta **Telnet (23)** vem ativada no desbloqueio para assegurar que qualquer computador consiga gerenciar o roteador sem bloqueios de chaves SSH. O serviço escuta **estritamente na rede local (LAN)** e é bloqueado 100% na WAN.

Para desativar o Telnet após concluir sua configuração:
* **No terminal do roteador:** digite:
  ```sh
  desativar-telnet
  ```
  *(Para reativar a qualquer momento, basta digitar: `ativar-telnet`)*.
* **Pelo computador:** Escolha a opção **`[3] Gerenciar Telnet (Hardening)`** na Central de Gerenciamento.

---

## 4. 🔗 Protocolo de Pesquisa: Acer Predator Connect X7 (5G CPE)

O modelo **Acer Predator Connect X7** compartilha o mesmo SoC Qualcomm IPQ5332, porém incorpora um modem celular 5G M.2 (Snapdragon X62) com firmware oficial `v50`.

> [!CAUTION]
> **TRAVA DE SEGURANÇA ATIVA:** As imagens v27 deste repositório são **EXCLUSIVAS do Predator Connect T7**. A gravação dessas imagens em um X7 causará **BRICK**. O script de gravação detecta a arquitetura e bloqueia tentativas indevidas.

* Proprietários do modelo X7 podem utilizar a opção **`[5] Área de Pesquisa do Modelo X7`** para coletar dumps de diagnóstico somente-leitura e colaborar com a engenharia reversa do módulo 5G.

---

<p align="center">
  <b>Desenvolvido pela Comunidade OpenWrt & Engenharia Reversa Independente</b><br>
  Licença MIT — Livre para uso, estudo e aprimoramento.
</p>
