# Cronometria de Boot do Wi-Fi, Comportamento dos LEDs e Credenciais: Acer Predator Connect T7

Este documento consolida a análise técnica dos tempos de inicialização das interfaces sem fio, a lógica física e de software dos LEDs de status e a validação das credenciais do sistema no **Acer Predator Connect T7**.

---

## 1. Cronometria Real de Inicialização do Wi-Fi (Qualcomm IPQ5322 / QCN6274)

Os dados abaixo foram cronometrados e extraídos diretamente dos registros em tempo real do Kernel Linux (`dmesg` e `hostapd`).

### 1.1 Primeiro Boot (Após restauração limpa de fábrica ou primeiro flash de ROM)
No primeiro boot limpo, o subsistema Qualcomm detecta a ausência de tabelas de RF pré-gravadas na NVRAM/ART e desativa propositalmente o *Fast Boot*:
```text
***** Fast boot is disabled for first boot wifi1 *****
```
Durante este processo de calibração automática de fábrica:
- **`ath0` (2.4 GHz - IPQ5322 Rádio Integrado):**
  - Início do driver: `82.6s`
  - Beacon ativo e rádio transmitindo: **`86.1s` (~1 minuto e 26 segundos)**
- **`ath2` (6.0 GHz Wi-Fi 7 - Qualcomm QCN6274 PCIe):**
  - Início do driver: `90.1s`
  - Beacon e quadros FILS ativos: **`90.4s` (~1 minuto e 30 segundos)**
- **`ath1` (5.0 GHz - IPQ5322 Rádio Integrado em HT160/EHT160):**
  - Início do driver: `83.7s`
  - **Checagem de Radar DFS (CAC - Channel Availability Check):** Como a largura de canal de 160 MHz (canal 36 a 64) sobrepõe faixas de radar meteorológico/aeronáutico DFS (5250–5350 MHz), a regulamentação internacional (FCC/Anatel/ETSI) e a Qualcomm obrigam uma **escuta passiva de silêncio de exatos 60 segundos** antes da transmissão.
  - Beacon ativo e rádio transmitindo: **`145.8s` (~2 minutos e 25 segundos)**.

> **Tempo total para todos os 3 rádios estarem 100% online no 1º Boot:** **~2 minutos e 25 segundos a 2 minutos e 30 segundos**.

---

### 1.2 Demais Boots Normais (Reboots subsequentes)
Nos boots comuns seguintes, o parâmetro Qualcomm Fast Boot já encontra as tabelas RF gravadas na flash:
- **Ganho de tempo:** Economia de aproximadamente **30 a 40 segundos** na inicialização dos controladores de RF.
- As redes de **2.4 GHz (`ath0`)** e **6.0 GHz Wi-Fi 7 (`ath2`)** tornam-se disponíveis em cerca de **50 a 60 segundos**.
- A rede de **5.0 GHz (`ath1`)**, se mantida em 160 MHz com sobreposição DFS, continua cumprindo a exigência de segurança de 60 segundos do DFS CAC, subindo entre **1m45s e 2m00s**.
  - *(Dica de otimização: Caso o rádio de 5 GHz seja configurado em 80 MHz fixo nos canais 36 a 48 sem faixa DFS, ele sobe instantaneamente junto com as demais faixas em menos de 1 minuto).*

---

## 2. Comportamento e Lógica Física dos LEDs

A arquitetura do Predator T7 utiliza o circuito integrado dedicado **Awinic AW21018** (controlador I2C de LEDs multicanal gerenciado pelo driver `/sys/class/leds/aw21018_led/led`) acoplado ao daemon em espaço de usuário `/usr/sbin/ledd` (`/etc/init.d/ledd`):

```
                        +----------------------------+
                        |      Kernel & Drivers      |
                        +--------------+-------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
         [hostapd_cli sockets]                    [ethtool eth0]
     (ath0, ath1, ath2 status)               (Detecção de Link WAN)
                   |                                       |
                   +-------------------+-------------------+
                                       |
                                       v
                        +----------------------------+
                        |   Daemon: /usr/sbin/ledd   |
                        +--------------+-------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
          LED FRONTAL DE STATUS                   LED SUPERIOR MAIOR
          - Vermelho: Boot / Wi-Fi subindo        - Apagado: Cabo WAN desconectado
          - Azul: 3 Rádios 100% Operacionais     - Aceso: Link WAN ativo + Internet
```

### 2.1 LED Frontal (Indicador de Status do Roteador / Wi-Fi)
- **Durante o Boot do Sistema:** Permanece **VERMELHO**.
- **Lógica Interna do Software:** O daemon `ledd` executa continuamente consultas de status via soquetes do hostapd:
  ```sh
  hostapd_cli -i ath0 -p /var/run/hostapd-wifi0 wps_get_status
  hostapd_cli -i ath1 -p /var/run/hostapd-wifi1 wps_get_status
  hostapd_cli -i ath2 -p /var/run/hostapd-wifi2 wps_get_status
  ```
  Enquanto qualquer uma das três interfaces ainda estiver em calibração ou no período de escuta passiva do DFS CAC (especialmente o rádio de 5 GHz), a variável interna permanece como `wifi_ap_status no`, mantendo o LED frontal **vermelho**.
- **Após Conclusão:** Quando o último rádio entra em estado operacional de emissão de beacons, a variável comuta para `wifi_ap_status ok`, e o LED frontal muda para **AZUL (ou verde/branco)**, indicando que o roteador está pronto para uso.

### 2.2 LED Superior Maior (Logo Predator / Anel Superior)
- **Lógica de Conexão Física:** O daemon monitora a porta Ethernet de 2.5 Gbps dedicada à WAN (`eth0`):
  ```sh
  ethtool eth0 | grep detected
  ```
- **Comportamento:**
  - **Cabo WAN Desconectado (`Link detected: no`):** O LED superior permanece apagado ou em stand-by.
  - **Cabo WAN Conectado com Link Ativo (`Link detected: yes`):** O LED superior acende imediatamente, refletindo a iluminação decorativa e o status da conexão de internet.

---

## 3. Validação das Credenciais de Acesso (Root e Admin)

A integridade do arquivo de senhas e autenticação foi conferida e validada:

- **Hash Criptográfico em `/etc/shadow`:**
  ```text
  root:$1$Um5WcEaV$hBKFxVMl2AbNBDfYfYMyW/:20733:0:99999:7:::
  admin:$1$Um5WcEaV$hBKFxVMl2AbNBDfYfYMyW/:20733:0:99999:7:::
  Admin:$1$Um5WcEaV$hBKFxVMl2AbNBDfYfYMyW/:20733:0:99999:7:::
  ```
- **Auditoria Reversa de Hash:**
  Execução do algoritmo padrão OpenWrt MD5-Crypt:
  ```sh
  openssl passwd -1 -salt Um5WcEaV root0100
  # Retorno: $1$Um5WcEaV$hBKFxVMl2AbNBDfYfYMyW/ (100% Idêntico)
  ```
- **Resultado:**
  - **Usuário SSH:** `root` (e `admin`) -> Senha: **`root0100`**
  - **Usuário Web LuCI:** `root` (e `admin`) -> Senha: **`root0100`**
  - **Usuário Web OEM Acer:** `admin` (ou `Admin`) -> Senha: **`root0100`**
  - **Chave SSH Autorizada:** Chave RSA Antigravity salva em `/etc/dropbear/authorized_keys` permitindo acesso direto sem senha via chave pública.

---

## 4. Hostname com Espaços & Neutralização de WHC e WSPLC

- **Nome com Espaço (`Predator Connect T7`):**
  - A restrição anterior que destacava o campo em vermelho era apenas uma regra sintática do validador JavaScript do LuCI herdada da RFC 952/1123 (norma de 1989 para servidores DNS).
  - Com o ajuste no `validation.js` e `system.js`, a interface aceita espaços normalmente.
  - **Impacto no Sistema:** Zero impacto negativo. O Linux e os serviços locais tratam a string entre aspas ou como nome de exibição de forma transparente.
- **Módulos WHC e WSPLC Eliminados:**
  - Controladores Qualcomm Mesh (`whc.lua`) e PLC HomePlug (`wsplc.lua`) foram substituídos por stubs inofensivos.
  - Rotas retornam **404** e não sobrecarregam mais a CPU nem geram concorrência nos rádios Wi-Fi.

> **🔄 [ATUALIZAÇÃO MASTER V2 — 14/10/2026 (Padronização RFC 1123)]**: Embora o LuCI tenha sido patcheado para não travar a interface caso o usuário digite espaços, no pacote `cfg_restauracao_master_v2.cfg` o hostname oficial foi padronizado com hifens como **`Predator-Connect-T7`** (`uci set system.@system[0].hostname='Predator-Connect-T7'`), garantindo 100% de conformidade com a RFC 1123 em servidores DHCP de operadoras e scripts POSIX.
