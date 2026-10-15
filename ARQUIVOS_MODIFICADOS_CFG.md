# 📋 Inventário de Arquivos Modificados — Pacote Master (`cfg_restauracao_master_v2.cfg`)
> **Acer Predator Connect T7 (IPQ5332 + QCN9224 DualMAC)**  
> **Status:** `✅ [ATIVO]` Homologado e Consolidado em Produção (14/10/2026).  
> **Regra Mandatória:** Somente incorporar ao `cfg_restauracao_master_v2.cfg` após 100% de validação em produção, estabilidade térmica e confirmação de clientes sem regressão.

---

## 1. Arquivos Modificados (Fase 1 — 100% Validados no Roteador)

Estes arquivos já passaram por validação no sistema físico, estão ativos e estáveis:

| Arquivo no Roteador | Arquivo no Repositório Git | Descrição do Ajuste Realizado | Status de Validação |
| :--- | :--- | :--- | :--- |
| `/usr/libexec/rpcd/predator` | `dev/luci-app-predator-wifi/root/usr/libexec/rpcd/predator` | • Correção do comando `iw set txpower fixed` para **mBm** (`$((TX * 100))`), evitando clamping e potência atenuada.<br>• Extração da temperatura real do silício e do `current level` de duty cycle via `thermaltool -i wifiX -get -g`.<br>• Suporte a parâmetro `zone` em `do_add_vif` para vincular redes às bridges corretas (`lan`, `guest`, `iot`). | **100% Validado** (`ubus call predator get_status` online, limpo, temp real 86/89 °C) |
| `/www/luci-static/resources/view/predator_wifi.js` | `dev/luci-app-predator-wifi/root/www/luci-static/resources/view/predator_wifi.js` | • Topologia corrigida: `wifi0` como SoC IPQ5332 (AHB) e `wifi1`/`wifi2` compartilhando o endpoint PCIe `0001:01:00.0` (QCN9224 DualMAC).<br>• Rótulos claros diferenciando **TxPower Conduzido** (medição `iw`) de **EIRP Estimado**.<br>• Expansão do espectro de 6 GHz até o canal 233 (5955–7115 MHz) incluindo todos os PSCs.<br>• Seletor de rede/bridge de destino (`br-lan`, `br-guest`, `br-iot`) na modal de criação.<br>• Esclarecimento técnico de que 4096-QAM inativo rebaixa para Wi-Fi 6E (HT160) e que MBSSID+MLO é restrição de profile QSDK. | **100% Validado** (Interface Web LuCI renderizando HTTP 200, sem erros JS de console) |
| `/sbin/wifi` e `/usr/sbin/predator-wifi-guard` | `dev/luci-app-predator-wifi/root/sbin/wifi` e `usr/sbin/predator-wifi-guard` | • Wrapper `/sbin/wifi` com destravamento de PID morto e chamada automática ao sanitizador `predator-wifi-guard fix` e watchdog `verify`. | **100% Validado no Master v2** |

---

## 2. Arquivos de Userspace, Drivers e Otimizações de Silício (Fase 2 — 100% Validados em Produção)

Estes binários, scripts e tabelas provêm da engenharia reversa do Cudy WR11000 release 2.5.34 (Qualcomm SPF 12.4 / hostapd v2.11-devel ARM32) e otimizações QSDK. *(Nota: binários pesados de hostapd da seção `dev/cudy-hostapd-upgrade/` destinam-se à imagem completa de Slot 2, enquanto no `.cfg` Master v2 o `hostapd.sh` nativo recebe o patch `sae-mixed` via `99-debloat-v2`/`rc.local` para boot limpo em 39s)*:

| Arquivo no Roteador | Arquivo no Repositório Git | Descrição do Ajuste / Upgrade | Status de Validação |
| :--- | :--- | :--- | :--- |
| `/usr/sbin/qca-hapd-supp` | `dev/cudy-hostapd-upgrade/qca-hapd-supp` | Binário multicall ARM32 moderno com patches de MLO, SAE, WPA3 e roaming de Wi-Fi 7 (hostapd v2.11-devel). 560 símbolos dinâmicos 100% resolvidos na libc/libnl/OpenSSL do T7. | **Validado (Imagem Slot 2)** |
| `/usr/sbin/hostapd` | `dev/cudy-hostapd-upgrade/hostapd` | Wrapper shell que garante invocação correta via `exec -a hostapd` por qualquer caminho (`$PATH` ou full path). | **Validado (Imagem Slot 2)** |
| `/usr/sbin/wpa_supplicant` | `dev/cudy-hostapd-upgrade/wpa_supplicant` | Wrapper shell que garante invocação correta via `exec -a wpa_supplicant`. | **Validado (Imagem Slot 2)** |
| `/usr/sbin/hostapd_cli` | `dev/cudy-hostapd-upgrade/hostapd_cli` | Cliente de controle v2.11-devel sincronizado à versão do daemon. | **Validado (Imagem Slot 2)** |
| `/lib/wifi/hostapd.sh` | `dev/cudy-hostapd-upgrade/hostapd.sh.patched` | Script com patch `sae-mixed` nativo + backport do fix `ap_isbasic` (`beacon_prot=0; add_sha256=0`) do Acer Predator Connect X7 `v1.01.000050` (agosto/2026) e fallback `idx=31` para `HT320`. | **100% Validado em Produção** |
| `/lib/wifi/qcawificfg80211.sh` | `dev/cudy-hostapd-upgrade/qcawificfg80211.sh.patched` | Script mestre QSDK com correções de sintaxe, backport de escapamento UCI (`'$ssidMain'`, `'$ssidwpass'`, `'$mesh_key'`) do X7 `v1.01.000050`, `dp_mlo_reo_rings_map=0` e `set_default_country()` seguro contra deadlock `State D`. | **100% Validado no Master v2** |
| `/lib/functions/repacd-map.sh` | Pacote Master v2 | Backport da função `del_wifi_teardown_vaps()` do Acer Predator Connect X7 `v1.01.000050` (agosto/2026), purgando automaticamente VAPs fantasmas `ssid='teardown'`. | **100% Validado no Master v2** |
| `/lib/wifi/cca_threshold.sh` | `dev/cudy-hostapd-upgrade/cca_threshold.sh` | Mitigação de sensibilidade e interferência CCA enviando `setUnitTestCmd 67 3 16 ...` via `wifitool` nos rádios `wifi0` e `wifi1`. | **Validado (Imagem Slot 2)** |
| `/ini/mlo_config.ini` | `dev/cudy-hostapd-upgrade/mlo_config.ini` | Matriz de adjacência de silício Qualcomm para 3 chips (SoC IPQ5332 + 2x QCN9224 PCIe) e 256 peers. | **Validado (Imagem Slot 2)** |
| `/ini/global.ini` e `/cfg/default/ini/global.ini` | `dev/cudy-hostapd-upgrade/global.ini.patched` | Sincronizados em `/ini` e `/cfg/default/ini` com `b_twt_enable=1`, `r_twt_enable=1` (802.11be Restricted TWT), `enable_peer_extended_rate_stats=1`, `enable_peer_extended_link_stats=1`, `ap_bss_color_collision_detection=1` e `enable_6ghz_sp_pwrmode_supp=1`. | **100% Validado no Master v2** |
| `/ini/internal/QCA5332_i.ini` e `/cfg/default/ini/internal/QCA5332_i.ini` | `dev/cudy-hostapd-upgrade/QCA5332_i.ini.patched` | Perfil `[512M]` e topo atualizados com `dp_tx_desc=0x4000` (16384), `dp_rxdma_refill_ring=4096`, `ppe_vp_core_mask=0x7`, `dp_rx_flow_tag_enable=1` e `dp_int_batch_threshold_rx/tx=128/256`. | **100% Validado no Master v2** |
| `/ini/internal/QCN9224_i.ini` e `/cfg/default/ini/internal/QCN9224_i.ini` | `dev/cudy-hostapd-upgrade/QCN9224_i.ini.patched` | Fix crítico `dp_mlo_reo_rings_map=0` (`DNR-02`), `ppe_vp_core_mask=0x7`, `dp_rx_flow_tag_enable=1` e expansão do perfil `[512M]` (`dp_tx_desc=0x4000`, `dp_tx_desc_limit_0=16384`, `dp_rxdma_refill_ring=8192`, `dp_rx_sw_desc_num=8192`, `dp_reo2ppe_ring=4096`, `dp_ppe2tcl_ring=4096`, `dp_ppeds_tx_desc=0x4000`). | **100% Validado no Master v2** |
| `/etc/init.d/predator_rf` e `/etc/rc.d/S99predator_rf` | `dev/luci-app-predator-wifi/root/etc/init.d/predator_rf` | Daemon de otimização de silício Qualcomm: carrega `qca-nss-mscs` + `ecm-wifi-plugin`, ativa `mscs 1`, `scs 1`, `hlos_tidoverride 1`, `he_su_bfme 1`, `he_mu_bfme 1` e `cake_enabled=1` / `latency_config_enabled=1` no `ecm_classifier_emesh`. | **100% Validado no Master v2** |
| `/etc/config/sqm` | `dev/sqm-gso-ecm-fix/sqm` | Sincronizado `download` `800000` (800 Mbps), `upload` `400000` (400 Mbps), `no-split-gso` e `enabled '0'` por padrão (100% aceleração PPE 2.5 Gbps quando desligado). | **100% Validado no Master v2** |
| `/etc/sysctl.d/99-panic-lock.conf` | Gerado + `99-debloat-v2` | `kernel.panic=0` + injeção de `nf_conntrack_max=65536` e otimizações de rede em `99-performance.conf` via `99-debloat-v2`. | **100% Validado no Master v2** |
| `/etc/config/wireless` | N/A (Configuração Master v2) | Perfil Padrão Ouro `single_ssid` (`Predator_7G` / `Predator0@`), **80 MHz (`HT80`)** no 5 GHz (boot instantâneo em 2s sem espera DFS, alternável para 160 MHz no LuCI) e **320 MHz (`HT320`)** no 6 GHz. | **100% Validado no Master v2** |
| `/etc/firewall.user` | `dev/firewall-hardened/firewall.user` | ✅ **[ATIVO NO MASTER V2]**: Clamping de TCP MSS (1452 IPv4 / 1432 IPv6) + filtragem seletiva de QUIC via `dnsmasq` + `ipset` (`quic_block_v4` / `quic_block_v6`), preservando HTTP/3 e VPNs corporativas. | **100% Validado no Master v2** |
| `/etc/config/firewall` | `dev/firewall-hardened/firewall.config` | **Blindagem de Redes Wi-Fi, Anti-Scan, QUIC Seletivo e IPv6:**<br>• `guest_dns` e `iot_dns`: Liberado TCP e UDP 53 (`tcp udp`).<br>• `Allow-DHCPv6` na WAN: Removido filtro `fc00::/6`.<br>• Regras `guest_dhcpv6`, `guest_icmpv6`, `iot_dhcpv6`, `iot_icmpv6` e `Reject-Selective-QUIC-v4/v6`. | **100% Validado no Master v2** |
| `/etc/config/dhcp` | N/A (Configuração Master v2) | **DNS Criptografado (DoH), IPSet QUIC e SLAAC IPv6:** Integrado ao `https-dns-proxy` (`127.0.0.1#5053` e `#5054`) com `allservers '1'`, `cachesize '5000'`, listas `ipset` para domínios com throttling QUIC e `ra='server'` + `ra_management='1'`. | **100% Validado no Master v2** |
| `/usr/sbin/https-dns-proxy` | `dev/doh-https-dns-proxy/https-dns-proxy` | Daemon DoH nativo compilado para Qualcomm IPQ5332. Túnel criptografado HTTPS (TCP 443) para resolução DNS segura, livre de adblocking ou amarras proprietárias. | **100% Validado no Master v2** |
| `/usr/lib/libev.so.4.0.0` | `dev/doh-https-dns-proxy/libev.so.4.0.0` | Biblioteca de loop de eventos assíncrono libev necessária pelo daemon DoH. | **100% Validado no Master v2** |
| `/etc/config/https-dns-proxy` | `dev/doh-https-dns-proxy/https-dns-proxy.config` | Configuração UCI definindo instâncias independentes redundantes: Cloudflare (porta 5053) e Google (porta 5054). | **100% Validado no Master v2** |
| `/etc/init.d/https-dns-proxy` | `dev/doh-https-dns-proxy/https-dns-proxy.init` | Script de inicialização `procd` com suporte a `respawn 3600 5 0` e gerenciamento independente de ciclo de vida das instâncias. | **100% Validado no Master v2** |
| `/lib/modules/5.4.213/wireguard.ko` | `dev/cudy-ported-packages/wireguard/wireguard.ko` | Módulo de kernel WireGuard Linux 5.4.213 compilado com vermagic e ABI 100% compatíveis com o kernel do Predator T7. VPN de altíssima performance no kernel. | **100% Validado no Master v2** |
| `/usr/bin/wg` | `dev/cudy-ported-packages/wireguard/wg` | Utilitário CLI wireguard-tools v1.0.20210223 para geração de chaves e configuração de interfaces. | **100% Validado no Master v2** |
| `/lib/netifd/proto/wireguard.sh` | `dev/cudy-ported-packages/wireguard/wireguard.sh` | Handler de protocolo netifd oficial para gerenciamento de interfaces `proto 'wireguard'`, sem travas de marca. | **100% Validado no Master v2** |
| `/usr/bin/etherwake` | `dev/cudy-ported-packages/etherwake/etherwake` | Utilitário C Wake-on-LAN para envio de Magic Packets e ligar dispositivos na LAN remotamente. | **100% Validado no Master v2** |
| `/bin/network-conflict-calc.sh` | `dev/cudy-ported-packages/utils/network-conflict-calc.sh` | Script awk de cálculo de sobreposição e conflito de sub-redes IPv4 entre LAN e WAN/VPN. | **100% Validado no Master v2** |
| `/usr/sbin/igmpproxy` | `dev/cudy-ported-packages/igmpproxy/igmpproxy` | Daemon de proxy e encaminhamento de multicast IGMP para IPTV de operadoras (desativado por padrão). | **100% Validado no Master v2** |
| `/usr/bin/wifi_schedule.sh` | `dev/cudy-ported-packages/wifi_schedule/wifi_schedule.sh` | Script oficial prpl Foundation para agendamento e desligamento de Wi-Fi por horário (desativado por padrão). | **100% Validado no Master v2** |
| `/etc/firewall.d/qca-nss-ecm` | `dev/firewall-hardened/qca-nss-ecm` | Script de aceleração Qualcomm ECM com verificação `iptables -C` e recriação limpa de cadeia `RATE-LIMIT`, evitando duplicatas em recargas. Permissão `755`. | **100% Validado no Master v2** |
| `/etc/firewall.d/99-predator-fixes` | `dev/firewall-hardened/99-predator-fixes` | Clamping de TCP MSS (1452 bytes IPv4, 1432 bytes IPv6) e rejeição seletiva de QUIC em UDP 443 via `ipset` (`quic_block_v4` / `quic_block_v6`) com verificação `iptables -C` idempotente. | **100% Validado no Master v2** |
| `/usr/sbin/boot-acer` e `/usr/sbin/boot-openwrt` | Pacote Master v2 | Utilitários CLI para alternância segura de partição de boot (`primaryboot=1` Slot 1 OEM / `primaryboot=0` Slot 2 OpenWrt) gravando `0:BOOTCONFIG` e `0:BOOTCONFIG1`. | **100% Validado no Master v2** |

### 2.1 Correção Definitiva do SQM CAKE Upload (`no-split-gso`) e Wi-Fi 7 6 GHz (`ecm front_end_stop`) (`dev/sqm-gso-ecm-fix/`)

| Arquivo no Roteador | Arquivo Local no Repositório | Status | Descrição da Modificação |
| :--- | :--- | :--- | :--- |
| `/etc/config/sqm` | `dev/sqm-gso-ecm-fix/sqm` | **Homologado em Produção** | Adicionado `option eqdisc_opts 'no-split-gso'` e `option iqdisc_opts 'no-split-gso'` na seção `sqm.wan`, eliminando 100% do descarte de super-pacotes GSO PPPoE (`ETH_P_PPP_SES`) no upload (destravou de `0.15 Mbps` para `366.42 Mbps`). |
| `/usr/lib/sqm/defaults.sh` | `dev/sqm-gso-ecm-fix/defaults.sh` | **Homologado em Produção** | Definido fallback padrão `no-split-gso`, `ethtool -K $IFACE gso on` e parada automática do bypass SFE (`front_end_ipv4_stop=1`, `front_end_ipv6_stop=1`, `defunct_all=1`), impedindo congelamento no pacote #25 no rádio 6 GHz (`ath2`). |
| `/etc/rc.local` | `dev/sqm-gso-ecm-fix/rc.local` | **Homologado em Produção** | Persistência no boot de `ethtool -K eth0 gso on`, sincronia de `/ini` -> `/cfg/default/ini`, disparo de `/etc/init.d/predator_rf start` e desativação condicional de offload SFE quando `sqm.wan.enabled=1`. |

### 2.2 Painel Inteligente Wi-Fi como WAN / Repetidor WISP (`dev/luci-app-wifi-wisp/`)

| Arquivo no Roteador | Arquivo Local no Repositório | Status | Descrição da Modificação |
| :--- | :--- | :--- | :--- |
| `/usr/sbin/wifi-wisp-tool` | `dev/luci-app-wifi-wisp/root/usr/sbin/wifi-wisp-tool` | **Homologado em Produção** | Motor backend de borda com suporte a escaneamento multi-banda, deduplicação BSSID/canal, auto-lock BSSID, disparo assíncrono (`connect_bg`), tracker de progresso em 4 etapas, telemetria detalhada (17 métricas: PHY rates, latência ping 1.1.1.1, bytes transferidos, uptime, DNS) e detecção/correção automática de colisão de sub-rede LAN. |
| `/www/luci-static/resources/view/wifi_wisp.js` | `dev/luci-app-wifi-wisp/root/www/luci-static/resources/view/wifi_wisp.js` | **Homologado em Produção** | Painel visual LuCI reativo: modal interativo em 4 passos com tolerância a drops momentâneos de Wi-Fi no reload (silêncio resiliente sem erro XHR), card de status conectado com 14 métricas em tempo real e remoção da barra desnecessária "Salvar e Aplicar". |
| `/usr/lib/lua/luci/controller/wifi_wisp.lua` | `dev/luci-app-wifi-wisp/root/usr/lib/lua/luci/controller/wifi_wisp.lua` | **Homologado em Produção** | Entrada de menu LuCI sob Rede > Wi-Fi como WAN (WISP) com suporte a view JS e fallback. |
| `/usr/share/luci/menu.d/luci-app-wifi-wisp.json` | `dev/luci-app-wifi-wisp/root/usr/share/luci/menu.d/luci-app-wifi-wisp.json` | **Homologado em Produção** | Definição de menu LuCI moderno (OpenWrt 19.07+ client-side routing). |
| `/usr/share/rpcd/acl.d/luci-app-wifi-wisp.json` | `dev/luci-app-wifi-wisp/root/usr/share/rpcd/acl.d/luci-app-wifi-wisp.json` | **Homologado em Produção** | Permissões ACL para o LuCI executar `/usr/sbin/wifi-wisp-tool` via ubus/rpcd. |

---

## 3. Arquivos Estritamente Protegidos (NÃO ALTERAR)

Confirmado pelos estudos de ABI e RF:

1. `/lib/firmware/qcn9224/bdwlan.b1015` e `b16`: Calibração analógica de fábrica inviolável. Não copiar de outros roteadores.
2. Módulos de Kernel `.ko` do Cudy (`umac.ko`, `qca_ol.ko`): Incompatíveis em tempo de link com o kernel atual do Acer por falta de símbolos exportados (`__netdev_alloc_skb_fast`, `pcie_parf_read`).

---

## 4. Procedimento de Empacotamento e Consolidação Final (`cfg_restauracao_master_v2.cfg` — 14/10/2026)

1. **Backup prévio do CFG Master:**
   ```bash
   cp cfg_restauracao_master_v2.cfg cfg_restauracao_master_v2.cfg.bak.$(date +%Y%m%d_%H%M%S)
   ```
2. **Extração, inserção dos arquivos validados e remontagem (sem metadados AppleDouble):**
   ```bash
   mkdir -p /tmp/cfg_repack && cd /tmp/cfg_repack
   tar -xzf "/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/cfg_restauracao_master_v2.cfg"
   # Copiar arquivos homologados e normalizar permissões 644 (views/json/configs) e 755 (scripts/binários)
   find . -name "._*" -o -name "*.orig" | xargs rm -f
   chmod -R a+rX www usr/share usr/lib/lua
   find www usr/share -type f -exec chmod 0644 {} +
   GZIP=-9 COPYFILE_DISABLE=1 tar --no-mac-metadata --uid 0 --gid 0 --uname root --gname root -czf "/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/cfg_restauracao_master_v2.cfg" .
   ```
3. **Métricas do Artefato Master Consolidado:**
   * **Tamanho Final Verificado**: `721 KB` (`738.427 bytes`)
   * **SHA-256 Oficial**: `6e5a00bc60e6d9960c4b98796e675a8eeb7573db1e211821d2a563146f7809a5`
   * **Módulos Adicionais Incorporados e Homologados em Produção**:
     - `/usr/sbin/wifi-wisp-tool` e `/www/luci-static/resources/view/wifi_wisp.js`: Painel Visual WISP com Anti-Loopback, Auto-Rollback de 15s, detecção de conflito de sub-rede, crachás de largura em MHz (`20/40/80/160/320 MHz`) e geração (`Wi-Fi 4/5/6/6E/7`).
     - `/www/luci-static/resources/view/status/include/60_wifi.js` e `/usr/share/rpcd/acl.d/luci-mod-status-predator.json`: Widget nativo Wi-Fi 7 na tela Status Overview do LuCI (com Piso de Ruído RF e % de Espectro Livre).
     - `/etc/uci-defaults/99-debloat-v2`: Padronização do hostname RFC 1123 (`Predator-Connect-T7`), SLAAC IPv6 (`ra='server'`), KSMBD auto-mount e limpeza de serviços conflitantes.
     - `/sbin/wifi`, `/usr/sbin/boot-acer`, `/usr/sbin/boot-openwrt`, `/usr/bin/iperf` (`v2.0.13-1` multi-thread `pthreads`), `/usr/sbin/ethtool` (`v5.10-1`), `/usr/sbin/igmpproxy` (`v0.2.1-4`), `/usr/bin/tracepath` (`v20210202-1`), `/etc/ssl/certs/ca-certificates.crt` (`ca-bundle 20260601`) e `/usr/lib/opkg/status` já com os 261 pacotes críticos em `hold` e zero atualizações pendentes.
     - **Trava Real de 40 MHz em 2.4 GHz (`HT40_FORCE`)**: Distinção explícita no frontend (`predator_wifi.js`) e backend (`usr/libexec/rpcd/predator`, `etc/init.d/predator_rf`, `usr/sbin/predator-wifi-guard`) entre `Auto (20/40 MHz)` (`HT40` com coexistência OBSS ativa) e `40 MHz` travado (`HT40_FORCE` com `disablecoext=1`, `chan_coex_disable=1`, `chwidth=1` e canal fixo caso estivesse em `auto`), ignorando o bit *40 MHz Intolerant* de clientes Apple/iOS.
     - **Frentes 1 & 2 (Backports do X7 `v1.01.000050` de Agosto/2026 + Desbloqueio de Silício Qualcomm)**: Backport de `ap_isbasic` (`beacon_prot=0; add_sha256=0`), escapamento UCI e `del_wifi_teardown_vaps()`, escalonamento de anéis DMA do perfil `[512M]` para nível `1GB-Tier` (`16384`/`8192`), ativação de `r-TWT`, `MSCS`, `SCS`, `HLOS TID Override`, `PPE-DS` com `cake_enabled=1` e telemetria ao vivo de Espectro RF (CCA Airtime / OBSS / Não-Wi-Fi / Noise Floor).
     - **Menu Dedicado de Engenharia de Silício Qualcomm, Controle de Conflitos, SQM em MB/Mbps e Localização Tri-Idioma (`PT-BR` / `EN` / `ES`)**: Painel interativo (`renderSiliconMenuCard` + `buildConflictsNode` em `predator_wifi.js`) + interface `/cgi-bin/luci/admin/network/sqm` (`sqm.lua`, `run.sh`, `defaults.sh`, `/etc/config/sqm`) exibindo e persistindo velocidades diretamente em **MB / Mbps** (`800` Download / `400` Upload, com conversão automática `x1000` para o `tc cake`), 100% traduzidos em Português, Inglês e Espanhol.
     - **Desbloqueio e Validação Real de 240 MHz (`HT240` / `11AEHT320` Punctured `0xf000`) em 5 GHz & 6 GHz + Página Dedicada `Predator Central de Apps` (`predator_apps.js`) + Escudo `opkg` Hold + Raio-X PMTU/2.5G/iperf**: Suporte completo a `240 MHz` em 5 GHz (`vht/he/eht_oper_chwidth=2` no `hostapd.sh` + `mode 11AEHT320`, `puncture_bitmap=61440`, `dfs_puncture_en=1`, `puncture_strict=0`, `set_cactimeout=1` no `qcawificfg80211.sh`, subindo em 1.1s com `center1: 5650 MHz`) e em 6 GHz, página dedicada `/cgi-bin/luci/admin/network/predator_apps` (WireGuard VPN, OpenVPN com model CBI `/usr/lib/lua/luci/model/cbi/openvpn.lua`, Wake-on-LAN, Agendador Eco Wi-Fi, DoH/QUIC/IPTV com crachás de status em tempo real e botões Ligar/Desligar/Restaurar, Auto-Otimizador CCA, Escudo `opkg` com 261 pacotes em `hold` e Card 8 de Diagnóstico de Rota PMTU `tracepath` + `ethtool 5.10` + `iperf 2.0.13`).
     - **Ponte QSDK Nativa para a Página LuCI Wireless Overview (`/cgi-bin/luci/admin/network/wireless`) e Sub-seções (`Scan`, `Join`, `Edit`, `Add`, `Restart`, `Associated Stations`) + Trava Atômica de Boot `predator_rf`**: Atualizados `/usr/libexec/rpcd/predator`, `/usr/libexec/rpcd/luci`, `/usr/share/rpcd/acl.d/luci-app-predator-wifi.json`, `/www/luci-static/resources/network.js`, `/www/luci-static/resources/view/network/wireless.js`, `/sbin/wifi` e `/etc/init.d/predator_rf` para comunicação direta e eficiente com o driver `qcawificfg80211` e proteção contra corrida de `wifi load` no boot.
