# PLAYBOOK DE COMANDOS HOMOLOGADOS - ACER PREDATOR CONNECT T7


## Entrada de contexto para IA

Leia este índice e as regras críticas; depois busque o assunto e leia seus trechos antes de executar comandos. O registro completo abaixo fica disponível para consulta por tema.

- Regras locais de investigação: [AGENTS.md](AGENTS.md).
- Índice de referências: [docs/README.md](docs/README.md).
- Computador, OpenWrt e critérios de evidência: [docs/IA-CONTEXTO.md](docs/IA-CONTEXTO.md).
- Estado e pendências da tarefa: [TASK.md](TASK.md).
- Arquivos e candidatos do CFG: [ARQUIVOS_MODIFICADOS_CFG.md](ARQUIVOS_MODIFICADOS_CFG.md).

**Antes de uma intervenção:** confirme versão e estado atuais, preserve acesso e recuperação e identifique o alvo físico. Os mapas e resultados registrados abaixo têm contexto próprio; não deduza o alvo de gravação apenas de nomes lógicos `rootfs`/`rootfs_1` nem trate uma observação anterior como estado atual.

**Leitura por assunto:** faça busca textual e extração limitada também em bytes/caracteres. Uma linha longa pode carregar muito contexto. Registre estado transitório no checkpoint e lições confirmadas na referência pertinente.

---

> **IMPORTANTE PARA AGENTES DE IA**: Consulte este arquivo antes de disparar qualquer comando SSH, Telnet ou script neste projeto. É proibido chutar comandos ou partições por tentativa e erro.

---

## 🛑 0. Armadilhas e Comandos Proibidos (DO-NOT-REPEAT — Leitura Obrigatória)

| ID | Subsistema | ❌ O que NUNCA fazer (Proibido) | 💥 Sintoma / Falha Causada | ✅ Solução Canônica Homologada |
| :--- | :--- | :--- | :--- | :--- |
| **DNR-01** | Watchdog / Boot | Executar `ubus call system watchdog '{"stop":true}'` ou `magicclose:true` | Reboot forçado pelo SoC Qualcomm exatamente 30s após parar alimentação | Manter `ubus call system watchdog '{"stop":false,"frequency":5}'`. |
| **DNR-02** | Wi-Fi 7 / QCN9224 | Usar `dp_mlo_reo_rings_map=0x7` em `QCN9224_i.ini` | Kernel Panic / Crash Q6 `ar_wal_mlo_ipc.c:1065 Assertion 0 failed` no boot | Fixar `dp_mlo_reo_rings_map=0` em `/ini/internal/QCN9224_i.ini` e `/cfg/default/ini/internal/QCN9224_i.ini`. |
| **DNR-03** | Driver QCA Boot | Disparar `wifi up` prematuro no `rc.local` ou `setCountryID 840` durante coldboot | Deadlock `State D` entre `insmod wifi_3_0` e `cfg80211tool` disputando probe lock | Aguardar fim do coldboot e neutralizar `setCountryID` prematuro em `set_default_country()`. |
| **DNR-04** | Failsafe Legacy | Manter `/etc/init.d/predator_dev` ativo contando uptime `< 75s` | Alterna partição de boot (`BOOTCONFIG`) em loop se houver reboot rápido | Manter `predator_dev` removido/desativado (`predator_dev.failsafe.enabled='0'`). |
| **DNR-05** | MLO vs Single-SSID | Ativar `mld0` Tri-Band MLO como padrão ou criar VAP secundária quando `mld0` existir | Queda de throughput em clientes legados, IP `169.254.x.x` ou kernel panic (`mlo_mbssid=0`) | Usar perfil Padrão Ouro **`single_ssid`** (`Predator_7G`, sem `mld0`) com `802.11k/v` + `rnr=1`. |
| **DNR-06** | SQM CAKE + PPPoE | Rodar CAKE na `eth0` com `split-gso` padrão ou com ECM SFE (`front_end_ipv4_stop=0`) ativo | Upload cai para `0.15 Mbps` (`-EPROTONOSUPPORT` em `0x8864`) e fluxos 6 GHz congelam no pacote #25 | Configurar `no-split-gso` em `eqdisc_opts`/`iqdisc_opts` e pausar SFE (`front_end_ipv4/v6_stop=1`) quando SQM estiver ativo. |
| **DNR-07** | QUIC / UDP 443 | Bloquear globalmente a porta `UDP 443` no firewall | Quebra HTTP/3 global e derruba túneis VPN corporativos (WireGuard/IPsec/MASQUE) | Usar filtragem seletiva via `dnsmasq` + `ipset` dinâmico (`quic_block_v4` / `quic_block_v6`). |
| **DNR-08** | WAN 2.5G (`eth0`) | Executar `ethtool --set-eee eth0 eee off` | PHY 2.5G não suporta flag EEE via ethtool e renegocia/derruba link WAN | Nunca invocar `--set-eee` na `eth0`. |
| **DNR-09** | Potência RF (`iw`) | Passar dBm direto em `iw dev athX set txpower fixed <valor>` (ex.: `26`) | Driver QSDK interpreta em **mBm** (`0.26 dBm`), derrubando alcance do Wi-Fi | Multiplicar sempre por 100 (`$((TX * 100))`, ex.: `2600` mBm = `26 dBm`). |
| **DNR-10** | Debloat / Firmware | Apagar `/cfg/default/ini`, parar `cnssdaemon` ou sobrescrever `bdwlan.b1015`/`b16` ou `mtd18` (`0:ART`) | `wifi config` quebra, PCIe QCN9224 falha QMI ou calibração RF de fábrica é perdida | Preservar `/cfg/default/ini`, `cnssdaemon -s` e arquivos BDF/`0:ART` intactos. |
| **DNR-11** | Hostname Sistema | Usar hostname com espaços (`Predator Connect T7`) em `/etc/config/system` | Viola RFC 1123, falha em leases DHCP de operadoras e quebra scripts POSIX | Usar estritamente `Predator-Connect-T7` (com hifens). |
| **DNR-12** | Empacotamento Mac | Criar `.cfg` ou `.tar.gz` no macOS sem `COPYFILE_DISABLE=1` | Arquivos `._*` quebram o parser UCI do OpenWrt | Usar `COPYFILE_DISABLE=1 tar --no-mac-metadata -czf`. |
| **DNR-13** | 5 GHz 240 MHz (`HT240`) | Passar `eht_oper_chwidth=4` em `hostapd-ath1.conf` no 5 GHz ou manter `puncture_strict=1` / typo `dfs_punctureEn` em `wifi1` | `hostapd` aborta em `dfs_get_start_chan_idx` (`DFS only VHT20..160 supported`) e `umac.ko` falha em `ieee80211_find_std_channel` (`0xf000` sem máscara 8-bit) | Em 5 GHz `HT240`, emitir `vht/he/eht_oper_chwidth=2` (`idx=114`) no `hostapd.sh` e configurar `mode 11AEHT320` + `puncture_bitmap=61440` + `dfs_puncture_en 1` + `puncture_strict 0` + `set_cactimeout 1` no `qcawificfg80211.sh`. |

### Índice Rápido do Playbook por Subsistema (Leitura Cirúrgica)
- **Seção 1 a 3**: Rede, SSH/Telnet (`root0100`), Dual-Boot A/B (`/sys/class/ubi/ubi0/mtd_num`) e Mapa MTD.
- **Rádio Wi-Fi 7, BDF, Canais e MLO vs Single-SSID**: Entradas `[AutoLearn]` de RF, `qca-hapd-supp`, `HT80`/`HT160` e `single_ssid`.
- **WAN, PPPoE, MSS Clamping, IPSet QUIC, DoH e IPv6**: Entradas de `https-dns-proxy` (`5053`/`5054`), `quic_block_v4/v6`, `ra_management='1'` e `wireguard.ko`.
- **SQM CAKE, KSMBD, WISP e Pacote Master v2**: Entradas finais (`no-split-gso`, ECM SFE, `ksmbd-disk-tool`, `wifi-wisp-tool`, `60_wifi.js` e cifra OEM `r1`/`n`).

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
* **[AutoLearn - Credenciais e Redes Homologadas]** *(🔄 [SUPERADO POR Padrão Master v2: SSID único `Predator_7G` / senha `Predator0@` / `root0100`])**:
  - Web UI (LuCI porta 80/443), SSH (porta 22) e Telnet (porta 23): Usuário `root` | Senha: `root0100`
  - SSID Homologado Unificado: `Predator_7G` (Tri-Band: 2.4 GHz, 5 GHz e 6 GHz)
  - Senha Wi-Fi padrão: `Predator0@`
  - Largura de Banda 5 GHz Padrão: `80 MHz` (`HT80` nos canais 36-48 non-DFS para boot instantâneo em 2s, configurável para 160 MHz no LuCI)
  - SQM (Cake QoS): Configurado por padrão como `enabled '0'` para vazão bruta de 2.5 Gbps via PPE

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
* **[AutoLearn - Arquitetura Padrão Ouro de Wi-Fi 7 vs Armadilha do Tri-Band MLO]** *(🔄 [SUPERADO POR `single_ssid` sem `mld0` — ver entrada Padrão Ouro Definitivo abaixo])**:
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
* **[AutoLearn - Rollback Inteligente Dinâmico por Contexto no LuCI Nativo (`uci.lua` + `ui.js`)]**:
  - Em vez de um timeout estático exagerado (ex: 300s para tudo), o LuCI nativo (`/usr/lib/lua/luci/model/uci.lua`, `/usr/lib/lua/luci/controller/admin/uci.lua` e `/www/luci-static/resources/ui.js`) inspeciona automaticamente `ubus call uci changes` antes de aplicar:
    - **Alterações comuns (LAN, Firewall, DHCP, DNS, Sistema)**: mantém **`90s`**, garantindo recuperação rápida caso o usuário erre um IP ou regra de firewall.
    - **Alterações de Wireless padrão (80 MHz / 2.4G / 6G sem DFS)**: eleva dinamicamente para **`140s`**, cobrindo com folga os ~30s de reinício dos 3 rádios Qualcomm e reconexão Wi-Fi.
    - **Alterações de Wireless com 5 GHz em 160 MHz (`HT160`) ou Canal DFS (`52–144` / `auto`)**: eleva dinamicamente para **`210s`**, absorvendo os 60s obrigatórios de escuta de radar CAC + ~30s de reinício do driver sem falso rollback.
* **[AutoLearn - Suporte a Repetidores Universais (WDS 4-Address) e Leases DHCP Persistentes]**:
  - Todos os VAPs AP (`wifi0_ap`, `wifi1_ap`, `wifi2_ap` e novos VAPs criados no daemon `predator`) possuem `option wds '1'` (e `cfg80211tool athX wds 1` no `predator_rf`), habilitando quadros 4-address na camada 2 para repetidores universais (ex: Intelbras RG 1200).
  - O `dnsmasq` utiliza `/etc/dnsmasq.conf` com `dhcp-broadcast` ativo e `option leasefile '/etc/dhcp.leases'` (com symlink `/tmp/dhcp.leases -> /etc/dhcp.leases` no `/etc/rc.local`), garantindo que impressoras 3D (Creality) e dispositivos IoT nunca sumam da lista de leases após reboot.
* **[AutoLearn - Permissões KSMBD USB Plug-and-Play (`0777` + `root`)]**:
  - Removido o atributo inválido `option force_user 'Admin'` (que sobrescrevia `force user = root` com um usuário inexistente no `/etc/passwd`) e adicionados `option force_create_mode '0777'` e `option force_directory_mode '0777'` em `/etc/config/ksmbd`, liberando leitura/escrita imediata sem intervenção manual.
* **[AutoLearn - Causa Raiz e Correção do Bug de DHCP no MLO (`mld0` fora da `br-lan` -> IP `169.254.x.x`)]**:
  - Quando os perfis MLO (`mlo_turbo` 5G+6G ou `mlo_full` 2.4G+5G+6G) eram ativados, o tráfego de dados dos clientes passava pela interface virtual `mld0`. Contudo, no `/sbin/wifi`, o laço `for device in ${2:-$DEVICES}; do ( ... ); done` roda em subshell, deixando `$device` vazio ao chamar `post_qcawificfg80211`. Na linha 8347 de `/lib/wifi/qcawificfg80211.sh`, `config_get type "$device" type` retornava vazio e abortava a função antes de chamar `add_mld_bridge`. Além disso, o `do_apply_topology` executava `brctl addif br-lan mld0` **antes** do `wifi reload` terminar.
  - Solução implementada em 3 camadas: (1) inicialização de `[ -z "$device" ] && device=$(echo ${2:-$DEVICES} | awk '{print $1}')` no topo de `post_qcawificfg80211` + `ifconfig $mld up` dentro de `add_mld_bridge` (`/lib/wifi/qcawificfg80211.sh`); (2) execução de `brctl addif br-lan mld0; ifconfig mld0 up` **após** o `wifi reload` no `/usr/libexec/rpcd/predator`; e (3) verificação no boot pelo `/etc/init.d/predator_rf`.
* **[AutoLearn - Toggle 4096-QAM (Wi-Fi 7 vs Wi-Fi 6E) sem Derrubar o Rádio 6 GHz (`wifi2`)]**:
  - Desativar o toggle `qam4096` gravava `hwmode='11ax'` mantendo `htmode='HT320'` no `wifi2`. No driver QCA (`/lib/wifi/qcawificfg80211.sh`), o modo Wi-Fi 6E em 6 GHz exige nomenclatura `11axa` e largura máxima `HT160` (`11AHE160`), pois `HT320` só existe em `11bea` (Wi-Fi 7).
  - Solução implementada: ao desligar `qam4096`, o daemon `/usr/libexec/rpcd/predator` configura `hwmode='11axa'` e reduz `HT320 -> HT160` (e restaura `11bea` + `HT320` ao religar), além de fallback explícito `*axa:HT320) hwmode=11AHE160;;` em `/lib/wifi/qcawificfg80211.sh`.
* **[AutoLearn - Timer de Sincronização da Central Predator (`safeReloadAfterRestart` 45s / Teto 90s)]**:
  - Em `predator_wifi.js`, o modal de contagem regressiva exibia 20s com corte forçado em 35s, o que causava recarregamento prematuro da página quando o usuário aplicava configurações conectado via Wi-Fi ou em canais DFS (60s CAC). O contador visual foi ajustado para `45s` e o teto de segurança para `90s`, mantendo o *early-exit* rápido a partir de `8s` (quando os 3 rádios já responderem `online` via cabo, conclui em ~10–12s).
* **[AutoLearn - NTP Inteligente Anycast Mundial + Auto-Detecção Global de Fuso Horário (`/etc/hotplug.d/iface/25-ntp-smart`)]**:
  - O arquivo `/etc/config/system` inclui a seção `config timeserver 'ntp'` habilitada com servidores Anycast globais (`time.cloudflare.com`, `time.google.com`), GeoDNS (`0.openwrt.pool.ntp.org`, `1.openwrt.pool.ntp.org`) e Stratum-1 nacional (`a.st1.ntp.br`).
  - Na subida da WAN (`ifup` ou boot), o hook `/etc/hotplug.d/iface/25-ntp-smart` executa *Fast-Sync* imediato (`ntpd -q`) e, caso o fuso horário ainda esteja no padrão inicial `'UTC'`, detecta automaticamente o país/cidade do IP público via Geo-IP (`ip-api.com` / `ipwho.is`), consulta a string POSIX correspondente no banco nativo do LuCI (`ubus call luci getTimezones`) e aplica `zonename` + `timezone` automaticamente para qualquer país ou estado do mundo, respeitando qualquer alteração manual feita posteriormente pelo usuário no LuCI.
* **[AutoLearn - Higienização Obrigatória da WAN no `.cfg` Público]**:
  - O arquivo `/etc/config/network` empacotado dentro do `cfg_restauracao_master_v2.cfg` DEVE manter `config interface 'wan'` sempre em modo genérico `option proto 'dhcp'` sem `macaddr` clonado e sem credenciais PPPoE pessoais. Credenciais PPPoE de bancada devem existir exclusivamente no roteador físico local, nunca no pacote `.cfg` distribuído no repositório.
* **[AutoLearn - Auto-Bringup Resiliente do Wi-Fi 7 no Boot a Frio (`predator_rf` + `rc.local`)]**:
  - Na inicialização a frio, o chip PCIe QCN9224 (6 GHz) leva ~25–30 segundos para calibrar o firmware (`cnss2`). Como o `/etc/init.d/network` roda prematuramente aos 18 segundos, os VAPs não subiam sozinhos após a remoção dos daemons proprietários da Acer (`wifi_status`).
  - O `/etc/init.d/predator_rf` (`START=99`) e a seção 7 do `/etc/rc.local` agora realizam verificação ativa (`[ -d /sys/class/net/ath2 ] && [ -d /sys/class/net/ath0 ]`): se as interfaces não estiverem no ar após a janela de calibragem, executam automaticamente `/sbin/wifi up`, garantindo que todos os 3 rádios subam 100% no ar em qualquer reboot a frio.
* **[AutoLearn - Resolução Definitiva de Falha em Fast.com / Waveform / CDNs (TCP MSS Clamping & PMTUD Blackhole em PPPoE)]**:
  - **Causa Raiz**: O link PPPoE possui MTU física de **1492** bytes. Clientes LAN/Wi-Fi (smartphones, PCs, Macs) conectam por padrão com MTU **1500** (MSS 1460 em IPv4 e 1440 em IPv6). Em sites com tráfego massivo e CDN Dual-Stack como `Fast.com` (Akamai IPv6) e `Waveform.com` (Cloudflare IPv4), os servidores enviam segmentos TCP de tamanho máximo com a flag DF (*Don't Fragment*). Como o BRAS/provedor descarta pacotes > 1492 bytes e o IPv6 não permite fragmentação intermediária por roteadores, conexões entravam em *PMTUD Blackhole* e congelavam indefinidamente.
  - **Solução Homologada em 3 Camadas**:
    1. `/etc/firewall.user`: Injeção de clamping explícito no mangle:
       - IPv4: `iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 1453:1536 -j TCPMSS --set-mss 1452`
       - IPv6: `ip6tables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 1433:1536 -j TCPMSS --set-mss 1432`
    2. `/etc/config/dhcp`: Adicionar `option ra_mtu '1492'` e `list dhcp_option '26,1492'` nas seções `lan`, `guest` e `iot`, instruindo o `odhcpd` (IPv6 RA) e o `dnsmasq` (DHCPv4) a informarem nativamente aos dispositivos clientes que o MTU do caminho é 1492.
    3. `/etc/config/firewall`: Inclusão de `list network 'wan_6'` na zona `wan` para garantir que a interface virtual dinâmica de IPv6 criada sobre o PPPoE herde todas as políticas de MTU fix e encaminhamento.
* **[AutoLearn - Limitação de Silício Qualcomm IPQ5332 (mlo_mbssid disabled) e Blindagem de Redes Adicionais]**:
  - **Limitação de Hardware**: O driver Qualcomm SPF-12.2 acusa explicitamente `mlo_mbssid disabled in lower band radios` ao criar VAPs secundários com MLD nas bandas baixas (2.4 GHz e 5 GHz). Criar uma segunda rede com MLO enquanto a principal já existe causa falha no hardware (`MLO peer create failed`), gerando um enlace zumbi onde dispositivos (ex: iPad) desconectam continuamente e perdem pacotes de dados.
  - **Arquitetura Homologada**: O recurso Wi-Fi 7 MLO (Multi-Link Operation) deve ser ativado exclusivamente na **Rede Principal** (através do **Perfil 4: MLO Turbo** ou **Perfil 3: Tri-Band MLO** no topo do painel), onde opera com 100% de estabilidade e suporte direto de silício.
  - **Blindagem em 3 Camadas**:
    1. No painel LuCI (`predator_wifi.js`), o checkbox de agrupar em MLO foi removido do modal "Criar Nova Rede" e substituído por uma caixa informativa direcionando para o Perfil 4;
    2. O modal valida ativamente tamanho mínimo de 8 caracteres para senhas de redes protegidas;
    3. O backend `/usr/libexec/rpcd/predator` (`do_add_vif`) opera defensivamente tratando todas as redes adicionais como VAPs multi-banda padrão (`wds '1'`, `rrm '1'`, `bss_transition '1'`), garantindo bridging correto na `br-lan` e escrita mandatória de chaves de criptografia (`psk2+aes` e `sae`).
* **[AutoLearn - Gerador Inteligente de Restauração Personalizada (`dev/gerar_cfg_personalizado.py`)]**:
  - Restaurar backups legados/brutos de outros usuários (ex: `backup-PREDATOR-*.tar.gz`) sobrescreve e destrói 100% das otimizações homologadas (MSS clamping, debloat, Anycast DNS, coldboot bringup, roaming k/v) e reintroduz centenas de arquivos de telemetria da Acer.
  - O procedimento homologado é utilizar `dev/gerar_cfg_personalizado.py`, que extrai automaticamente do backup antigo do usuário os parâmetros estritamente pessoais (MACs de hardware dos rádios, IP de LAN, SSIDs, senhas Wi-Fi e hash de root) e os mescla na base ouro `cfg_restauracao_master_v2.cfg`. O arquivo gerado (~33 KB) sobe pronto para restauração no LuCI preservando toda a suíte de otimizações do projeto.
* **[AutoLearn - PROIBIDO: `ethtool --set-eee eth0` na WAN 2.5G (registro anterior estava ERRADO)]**:
  - Executar `ethtool --set-eee eth0 eee off` no PHY da WAN (`nss-dp 3a504000.dp1`, PHYAD 4) gera `WARNING ... phy_error+0x20/0x4c` no kernel e deixa a porta em `Speed: 10Mb/s Half / Link detected: no`. Resultado: PPPoE cai e o roteador fica sem internet.
  - Recuperação homologada: remover qualquer linha `set-eee` do `/etc/rc.local` e rodar `/etc/init.d/network restart` (reinicializa o PHY). ATENÇÃO: `network restart` derruba o Dropbear se `dropbear.@dropbear[0].enable='0'`; manter `enable='1'` no UCI (o Telnet porta 23 serve de acesso reserva).
  - O flapping da WAN (`PHY Link is down` a cada 10–20 s, a 1000 Mbps) com a ONT LinqTelecom **continua SEM causa raiz confirmada**. Não aplicar "correções" de PHY às cegas; investigar cabo/ONT/negociação primeiro.
* **[AutoLearn - Sistema Antiburro e Auto-Rollback do Wi-Fi (`predator-wifi-guard`)]**:
  - **Problema**: Erros de digitação ou configurações inválidas de Wi-Fi (ex: redes criptografadas sem senha, senhas < 8 caracteres, caracteres especiais não escapados no SSID como aspas e ponto-e-vírgula, seleção de larguras inexistentes no hardware como 160 MHz no canal 149 ou 320 MHz no 2.4/5G, descompasso entre `key` e `sae_password`, ou tentativa de MBSSID com MLO) quebravam o `hostapd`, entravam em loop de crash e derrubavam as redes sem recuperação automática.
  - **Solução Homologada em 4 Camadas**:
    1. **LuCI UI (`predator_wifi.js`)**: Validação de SSID (1-32 chars, regex contra `['"`;\\]`), aviso de clientes desconectados na troca de perfil, validação estrita de senha (8-63 chars) e **autopreenchimento obrigatório da senha existente** quando o campo de senha for deixado em branco ao editar uma rede existente ou mudar de perfil.
    2. **Backend RPCD (`/usr/libexec/rpcd/predator`)**: Validações defensivas nos métodos `apply_topology`, `edit_vif` e `add_vif`; auto-pull da senha do UCI (`wireless.$SEC.key`) se o campo vier vazio; chamada obrigatória a `predator-wifi-guard fix` pré-aplicação e disparo do cão de guarda em background.
    3. **Sanitizador Pré-Aplicação (`/usr/sbin/predator-wifi-guard fix` integrado ao `/sbin/wifi`)**: Executado antes de qualquer `wifi reload` ou `wifi up` (cobrindo CLI, LuCI e daemons). Força limites físicos de hardware (2.4G <= 40 MHz; 5G <= 160 MHz apenas nos canais 36-64/100-128; 6G WPA3-SAE obrigatório; remoção de MLO de redes secundárias; sincronização automática de `sae_password` com `key`).
    4. **Watchdog e Auto-Rollback (`/usr/sbin/predator-wifi-guard verify`)**: Aguarda a subida dos rádios e valida se atingiram `state=ENABLED` ou `DFS`. Se o subsistema falhar após 15 tentativas (75s), restaura automaticamente a última configuração boa (`/etc/predator/wireless.lastgood`), salva a defeituosa em `/etc/predator/wireless.failed`, faz um reinício limpo do hostapd e gera notificação visual no painel LuCI com botão "Entendido".
* **[AutoLearn - Permissões de Arquivos Web no LuCI (`/www/`) e Erro HTTP 403 Forbidden]**:
  - **Problema**: Ao transferir arquivos estáticos de JavaScript (`.js`), HTML ou ACL (`.json`) do macOS para o roteador via SCP, os arquivos podem herdar permissão restritiva `0700` (`-rwx------`). Quando o navegador tenta carregar a classe LuCI, o servidor `uhttpd` rejeita a leitura e exibe `NetworkError: HTTP error 403 while loading class file "/luci-static/resources/view/predator_wifi.js"`.
  - **Solução Homologada**: Aplicar permissão de leitura pública `chmod 644` em arquivos estáticos (`/www/luci-static/resources/view/*.js`, `/usr/share/rpcd/acl.d/*.json`, `/usr/share/luci/menu.d/*.json`) e `chmod 755` em executáveis (`/usr/sbin/predator-wifi-guard`, `/sbin/wifi`, `/usr/libexec/rpcd/predator`), seguido de reinício do `rpcd` e `uhttpd`.
* **[AutoLearn - Suporte a `sae-mixed` (WPA2/WPA3 Misto) no Driver QCA (`/lib/wifi/hostapd.sh`)]**:
  - **Problema**: O script proprietário `/lib/wifi/hostapd.sh` da Qualcomm/Acer só testava `*psk*` nos blocos de `keymgmt`. Ao configurar `option encryption 'sae-mixed'`, o script caía no fallback `*)` e gerava configuração de WPA3 Puro (`wpa_key_mgmt=SAE`, `ieee80211w=2`), impedindo dispositivos WPA2 legados de conectarem no 5 GHz.
  - **Correção Homologada**: Injetar `*sae-mixed*` ao lado de `*psk*` nas linhas 802, 828, 889 e 920 de `/lib/wifi/hostapd.sh`. Com isso, o hostapd gera fielmente `wpa_key_mgmt=WPA-PSK SAE` com `ieee80211w=1` (PMF Opcional), permitindo que aparelhos modernos (iPhone, Mac, PCs) negociem WPA3-SAE e aparelhos antigos conectem em WPA2-PSK sem avisos de segurança no iOS.
* **[AutoLearn - Diagnóstico Definitivo Waveform.com / Cloudflare Turnstile em 5G/6G]**:
  - **Criptografia Wi-Fi vs Navegação Web**: A criptografia Wi-Fi (L2) não interfere no tráfego HTTP/HTTPS. No rádio de 6 GHz, WPA3-SAE puro (`ieee80211w=2`) é mandatório por norma internacional (WPA2 é proibido em 6 GHz). No 5 GHz, WPA2/WPA3 Misto (`sae-mixed`) é o padrão ouro.
  - **Causas Reais de Bloqueio/Congelamento no Waveform.com**:
    1. **Prefixo IPv6 Morto (`deprecated`) na `br-lan`**: Ao reiniciar a WAN PPPoE, a operadora pode delegar um novo prefixo IPv6 enquanto o kernel mantém o antigo como obsoleto. Como o Cloudflare (`challenges.cloudflare.com`) responde em IPv6, clientes nas bandas rápidas tentavam rotear pacotes pelo prefixo morto gerando timeout. Solução: limpar prefixos residuais via `ip -6 addr del <prefixo_morto> dev br-lan` e reiniciar o `odhcpd`.
    2. **Apple "Limitar Rastreamento de Endereço IP" (iCloud Private Relay)**: Ao conectar em SSIDs novos de 5 GHz ou 6 GHz, o iOS ativa por padrão a proteção de rastreamento de IP. Os proxies de saída da Apple sofrem bloqueio/desafio severo pelo Cloudflare Turnstile no Waveform.com. Solução no celular: nos Ajustes do Wi-Fi da rede conectada (ícone "i"), desligar "Limitar Rastreamento de Endereço IP".
* **[AutoLearn - Topologia Real dos Rádios no Silício (SoC AHB vs PCIe DualMAC QCN9224)]**:
  - **Mapeamento Físico Comprovado via Sysfs**:
    - `ath0 / phy1` (2.4 GHz): Conectado diretamente ao SoC IPQ5332 pelo barramento AHB (`/sys/devices/platform/soc/c000000.wifi`).
    - `ath1 / phy2` (5 GHz) **E** `ath2 / phy3` (6 GHz): **Compartilham o MESMO endpoint PCIe externo (`0001:01:00.0`, PCI ID `17cb:1109`, família QCN9224/QCN6274 DualMAC, com `num_radios=2`)**.
    - Ambos os rádios de alta frequência (5G e 6G) utilizam o firmware `amss_dualmac.bin`. Qualquer instabilidade ou crash com reinicialização de subsistema (SSR) no barramento PCIe derruba simultaneamente as bandas de 5 GHz e 6 GHz.
  - **Limitação de Largura de Banda no MLO Turbo**: No perfil MLO Turbo, o rádio de 5 GHz opera estavelmente em **80 MHz** (`HT80` no Canal 36) e o de 6 GHz em **320 MHz** (`HT320` no Canal 37 PSC). A banda de 2.4 GHz permanece 100% independente em WPA2 puro para IoT.
* **[AutoLearn - Compatibilidade Universal de IPv6 no iOS/Android (SLAAC `ra_management '1'` vs Stateful '2')]**:
  - **Problema**: O firmware OEM da Acer vinha com `option ra_management '2'` (Stateful DHCPv6) e `option ra 'hybrid'` com `option interface 'wan6'` (descasado da interface PPPoE dinâmica `wan_6`).
  - **Causa Raiz**: O iOS (iPhone/iPad) e o Android por especificação deliberada (RFC 4862) **NÃO implementam cliente DHCPv6 Stateful** (apenas SLAAC). Ao entrar em redes rápidas (5G/6G MLO) onde o iOS força o Happy Eyeballs para IPv6, a falta de SLAAC autônomo fazia o handshake TLS congelar, gerando timeout exibido no Safari como "Erro de Certificado SSL / Não foi possível estabelecer conexão segura" em sites como Speedtest e Waveform.
  - **Solução Homologada**:
    1. Configurar `ra='server'`, `dhcpv6='server'` e `ra_management='1'` (SLAAC + Stateless DHCPv6) em todas as interfaces locais (`lan`, `guest`, `iot`);
    2. Ajustar `dhcp.wan6.interface='wan_6'` para amarrar perfeitamente a interface dinâmica do PPPoE;
    3. Manter `ra_mtu '1492'`, `dhcp_option '26,1492'` e clamping de MSS IPv6 (`1432`);
    4. Sincronizar as configurações de DHCP no pacote `cfg_restauracao_master_v2.cfg`.
* **[AutoLearn - Resolução de Erros `NSURLErrorDomain` no Safari (Fallback Rápido de HTTP/3 QUIC UDP 443 em PPPoE)]** *(🔄 [SUPERADO POR Filtragem Seletiva de QUIC via IPSet Dinâmico `quic_block_v4`/`v6` no Pacote Master v2])**:
  - **Problema**: O Safari no iOS/macOS gerava exceções de `NSURLErrorDomain` (como erro `-1200` SSL / `-1005` Conexão Perdida / `-1001` Timeout) ao carregar sites hospedados em CDNs como Cloudflare (Waveform.com e Speedtest.net).
  - **Causa Raiz**: O protocolo HTTP/3 (QUIC) opera sobre UDP na porta 443. Diferente do TCP (que possui MSS Clamping a 1452/1432), o UDP não tem negociação de MSS. As CDNs enviam datagramas UDP com 1500 bytes (MTU padrão de Ethernet). No link PPPoE da WAN (MTU 1492), qualquer pacote UDP > 1492 bytes com DF é descartado silenciosamente pela operadora (*UDP MTU Blackhole*). O Safari ficava aguardando os pacotes UDP que nunca chegavam, sofria timeout e abortava a conexão.
  - **Solução Homologada**:
    - Injetar no topo da cadeia `FORWARD` de `/etc/firewall.user`:
      `iptables -I FORWARD 1 -p udp --dport 443 -j REJECT --reject-with icmp-port-unreachable`
      `ip6tables -I FORWARD 1 -p udp --dport 443 -j REJECT --reject-with icmp6-port-unreachable`
    - Com a rejeição explícita via ICMP em 0.1 ms, o Safari e o Chrome sabem instantaneamente que o HTTP/3 não está disponível e realizam fallback imediato para HTTP/2 sobre TCP (que é 100% clampado a 1452/1432 bytes), abrindo as páginas no iOS em menos de 50 ms sem qualquer erro de certificado.
* **[AutoLearn - Padrão Ouro Definitivo: Rede Única Tri-Band (`single_ssid`) sem MLO no CFG Master]**:
  - **Problema**: O perfil MLO Turbo (`mld0`) agrupando 5 GHz e 6 GHz causava 7.822 erros de transmissão (TX Errors) e travamento total de testes de velocidade (Speedtest) e Bufferbloat (Waveform) quando clientes Wi-Fi 5 (802.11ac) e Wi-Fi 6/6E (802.11ax, como o iPhone em modo `[HE][6GHZ]`) conectavam à rede, pois dispositivos pré-Wi-Fi 7 não suportam o protocolo MLO e a camada de tradução do driver Qualcomm descartava os quadros na ponte `mld0`.
  - **Solução Homologada Definitiva**:
    1. A **Rede Única Tri-Band (`single_ssid`)** foi adotada como o padrão definitivo absoluto no `cfg_restauracao_master_v2.cfg`;
    2. A interface virtual `mld0` foi eliminada: os rádios `ath0` (2.4G), `ath1` (5G) e `ath2` (6G) conectam-se diretamente à ponte `br-lan`, eliminando 100% dos erros de TX;
    3. Criptografia híbrida inteligente: 2.4 GHz em WPA2 puro (`psk2+aes`) para IoT; 5.0 GHz em WPA2/WPA3 Misto (`sae-mixed`) para Wi-Fi 5/6; e 6.0 GHz em WPA3 puro (`sae`) em 320 MHz;
    4. Roaming 802.11k/v ativo para alternância transparente entre bandas;
    5. Injeção de `list dhcp_option '6,1.1.1.1,8.8.8.8'` no `/etc/config/dhcp` para entrega automática de DNS Cloudflare e Google aos clientes.
* **[AutoLearn - Sintaxe Exata do Comando iw txpower no QSDK (Unidade Obrigatória em mBm)]**:
  - **Causa Raiz**: O utilitário padrão `iw` do Linux Wireless (`iw dev <dev> set txpower fixed <val>`) opera estritamente em **mBm** (mili-dBm, onde 100 mBm = 1 dBm). O envio de comandos com valores puros em dBm (ex: `fixed 20`) é interpretado como 20 mBm (0.20 dBm); como 0.20 dBm está abaixo do piso mínimo de calibração do FEM, o driver descarta o comando e mantém a potência anterior inalterada.
  - **Procedimento Homologado**: Todo comando `iw` disparado por scripts ou deamons (`rpcd/predator`, `predator_rf`) DEVE multiplicar o valor em dBm por 100 antes da execução:
    - 20 dBm: `iw dev ath2 set txpower fixed 2000`
    - 22 dBm: `iw dev ath0 set txpower fixed 2200`
    - 23 dBm: `iw dev ath1 set txpower fixed 2300`
    - 26 dBm: `iw dev ath1 set txpower fixed 2600` (U-NII-3 em 80 MHz)
* **[AutoLearn - Termometria Real Qualcomm e Governança de Duty Cycle vs Falsos Alarmes]**:
  - **Funcionamento Físico**: O SoC IPQ5332 e o rádio PCIe QCN9224 operam normalmente em temperaturas elevadas de junção (78–88 °C em idle ou carga moderada).
  - **Política de Proteção**: O subsistema Qualcomm opera via mitigação por *Duty Cycle* (`dcoffpercent` configurável via `thermaltool -i wifiX -get -g`), e NÃO por desligamento abrupto de transistores:
    - **Nível 0 (Normal / 100% Rendimento)**: até 105 °C (5G/6G) e 110 °C (2.4G) com 0% de corte.
    - **Nível 1 (Mitigação Suave)**: 50% de redução de duty cycle (dcoff=50).
    - **Nível 2 (Mitigação Moderada)**: 90% de redução de duty cycle (dcoff=90).
    - **Nível 3 (Mitigação Máxima RF)**: 100% de tempo de repouso (dcoff=100) em 120 °C (5G/6G) e 125 °C (2.4G).
    - **Trip Point Crítico do Kernel**: 125 °C no sensor tsens do SoC ativa reinicialização de segurança preventiva.
  - **Leitura Homologada**: A verificação de throttling deve ser extraída exclusivamente do campo `current level` do comando `thermaltool -i wifiX -get -g`, sem recorrer a comparações sintéticas por constantes arbitrárias no frontend.
* **[AutoLearn - Inviolabilidade dos Arquivos BDF de Calibração (bdwlan.b1015 e b16)]**:
  - **Aviso Crítico de RF**: O Predator T7 utiliza tabelas de calibração RF exclusivas de sua placa e antenas (`bdwlan.b1015` para o chip PCIe e `bdwlan.b16` para o SoC).
  - Roteadores concorrentes de mesma base (ex: Cudy WR11000) utilizam BDFs distintos (`bdwlan.b1019`).
  - **PROIBIÇÃO ABSOLUTA**: JAMAIS sobrescrever `/lib/firmware/qcn9224/bdwlan.b1015` por arquivos BDF de outros produtos. A troca de BDF causa descasamento de impedância nos FEMs Skyworks, perda drástica de potência de recepção (RSSI), espúrios fora da máscara espectral e risco real de queima dos amplificadores.
* **[AutoLearn - Avaliação de ABI dos Módulos do Cudy 2.5.34 vs Binários Userspace]**:
  - **Módulos de Kernel (.ko)**: Embora os módulos do Cudy WR11000 firmware 2.5.34 sejam ELF32 ARMv7 e compartilhem o vermagic exato do T7 (`5.4.213 SMP preempt mod_unload ARMv7 p2v8`), eles chamam símbolos de kernel inexistentes na compilação da Acer (`__netdev_alloc_skb_fast` e `pcie_parf_read`). O carregamento via `insmod` falha por símbolos não resolvidos.
  - **Binários de Espaço de Usuário (`hostapd` e `wpa_supplicant`)**: Possuem **100% de compatibilidade dinâmica (560 símbolos resolvidos)** com a `libc`/`libubox`/`libnl` do T7, constituindo o caminho seguro e homologado para atualização de rotinas MLO de userspace sem risco de instabilidade no kernel.
* **[AutoLearn - Desmistificação de Bloqueios de Software vs Silício (mlo_mbssid)]**:
  - A restrição documentada no log como `mlo_mbssid disabled in lower band radios` é um parâmetro de perfil de compilação da árvore QSDK SPF-12, e NÃO uma incapacidade física universal de silício do IPQ5332.
  - O scaffolding original de `/lib/wifi/qcawificfg80211.sh` suporta até 10 MLDs (`mld0` a `mld9`). O limite de uma única rede MLO na Central decorre do escopo de gerência da aplicação `/usr/libexec/rpcd/predator`, que centraliza o controle exclusivamente no grupo `mld0`.
* **[AutoLearn - Inventário Rigoroso e Incorporação ao CFG Master (`ARQUIVOS_MODIFICADOS_CFG.md`)]**:
  - Toda modificação realizada no projeto é formalmente catalogada em `ARQUIVOS_MODIFICADOS_CFG.md` contendo caminho no roteador, arquivo Git correspondente, justificativa e status de validação.
  - **Regra de Ouro**: Nenhum arquivo modificado deve ser inserido no arquivo de restauração mestre `cfg_restauracao_master_v2.cfg` antes de alcançar 100% de validação em produção em bancada, estabilidade térmica e aprovação expressa do usuário.
* **[AutoLearn - Invocação do Binário Multicall QSDK (`qca-hapd-supp`) via Shell Wrapper]**:
  - O binário `qca-hapd-supp` da Qualcomm/Cudy 2.5.34 (hostapd v2.11-devel) inspeciona diretamente `argv[0]` via `strncmp(name, argv[0], strlen(argv[0]))` para chavear internamente entre os daemons `hostapd` e `wpa_supplicant`.
  - Quando chamado por caminho absoluto (ex: `/usr/sbin/hostapd` ou `/tmp/hostapd`), o `argv[0]` contém o prefixo de diretório e o binário aborta com `Invalid command. Usage: %s wpa_supplicant|hostapd`.
  - **Padrão Homologado**: Criar wrappers `/usr/sbin/hostapd` e `/usr/sbin/wpa_supplicant` usando `exec -a hostapd /usr/sbin/qca-hapd-supp "$@"` e `exec -a wpa_supplicant /usr/sbin/qca-hapd-supp "$@"`. Isso garante 100% de compatibilidade em qualquer invocação do sistema (`procd`, init scripts, CLI).
* **[AutoLearn - Limite Espectral de 5 GHz vs 6 GHz (Inexistência de 240 MHz em 5 GHz)]** `🔄 [SUPERADO POR #AL-T7-065]`:
  - *(Registro histórico superado)*: Antes do disassembly de `wlan_get_320_center_freq` (`0x1e80bc` em `umac.ko`), supunha-se que 240 MHz só existia em 6 GHz. Veja `#AL-T7-065` para a implementação real de 240 MHz (`11AEHT320` com `ccfs=130` e `puncture_bitmap=61440`) em 5 GHz e 6 GHz.
* **[AutoLearn - Topologia de Silício MLO Tri-Band Obrigatória (`/ini/mlo_config.ini`)]**:
  - **Problema**: O driver de hardware Qualcomm (`wifi_3_0.ko`, `qca_ol.ko`) exige uma matriz de adjacência de silício para gerenciar as filas de reordenamento de pacotes (`dp_mlo_reo_rings_map=0x7`) entre os chips. No script original da Acer, a função `create_mlo_config()` checava apenas `grep -c ipq9574`; como o T7 é `ipq5332`, o arquivo `/ini/mlo_config.ini` nunca era gerado, deixando o driver cego para o tráfego MLO cross-chip.
  - **Solução Homologada**: Gerar `/ini/mlo_config.ini` com perfil `ap-mi01` (3 chips, Chip 0 integrado + Chips 1/2 PCIe, 256 peers), e atualizar `/lib/wifi/qcawificfg80211.sh` com suporte à família `ap-mi01`.
* **[AutoLearn - Isolamento de Arquivos e Locks de MLD no Hostapd (`mld_link_id`)]**:
  - **Problema**: Em redes MLO onde múltiplos rádios (5 GHz e 6 GHz) compartilham o mesmo nome lógico de interface (`ifname=mld0`), o script de inicialização antigo gerava o arquivo estático `/var/run/hostapd-mld0.conf` e criava `/var/run/hostapd-mld0.lock`. Quando o segundo rádio subia, ele sobrescrevia a configuração do primeiro rádio ou era abortado pelo lock existente.
  - **Solução Homologada**: Sufixar os arquivos de configuração e locks com o ID de link de cada rádio (`/var/run/hostapd-$ifname$mld_link_id.conf` e `.lock`), garantindo independência total na subida de múltiplos links.
* **[AutoLearn - Afinidade de Interrupções de CPU para DMA e PCIe (`set_pci_ce_irq_affinity`)]**:
  - **Problema**: Todas as interrupções de hardware dos rádios Wi-Fi caíam amontoadas no Core 0 da CPU (mais de 300.000 interrupts), gerando sobrecarga desbalanceada sob downloads rápidos.
  - **Solução Homologada**: Mapear via `/proc/irq/*/smp_affinity`:
    - Interrupções do SoC 2.4G (`ce0` a `ce9`) -> Core 2 (`affinity=4`);
    - Interrupções do rádio PCIe externo QCN9224 (`pci1_wlan_ce_*`) -> Core 3 (`affinity=8`);
    - Cores 0 e 1 preservados exclusivamente para sistema operacional, PPPoE, firewall NAT e tráfego LAN de 2.5 Gbps.
* **[AutoLearn - Agrupamento de Interrupções de TX (Batching Coalescing)]**:
  - Em `/ini/internal/QCA5332_i.ini` e `QCN9224_i.ini`, atualizar `dp_int_batch_threshold_tx=256` e `dp_int_timer_threshold_tx=1000`. Isso faz o silício agrupar 256 pacotes antes de gerar interrupção de hardware para a CPU, reduzindo o consumo de processamento em até 60% sob tráfego gigabit.
* **[AutoLearn - Configuração Real de 160 MHz no 5 GHz (`wifi1`)]**:
  - Para cravar 160 MHz reais em 5 GHz no padrão IEEE 802.11be, configurar `option htmode 'HT160'` no `/etc/config/wireless` no `wifi1`. O script calcula automaticamente o centro espectral no Canal 50 (5250 MHz abrangendo canais 36 a 64), subindo `ath1` com `width: 160 MHz` e `eht_oper_chwidth=2`.
* **[AutoLearn - DNS Criptografado (DoH) Livre e Redundante via `https-dns-proxy`]**:
  - **Arquitetura Homologada**: Daemon C `https-dns-proxy` portado do SPF 12.4 com suporte nativo `procd`. Executa duas instâncias concorrentes sob uid `nobody`:
    - Instância Cloudflare: `127.0.0.1:5053` (`https://cloudflare-dns.com/dns-query`, bootstrap `1.1.1.1,1.0.0.1`);
    - Instância Google: `127.0.0.1:5054` (`https://dns.google/dns-query`, bootstrap `8.8.8.8,8.8.4.4`).
  - **Zero AdBlock / Livre de Bloqueios**: Aponta estritamente para DNS público irrestrito (Cloudflare + Google), sem filtros arbitrários, quebras de páginas bancárias ou dependência de terceiros (sem Shiild / AdGuard).
  - **Integração com Dnsmasq e Cache em RAM**:
    - `dnsmasq` configurado com `list server '127.0.0.1#5053'`, `list server '127.0.0.1#5054'`, `option allservers '1'` e `option noresolv '1'`.
    - `cachesize '5000'`: Primeira consulta ~20ms (ida e volta HTTPS criptografada sobre TLS TCP 443). Consultas repetidas: **0.00s instantâneo em RAM**.
* **[AutoLearn - WireGuard Nativo no Kernel Linux 5.4.213 (`wireguard.ko`)]**:
  - **Compatibilidade de Silício e ABI**: Ao contrário dos módulos Wi-Fi QCA que possuem símbolos ausentes, o módulo `wireguard.ko` portado do Cudy WR11000 possui exatamente o mesmo vermagic (`5.4.213 SMP preempt mod_unload ARMv7 p2v8`) e 100% dos símbolos dinâmicos de rede resolvidos no kernel do Predator T7.
  - Carregamento homologado: `/lib/modules/5.4.213/wireguard.ko` via `/etc/modules.d/wireguard`.
  - Suporte de Userspace e Netifd: `/usr/bin/wg` (wireguard-tools) e handler `/lib/netifd/proto/wireguard.sh` (com remoção de trava proprietária OEM `system.board.type`). Permite criar interfaces de alto rendimento gigabit `proto 'wireguard'`.
* **[AutoLearn - Blindagem de Firewall para Wi-Fi Secundário (Guest / IoT) e IPv6]**:
  - **DNS TCP 53 Obrigatório**: Regras de DNS de zonas isoladas (`guest_dns` e `iot_dns`) DEVEM conter `option proto 'tcp udp'`. Consultas com respostas grandes (>512 bytes, DNSSEC/DKIM) fazem fallback obrigatório para TCP 53; se apenas UDP estiver liberado, a consulta morre.
  - **IPv6 Discovery em Zonas de Input REJECT**: Zonas com política de entrada `REJECT` (como `guest` e `iot`) DEVEM ter regras explícitas liberando `icmp` (tipos router-solicitation 133, neighbour-solicitation 135 e neighbour-advertisement 136) e UDP 546->547 para permitir que os clientes descubram o gateway e obtenham prefixos IPv6 do `odhcpd` sem quebrar o isolamento.
  - **Regra WAN Allow-DHCPv6**: NUNCA colocar restrição de `src_ip 'fc00::/6'` na regra de entrada DHCPv6 da WAN. Provedores respondem a partir de `fe80::/10` (link-local), não de ULA.
  - **Idempotência em Scripts de Firewall**: Scripts invocados via `/etc/firewall.d/` ou `/etc/firewall.user` devem SEMPRE usar verificação prévia (`iptables -C ... || iptables -A ...`) para evitar duplicação cumulativa de regras a cada recarga.



* **[AutoLearn - Bug do Upload `< 1 Mbps` (`0.15 Mbps`) no SQM CAKE com PPPoE (`split-gso` + `ETH_P_PPP_SES`)]**:
  - **Causa Raiz**: No kernel Qualcomm QSDK 5.4.213, a interface `pppoe-wan` não segmenta super-pacotes GSO (`frag_list` de até `17.304 bytes` criados pelo GRO da LAN/Wi-Fi) em software, encapsulando-os diretamente com o cabeçalho PPPoE (`skb->protocol = htons(ETH_P_PPP_SES)` / `0x8864`) para que a controladora física `eth0` (`qca_nss_dp`) faça o *segmentation offload* em hardware. Porém, quando o **SQM CAKE** está anexado à `eth0` com a flag padrão **`split-gso`**, a função `cake_enqueue()` invoca `skb_gso_segment()` do kernel Linux antes do driver `qca_nss_dp`. Como o kernel Linux 5.4 não possui *offload handler* de software registrado para `ETH_P_PPP_SES` (`0x8864`), `skb_gso_segment()` retorna `-EPROTONOSUPPORT` (`ERR_PTR(-93)`) e o CAKE **descarta 100% dos super-pacotes GSO de upload**, reduzindo o upload de `400 Mbps` para `0.15 Mbps` (`~19 KB/s`).
  - **Solução Homologada**:
    1. Em `/etc/config/sqm` (seção `sqm.wan`), definir `option qdisc_advanced '1'`, `option qdisc_really_really_advanced '1'`, `option eqdisc_opts 'no-split-gso'` e `option iqdisc_opts 'no-split-gso'`.
    2. Garantir `ethtool -K eth0 gso on` ativo na `eth0`.
    3. Em `/usr/lib/sqm/defaults.sh`, definir fallback padrão `IQDISC_OPTS="no-split-gso"` e `EQDISC_OPTS="no-split-gso"`.
* **[AutoLearn - Congelamento de Fluxos IPv4 no Wi-Fi 7 6 GHz (`ath2` / QCN9224) no Pacote #25 com SQM + ECM SFE]**:
  - **Causa Raiz**: Quando o acelerador `qca-nss-ecm` (`sfe`) está ativo (`front_end_ipv4_stop = 0`) simultaneamente com o redirecionamento `ifb4eth0` do SQM e PPPoE, qualquer fluxo TCP IPv4 no rádio PCIe de 6 GHz (`ath2` com PPE-DS/VP) transfere exatamente **25 pacotes (`~30 KB`, gatilho `accel_delay_pkts = 25`)** e congela ao sofrer offload para o Virtual Port do PPE, além de o SFE burlar a fila `ifb4eth0` do SQM.
  - **Solução Homologada**: Em `/usr/lib/sqm/defaults.sh` e `/etc/rc.local` (quando `sqm.wan.enabled='1'`), aplicar:
    ```sh
    echo 1 > /sys/kernel/debug/ecm/front_end_ipv4_stop
    echo 1 > /sys/kernel/debug/ecm/front_end_ipv6_stop
    echo 1 > /sys/kernel/debug/ecm/ecm_db/defunct_all
    ```
  - **Resultado Homologado em Produção**:
    - **Cabo (`en10` Gigabit)**: Waveform **Nota A+** (`748.6 Mbps` Down / `356.7 Mbps` Up / `+0 ms` Down / `+0 ms` Up); Speedtest.net **`739.07 Mbps` Down / `366.42 Mbps` Up / Ping `2 ms`**.
    - **Wi-Fi 7 6 GHz (`en0`, `802.11be`, Canal 37, `160 MHz`, PHY `2161 Mbps`)**: Waveform **Nota A** (`557.1 Mbps` Down / `305.7 Mbps` Up); Speedtest.net **`535.51 Mbps` Down / `320.27 Mbps` Up / Ping `7 ms`**.
* **[AutoLearn - Causa Raiz do Boot Loop de 60-100s na Partição 1 (`mtd21`) e Estabilização Definitiva]**:
  - **Causa Raiz 1 (Procd Watchdog vs Hardware Watchdog)**: O `procd` abre `/dev/watchdog` no boot com timeout de 30s. Qualquer chamada de `ubus call system watchdog '{"stop":true}'` ou `{"magicclose":true}` sem manter o procd alimentando o hardware fazia o chip Qualcomm SoC resetar o roteador exatamente 30s após a parada da alimentação. O comando correto e homologado para manter a alimentação ininterrupta é `ubus call system watchdog '{"stop": false, "frequency": 5}'`.
  - **Causa Raiz 2 (Crash MLO IPC no Q6 MPD & qca_ol.ko)**: No arquivo `/ini/internal/QCN9224_i.ini`, `dp_mlo_reo_rings_map=0x7` tentava inicializar anéis MLO entre o SoC e a placa PCIe antes da calibração a frio terminar, disparando `ar_wal_mlo_ipc.c:1065 Assertion 0 failed` no firmware `5332.wlanfw.evalQ` e `Assertion failed! 0:ol_ath_unified_event_handler` (`kernel BUG at i_qdf_trace.h:402`) no `qca_ol.ko`. A solução homologada é fixar `dp_mlo_reo_rings_map=0` em `/ini/internal/QCN9224_i.ini` e `/cfg/default/ini/internal/QCN9224_i.ini`.
  - **Causa Raiz 3 (Deadlock State D por setCountryID Prematuro e Loops de wifi up)**: Scripts prematuros (`sleep 8` no `/etc/rc.local` e loops de `wifi up` no `/etc/init.d/predator_rf`) disparavam `wifi up` enquanto o driver ainda estava calibrando a frio (60s). Isso fazia `qcawificfg80211.sh` linha 1063 disparar `cfg80211tool wifi0 setCountryID 840`, travando `cfg80211tool.1` e `insmod wifi_3_0` em sono ininterruptível (Estado D) disputando o `probe lock`. A solução homologada foi remover os disparos prematuros de `wifi up` e substituir a chamada prematura de `setCountryID 840` na função `set_default_country()` por `:`.
  - **Causa Raiz 4 (Failsafe predator_dev)**: O script `/etc/init.d/predator_dev` contava falhas se o uptime fosse < 75s e forçava troca de partição via U-Boot BOOTCONFIG. Foi removido e desativado com `uci set predator_dev.failsafe.enabled='0'`.
* **[AutoLearn - Pacote Master Restaurador v2 (`cfg_restauracao_master_v2.cfg`), Painel KSMBD e Acesso Remoto Blindado]**:
  - **Estrutura Completa do CFG (`420 KB` / `430.756 bytes` - SHA256 `6eb0db32e5a1418456009ad3516b23d85226d1b4bbc2a604049221ff264c2955`)**:
    - **Painel KSMBD (Network Shares)**: Inclui `/www/luci-static/resources/view/ksmbd.js` (com máscaras 0777, `browseable` e `hide_dot_files`), `/usr/lib/lua/luci/controller/ksmbd.lua`, `/usr/share/luci/menu.d/luci-app-ksmbd.json`, `/usr/share/rpcd/acl.d/luci-app-ksmbd.json`, binário auxiliar de formatação/gestão `/usr/sbin/ksmbd-disk-tool`, `/etc/config/ksmbd`, `/etc/init.d/ksmbd`, `/etc/ksmbd/smb.conf.template`, senhas `/etc/ksmbd/ksmbdpwd.db` e `/etc/config/fstab` (auto-mount de pen drives/discos USB em `/mnt`).
    - **Painel Predator Wi-Fi 7**: Inclui `/www/luci-static/resources/view/predator_wifi.js`, menu JSON `/usr/share/luci/menu.d/luci-app-predator-wifi.json`, ACLs `/usr/share/rpcd/acl.d/luci-app-predator-wifi.json`, backend rpcd `/usr/libexec/rpcd/predator`, wrapper `/sbin/wifi` e guardião anti-erro `/usr/sbin/predator-wifi-guard`.
    - **Acesso Remoto Blindado (SSH e Telnet) e Chaveadores CLI**: Dropbear configurado sem restrição de interface (ouve em todas as sub-redes locais na porta 22), senha `root0100`, chave pública em `/etc/dropbear/authorized_keys`. Telnet nativo com auto-respawn via `procd` em `/etc/init.d/telnet` e fallback no `/etc/rc.local`. Scripts `/usr/sbin/boot-acer` e `/usr/sbin/boot-openwrt` integrados.
    - **Filtragem Seletiva de QUIC via IPSet Dinâmico (Padrão RFC)**: O bloqueio global de UDP 443 foi eliminado (preservando VPNs corporativas e HTTP/3 para sites compatíveis). O `dnsmasq` intercepta consultas de domínios problemáticos (`googlevideo.com`, `youtube.com`, `fbcdn.net`, `waveform.com`) e popula dinamicamente as tabelas hash `quic_block_v4` e `quic_block_v6`. O firewall rejeita com ICMP unreach apenas os IPs desse set.
    - **Proposta Upstream para o ARK Router**: Documentada detalhadamente em [docs/PROPOSTA_INTEGRACAO_ARK_ROUTER.md](docs/PROPOSTA_INTEGRACAO_ARK_ROUTER.md).
  - **Neutralização de Erros e Estabilidade do Waveform**:
    - O SQM CAKE está protegido por `no-split-gso` e desativação condicional do bypass do ECM SFE em `/usr/lib/sqm/defaults.sh` e `/etc/rc.local` (ativa somente quando `sqm.wan.enabled='1'`).
    - Testes do Waveform em dispositivos Apple (iPhone/Mac) exigem desativar o "Limitar Rastreamento de IP" (iCloud Private Relay) nas configurações do Wi-Fi para evitar bloqueios Cloudflare nos servidores de teste.
    - Qualquer alteração manual de Wi-Fi é vigiada pelo `predator-wifi-guard`, revertendo automaticamente para `wireless.lastgood` caso um comando inadequado desative os rádios.

* **[AutoLearn - [AL-T7-056] Painel Visual Inteligente & Blindado de Wi-Fi como WAN (WISP — Módulo 8)]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: Conectar um rádio como cliente STA (`wwan`) na mesma sub-rede da LAN (`192.168.76.1`) ou no próprio BSSID local gera *broadcast storm* ou perda de roteamento; além disso, uma senha incorreta no STA derruba o AP da mesma banda no driver QCA.
  - **Armadilha (❌)**: Configurar STA manualmente via `/etc/config/wireless` sem isolamento de BSSID local, sem timeout de reversão e sem métrica superior ao cabo WAN.
  - **Sintoma**: Loopback de rede, perda do AP local quando a rede superior some ou conflito de IP `192.168.x.1`.
  - **Solução Canônica (✅)**: Backend `/usr/sbin/wifi-wisp-tool` + view `/www/luci-static/resources/view/wifi_wisp.js` com Anti-Loopback (bloqueio de SSID/BSSID próprios), Auto-Rollback de 15s se não autenticar, detecção de conflito de sub-rede com correção em 1 clique para `192.168.77.1`, métrica `20` na WWAN vs métrica `10` na WAN Ethernet (`eth0`) e detecção de Captive Portal.
* **[AutoLearn - [AL-T7-057] Widget Wi-Fi 7 Nativo no LuCI Overview (`60_wifi.js`) e Hostname RFC 1123 (Módulo 9)]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: O QSDK proprietário não expõe `iwinfo` padrão ao LuCI Status Overview, deixando a página inicial sem telemetria dos rádios Wi-Fi 7; paralelamente, o hostname de fábrica com espaços (`Predator Connect T7`) viola a RFC 1123.
  - **Armadilha (❌)**: Manter espaços no hostname em `/etc/config/system` ou depender do widget nativo de wireless do LuCI.
  - **Sintoma**: Leases DHCP rejeitados em ONTs de operadoras, quebra de variáveis não escapadas em scripts POSIX e ausência de status de clientes/temperatura na Home do LuCI.
  - **Solução Canônica (✅)**: Widget `/www/luci-static/resources/view/status/include/60_wifi.js` + ACL `/usr/share/rpcd/acl.d/luci-mod-status-predator.json` consumindo `predator.get_status` (exibindo 2.4G, 5G, 6G Wi-Fi 7, temperatura do silício, ruído RF e espectro livre) e hostname padronizado como `Predator-Connect-T7` em `/etc/config/system` e `99-debloat-v2`.
* **[AutoLearn - [AL-T7-058] Engenharia Reversa da Cifra Polialfabética OEM (`r1` / `n`) e Prova de Fogo 0km em 39s]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: No firmware Stock OEM da Acer (`app.js` + binário FastCGI `/www/cgi-bin/faiotfcgi`), todas as chamadas `/action/login_app` e `data.html` exigem ofuscação por substituição polialfabética de 84 caracteres (`r1` / `n`), além de obrigar troca de senha no primeiro login após `firstboot -y`.
  - **Armadilha (❌)**: Enviar JSON puro ou Base64 simples para `/action/login_app` ou tentar upload de `.cfg` antes de cumprir o fluxo de primeiro acesso (`method=user_pwd`).
  - **Sintoma**: Rejeição de login e falha no restore automatizado pós-reset de fábrica.
  - **Solução Canônica (✅)**: Fluxo validado em bancada (14/10/2026): login inicial com senha de etiqueta (`TamFDH66`) cifrada com `r1`/`n` -> troca obrigatória (`method=user_pwd`) -> obtenção de CSRF token -> upload de `cfg_restauracao_master_v2.cfg` (`430.266 bytes`, SHA-256 `bcfa53918ce217a381b491f9b8e366fcb990c1a59cee217257fcc506a6194e18`) via `/action/genepost` (`webUploadResult: "0"`) -> reboot e estabilização completa em **39 segundos** com SSH (`22`), Telnet (`23`), LuCI (`80`), DoH (`5053`/`5054`) e 3 rádios Wi-Fi 7 ativos.
* **[AutoLearn - [AL-T7-059] Sincronia de Baseline `wireless.lastgood`, `sae_password` e `99-debloat-v2` no Pacote Master]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: O guardião `predator-wifi-guard` utiliza `/etc/predator/wireless.lastgood` para rollback em caso de falha, enquanto `hostapd.sh` lê `sae_password` nas interfaces WPA3/SAE-Mixed e `99-debloat-v2` roda após a extração do `/etc/config/dhcp` no primeiro boot.
  - **Armadilha (❌)**: Alterar apenas `option key` em `/etc/config/wireless` esquecendo `sae_password` e `wireless.lastgood`, ou manter `uci set dhcp.lan.ra='hybrid'` dentro de `99-debloat-v2` e `tar -czf ... etc` (apenas diretório `etc`) no `gerar_cfg_personalizado.py`.
  - **Sintoma**: Descompasso de senha entre clientes WPA2 e WPA3, rollback para SSID antigo de bancada, perda de SLAAC IPv6 no 1º boot e descarte das árvores `/usr` e `/www` em `.cfg` personalizado.
  - **Solução Canônica (✅)**: Manter `key` e `sae_password` idênticos (`Predator0@`), sincronizar `etc/predator/wireless.lastgood` com `etc/config/wireless`, garantir `dhcp.lan.ra='server'` + `ra_management='1'` no `99-debloat-v2` e empacotar todas as árvores da raiz no `dev/gerar_cfg_personalizado.py`.
* **[AutoLearn - [AL-T7-060] Trava Real de 40 MHz no Rádio 2.4 GHz (`wifi0` / `ath0`) contra Coexistência 20/40 OBSS e Bit *40 MHz Intolerant* de Clientes Apple]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: Em 2.4 GHz (`wifi0`), a norma IEEE 802.11n/ax/be ativa por padrão a coexistência 20/40 MHz. Quando um iPhone/iPad associa enviando `HT Capabilities Info: 0xc82d` (`Forty MHz Intolerant = 1`, `num_sta_ht40_intolerant=1`), ou quando há redes vizinhas próximas, o `hostapd` do QSDK derruba `secondary_channel` de `1` para `0` (`ht_op_mode=0x4`), rebaixando `ath0` para 20 MHz. Além disso, o binário `hostapd` da Qualcomm não possui o patch `noscan=1` do OpenWrt upstream, controlando a coexistência via parâmetros proprietários `chan_coex_disable` e `disablecoext` no `/lib/wifi/qcawificfg80211.sh`, e `/lib/wifi/hostapd.sh` só emite `[HT40+]`/`[HT40-]` quando `channel` é numérico (`1` a `13`).
  - **Armadilha (❌)**: Usar o mesmo valor `HT40` tanto para `'Auto (20/40 MHz)'` quanto para `'40 MHz'` no dropdown de `predator_wifi.js`, tentar usar `noscan=1` no QSDK ou deixar `channel='auto'` ao forçar 40 MHz.
  - **Sintoma**: Ao selecionar `40 MHz` em 2.4 GHz e salvar, o seletor voltava sozinho para `Auto (20/40 MHz)` e o rádio operava em `real_width: "20"` (`width: 20 MHz`) sempre que um iPhone conectava.
  - **Solução Canônica (✅)**: Diferenciar no frontend (`predator_wifi.js`) e no backend (`usr/libexec/rpcd/predator`, `etc/init.d/predator_rf`, `usr/sbin/predator-wifi-guard`) os modos `HT40` (`Auto 20/40 MHz`, com `disablecoext='0'` e `chan_coex_disable='0'`) e `HT40_FORCE` (`40 MHz` travado, que grava `wireless.wifi0.htmode='HT40'`, `wireless.wifi0.chan_coex_disable='1'`, `wireless.wifi0_ap.disablecoext='1'`, fixa `channel='6'` caso estivesse em `auto` e aplica `cfg80211tool wifi0 chan_coex_disable 1`, `cfg80211tool ath0 disablecoext 1` e `cfg80211tool ath0 chwidth 1`). Validado ao vivo em `192.168.76.1` com `iw dev ath0 info` (`width: 40 MHz, center1: 2447 MHz`) e `hostapd_cli -i ath0 status` (`secondary_channel=1`, `ht_op_mode=0x0`).
* **[AutoLearn - [AL-T7-061] Backport do Firmware Irmão Acer Predator Connect X7 `v1.01.000050` (31/08/2026) vs T7 `v1.01.000027`]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: O firmware mais recente do dispositivo irmão de mesmo silício (`Acer Predator Connect X7 v1.01.000050`, compilado em agosto/2026 sobre QSDK `5.4.213`) revelou três bugs corrigidos pela ODM em scripts Wi-Fi que permaneciam abertos no T7 (`v1.01.000027`, julho/2025):
    1. Em `/lib/wifi/hostapd.sh`: quando `ap_isbasic=1` (VAP principal WPA2/WPA3-Mixed), o QSDK injetava `beacon_prot=1` e `WPA-PSK-SHA256` (`add_sha256=1`) junto com PMF opcional (`ieee80211w=1`), causando rejeição de handshake 4-way (`RSN IE mismatch`) em Smart TVs, clientes IoT e dispositivos Wi-Fi 5/6 legados.
    2. Em `/lib/wifi/qcawificfg80211.sh` (linhas 6977/6983/7038): `uci set` de `ssid` e `key` sem aspas simples (`$ssidMain`, `$ssidwpass`, `$mesh_key`) truncava SSIDs/senhas com espaços ou caracteres especiais durante sincronização de VAPs.
    3. Em `/lib/functions/repacd-map.sh`: interfaces temporárias com `ssid='teardown'` criadas pelo EasyMesh permaneciam órfãs em `/etc/config/wireless`, sendo necessária a função `del_wifi_teardown_vaps()`.
  - **Armadilha (❌)**: Manter `hostapd.sh`, `qcawificfg80211.sh` e `repacd-map.sh` da revisão de julho/2025 do T7 sem os fixes de agosto/2026 do X7.
  - **Sintoma**: Falha intermitente de autenticação em Smart TVs/IoT quando `sae-mixed` (`ieee80211w=1`) está ativo, truncamento de senhas em reconfigurações UCI e VAPs `teardown` fantasmas.
  - **Solução Canônica (✅)**: Incorporados ao `cfg_restauracao_master_v2.cfg` o `/lib/wifi/hostapd.sh` com o fix `if [ "$ap_isbasic" == "1" ]; then beacon_prot=0; add_sha256=0; fi` + suporte nativo a `sae-mixed`, `/lib/wifi/qcawificfg80211.sh` com escapamento em aspas simples e `/lib/functions/repacd-map.sh` com `del_wifi_teardown_vaps()`.
* **[AutoLearn - [AL-T7-062] Desbloqueio de Silício Qualcomm (`[512M]` DMA Rings, PPE-DS, 802.11be MSCS/SCS/r-TWT/T2LM e Telemetria CCA de Espectro)]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: Três mecanismos internos do driver Qualcomm QSDK 12.x (`qca_ol.ko` + `umac.ko` + `wifi_3_0.ko`) impediam que ajustes tradicionais surtissem efeito:
    1. O script `/lib/wifi/qcawificfg80211.sh` (linha 1526) executa `cp /cfg/default/ini/global.ini /ini/global.ini` em todo `wifi load`, sobrescrevendo qualquer alteração feita apenas em `/ini/global.ini`.
    2. Como a Device Tree do T7 exporta `/sys/firmware/devicetree/base/MP_512`, o parser `qca_ol.ko` ignora os tamanhos de anéis DMA do topo de `QCN9224_i.ini` / `QCA5332_i.ini` e aplica a seção `[512M]` do final do arquivo (que limitava `dp_tx_desc=0x2000` / `8192` e `dp_rxdma_refill_ring=4096`).
    3. O pacote `/etc/init.d/predator_rf` não possuía symlink `/etc/rc.d/S99predator_rf`, e os módulos `qca-nss-mscs.ko` / `ecm-wifi-plugin.ko` e classificadores `ecm_classifier_mscs` + `ecm_classifier_emesh/cake_enabled` permaneciam desligados no boot.
  - **Armadilha (❌)**: Editar apenas `/ini/global.ini` (sem espelhar em `/cfg/default/ini/global.ini`), editar apenas o topo de `QCN9224_i.ini` (sem atualizar a seção `[512M]`) ou usar chaves INI inexistentes no `.rodata` do `qca_ol.ko`.
  - **Sintoma**: Parâmetros de `global.ini` perdidos a cada reload do Wi-Fi, anéis DMA de TX/RX travados no perfil reduzido de 512M e recursos 802.11be (`r_twt_enable`, `MSCS`, `SCS`, `HLOS TID Override`, `PPE-DS` com `cake_enabled`) inativos.
  - **Solução Canônica (✅)**:
    1. Sincronizar `/ini/global.ini` e `/cfg/default/ini/global.ini` com `b_twt_enable=1`, `r_twt_enable=1` (802.11be Restricted TWT), `enable_peer_extended_rate_stats=1`, `enable_peer_extended_link_stats=1`, `ap_bss_color_collision_detection=1` e `enable_6ghz_sp_pwrmode_supp=1`.
    2. Atualizar a seção `[512M]` em `QCN9224_i.ini` e `QCA5332_i.ini` (`dp_tx_desc=0x4000`, `dp_tx_desc_limit_0=16384`, `dp_rxdma_refill_ring=8192`, `dp_rx_sw_desc_num=8192`, `dp_reo2ppe_ring=4096`, `dp_ppe2tcl_ring=4096`, `dp_ppeds_tx_desc=0x4000`, `ppe_vp_core_mask=0x7`, preservando `dp_mlo_reo_rings_map=0`).
    3. Criar `/etc/rc.d/S99predator_rf` e configurar `/etc/init.d/predator_rf` para carregar `qca-nss-mscs` + `ecm-wifi-plugin`, ativar `mscs 1`, `scs 1`, `hlos_tidoverride 1`, `he_su_bfme 1`, `he_mu_bfme 1` e `cake_enabled=1` / `latency_config_enabled=1` no `ecm_classifier_emesh`.
    4. Expor telemetria de espectro RF em tempo real sem varredura destrutiva (`get_channf`, `g_chanutil`, `g_ch_util_ap_tx/rx`, `g_ch_util_obss`, `g_ch_util_nwifi`, `g_ch_util_free`, com sanitização `> 100` contra wraparound uint8 transitório) no `/usr/libexec/rpcd/predator`, `predator_wifi.js` e `60_wifi.js`.
* **[AutoLearn - [AL-T7-063] Menu Dedicado de Engenharia de Silício Qualcomm e Isolamento de Conflitos (`WISP STA vs AP`, `MSCS/SCS vs noackpolicy`, `SQM CAKE vs SFE`, `CCA Mitigation`)]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: Ao ativar os recursos avançados do silício Qualcomm (`IPQ5332` + `QCN9224`), quatro conflitos diretos de subsistema precisam ser coordenados:
    1. **WISP STA (`wwan_sta`) vs Canal/Largura do AP**: Como o STA e o AP da mesma banda física compartilham um único sintetizador PLL no `QCN9224`/`IPQ5332`, enquanto `wireless.wwan_sta` estiver ativo em `wifi1` (ex.: `Golden Tower 2021` no Canal 149 @ 40 MHz), o driver ignora a configuração do usuário (`Canal 36 @ 80/160 MHz`) e crava o AP `ath1` no canal/largura do roteador superior.
    2. **QoS `MSCS`/`SCS`/`HLOS TID Override` vs `noackpolicy`**: Com `hlos_tidoverride 1`, `mscs 1`, `scs 1` e o daemon `/usr/sbin/scs_tool` rodando, fluxos de voz, vídeo, jogos e VR são promovidos para a fila de hardware `AC_VO` (TID 6/7). Se o `Gaming Mode` ativasse `noackpolicy` na fila `AC_VO`, qualquer colisão RF descartaria o pacote sem retransmissão MAC Layer-2.
    3. **Fast-Path `SFE` + `PPE-DS` (2.5 Gbps) vs `SQM CAKE`**: O `SFE` desvia os pacotes da pilha `tc` do kernel depois dos primeiros ~25 pacotes; se `sqm.wan.enabled=1` rodar com `front_end_ipv4_stop=0`, conexões em 6 GHz (`ath2`) congelam.
    4. **Mitigação de CCA (`cca_threshold.sh`) vs Clientes Distantes**: Elevar o limiar de detecção de energia (`setUnitTestCmd 67 3 16 1 26/28`) ignora ruído de vizinhos (`OBSS`), mas pode reduzir a recepção de clientes no limite extremo de cobertura (`< -82 dBm`).
  - **Armadilha (❌)**: Deixar esses recursos fixos sem chave seletora na UI ou permitir que `Gaming Mode` desative ACKs em filas priorizadas por `MSCS`/`SCS`.
  - **Sintoma**: Usuário seleciona Canal 36 (80/160 MHz) no 5 GHz mas o rádio continua travado no Canal 149 (40 MHz) por causa do WISP; micro-cortes de voz/vídeo se `noackpolicy` colidir com `MSCS`; ou perda do Fast-Path de 2.5 Gbps quando o SQM não é necessário.
  - **Solução Canônica (✅)**: Implementado o **Menu Dedicado: Engenharia de Silício Qualcomm, QoS Wi-Fi 7 & Controle de Conflitos** (`renderSiliconMenuCard` + `buildConflictsNode` em `predator_wifi.js` e `do_set_feature` em `/usr/libexec/rpcd/predator` + `/etc/init.d/predator_rf` + `/lib/wifi/cca_threshold.sh` + `/lib/wifi/hostapd.sh`):
    - **Detector de Conflitos Ativos (`buildConflictsNode`)**: Exibe alerta em tempo real quando o WISP (`wwan_sta`) está sequestrando o canal/largura do 5 GHz, com botão de 1 clique (`Desativar WISP e Destravar 5 GHz`).
    - **Isolamento `noackpolicy 0 0` e `noackpolicy 6 0`**: O `Gaming Mode` mantém ACKs Layer-2 100% ativos em `AC_BE` e `AC_VO` enquanto `/usr/sbin/scs_tool` gerencia `MSCS`/`SCS` com zero perda de pacotes.
    - **5 Controles Dedicados no Painel**: `mscs_scs` (QoS Wi-Fi 7 `MSCS+SCS+TID Override` + daemon `scs_tool`), `twt` (`802.11be r-TWT & b-TWT` em tempo real sem reload), `cca_mitigation` (`wifitool setUnitTestCmd 67 3 16` em tempo real), `compat_iot` (fix X7 `ap_isbasic` `beacon_prot=0; add_sha256=0` vs WPA3-SAE estrito) e `sqm_cake` (comutação automática entre **Aceleração Pura PPE-DS + SFE 2.5 Gbps** e **SQM CAKE Anti-Bufferbloat**).
* **[AutoLearn - [AL-T7-064] SQM QoS Nativo em MB/Mbps (`800` / `400`) com Escalonamento Transparente `tc cake` e Localização Tri-Idioma (`PT-BR` / `EN` / `ES`)]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: O pacote `luci-app-sqm` original trabalha internamente em `kbit/s` e depende de binários `.lmo` ausentes na ROM para tradução, enquanto os scripts `/usr/lib/sqm/run.sh` e `/usr/lib/sqm/defaults.sh` repassam `UPLINK` e `DOWNLINK` diretamente para o `tc qdisc add ... cake bandwidth ${UPLINK}kbit`.
  - **Armadilha (❌)**: Alterar apenas o texto da interface `sqm.lua` para `MB / Mbps` sem converter o valor em `run.sh` e `defaults.sh`, o que faria o usuário digitar `800` e limitar a WAN a `800 kbit/s` (`0.8 Mbps`).
  - **Sintoma**: Confusão ao digitar velocidades em `kbit/s` (`800000` / `400000`) ou estrangulamento acidental da conexão caso o usuário digite `800` achando que é `800 Mega`, além de textos sem tradução na página `/cgi-bin/luci/admin/network/sqm`.
  - **Solução Canônica (✅)**:
    1. Em `/usr/lib/lua/luci/model/cbi/sqm.lua`, `cfgvalue` converte valores legados `> 10000` (`kbit/s`) para `MB / Mbps` na exibição e `write` grava o número em `MB / Mbps` (`800` / `400`) diretamente em `/etc/config/sqm`, acionando `m.on_after_commit` para sincronizar `front_end_ipv4_stop` / `front_end_ipv6_stop` e recarregar `/etc/init.d/sqm reload`.
    2. Em `/usr/lib/sqm/run.sh` e `/usr/lib/sqm/defaults.sh`, valores entre `1` e `10000` são multiplicados automaticamente por `1000` antes de alimentar o `tc cake` (`800` -> `800000 kbit/s` = `bandwidth 800Mbit`; `400` -> `400000 kbit/s` = `bandwidth 400Mbit`).
    3. Implementado helper `tr3(ptStr, enStr, esStr)` em `sqm.lua` (lendo `uci:get("luci", "main", "lang")`) e em `predator_wifi.js` (lendo `getActiveLang()`), garantindo 100% de localização nos 3 idiomas (`pt_br`, `en`, `es`).
* **[AutoLearn - [AL-T7-065] Desbloqueio e Validação Real de 240 MHz (`HT240` / `11AEHT320` Punctured `0xf000`) em 5 GHz & 6 GHz, WISP `vap_diff_mode=1`, Central de Apps Dedicada (`predator_apps.js`) e Escudo `opkg` Hold]** `✅ [ATIVO]`:
  - **Comportamento Oculto**:
    1. O rádio de 5 GHz (`wifi1` no `QCN9224`) exporta `/sys/class/net/wifi1/5g_maxchwidth = 320` e `/sys/class/net/wifi1/hwmodes = 11BEA_EHT320`. O disassembly de `wlan_cfg80211_start_ap` (`0x155478`), `wlan_cfg80211_set_phymode` (`0x1553c0`), `wlan_get_320_center_freq` (`0x1e80bc`), `ieee80211_find_std_channel` (`0x276f8`) e `ieee80211_find_puncture_bitmap` (`0x2644c`) em `umac.ko`, junto com `dfs_get_start_chan_idx` (`0x1e336c` em `/usr/sbin/hostapd`), revelou **3 travas encadeadas** em 5 GHz `240 MHz`:
       - **Trava 1 (`hostapd` `dfs_get_start_chan_idx`)**: O `hostapd` upstream só aceita `eht_oper_chwidth=4` (`320 MHz`, `op_class=137`) na banda de 6 GHz (`is_6ghz_freq`). Em 5 GHz (`band != 3`), passar `eht_oper_chwidth=4` em `hostapd-ath1.conf` faz `dfs_get_start_chan_idx` abortar com `"DFS only VHT20/40/80/160/80+80 is supported now"` antes de enviar `NL80211_CMD_START_AP`. A arquitetura Qualcomm para 5 GHz 240 MHz exige que o `hostapd-ath1.conf` passe `vht/he/eht_oper_chwidth=2` (`160 MHz`, `idx=114`) enquanto o `qcawificfg80211.sh` configura `cfg80211tool ath1 mode 11AEHT320` (`vap->iv_user_sup_mode = 43` = `IEEE80211_MODE_11BEA_EHT320`) e `puncture_bitmap=61440` (`0xf000`). No `NL80211_CMD_START_AP`, `wlan_cfg80211_set_phymode` preserva `mode 43` e `wlan_cfg80211_start_ap` (`0x155b10`) chama `wlan_get_320_center_freq(5500, &cfreq2)`, promovendo automaticamente `center_freq1` de `5570 MHz` (`114`) para `5650 MHz` (`0x1612` = `ccfs 130`) e emitindo os 240 MHz via QCN IE (`ieee80211_add_240_mhz_qcn_ie`).
       - **Trava 2 (`umac.ko` `ieee80211_find_std_channel` 16-bit bitmap bug)**: Ao montar o EHT Operation IE padrão em `ieee80211_add_ehtop` (`0x8cf34`), `ieee80211_find_std_channel` (`0x27774..0x27790`) esquece de aplicar máscara de 8 bits (`& 0xff`) em `ic_puncture_bitmap` (`0xf000`) quando `ic_freq <= 5650`, passando `0xf000` para `ieee80211_find_dot11_channel(..., 11BEA_EHT160)`. Se `puncture_strict=1` (`[ic + 0x1dc05]`), `ieee80211_find_puncture_bitmap` (`0x265cc`) compara `0xf000` (16 bits) com `0x0000` (8 bits) e rejeita o canal (`Could not find 160/80 MHz valid channel`). Além disso, `qcawificfg80211.sh` linha 4922 tinha um typo da QCA (`dfs_punctureEn` em vez de `dfs_puncture_en`).
       - **Trava 3 (DFS CAC de 62s)**: Canais `100–144` exigem 62s de escuta passiva CAC por padrão (`get_cactimeout: 62`) se `set_cactimeout 1` não for aplicado antes do `hostapd_setup_vif`.
    2. O controlador nativo `/rom/usr/lib/lua/luci/controller/openvpn.lua` estava na ROM, mas sem o nó pai `{"admin", "vpn"}` e sem o arquivo `/usr/lib/lua/luci/model/cbi/openvpn.lua`.
  - **Armadilha (❌)**: Passar `eht_oper_chwidth=4` no `hostapd-ath1.conf` em 5 GHz, deixar `puncture_strict=1` ou `dfs_puncture_en=0` em `wifi1`, ou não definir `cactimeout=1`.
  - **Sintoma**: `ath1` falha ao subir em `240 MHz` (`status: "offline"`, `real_width: "20"`, `DFS only VHT20..160 supported` no `hostapd` ou `ieee80211_add_ehtop: Could not find std valid channel` no `dmesg`) ou leva 62s em silêncio DFS CAC.
  - **Solução Canônica (✅)**:
    1. Em `/lib/wifi/hostapd.sh` e `/lib/wifi/qcawificfg80211.sh` + `/etc/init.d/predator_rf`: em 5 GHz `HT240`/`EHT240`, emitir `vht/he/eht_oper_chwidth=2` (`idx=114` para canais `100–128`) no `hostapd.sh`, configurar `mode 11AEHT320` + `puncture_bitmap=61440` (`0xf000`), corrigir `cfg80211tool wifi1 dfs_puncture_en 1`, aplicar `cfg80211tool wifi1 puncture_strict 0` e `cfg80211tool ath1 set_cactimeout 1`. Validado ao vivo em `192.168.76.1` subindo em **1.1s** com `iw dev ath1 info` = `channel 100 (5500 MHz), width: 320 MHz, center1: 5650 MHz`, `get_mode: 11AEHT320`, `get_puncture_bitmap: 61440` e `real_width: "240"`.
    2. Criada a página dedicada **Predator Central de Apps** (`/cgi-bin/luci/admin/network/predator_apps` -> `/www/luci-static/resources/view/predator_apps.js`) com WireGuard VPN completo, OpenVPN (`VPN ➔ OpenVPN` com `/usr/lib/lua/luci/model/cbi/openvpn.lua`), Wake-on-LAN (`etherwake`), Agendador Eco Wi-Fi, DoH/QUIC/IPTV, Auto-Otimizador CCA e Escudo `opkg` (`261` pacotes em `hold`, `mwan3` removido em favor do failover FIB nativo Cabo Métrica 10 vs WISP Métrica 20).
* **[AutoLearn - [AL-T7-066] Engenharia Reversa Multi-Vendor IPQ5332 (`UniFi U7 Pro v8.7.11`, `Linksys LN1400/MBE70WRT`, `JDCloud BE6500`, `ImmortalWrt v83`) — Fix MLO Pós-CAC DFS, Supressão de AST Duplicada no Host e Coalescência TX]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: A auditoria cruzada de `miami_config_init()` (`/usr/etc/rc.d/rc.modules` do **Ubiquiti UniFi U7 Pro `v8.7.11+19419`**) e dos arquivos `/ini/internal/` do **Linksys Velop Pro 7 (`LN1400 v1.0.14.216698` / `MBE70WRT v1.2.0.15`)** contra o binário `/lib/modules/5.4.213/umac.ko` do Acer T7 comprovou que o `umac.ko` do T7 já possui compilados os parsers de 2ª geração Beryllium que estavam desligados nos arquivos `.ini` da Acer:
    1. **MLO + DFS CAC (`mlme_mlo_reconfig_reassoc_enable=1` e `enable_mloadvert_degrade_on_cac=1` em `global.ini`)**: Permite que estações Wi-Fi 7 MLO já associadas em 2.4G/6G adicionem/reconfigurem dinamicamente o link de 5 GHz após o fim do CAC DFS e evita travamento de associação durante a janela de CAC.
    2. **EAPOL sobre Netlink (`enable_eapol_over_nl=1` em `global.ini`)**: Envia frames EAPOL (4-way handshake WPA3-SAE/OWE e renovação GTK/IGTK MLO) via Netlink em vez do datapath L2 desviado pelo PPE-DS.
    3. **Desativação da Tabela AST no Host (`host_ast_db_enable=0` e `fw_ast_indication_disable=1` em `QCA5332_i.ini` e `QCN9224_i.ini`)**: Na geração 7 (Beryllium), o firmware Q6 já mantém a *Address Search Table* em hardware (`# Beryllium (gen7 802.11be) has an ast_db in ol fw, we don't need it on host side`). Manter `host_ast_db_enable=1` no T7 duplica a tabela na RAM do host (`MP_512`) e gera tráfego IPC HTT `PEER_MAP` desnecessário.
    4. **Coalescência de IRQs TX (`dp_int_batch_threshold_tx=256`, `dp_int_timer_threshold_tx=1000`), RXDMA Ring (`dp_rxdma_buf_ring=4096` no `QCN9224_i.ini`) e Redução de Monitor Rings ao Mínimo Compilado (`16`/`48`/`4096`)**: Reduz em 75% a pressão de interrupções `WBM2SW` TX, quadruplica o anel RXDMA em 160/240/320 MHz (`1024 -> 4096`) e reduz de `4096` para **`16` entradas** a alocação de `dp_mon_soc_attach_2_0` quando não há VAP monitor (ver `[AL-T7-072]` para os limites exatos de `cfg_uint_item_handler`).
  - **Armadilha (❌)**: Manter `host_ast_db_enable=1`, `dp_rxdma_buf_ring=1024` (ou usar `8192`, que excede `[1024, 4096]` e cai para `1024`), definir `dp_*_monitor_*_ring=0` (que é rejeitado por `cfg_uint_item_handler` e cai para `4096`!) e omitir as seções `[1G-5GL]`/`[1G-5GH]`/`[1G-6GL]`/`[1G-6GH]` no `QCN9224_i.ini`. (**Nota importante**: Ao contrário do Linksys e UniFi, **NÃO** remova `ema_ap_support_wps_in_6ghz=1` de `/ini/QCN9224.ini` no Acer T7 — veja `[AL-T7-071]`).
  - **Sintoma**: Consumo extra de Kernel Slab irreclamável, erro `[E:TIF] init_deinit_ready_event_handler: Host Requested 1058 peers. FW Supports 290 peers` no `dmesg`, pico de SoftIRQ em rajadas Wi-Fi 7, clientes MLO não anexando o link de 5 GHz após CAC e falhas esporádicas de rekeying WPA3 sob offload PPE-DS.
  - **Solução Canônica (✅)**: Aplicada em `/ini/` e `/cfg/default/ini/` e integrada em `cfg_restauracao_master_v2.cfg` (ver `[AL-T7-071]`, `[AL-T7-072]` e [docs/ENGENHARIA_REVERSA_COMPARATIVA_IPQ5332.md](docs/ENGENHARIA_REVERSA_COMPARATIVA_IPQ5332.md)).
* **[AutoLearn - [AL-T7-067] QoS em Hardware PPE Nativo no T7 (`qca-nss-ppe-qdisc.ko` + `/usr/sbin/tc` `ppehtb` / `ppered` / `ppepfifo`) vs SQM CAKE (`sch_cake.ko` `no-split-gso`)]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: A engenharia reversa do patch `600-add-ppe-qdisc.patch` e `be6500-qos-apply` do **ImmortalWrt `v83`** cruzada com os binários do Acer T7 revelou que o T7 **já traz de fábrica** os módulos `qca-nss-ppe-qdisc.ko` + `qca-nss-ppe-rule.ko` (`/etc/modules.d/52-qca-nss-ppe-qdisc`) e o binário `/usr/sbin/tc` compilado com as qdiscs em silício do PPE (`ppehtb`, `ppetbl`, `ppeprio`, `ppewrr`, `ppewfq`, `ppered`, `ppebfifo`, `ppepfifo`, `nssmirred`).
  - **Armadilha (❌)**: Usar SQM CAKE em software em conexões WAN multi-gigabit (`> 800 Mbps a 2.5 Gbps`, onde a CPU Cortex-A53 vira gargalo), ou alterar regras de QoS/Firewall sem invalidar a tabela de fluxos acelerados do ECM (`defunct_all`).
  - **Sintoma**: Saturação de CPU em links acima de 1 Gbps ao usar CAKE em software, ou fluxos já estabelecidos ignorando novas regras de QoS/DSCP por continuarem presos no estado antigo do ECM/PPE.
  - **Solução Canônica (✅)**:
    1. Para conexões até ~800 Mbps, usar **SQM CAKE (`no-split-gso`)** pela precisão cirúrgica por fluxo (COBALT + `triple-isolate` + `ack-filter`).
    2. Para conexões de **1 Gbps a 2.5 Gbps**, o T7 suporta nativamente shaping em silício a **0% de CPU** via `tc qdisc add dev eth0 root handle 1: ppehtb` + `ppepfifo`/`ppered` (receita completa na Seção 3.3 e 5 de [docs/ENGENHARIA_REVERSA_COMPARATIVA_IPQ5332.md](docs/ENGENHARIA_REVERSA_COMPARATIVA_IPQ5332.md)).
    3. Sempre executar `echo 1 > /sys/kernel/debug/ecm/ecm_db/defunct_all` (já automatizado em `/etc/init.d/predator_rf` e `/usr/lib/sqm/run.sh`) após aplicar ou alterar regras de QoS/DSCP para forçar a reclassificação imediata dos fluxos ativos.
* **[AutoLearn - [AL-T7-068] Comandos Nativos `cfg80211tool` (`preCACEn`, `rCACEn`, `acs_6g_only_psc`, `mcastenhance 2`, `ani_enable 1`), WAR do Canal 36 (`edge_ch_dep_applicable`) e Sysctls TCP Thin (`UniFi U7 Pro` & `Linksys MBE70WRT`)]** `✅ [ATIVO]`:
  - **Comportamento Oculto**:
    1. O binário `ubntbox` do **UniFi U7 Pro (`v8.7.11`)** expõe chamadas `cfg80211tool` suportadas pelo `umac.ko` do T7: `cfg80211tool wifi1 rCACEn 1` (Rolling CAC Zero-Wait DFS no QCN6274/9224), `cfg80211tool wifi2 acs_6g_only_psc 1` (restringe ACS em 6 GHz aos canais PSC), `cfg80211tool wifiX ani_enable 1` + `ani_ofdm_level 0x80` (imunidade a ruído OFDM).
    2. Em `/lib/wifi/qcawificfg80211.sh`, a Wistron comentou no T7 o bloco `WAR to not use chan 36 as primary channel, when using higher BW` (`edge_ch_dep_applicable`), que no Linksys `MBE70WRT` está ativo e move o canal primário de `36` para `40` em 80/160 MHz para evitar o corte de 3–6 dB de *Band-Edge Backoff* junto a `5150 MHz`. (Ao descomentar no T7, deve-se quotar `[ "${band:-0}" = "0" ]`, `[ "${channel:-0}" = "36" ]` e `[ "${edge_channel_deprioritize:-0}" = "1" ]` para evitar `sh: missing ]` no BusyBox `ash`).
    3. O `rc.sysinit` do UniFi U7 Pro ativa `net.ipv4.tcp_thin_linear_timeouts=1`, `net.ipv4.tcp_mtu_probing=1`, `net.ipv4.tcp_base_mss=1024`, `net.ipv4.tcp_notsent_lowat=131072` e `echo 0 > /proc/sys/ppe/bridge_mgr/fdb_disabled` (nota: `net.ipv4.tcp_thin_dupack` não existe no Kernel 5.4.213).
  - **Armadilha (❌)**: Usar o canal 36 como primário em 80/160 MHz na banda UNII-1 (sofre penalidade de borda no BDF) ou deixar ACS de 6 GHz escolher canais fora da grade PSC.
  - **Sintoma**: Alcance reduzido em Beacons/ACKs no canal 36 em 80/160 MHz, demora na descoberta do SSID 6 GHz em smartphones e retransmissão lenta de pacotes TCP em jogos/SSH/VoIP.
  - **Solução Canônica (✅)**: Integrada em `/etc/init.d/predator_rf`, `/etc/sysctl.conf` e `/lib/wifi/qcawificfg80211.sh`.
* **[AutoLearn - [AL-T7-069] Ponte QSDK Nativa para a Página LuCI Wireless Overview (`/cgi-bin/luci/admin/network/wireless`) e Sub-seções (`Scan`, `Join`, `Edit`, `Add`, `Restart`, `Associated Stations`)]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: A página nativa do OpenWrt `/cgi-bin/luci/admin/network/wireless` falha em 6 camadas distintas na arquitetura Qualcomm QSDK (`qcawificfg80211`):
    1. `ubus call luci-rpc getWirelessDevices` retorna `{}` vazio porque `luci.so` consulta `ubus call network.wireless status` (do `netifd`), mas no QSDK os rádios são gerenciados por `/sbin/wifi` + `/lib/wifi/qcawificfg80211.sh`, que gravam os nomes reais das interfaces (`ath0`, `ath1`, `ath2`, `ath11`) em `/var/state/wireless`.
    2. A biblioteca `libiwinfo.so` desta ROM compilou apenas o backend legado WEXT (`ioctl`), que rejeita `wifi0`/`wifi1`/`wifi2` (`Not found`), reporta `"Generic WEXT"` / `hwmodes: ["b","g"]` para `athX`, retorna `assoclist: []` vazio e falha em `iwinfo scan` nas bandas de 5 GHz/6 GHz por não enviar a flag Netlink `NL80211_SCAN_FLAG_AP` (`ap-force`).
    3. `/usr/libexec/rpcd/luci` (`getFeatures`) executava `/usr/sbin/hostapd -v<feature>`, que no `hostapd` da QCA retorna erro `1` (`invalid option`), marcando `sae`, `owe`, `11w`, `11r`, `11ac`, `acs` e `eap` como `false`.
    4. `/www/luci-static/resources/view/network/wireless.js` filtrava opções por `hwtype == 'mac80211'`, ocultando TX Power, Country Code, WPA2/WPA3-SAE, Filtro MAC, Isolamento de Clientes, Hide ESSID e 802.11k/v/r/w quando `type == 'qcawificfg80211'`.
    5. `CBIWifiFrequencyValue` em `wireless.js` desconhecia a banda de 6 GHz (`wifi2`), os modos `11beg`/`11bea` (Wi-Fi 7) e as larguras `HT80`/`HT160`/`HT240`/`HT320`.
    6. Editar a senha WPA3 (`sae` / `sae-mixed`) pelo LuCI alterava apenas `option key`, deixando `option sae_password` dessincronizado para o `qcawificfg80211.sh`.
  - **Armadilha (❌)**: Depender de `luci-rpc getWirelessDevices` ou `iwinfo` nativo no QSDK, ou editar `/etc/config/wireless` via LuCI sem sincronizar `sae_password` e as invariantes `HT240` (`ccfs=130`, `puncture_bitmap=61440`, `cactimeout=1`).
  - **Sintoma**: Página `/cgi-bin/luci/admin/network/wireless` exibe `Generic 802.11bg / Device is not active / Wireless is not associated / disabled` em todos os rádios, `Scan` vazio em 5G/6G e modal `Edit` sem opções de criptografia WPA3 nem larguras Wi-Fi 6/7.
  - **Solução Canônica (✅)**:
    1. Implementados 4 métodos RPC em `/usr/libexec/rpcd/predator`: `get_luci_wireless` (sintetiza o estado completo de `wifi0`/`wifi1`/`wifi2` e VAPs `athX` combinando UCI, `/var/state/wireless`, `iw dev athX info`, `cfg80211tool` e `wlanconfig`), `luci_wifi_assoclist` (parseia `wlanconfig athX list sta` com flags `eht`/`he`/`vht`/`ht`, MCS, NSS e largura em MHz), `luci_wifi_scan` (dispara `iw dev athX scan ap-force` e parseia `iw scan dump` com largura `20/40/80/160/320 MHz`, incluindo detecção de `160 MHz` via `center freq segment 2 > 0`, e geração `Wi-Fi 4/5/6/6E/7`) e `luci_wifi_action` (`restart_radio`, `disconnect_client`, `reload` com sincronização automática de `sae_password` e invariantes `HT240`).
    2. Atualizados `/usr/libexec/rpcd/luci` (`getFeatures` reportando suporte completo a `11n`/`11ac`/`11ax`/`11be`/`sae`/`owe`/`11r`/`11w`/`acs`/`eap`), `/www/luci-static/resources/network.js` e `/www/luci-static/resources/view/network/wireless.js` para `qcawificfg80211`.
* **[AutoLearn - [AL-T7-070] Permissões Sintéticas `0700` de Volumes ExFAT no macOS Causando `HTTP/1.1 403 Forbidden` no `uhttpd`]** `✅ [ATIVO]`:
  - **Comportamento Oculto**: No macOS, arquivos armazenados em volumes ExFAT (`/Volumes/--400GB--`) recebem permissão sintética `0700` (`-rwx------`) e `uid=501`. Ao copiá-los com `cp` para um diretório de staging em `/tmp` ou enviá-los via `tar` diretamente para o roteador, o cabeçalho POSIX do `tar` preserva o modo `0700` (`-rwx------`). O servidor web `uhttpd` do OpenWrt exige bit de leitura global (`0644` / `o+r`) para servir arquivos estáticos em `/www/luci-static/`.
  - **Armadilha (❌)**: Empacotar ou enviar arquivos `.js`/`.css`/`.json` a partir de um volume ExFAT sem normalizar permissões (`chmod 0644`) e ownership (`--uid 0 --gid 0`).
  - **Sintoma**: O navegador exibe erro `NetworkError: HTTP error 403/404 while loading class file "/luci-static/resources/..."` mesmo com o arquivo fisicamente presente em `/www/luci-static/`.
  - **Solução Canônica (✅)**: Sempre normalizar permissões na árvore de staging (`chmod -R a+rX` + `find www usr/share -type f -exec chmod 0644 {} +` + `chmod 0755` nos executáveis) e gerar o `cfg_restauracao_master_v2.cfg` com `GZIP=-9 COPYFILE_DISABLE=1 tar --no-mac-metadata --uid 0 --gid 0 --uname root --gname root -czf`.
* **[AutoLearn - [AL-T7-071] Validação Real das Otimizações Multi-Vendor: Eliminação do Erro `Host Requested 1058 peers` (`[1G-5GL/5GH/6GL/6GH]`), Economia de Kernel Slab e Obrigatoriedade de `ema_ap_support_wps_in_6ghz=1` no T7]** `✅ [ATIVO]`:
  - **Comportamento Oculto**:
    1. O módulo `qca_ol.ko` no Acer T7 (`1 GB RAM`, QCN9224 em modo Split-PHY `5GH` + `6GL`) busca no `QCN9224_i.ini` as seções `[1G-5GL]`, `[1G-5GH]`, `[1G-6GL]` e `[1G-6GH]`. Como o `QCN9224_i.ini` original da Acer continha apenas `[1G-2G]`, `[1G-5G]` e `[1G-6G]`, o driver caía no fallback `[5GH]`/`[6GL]` (`num_peers=512`, `num_monitor_vaps=1`), alocando estruturas no host para **1.058 peers** (`512 + 512 + 34 vdevs`) quando o firmware `fw_wcss_qcn9224_v2.bin` suporta no máximo **290 peers** (`[E:TIF] init_deinit_ready_event_handler: Host Requested 1058 peers. FW Supports 290 peers`).
    2. Embora Linksys (`LN1400`) e Ubiquiti (`U7 Pro`) omitam `ema_ap_support_wps_in_6ghz=1` em `/ini/QCN9224.ini`, o `/lib/wifi/hostapd.sh` do Acer T7 injeta parâmetros WPS (`WPS: Converting push_button to virtual_push_button for WPS 2.0 compliance`) em `/var/run/hostapd-ath2.conf`. Sem `ema_ap_support_wps_in_6ghz=1` no `/ini/QCN9224.ini`, o `umac.ko` bloqueia o `NL80211_CMD_NEW_BEACON` em 6 GHz (`Failed to set beacon parameters`).
  - **Armadilha (❌)**: Remover `ema_ap_support_wps_in_6ghz=1` de `/ini/QCN9224.ini` no Acer T7 ou deixar `QCN9224_i.ini` sem as seções `[1G-5GL]`/`[1G-5GH]`/`[1G-6GL]`/`[1G-6GH]`.
  - **Sintoma**: Sem `ema_ap_support_wps_in_6ghz=1`, `ath2` (6 GHz) falha ao iniciar o AP (`Interface initialization failed`) e cai em `channel 1 (5955 MHz), width: 20 MHz` sem SSID. Sem `[1G-5GL/5GH/6GL/6GH]` e com `host_ast_db_enable=1` + monitor rings ativos, o kernel desperdiça megabytes de Slab irreclamável e registra `Host Requested 1058 peers. FW Supports 290 peers`.
  - **Solução Canônica (✅)**: Manter `ema_ap_support_wps_in_6ghz=1` em `/ini/QCN9224.ini`, definir `num_peers=128`, `num_monitor_vaps=0`, `full_mon_mode=0`, `host_ast_db_enable=0`, `fw_ast_indication_disable=1`, `dp_mlo_reo_rings_map=0x7` e adicionar `[1G-5GL]`, `[1G-5GH]`, `[1G-6GL]`, `[1G-6GH]` em `QCN9224_i.ini`.
* **[AutoLearn - [AL-T7-072] Limites Exatos Compilados de `cfg_uint_item_handler` (`dp_*_monitor_*_ring=16/48/4096`, `dp_rxdma_buf_ring=4096`, `gScanAgingTime=200`), `ppe_vp_core_mask=0x7` Multi-Core e Balanceamento de IRQs PCIe `ap-mi01.6`]** `✅ [ATIVO]`:
  - **Comportamento Oculto**:
    1. A auditoria do `dmesg` durante o cold boot (`dmesg | grep cfg_uint_item_handler`) revelou que o parser `cfg_uint_item_handler` compilado no `umac.ko`/`qca_ol.ko` do Acer T7 possui limites `[min, max]` estritos:
       - `dp_rxdma_monitor_buf_ring` e `dp_tx_monitor_buf_ring`: faixa `[16, 8192]` (default `4096`). Definir `0` (como nos scripts do Linksys/UniFi de outro build QSDK) dispara `Out of range [16, 8192]; Using 4096`, fazendo o `dp_mon_soc_attach_2_0` alocar **4.096 buffers** em vez de desligá-los! Definir `16` reduz a alocação para apenas **16 entradas** (`256x` menor).
       - `dp_rxdma_monitor_dst_ring` e `dp_tx_monitor_dst_ring`: faixa `[48, 8192]` (default `2048`) -> mínimo válido `48`.
       - `dp_rxdma_monitor_status_ring`: faixa `[16, 8192]` (default `1024`) -> mínimo válido `16`.
       - `dp_rxdma_monitor_desc_ring`: faixa `[4096, 16384]` (default `4096`) -> mínimo válido `4096`.
       - `dp_rxdma_buf_ring`: faixa `[1024, 4096]` (default `1024`). Definir `8192` dispara `Out of range [1024, 4096]; Using 1024` (voltando ao mínimo!). Definir `4096` ativa o ganho real de **4x** nos buffers RXDMA do QCN9224.
       - `gScanAgingTime`: faixa `[0, 200]` (default `30`) -> máximo válido `200`.
    2. Nas sub-seções `[5G]`/`[5GL]`/`[5GH]` e `[6G]`/`[6GL]`/`[6GH]` do `QCN9224_i.ini` original da Acer, `ppe_vp_core_mask` estava fixado em `4` (apenas CPU2 para 5 GHz) e `3` (CPU0+CPU1 para 6 GHz), sobrescrevendo o valor global. Alinhar todas as sub-seções para `ppe_vp_core_mask=0x7` e `[SINGLE_PHY_*]`/`[SPLIT_PHY_*]` para `dp_reo_rings_map=0x7` distribui o PPE-DS nos 3 cores de datapath (`osif_pltfrm_create_ppe_vp: vpai.core_mask: 7` em `vpnum 64, 65, 66`).
    3. O script `/lib/update_smp_affinity.sh` da Acer não possuía `case` para a board `ap-mi01.6`, deixando `pci1_wlan_grp_dp_8` 100% preso na `CPU0` e `pci1_wlan_ce_1` + `pci1_wlan_ce_2` empilhados na `CPU2`.
    4. No primeiro boot imediatamente após um restore de `.cfg`, `S10boot` executa `/etc/uci-defaults/99-debloat-v2` (~5s) antes de chamar `/sbin/kmodloader` (`40-bonding`), enquanto `S10qcawifi-config-cmd` roda em paralelo e tenta inserir `qdf.ko` aos `19.2s` sem `bonding.ko` carregado (`qdf: Unknown symbol bond_create_mlo (err -2)`), abortando a carga do Wi-Fi se `bonding.ko` não for pré-carregado.
  - **Armadilha (❌)**: Usar `0` nos anéis `dp_*_monitor_*_ring`, `8192` em `dp_rxdma_buf_ring`, `3600` em `gScanAgingTime`, usar `grep "$iname"` sem `-w -m1` ao buscar `pci1_wlan_ce_1` em `/proc/interrupts`, ou não garantir `insmod bonding.ko` antes do `qdf.ko` em `load_qcawificfg80211`/`99-debloat-v2`/`predator_rf`.
  - **Sintoma**: Avisos `cfg_uint_item_handler: Out of range` no `dmesg`, alocação silenciosa de `4096` buffers de monitor (`dp_mon_soc_attach_2_0: rx mon buf entries: 4096`), `dp_rxdma_buf_ring` revertendo para `1024`, gargalo de interrupções PCIe na `CPU0`/`CPU2`, ou falha `qdf: Unknown symbol bond_create_mlo` no primeiro boot pós-restore.
  - **Solução Canônica (✅)**: Definir os mínimos compilados exatos (`16`/`48`/`4096`), `dp_rxdma_buf_ring=4096`, `gScanAgingTime=200`, `ppe_vp_core_mask=0x7` em todas as sub-seções de banda, garantir `[ -d /sys/module/bonding ] || insmod_cmd bonding` antes de `qdf` em `/lib/wifi/qcawificfg80211.sh` + `/etc/uci-defaults/99-debloat-v2` + `/etc/init.d/predator_rf`, e distribuir `pci1_wlan_ce_1:2`, `pci1_wlan_ce_2:4`, `pci1_wlan_grp_dp_8:8`, `pci1_wlan_grp_dp_9:2`, `pci1_wlan_grp_dp_11:4` via `grep -w -m1` no `/etc/init.d/predator_rf`. Validado após `firstboot -y` 0km + restore master (`MemFree: 543.784 kB`, `MemAvailable: 582.040 kB`, `Slab: 176.856 kB`, `ZERO_DMESG_CFG_ERRORS`, `rx/tx mon buf entries: 16`, `vpai.core_mask: 7`).


