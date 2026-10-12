# PLAYBOOK DE COMANDOS HOMOLOGADOS - ACER PREDATOR CONNECT T7
> **IMPORTANTE PARA AGENTES DE IA**: Consulte este arquivo antes de disparar qualquer comando SSH, Telnet ou script neste projeto. É proibido chutar comandos ou partições por tentativa e erro.

---

## 1. Dados de Rede e Acesso
* **IP Slot Principal (A)**: `192.168.76.1`
* **IP Slot Alternativo (B)**: `192.168.73.1` (ou `10.203.73.5` em setups de laboratório)
* **SSH**: Porta `22` (Dropbear). As chaves `ssh-rsa` e bypass de hostkey já estão pré-configurados no `~/.ssh/config` do Mac.
* **Telnet**: Porta `23` (Disponível para recuperação e comandos diretos).
* **Credenciais Homologadas**:
  - Usuário: `root` | Senha: `root` (ou `root0100` em builds legadas)
  - Alternativa OEM: `admin` | Senha: `admin`

---

## 2. Comandos Operacionais Homologados (Executar Sem Erros)

### Como Checar o Slot Ativo (Dual-Boot A/B):
```sh
ssh root@192.168.76.1 "cat /proc/cmdline"
# Se contiver 'rootfs_1' ou 'boot_partition=1' -> Slot B
# Se contiver 'rootfs' ou 'boot_partition=0'   -> Slot A
```

### Como Transferir Arquivos (Sem Quebrar no SFTP):
```bash
# Dropbear não tem sftp-server; use SEMPRE a flag -O:
scp -O meu_arquivo.ipk root@192.168.76.1:/tmp/

# Ou envie por pipe SSH direto:
ssh root@192.168.76.1 "cat > /tmp/meu_arquivo.ipk" < meu_arquivo.ipk
```

### Como Extrair Logs e Dados de Partições Flash:
```sh
# NUNCA envie comandos python3 para rodar no roteador (não existe Python no BusyBox).
# Use comandos nativos do BusyBox:
strings /dev/mtd23 | grep -E '^<[0-9]>\[ *(2[0-9]|3[0-2])\.' | head -n 60

# Ou traga os dados binários para o Mac via SSH para processar com Python local:
ssh root@192.168.76.1 "cat /dev/mtd26" | python3 -c '...'
```

### Pausas e Delays no Roteador:
```sh
# BusyBox NÃO aceita números decimais no sleep (gera "sleep: invalid number '0.2'").
sleep 1                # Para 1 segundo ou mais
usleep 200000          # Para 200 milissegundos (0.2s)
```

### Verificação de Rádios Wi-Fi 7:
```sh
# 'iwinfo' pode não estar instalado na stock/debloat. Use sempre o binário nativo:
/usr/sbin/iw dev
```

---

## 3. Mapa Rápido de Partições Flash MTD Críticas
| Partição | Tamanho | Função | Alerta / Observação |
| :--- | :--- | :--- | :--- |
| `mtd18` | 2.0 MB | `0:ART` | **CRÍTICO - NUNCA GRAVAR**. Calibração única de rádio Wi-Fi. |
| `mtd20` | 240 MB | `rootfs_1` | Imagem do Sistema no **Slot B**. |
| `mtd21` | 240 MB | `rootfs` | Imagem do Sistema no **Slot A**. |
| `mtd23` | 512 KB | `0:SYSTRACE` | Rastreamento e logs de crash do sistema. |
| `mtd25` | 8.3 MB | `wifi_fw` | Firmware proprietário Qualcomm Wi-Fi 7 (IPQ5332). |
| `mtd26` | 4.0 MB | `kernel` | Imagem do Kernel Linux montada. |
| `mtd27` | 38 MB | `ubi_rootfs` | Sistema Base `/rom` (SquashFS somente leitura). |
| `mtd28` | ~166 MB | `rootfs_data`| Camada gravável OverlayFS montada em `/overlay`. |

---

## 4. Registro Contínuo de Descobertas (AutoLearn)
> *Esta seção é atualizada automaticamente pelos agentes de IA sempre que uma nova particularidade técnica ou solução for descoberta neste projeto.*

* **[AutoLearn - Wi-Fi 7 QCN9224 & BDF Default vs FCC]**: O arquivo `bdwlan_default.b1015` possui tabelas CTL desvinculadas das travas LPI da FCC (offset `0x1bcb0` com limite de 40 dBm / valor 80). Ele permite extrair as potências máximas de **20 dBm e 21 dBm (até 1.150 mW EIRP)** no rádio de 6 GHz (QCN9224). O `bdwlan_fcc.b1015`, por sua vez, trava o rádio a 15 dBm em 320 MHz. Portanto, para extrair a máxima potência desbloqueada, `/lib/firmware/qcn9224/bdwlan.b1015` deve apontar para `bdwlan_default.b1015`.
* **[AutoLearn - Canal 149 no 5 GHz (U-NII-3)]**: Nos canais baixos (36 a 64 / U-NII-1/2A), a FCC limita a potência a 23 dBm em 160 MHz. No Canal 149 (faixa U-NII-3), não há radar DFS (sobe instantâneo no boot) e o teto sobe para 30 dBm, liberando a potência máxima de **26 dBm conduzido (5.495 mW EIRP / 5.5 Watts)**.
* **[AutoLearn - Subida Segura do Wi-Fi]**: A potência e ajustes finos de RF NUNCA devem ser aplicados antes do boot do driver. O driver faz o coldboot limpo no boot e os ajustes de potência são aplicados assincronamente após as interfaces `ath0/1/2` estarem no ar.
* **[AutoLearn - cnssdaemon Obrigatório]**: O script `/etc/init.d/load_cnss2` deve manter a função `boot_cnss2()` intacta para subir `/usr/bin/cnssdaemon -s`. Sem o daemon ativo em espaço de usuário, o driver `wifi_3_0.ko` não conclui o handshake QMI e a placa PCIe QCN9224 trava com `Fatal error received from wcss software!`.
* **[AutoLearn - /cfg/default/ini Intacto]**: Nunca deletar `/cfg/default/ini` no debloat. O script oficial `/sbin/wifi config` requer `/cfg/default/ini/global.ini` para gerar `/etc/config/wireless`.
* **[AutoLearn - Slot Detection em wifi_fw_mount]**: No Slot 2 iniciado via BOOTCONFIG, `/proc/cmdline` pode não exibir `rootfs_1`. A detecção infalível da partição ativa deve consultar `/sys/class/ubi/ubi0/mtd_num` (21 = Slot 2 / rootfs_1; 20 = Slot 1 / rootfs).
* **[AutoLearn - Blindagem de Watchdog kernel.panic=0]**: Configurar `kernel.panic = 0` em `/etc/sysctl.conf` e `/etc/sysctl.d/99-panic-lock.conf` impede que o Linux desligue os CPUs e derrube o switch Ethernet enquanto um firmware PCIe inicializa.
* **[AutoLearn - Módulos de Mesh Qualcomm (repacd, wsplcd, lbd)]**: NUNCA deletar esses binários nem seus configs (`/etc/config/repacd`, `/etc/config/wsplcd`) via `rm -f`. Eles são binários proprietários Qualcomm SPF-12.2 (março/2025) e não devem ser substituídos por pacotes genéricos do OpenWrt devido a quebra de ABI (`libhyficommon.so`). O procedimento homologado é mantê-los desativados via UCI (`repacd.repacd.Enable='0'`), o que resulta em zero consumo de CPU/RAM e preserva a capacidade de Mesh se o usuário quiser usar no futuro.
* **[AutoLearn - Suporte SQM & CAKE Nativo]**: O kernel Linux 5.4.213 do T7 já possui `sch_cake.ko` e `ifb.ko` carregados na memória. O pacote `sqm-scripts` + `luci-app-sqm` (compatível com LuCI 22 CBI) foi integrado para a interface WAN (`eth0`) com algoritmo CAKE (`piece_of_cake.qos`) e overhead Ethernet (44/64), configurado por padrão como `enabled '0'`. Quando desligado, a aceleração de hardware PPE/ECM opera a 100% (2.5 Gbps); quando o usuário ativa no LuCI, o Cake elimina bufferbloat com priorização inteligente.
* **[AutoLearn - Mapeamento Físico de Portas LAN no Switch]**: O switch interno (switch1) utiliza a Porta 0 exclusivamente como tronco interno CPU (0t). As portas físicas RJ45 Gigabit são: Porta 1 = LAN 1, Porta 2 = LAN 2. A porta WAN de 2.5 Gbps (`eth0`) é um PHY PCIe dedicado fora do switch1. Qualquer leitura de link via `swconfig` para LAN 1 deve apontar para a Porta 1, e para LAN 2 deve apontar para a Porta 2; ler a Porta 0 como LAN causava o bug de exibir a porta LAN 1 conectada a 1 Gbps ininterruptamente mesmo sem cabo.
* **[AutoLearn - Credenciais e Redes Homologadas]**:
  - Web UI (LuCI porta 80/443), SSH (porta 22) e Telnet (porta 23): Usuário `root` | Senha: `root0100`
  - SSIDs de Fábrica: `PREDATOR T7_2.4GHz`, `PREDATOR T7_5GHz`, `PREDATOR T7_6GHz`, `PREDATOR T7_MLO`
  - Senha Wi-Fi padrão: `123456789`

* **[AutoLearn - Largura de Banda 160 MHz vs 80 MHz no 5 GHz (IPQ5332)]**:
  - No **Canal 149** (faixa U-NII-3, 5735 a 5815 MHz), existem apenas 4 canais contíguos de 20 MHz (149, 153, 157, 161), totalizando exatamente 80 MHz. Portanto, no canal 149 a largura máxima física estipulada pelo padrão IEEE 802.11 é **80 MHz**.
  - Para atingir a largura completa de **160 MHz** no rádio de 5 GHz (alcançando links de até 2.400 / 4.800 Mbps), deve-se selecionar os canais baixos: **Canal 36** (ou 44 ou `auto`) com `htmode 'HT160'`. Esses canais ocupam o bloco contíguo de 36 a 64 (com frequência central em 5250 MHz / Canal 50).
  - Todas as modificações de rede feitas pelo usuário (via Web LuCI ou comandos `uci` no terminal) são gravadas na camada persistente `/overlay` (`mtd28`) e sobrevivem a qualquer reinicialização.
* **[AutoLearn - Injeção Obrigatória de he_oper_chwidth=2 e vht_oper_chwidth=2 em 11bea:HT160]**:
  - No script oficial `/lib/wifi/hostapd.sh` para o modo `*bea:HT160` (Wi-Fi 7), a Qualcomm/Acer adicionou apenas a tag `eht_oper_chwidth=2`.
  - Dispositivos Wi-Fi 6 (802.11ax) e Wi-Fi 5 (802.11ac) não interpretam elementos EHT de Wi-Fi 7. Sem `he_oper_chwidth=2` e `vht_oper_chwidth=2` nos beacons gerados pelo hostapd, os clientes Wi-Fi 6 caíam em fallback de 80 MHz e limitavam a conexão em 1201 Mbps.
  - Com a injeção de `vht_oper_chwidth=2`, `he_oper_chwidth=2` e `centr_freq_seg0_idx=50`, os beacons transmitem a operação de 160 MHz para todas as gerações (Wi-Fi 5, Wi-Fi 6 e Wi-Fi 7), liberando a negociação em 2.402 Mbps (2.4 Gbps).
* **[AutoLearn - Suporte a 320 MHz no Roteador vs 160 MHz em Smartphones (Ex: iPhone)]**:
  - O roteador transmite nativamente em **320 MHz** no rádio de 6 GHz (`ath2`, Canal 33 / U-NII-5, `eht_oper_chwidth=4`).
  - Dispositivos como o Apple iPhone (iPhone 15 Pro com Wi-Fi 6E e iPhone 16/16 Pro com Wi-Fi 7) possuem chipsets com limitação de silício/antena de fábrica para no máximo **160 MHz** (`IEEE80211_MODE_11BEA_EHT160`), negociando no seu teto físico de 2.402 / 2.882 Mbps.
  - Clientes com placas Wi-Fi 7 completas de 320 MHz (ex: Intel BE200 em PCs ou Snapdragon FastConnect 7800) negociam os 320 MHz completos com link de até 5.760 Mbps.
* **[AutoLearn - Configuração Homologada WAN PPPoE com Host-Uniq e Clonagem de MAC]**:
  - Para conexões PPPoE de provedores de fibra que exigem autenticação casada (Host-Uniq e MAC da ONT de fábrica):
    - No `/etc/config/network`, configurar `config device 'wan_dev'` com `option name 'eth0'` e `option macaddr '<MAC>'` para cravar o MAC spoofing na camada física netifd.
    - Na interface `wan`, utilizar `option proto 'pppoe'`, `option ifname 'eth0'`, `option macaddr '<MAC>'`, `option host_uniq '<MAC_SEM_DOIS_PONTOS>'`, `option mtu '1492'` e `option ipv6 'auto'`.
    - Com `ipv6 'auto'`, o netifd e o script `/lib/netifd/ppp6-up` inicializam a interface virtual dinâmica `wan_6` sobre `@wan` (`pppoe-wan`) com `dhcpv6` para delegação de prefixo IPv6 (`/60` ou `/64`), dispensando a interface estática `wan6` na porta `eth0` física.
* **[AutoLearn - Calibração dos Seletores de Potência RF (Zero Divergência)]**:
  - Os seletores de potência tanto na Central Predator (`predator_wifi.js`) quanto na página padrão do LuCI (`wireless.js`) foram calibrados para refletir fielmente a **potência conduzida real** enviada aos conectores das antenas, casando 100% com a telemetria ao vivo:
    - **2.4 GHz (IPQ5332)**: Máx Real = `22 dBm` (158 mW conduzido / 708 mW EIRP c/ ganho de 6.5 dBi).
    - **5.0 GHz (IPQ5332)**: Em 160 MHz = `23 dBm` (200 mW conduzido / 2.180 mW EIRP c/ ganho de 10.38 dBi); em 80 MHz Ch 149+ = `26 dBm` (398 mW conduzido / 5.495 mW EIRP).
    - **6.0 GHz (QCN9224 Wi-Fi 7)**: Máx Real Desbloqueado (BDF Default) em 320 MHz = `20 dBm` (100 mW conduzido / ~1.000 mW EIRP c/ ganho de 9.62 dBi).
* **[AutoLearn - Recarga do Wi-Fi na Página Padrão do LuCI e Correções no Driver QCA]**:
  - **`ucitrack` e `/sbin/luci-reload`**: O script `/sbin/luci-reload` do LuCI não percorre listas de dependência `affects`. Para que o botão "Salvar e Aplicar" da página padrão do LuCI (`/admin/network/wireless`) efetivamente recarregue o Wi-Fi, `/etc/config/ucitrack` deve conter `option exec '/sbin/wifi reload'` no bloco `config wireless`.
  - **Correção de Sintaxe no `/lib/wifi/qcawificfg80211.sh`**:
    - Linha 2843: `$device_if` era invocado antes de ser inicializado (`eval: line 2843: : Permission denied`). A inicialização foi antecipada para antes do bloco `case "$board_name"`.
    - Linhas 7360/7375/7378: Substituída a sintaxe malformada `[[ -z ... ] -o [ ... ]]` por `[ ... ] || [ ... ]` e adicionadas aspas em `"$mld_netdev"`, eliminando erros fatais de `sh: missing ]` e `unknown operand`.
    - Linha 7578: Corrigido teste de RTS sem aspas `[ $rts == "off" ]` para `[ "$rts" = "off" ]`.
    - Linhas 7706-7740: Adicionadas verificações defensivas de variáveis vazias em `$vif_txpower` e `$txpower`, e implementado tratamento para `txpower="auto"` (chamando `iw dev set txpower auto` em vez de `fixed auto`).
    - Linha 4109: Injetadas as chamadas a `/lib/wifi_hardware_tune.sh` e `/etc/init.d/predator_rf start` no hook `post_common_qcawificfg80211()`, garantindo que toda e qualquer alteração de Wi-Fi feita pelo sistema (LuCI padrão, Central Predator, CLI ou hotplug) restaure automaticamente o Tx Beamforming Sounding (100ms), Preamble Puncturing estrito e Gaming Mode no silício de hardware.
  - **Auto-Canal em 320 MHz no `/lib/wifi/hostapd.sh`**:
    - Adicionado fallback `*) idx=31;;` no bloco `*bea:HT320`. Quando `channel=auto` era configurado em 6 GHz, o script deixava o índice de frequência central vazio, forçando o hostapd a rebaixar o rádio de 320 MHz para 160 MHz. Com o fallback no canal central 31, o auto-canal opera em 320 MHz plenos.
  - **Monitoramento Confiável de Trava e Telemetria no `/usr/libexec/rpcd/predator`**:
    - O verificador de lock foi restrito aos arquivos de lock específicos do Wi-Fi (`/var/run/wifilock`, `/var/run/wifi_global_lock`, etc.), eliminando falsos positivos causados por locks de outros serviços do roteador (como `mwan3.lock`).
* **[AutoLearn - Repasse de Prefixo IPv6 (DHCPv6-PD) e `ip6assign '64'`]**:
  - Quando o provedor delega um bloco IPv6 `/60` (16 sub-redes `/64`), as interfaces locais (`lan`, `guest`, `iot`) em `/etc/config/network` NUNCA devem ter `option ip6assign '60'`. Caso contrário, a primeira interface inicializada consome 100% do bloco e esgota o prefixo para as demais interfaces, além de quebrar o SLAAC (RFC 4291 exige sub-redes `/64` para autoconfiguração de clientes).
  - O padrão homologado é `option ip6assign '64'` em todas as interfaces locais com `option ip6hint '0'` (`lan`), `option ip6hint '1'` (`guest`) e `option ip6hint '2'` (`iot`). Isso fatia o `/60` delegado em sub-redes `/64` distintas (`2804:3d90:5e:20::/64`, `2804:3d90:5e:21::/64`, etc.), permitindo que o `odhcpd` distribua endereços globais e DNS IPv6 instantaneamente para celulares, PCs e TVs via SLAAC/DHCPv6.
* **[AutoLearn - Descoberta Instantânea em 6 GHz / Wi-Fi 7 e Limites de Silício dos Clientes]**:
  - **Descoberta Rápida 6 GHz (FILS & RNR ESS)**: O padrão Wi-Fi 7 / 6E possui 59 canais e proíbe varreduras ativas cegas. Para que a rede de 6 GHz apareça instantaneamente nos smartphones e iPads, são obrigatórios:
    1. Canal PSC primário (Canal 37);
    2. FILS Discovery Frames (`ieee80211ai '1'`, `fils_fd_period '20'`, `cfg80211tool ath2 enable_fils 1 20`), emitindo quadros condensados a cada 20 ms;
    3. RNR Co-located e membro de ESS (`cfg80211tool wifi2 rnr_member_ess_colocated_en 1` e `rnr_6ghz_colocated 1 7`), anunciando a rede 6 GHz nos beacons de 2.4 GHz e 5 GHz.
  - **Limitação de Silício Apple (iPhone / iPad Pro M4/M5)**: Dispositivos móveis da Apple suportam Wi-Fi 7 (802.11be, 4096-QAM), mas possuem limitação física de arquitetura (2x2 MIMO e largura máxima de **160 MHz** / 2.882 Mbps teóricos) para controle térmico e evitar interferência nas bandas celulares 5G/UWB. Canais de 320 MHz plenos (até 5.764 Mbps) são aproveitados por placas Wi-Fi 7 completas de PC/notebook (Intel BE200, Killer BE1750) e celulares gamer selecionados (Snapdragon 8 Gen 3/4).
* **[AutoLearn - Arquitetura de DNS Dual-Stack de Alta Performance (Cloudflare & Google Anycast)]**:
  - Para eliminar gargalos e falhas de resolução causados por servidores DNS de provedores locais/regionais:
    - No `/etc/config/dhcp` (`dnsmasq`): Configurar `option noresolv '1'` (ignora `/tmp/resolv.conf.auto` da operadora), `option allservers '1'` (passa `--all-servers` para o daemon, disparando as consultas recursivas em paralelo a todos os servidores e entregando o primeiro a responder em 1-5 ms) e cadastrar as listas de servidores IPv4 e IPv6: `1.1.1.1`, `1.0.0.1`, `8.8.8.8`, `8.8.4.4`, `2606:4700:4700::1111`, `2606:4700:4700::1001`, `2001:4860:4860::8888`, `2001:4860:4860::8844`.
    - No `/etc/config/network` (`wan`): Configurar `option peerdns '0'` e replicar os servidores nas listas `dns`.
    - Isso mantém o cache local ultra veloz de 10.000 entradas do roteador, preserva a resolução de nomes locais da LAN (`.lan`) e distribui via DHCPv4 (`192.168.76.1`) e RDNSS IPv6 (`fdf3:6c8d:fbf3::1`) a rota mais rápida possível para todos os clientes.
* **[AutoLearn - Eliminação do Loop de Reinicialização de Interface CLAT (`wan_6_4` / 464xlat)]**:
  - Em conexões dual-stack nativas (IPv4 via PPPoE e IPv6 via DHCPv6-PD), a presença do pacote `464xlat` faz com que o script `/lib/netifd/dhcpv6.script` tente instanciar automaticamente a interface virtual `wan_6_4` (CLAT RFC 6877). Como o provedor não anuncia prefixo NAT64 (PLAT), o `464xlatcfg` falha com `CLAT_CONFIG_FAILED`, entrando em loop infinito de subida/descida a cada 3 segundos e inundando o `logread`.
  - A solução homologada consiste na remoção do script/pacote (`opkg remove 464xlat` e inclusão de `rm -f /lib/netifd/proto/464xlat.sh` no `/etc/rc.local`), garantindo que o `netifd` e `odhcp6c` operem em modo dual-stack nativo puro com logs 100% limpos.
* **[AutoLearn - UX e Polling Inteligente na Central Predator (`predator_wifi.js`)]**:
  - O status badge do cabeçalho agora reflete com precisão os estados de transição do roteador:
    - `"⏳ Inicializando / Calibrando..."` (âmbar suave) durante o boot a frio da placa PCIe QCN9224 (60-90s) ou recargas de driver.
    - `"⚠️ Travado (/var/run/wifilock)"` (vermelho) apenas em casos reais de deadlock do netifd.
    - `"✅ Operacional"` (verde brilhante) quando todos os 3 rádios estão ativos.
  - O polling é executado a cada 2 segundos via LuCI Poll API (`poll.add(..., 2)`), pausando automaticamente via `document.hidden` para economizar ciclos de CPU do navegador e do roteador quando a aba não estiver visível.
* **[AutoLearn - Roaming 802.11k/v em Rádios QCA (BSS Transition & Neighbor Reports)]**:
  - Por padrão, o OpenWrt/QSDK gerava `/etc/config/wireless` sem `bss_transition` nem `rrm_neighbor_report`. Com isso, o `hostapd` nunca anunciava capacidade de roaming aos clientes nem enviava quadros BTM.
  - O padrão homologado agora injeta `option bss_transition '1'`, `option rrm_neighbor_report '1'`, `option rrm_beacon_report '1'` e `option wnm_sleep_mode '1'` em todos os VAPs. Isso ativa a assistência nativa por hardware para troca transparente entre 2.4 GHz e 5 GHz (160 MHz) sem queda de conexão ou congelamento de VoIP/jogos.
* **[AutoLearn - Arquitetura Padrão Ouro de Wi-Fi 7 vs Armadilha do Tri-Band MLO]**:
  - O padrão IEEE 802.11be impõe WPA3-SAE obrigatório com PMF (`ieee80211w=2`) em todas as frequências agregadas em um grupo MLD.
  - Incluir a banda 2.4 GHz no MLD força o rádio 2.4 GHz para WPA3 puro, desconectando 99% das lâmpadas, tomadas e sensores IoT (Tuya, Sonoff, Shelly).
  - O perfil homologado definitivo é o **MLO Turbo**: 5 GHz (160 MHz) + 6 GHz (320 MHz) agregados sob MLD com WPA3-SAE para velocidades gigabit e latência zero, enquanto a banda de 2.4 GHz permanece totalmente independente em WPA2 puro (`psk2+aes`) para automação residencial.
* **[AutoLearn - Normalização de Criptografia no LuCI (`psk2+aes` vs `psk2`)]**:
  - O UCI armazena `encryption='psk2+aes'`. Quando os componentes `<select>` do LuCI em JavaScript só continham opções com `value: 'psk2'`, o navegador não casava o valor e exibia o seletor completamente vazio/em branco.
  - A correção homologada implementa normalização de strings antes do binding (`psk` / `psk2` -> `psk2+aes`) e disponibiliza `psk2+aes` explicitamente em todos os formulários.
* **[AutoLearn - Perfil 5: Rede Única Tri-Band (`single_ssid`)]**:
  - Permite configurar o mesmo SSID e senha nas 3 bandas (2.4G, 5G, 6G) mantendo criptografia cirurgicamente separada por rádio:
    - `wifi0_ap` (2.4 GHz): `psk2+aes` (WPA2 puro) para 100% de compatibilidade e pareamento sem falhas de dispositivos IoT (Tuya, Sonoff, ESP8266/ESP32).
    - `wifi1_ap` (5.0 GHz): `sae-mixed` (WPA2/WPA3 Misto) funcionando como ponte suave para evitar alertas de Downgrade Attack no iOS/Android.
    - `wifi2_ap` (6.0 GHz): `sae` (WPA3-SAE Puro com PMF obrigatório).
  - Conta com roaming 802.11k/v (BSS Transition + RRM Neighbor Reports) ativo para transição contínua dos celulares entre as 3 frequências e sincronização de 152 chaves de tradução entre `en`, `pt_br` e `es`.

