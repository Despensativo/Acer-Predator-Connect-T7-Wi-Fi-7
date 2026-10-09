# Guia de Engenharia e Especificação Técnica: Debloat Stock Max (v27)
## Acer Predator Connect T7 (Qualcomm IPQ5332 / Wi-Fi 7) — Slot 2

> **Documento:** `deboat stock max.md`  
> **Status:** Compilado e Validado  
> **Firmware Base:** Acer OEM v1.01.000027 (Linux 5.4.213 / QSDK Miami)  
> **Alvo:** Slot 2 (`mtd20` / `ubi1_2` / `ubi_rootfs`)  
> **Salvaguarda:** Slot 1 (`mtd21` / OEM v24) 100% Preservado e Bloqueado  
> **Hash MD5 da Imagem Compilada:** `1fea17ad25406d6610ec3ede047c1705`  
> **Tamanho do SquashFS:** `39.635.554 bytes` (Margem livre: 234.910 bytes no volume UBI de 38.0 MB)

---

## 1. Visão Geral da Arquitetura "Debloat Stock Max"

O **Debloat Stock Max** transforma a imagem oficial do firmware Acer Predator Connect T7 em um **OpenWrt puro de alta performance**, nativo e definitivo diretamente no nível da partição Flash NAND (`rootfs.squashfs`).

Em vez de depender de scripts externos rodando correções temporárias pós-boot ou restaurando backups sobre a camada gravável (overlay), **todas as correções, debloats e calibrações de rede foram integradas diretamente dentro do sistema de arquivos de fábrica**.

---

## 2. Mapa Completo de Modificações por Arquivo

### A. Subsistema de Rádio Wi-Fi 7 (`/etc/config/wireless`)
* **Remoção de VAPs Fantasmas:** Eliminadas as 12 interfaces virtuais órfãs herdadas do modelo Predator X7 (Guest 2.4/5/6, IoT, MLO celular atrelado ao `mld0` e VAPs duplicadas).
* **Calibração de Canais e Largura:**
  * **2.4 GHz (`wifi0`):** Canais 1, 6, 11 (auto), largura `HT40`, potência 22 dBm, TWT e BSS Coloring ativos.
  * **5 GHz (`wifi1`):** Travado em **160 MHz (`HT160`)**, canal 36 (36-48), com `blockdfslist '0'` (desbloqueio total sem quedas por radar).
  * **6 GHz (`wifi2`):** Travado em **320 MHz (`HT320`)**, canal 37 PSC (`option psc '1'`), potência 22 dBm, Preamble Puncturing Wi-Fi 7 (`eht_puncturing '1'`) e WPA3-SAE obrigatório.
* **Redes Nativas Criadas (Tri-Band Arquitetura 3-em-1):**
  1. **`Predator_T7_Triband`:** Rede inteligente unificada nas 3 frequências (2.4 + 5G + 6G) com `sae-mixed` e roaming contínuo 802.11k/v.
  2. **`Predator_T7_Dualband`:** Rede de compatibilidade WPA2-PSK puro (2.4 + 5 GHz) para dispositivos legados e IoT.
  3. **`Predator_T7_WiFi7_6G`:** Rede exclusiva para 6 GHz puro a 5.76 Gbps (@ 320 MHz).
  * **Senha padrão unificada:** `Predator0100@`.

---

### B. Interface Web LuCI e Suporte Wi-Fi 7 (`/www/luci-static/resources/view/network/wireless.js`)
* **Patch de Modos de Rádio:** Expandida a classe `CBIWifiFrequencyValue` para aceitar os modos `AX (Wi-Fi 6)` e `BE (Wi-Fi 7)`.
* **Patch de Larguras de Banda:** Adicionadas opções `HT160` (160 MHz), `HT320` (320 MHz) e `EHT320`.
* **Patch de Canais 6 GHz:** Injetada a lista de canais PSC (37, 53, 69, 85, 101, 117).
* **Resultado:** Quando o usuário edita ou altera canais e potências pelo LuCI, o JavaScript não corrompe mais as opções do driver Qualcomm e salva com sucesso.

---

### C. Autenticação, Usuários e Validador de Senha
* **Sincronização Atômica (`/usr/libexec/rpcd/luci`):**
  * Modificado o método `setPassword` para executar `passwd root` **e** `passwd Admin` simultaneamente.
  * Sincroniza em tempo real com `/etc/config/web_info` e `/etc/config/userinfo`.
* **Flexibilização do Validador Web (`/www/luci-static/resources/view/system/password.js`):**
  * Reduzida a barreira do validador de senha para aceitar senhas comuns a partir de 4 caracteres, permitindo ao usuário definir a senha desejada sem bloqueios da UI.
* **Permissões RPC (`/etc/config/rpcd`):**
  * Criadas ACLs completas para ambos os usuários (`root` e `Admin`).
* **Credenciais de Fábrica Padronizadas (`/etc/passwd` e `/etc/shadow`):**
  * Usuários `root`, `Admin` e `admin` configurados com UID 0 e senha inicial `admin0100`.

---

### D. Servidor Web LuCI na Porta 80
* **Desativação do Painel Acer (`lighttpd`):**
  * Binários e scripts em `/etc/init.d/lighttpd.init` e `/usr/sbin/lighttpd` desativados e removidos da inicialização.
* **Ativação Nativa do `uhttpd`:**
  * Descomentadas rotinas em `/etc/init.d/uhttpd`.
  * `/etc/config/uhttpd` escuta em `0.0.0.0:80` (HTTP) e `0.0.0.0:443` (HTTPS).
  * Redirecionamentos em `/www/index.html` e `/www/pub/dist/index.html` apontando diretamente para `/cgi-bin/luci/`.

---

### E. Fim do Alerta Falso de "wpad" Ausente
* **Patch no `rpcd` (`/usr/libexec/rpcd/luci`):**
  * O binário `hostapd` proprietário da Qualcomm não suportava a flag de teste `-vsae` do OpenWrt puro.
  * O método `getFeatures` foi modificado para reportar `true` para `sae`, `11w`, `11r`, `11ac` e `11n`. O LuCI agora libera todos os seletores de WPA3 e PMF sem alertas de dependência.

---

### F. Hostname RFC 1123 (`/etc/config/system`)
* Hostname corrigido de `OpenWrt` / `Predator Connect T7` para **`Predator-Connect-T7`** (sem espaços), eliminando avisos de validação em páginas de configuração de sistema.

---

### G. Rede, IPv6 Universal Híbrido e DNSmasq (`/etc/config/dhcp` e `/etc/config/network`)
* **IPv6 Híbrido:** `dhcpv6`, `ra` e `ndp` configurados em modo `hybrid` na LAN e WAN6 (`master 1`). Funciona de forma transparente tanto em conexões diretas (Bridge/PPPoE) quanto atrás de modems de operadora (Duplo NAT).
* **Blindagem Apple SLAAC (RFC 4862 / RFC 8106):** Flag `managed-config` removida e `other-config` ativada; `ra_prefer_old 0` (RFC 9096) para eliminar prefixos expirados.
* **Turbo Cache DNSmasq:** Cache expandido para **10.000 entradas** na RAM (`cachesize 10000`, `min_cache_ttl 300`) para consultas em 0 ms.
* **Limpeza de Interfaces Órfãs:** Removidas do `network` e `firewall` as interfaces `guest`, `iot`, `wan1` (celular 5G) e `xlatd`.

---

### H. Desativação Permanente de FOTA e Daemons do X7 (Fim do Bug USB)
* **Desarmamento de FOTA:**
  * Linhas de `download_img`, `update_img` e `silent-reboot` removidas dos crontabs (`/etc/crontabs/root` e `/etc/crontabs/Admin`).
  * Desativada a permissão de execução de `/usr/sbin/fota` e scripts em `/lib/functions/`.
* **Daemons Inúteis Eliminados do Boot (`/etc/rc.d/`):**
  * `modem-monitor`, `modem_read_init`, `modem_datausage`, `at_ril`, `ril` (modem celular inexistente no T7).
  * `monitord`, `sodd`, `cwmp` (TR-069), `mqtt_client`, `breakpad`.
* **Estabilidade da Porta USB:**
  * O daemon conflitante `ksmbd` foi removido da inicialização automática.
  * O compartilhamento USB fica sob responsabilidade exclusiva do **Samba4** via **Services $\rightarrow$ Network Shares** no LuCI, eliminando a concorrência de portas e o bug crônico de desconexão nos reboots.

---

### I. Aceleração Multicore e Kernel (`/etc/sysctl.d/` e `/etc/hotplug.d/`)
* **`/etc/sysctl.d/99-performance.conf`:**
  * `net.netfilter.nf_conntrack_max = 65536`
  * `net.ipv4.tcp_fastopen = 3`
  * `net.core.somaxconn = 1024`
  * `net.core.netdev_max_backlog = 2048`
  * `net.bridge.bridge-nf-call-iptables = 0` (Bypass L2 para latência mínima)
* **`/etc/hotplug.d/net/90-ark-rps-tune`:**
  * Roteamento de filas de pacotes das interfaces Wi-Fi e Ethernet balanceado entre os **4 núcleos da CPU Qualcomm IPQ5332**.

---

### J. Terminais Nativos e Atalhos de Emergência
* **SSH (Dropbear):** Ativo e liberado na porta 22 em `/etc/config/dropbear`.
* **Telnet:** Ativo e liberado na porta 23 chamando `/bin/ash` direto.
* **Rollback Instantâneo:** Atalhos instalados em `/usr/sbin/boot-acer` (retorna para o Slot 1 OEM estável) e `/usr/sbin/boot-openwrt` (força Slot 2).

---

## 3. Especificações Técnicas de Recompilação do SquashFS

Para reconstrução reproduzível da imagem no macOS ou Linux:

```bash
# Comando de compilação oficial compatível com UBI/Qualcomm:
mksquashfs rootfs_extracted rootfs.squashfs \
    -comp xz \
    -Xbcj arm,armthumb \
    -Xdict-size 256k \
    -b 256k \
    -noappend \
    -nopad \
    -no-xattrs \
    -all-root \
    -p "dev/console c 600 0 0 5 1"
```

* **Estrutura dos 3 Componentes do Slot 2 (`mtd20`):**
  1. `ubi1_0`: `wifi_fw.bin` (Microcódigo Qualcomm Intocado — MD5: `f1091a9c062ff50dd3348e06a8a5457e`)
  2. `ubi1_1`: `kernel.bin` (Kernel Linux 5.4 FIT Intocado — MD5: `ade31977f9c740a36ecfe50ac9e335d9`)
  3. `ubi1_2`: `rootfs.squashfs` (Custom Debloat Stock Max — MD5: `1fea17ad25406d6610ec3ede047c1705`)

---

## 4. Guia Operacional: Modo de Emergência (Failsafe) e Botão Reset Físico

### A. Botão de Reset Físico (Localizado embaixo do aparelho)
No firmware original da Acer, toques rápidos de menos de 2 segundos reiniciavam o aparelho intempestivamente. No **Debloat Stock Max**, o comportamento foi blindado contra qualquer toque acidental:
* **Toques rápidos ou acidentais (< 20 segundos):** São **100% ignorados** pelo sistema. O roteador não reinicia, não reseta e não interrompe a conexão.
* **Factory Reset Intencional (Segurar por 20 segundos ou mais):**
  * O sistema executa o comando nativo `jffs2reset -y && reboot`.
  * **O que acontece:** O roteador **NÃO apaga o sistema operacional**. Ele apenas limpa a partição de sobreposição (`/overlay` no `ubi1_3`), apagando personalizações de teste do usuário.
  * **Como ele acorda:** Ele renasce imediatamente carregando este RootFS pré-configurado: LuCI ativo na porta 80, redes Wi-Fi 7 Tri-Band funcionando, SSH/Telnet liberados e senha `admin0100`.

### B. Modo de Recuperação de Emergência (Failsafe Mode)
Se por qualquer motivo o usuário aplicar uma regra de firewall que bloqueie o acesso ou corrompa a rede na partição overlay:

1. **Como entrar no Modo Failsafe:**
   * Desligue e ligue o roteador na tomada.
   * Assim que o LED de status começar a piscar rápido durante o estágio de pré-inicialização (`preinit` — primeiros 2 a 3 segundos de boot), **pressione repetidamente o botão Reset ou WPS**.
2. **O que o Modo Failsafe faz:**
   * **Ignora completamente o overlay corrompido** (não monta `/overlay`).
   * Desativa o Wi-Fi e daemons pesados.
   * Configura a porta de rede cabeada no IP estático de emergência: **`192.168.1.1`**.
   * Abre um **Telnet de socorro irrestrito sem senha** na porta 23.
3. **Como recuperar o roteador via terminal no PC:**
   * Configure a placa de rede do seu PC manualmente para:
     * IP: `192.168.1.2`
     * Máscara: `255.255.255.0`
     * Gateway: `192.168.1.1`
   * Abra o terminal do computador e conecte direto:
     ```bash
     telnet 192.168.1.1
     ```
   * No prompt do Failsafe, digite:
     ```bash
     firstboot -y     # Limpa o overlay corrompido
     reboot -f        # Reinicia o roteador no estado perfeito de fábrica
     ```

---

## 5. Especificação Técnica: Aceleração Multicore nos 4 Núcleos (IPQ5332)

O SoC Qualcomm IPQ5332 possui 4 núcleos de processamento ARM Cortex-A53 (identificados no Linux como `CPU0`, `CPU1`, `CPU2` e `CPU3`).

### O Problema do Firmware de Fábrica:
No firmware OEM da Acer, quase todas as interrupções de rede cabeada e Wi-Fi ficavam concentradas na `CPU0`. Sob cargas intensas de tráfego a 2.5 Gbps ou múltiplos downloads simultâneos, a `CPU0` batia 100% de uso enquanto os outros 3 núcleos ficavam ociosos, gerando picos de jitter e queda de throughput.

### Como funciona a Aceleração Multicore Implementada:
1. **RPS Tuning Dinâmico (`/etc/hotplug.d/net/90-ark-rps-tune`):**
   * Toda vez que uma interface de rede física ou sem fio sobe (`eth0`, `eth1.1`, `eth1.2`, `ath0`, `ath1`, `ath2`, `ath21`), o script hotplug injeta a máscara hexadecimal `f` (binário `1111`) em `/sys/class/net/<interface>/queues/rx-*/rps_cpus`.
   * A máscara `f` instrui o subsistema de rede do kernel Linux a distribuir o processamento das filas de recepção de pacotes uniformemente entre **todos os 4 núcleos da CPU**.
2. **Buffer de Fluxos de Rede (`rps_flow_cnt = 4096`):**
   * Aumenta a tabela de direcionamento de fluxos de conexões TCP/UDP individuais, evitando que conexões simultâneas de torrents ou streaming concorram no mesmo núcleo que um jogo online de baixa latência.
3. **Distribuição de Interrupções por Hardware (EDMA NSS Queues):**
   * As filas de hardware do controlador Ethernet Qualcomm (`edma_txcmpl`) são mapeadas pelo kernel diretamente nos 4 núcleos:
     * `CPU0`: Gerencia interrupções de timer e controle base.
     * `CPU1`, `CPU2`, `CPU3`: Dedicadas para transporte acelerado de pacotes de dados LAN/WAN e Wi-Fi 7 em tempo real.

