# Especificação Técnica e Proposta de Integração: Módulos de Estabilidade e Performance para o ARK Router

> **Documento de Engenharia de Sistemas & Redes**  
> **Plataforma Alvo**: Acer Predator Connect T7 (Qualcomm IPQ5332 + QCN9224 / OpenWrt QSDK Linux 5.4.213)  
> **Projeto de Destino**: [ARK Router (`luci-app-ark-router`)](https://github.com/Despensativo/ark-router)  
> **Data de Homologação**: 14 de Outubro de 2026  
> **Status**: Pronto para Upstream / Homologado em Produção

---

## 1. Sumário Executivo e Objetivos

Durante a engenharia reversa e otimização intensiva do roteador **Acer Predator Connect T7 (Wi-Fi 7 Tri-Band)**, foram identificados e solucionados problemas estruturais graves presentes tanto no firmware de fábrica da OEM quanto em compilações genéricas de OpenWrt para a arquitetura Qualcomm IPQ53xx/QCN92xx.

Este documento consolida todas as causas-raiz descobertas, procedimentos implementados, arquitetura técnica e justificativas de engenharia, servindo como **proposta formal e guia de integração direta para a suíte oficial ARK Router**.

### Benefícios Diretos para o ARK Router:
1. **Zero Boot Loop**: Eliminação definitiva dos resets cíclicos de 60 a 100 segundos da Qualcomm.
2. **Wi-Fi 7 Real em 320 MHz e 160 MHz**: Integração com orquestrador de rádio e guardião anti-erro com rollback automático.
3. **Compartilhamento de Arquivos de Alta Performance (KSMBD)**: Substituição do Samba 4 por módulo nativo no kernel Linux, reduzindo o consumo de RAM de ~200 MB para < 10 MB.
4. **Resolução Definitiva de Bufferbloat (SQM CAKE)**: Neutralização do afunilamento de upload PPPoE (< 1 Mbps para 350+ Mbps) e eliminação do congelamento de fluxos Wi-Fi 7 no pacote #25 (conflito ECM SFE).
5. **Filtragem Seletiva Dinâmica de QUIC (HTTP/3)**: Abordagem padrão RFC via `ipset` e `dnsmasq`, acabando com o bloqueio global de UDP 443 e preservando VPNs corporativas.
6. **DNS Criptografado Ultraleve (DoH)**: Dual-resolver Cloudflare + Google via daemon em C com cache instantâneo em RAM.

---

## 2. Diagnóstico das Falhas e Causas-Raiz no Acer T7

### 2.1. O Ciclo de Reinicialização de 60–100s (SoC Hardware Watchdog)
* **Causa Raiz**: O `procd` abre `/dev/watchdog` na inicialização com timeout de 30 segundos. Scripts de debloat ou customizações executavam chamadas como `ubus call system watchdog '{"stop": true}'` ou tentavam encerrar daemons usando o método de encerramento mágico (*magic close*). Como o watchdog de hardware do chip Qualcomm IPQ5332 não era alimentado por outro processo, ele disparava um *hard reset* de hardware exatamente 30s após a interrupção.
* **Solução Implementada**: Forçar a alimentação contínua via procd com frequência segura de 5s:
  ```sh
  ubus call system watchdog '{"stop": false, "frequency": 5}'
  ```

### 2.2. O Crash do Firmware QCN9224 MLO IPC (`ar_wal_mlo_ipc.c:1065`)
* **Causa Raiz**: No arquivo `/ini/internal/QCN9224_i.ini`, o parâmetro de fábrica `dp_mlo_reo_rings_map=0x7` tentava inicializar anéis de MLO entre o SoC e a placa PCIe antes do término da calibração a frio da RF. Isso gerava um `Assertion 0 failed` no microcódigo do subsistema de rádio (`5332.wlanfw.evalQ`), levando o kernel Linux a entrar em pânico no driver `qca_ol.ko` (`Assertion failed! 0:ol_ath_unified_event_handler` / `kernel BUG at i_qdf_trace.h:402`).
* **Solução Implementada**: Cravar `dp_mlo_reo_rings_map=0` tanto em `/ini/internal/QCN9224_i.ini` quanto em `/cfg/default/ini/internal/QCN9224_i.ini`.

### 2.3. O Deadlock em Estado D (Sono Ininterruptível) por `setCountryID 840`
* **Causa Raiz**: O script de bring-up da Qualcomm `/lib/wifi/qcawificfg80211.sh` disparava prematuramente `cfg80211tool wifi0 setCountryID 840` na função `set_default_country()`. Como os módulos PCIe ainda estavam executando calibração RF a frio em background, o comando colidia com a trava do driver (`probe lock`), travando o processo `cfg80211tool.1` e a chamada `wifi up` em Estado D no kernel.
* **Solução Implementada**: Bypassar a execução prematura do `setCountryID 840` na função `set_default_country()`, permitindo que os rádios completem a calibração antes de qualquer chamada de userspace.

### 2.4. O Failsafe Reiniciador (`predator_dev`)
* **Causa Raiz**: O script proprietário `/etc/init.d/predator_dev` incrementava contadores de falha se o uptime fosse menor que 75 segundos e gravava a troca de partição nas variáveis de ambiente do U-Boot (`boot_fail_count`). Se o roteador reiniciasse duas vezes, o script invertia a partição ativa e travava o dispositivo em loop entre Slot 1 e Slot 2.
* **Solução Implementada**: Remoção dos symlinks de inicialização `/etc/rc.d/*predator_dev*`, desativação via UCI (`uci set predator_dev.failsafe.enabled='0'`) e zeramento do contador na U-Boot NVRAM.

---

## 3. Módulos Propostos para Upstream no ARK Router

```
                      ┌─────────────────────────────────────────────────────────────┐
                      │                 ARK ROUTER MASTER SUITE                     │
                      └──────────────────────────────┬──────────────────────────────┘
                                                     │
       ┌──────────────┬──────────────┬───────────────┼──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼               ▼              ▼              ▼              ▼
 ┌───────────┐  ┌───────────┐  ┌───────────┐   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
 │  MÓDULO 1 │  │  MÓDULO 2 │  │  MÓDULO 3 │   │  MÓDULO 4 │  │  MÓDULO 5 │  │  MÓDULO 6 │  │  MÓDULO 8 │
 │ Estabiliz.│  │  Wi-Fi 7  │  │   KSMBD   │   │ QUIC IPSet│  │ SQM CAKE  │  │ DoH Cache │  │ WISP WAN  │
 │ Hardware  │  │ Tri-Band  │  │  Kernel   │   │ Seletivo  │  │ Coexist.  │  │ Dual-DNS  │  │ Blindado  │
 │ Watchdog  │  │ Orquestr. │  │  SMB 3.1  │   │  RFC 8899 │  │ PPPoE Fix │  │ Criptogr. │  │ Anti-Loop │
 └───────────┘  └───────────┘  └───────────┘   └───────────┘  └───────────┘  └───────────┘  └───────────┘
```

---

### Módulo 1: Motor de Estabilização e Watchdog de Hardware
**Arquivo Alvo no ARK**: `/etc/rc.local` e `/etc/sysctl.d/99-panic-lock.conf`

* **Alimentação Contínua de Hardware**:
  ```sh
  ubus call system watchdog '{"stop": false, "frequency": 5}' 2>/dev/null
  ```
* **Imunidade a Pânico de Kernel**:
  Evita que erros não-críticos de módulos proprietários de Wi-Fi reiniciem a máquina:
  ```conf
  kernel.panic = 0
  kernel.panic_on_oops = 0
  ```
* **Trava do Parâmetro MLO IPC**:
  Garante que nenhuma restauração de backup sobrescreva o valor seguro:
  ```sh
  [ -f /ini/internal/QCN9224_i.ini ] && sed -i 's/dp_mlo_reo_rings_map=.*/dp_mlo_reo_rings_map=0/' /ini/internal/QCN9224_i.ini 2>/dev/null || true
  ```

---

### Módulo 2: Orquestrador Wi-Fi 7 Tri-Band & Guardião Anti-Erro
**Arquivos Alvo no ARK**:
* `/www/luci-static/resources/view/predator_wifi.js` (Interface LuCI JS)
* `/usr/share/luci/menu.d/luci-app-predator-wifi.json` (Manifesto de Menu)
* `/usr/share/rpcd/acl.d/luci-app-predator-wifi.json` (Permissões ACL)
* `/usr/libexec/rpcd/predator` (Backend RPC)
* `/usr/sbin/predator-wifi-guard` (Daemon Guardião)

#### O Guardião de Auto-Cura (`predator-wifi-guard`):
1. **Validação Prévia**: Intercepta comandos de `/sbin/wifi` e valida se a sintaxe de canal, largura (`HT40`, `HT160`, `HT320`) e potência são aceitas pelo rádio.
2. **Rollback Automático**: Monitora o estado de `hostapd` pós-aplicação. Se os 3 rádios não atingirem o status `ENABLED` dentro de 30 segundos, o guardião reverte automaticamente para o backup validado em `/etc/predator/wireless.lastgood`.
3. **Co-locação RNR (Reduced Neighbor Reporting)**: Anuncia a presença da banda de 6 GHz nos beacons das bandas de 2.4 GHz e 5 GHz, permitindo descoberta imediata de clientes Wi-Fi 7 (iPhone 16, Galaxy S24, placas Intel BE200).

---

### Módulo 3: Armazenamento no Kernel (KSMBD SMB 3.1.1) vs. Samba 4
**Arquivos Alvo no ARK**:
* `/www/luci-static/resources/view/ksmbd.js`
* `/usr/lib/lua/luci/controller/ksmbd.lua` e `/usr/share/luci/menu.d/luci-app-ksmbd.json`
* `/usr/share/rpcd/acl.d/luci-app-ksmbd.json`
* `/usr/sbin/ksmbd-disk-tool`
* `/etc/config/ksmbd` e `/etc/init.d/ksmbd`
* `/etc/config/fstab`

#### Comparativo de Engenharia: Samba 4 vs. KSMBD
| Métrica | Samba 4 Legado | KSMBD (Kernel Linux) | Ganho no ARK Router |
| :--- | :--- | :--- | :--- |
| **Camada de Execução** | Userspace (`smbd`, `nmbd`) | Kernel-space (`/sys/module/ksmbd`) | Zero context-switching de CPU |
| **Consumo de Memória RAM** | 150 MB a 250 MB | **< 10 MB** | **Economia de >90% de RAM** |
| **Throughput em SSD USB 3.0** | ~60–80 MB/s (gargalo CPU) | **112+ MB/s (Line-Rate Gigabit)** | Saturação total da porta física |
| **Compatibilidade Apple/macOS** | Requer VFS modules pesados | Suporte nativo a `streams_xattr` | Time Machine e Finder instantâneos |

#### Travas de Segurança do `ksmbd-disk-tool`:
O utilitário foi desenhado com verificação estrita de barramento:
```sh
case "$DEV" in
    *mtd*|*ubi*|*rom*|*boot*|*kernel*|*rootfs*)
        echo "FATAL: Partição interna de sistema! Operação abortada."; exit 1 ;;
    /dev/sd[a-z][0-9]*|/dev/nvme*) ;; # Aceito exclusivamente discos externos
    *) exit 1 ;;
esac
```

---

### Módulo 4: Filtragem Seletiva Dinâmica de QUIC (HTTP/3) via IPSet
**Arquivos Alvo no ARK**: `/etc/config/dhcp`, `/etc/config/firewall`, `/etc/firewall.user`

#### Por que o bloqueio global de UDP 443 é um erro em 2026?
Bloquear `udp --dport 443` globalmente destrói:
* VPNs corporativas (WireGuard/OpenVPN em UDP 443 usadas em home office);
* A migração de conexão (*Connection Migration*) do QUIC (chamadas FaceTime/WhatsApp sem queda ao trocar de Wi-Fi);
* O benefício anti-Head-of-Line Blocking do HTTP/3.

#### A Solução Padrão RFC (Dnsmasq + IPSet):
O `dnsmasq` intercepta dinamicamente a resolução DNS dos serviços onde o QUIC sabidamente sofre estrangulamento (*throttling*) de operadoras ou incompatibilidade de MTU, e preenche uma tabela hash na memória RAM do kernel:

1. **Alimentação no `/etc/config/dhcp`**:
   ```uci
   list ipset '/googlevideo.com/quic_block_v4,quic_block_v6'
   list ipset '/youtube.com/quic_block_v4,quic_block_v6'
   list ipset '/ytimg.com/quic_block_v4,quic_block_v6'
   list ipset '/gvt1.com/quic_block_v4,quic_block_v6'
   list ipset '/fbcdn.net/quic_block_v4,quic_block_v6'
   list ipset '/instagram.com/quic_block_v4,quic_block_v6'
   list ipset '/waveform.com/quic_block_v4,quic_block_v6'
   list ipset '/speedtest.net/quic_block_v4,quic_block_v6'
   list ipset '/fast.com/quic_block_v4,quic_block_v6'
   ```
2. **Regras de Rejeição Rápida no Firewall (`/etc/config/firewall`)**:
   ```uci
   config rule
       option name 'Reject-Selective-QUIC-v4'
       option src 'lan'
       option dest 'wan'
       option proto 'udp'
       option dest_port '443'
       option ipset 'quic_block_v4'
       option target 'REJECT'
   ```
3. **Resultado**: 
   * Na primeira conexão, a resolução DNS ocorre antes do primeiro pacote UDP. O IP cai na tabela em microssegundos.
   * O YouTube e sites de teste fazem fallback imediato para HTTP/2 (TCP) onde o MSS Clamping atua perfeitamente.
   * **Todo o restante da internet moderna continua usando HTTP/3 / QUIC nativo.**

---

### Módulo 5: Coexistência de SQM CAKE e Aceleração de Hardware (ECM SFE)
**Arquivos Alvo no ARK**: `/etc/config/sqm`, `/usr/lib/sqm/defaults.sh`

1. **Correção do Upload PPPoE (`no-split-gso`)**:
   * O kernel QSDK 5.4 não possui handler de descarregamento para super-pacotes encapsulados em PPPoE (`ETH_P_PPP_SES` / `0x8864`). A flag padrão `split-gso` do CAKE descartava esses pacotes, derrubando o upload de 400 Mbps para 0.15 Mbps.
   * **Ajuste Homologado**: Forçar `IQDISC_OPTS="no-split-gso"` e `EQDISC_OPTS="no-split-gso"` em `/usr/lib/sqm/defaults.sh` e `/etc/config/sqm`.
2. **Neutralização do Congelamento no Pacote #25**:
   * O acelerador `qca-nss-ecm` (`sfe`), ao tentar desviar o fluxo do rádio de 6 GHz (`ath2` com Virtual Port PPE), causava congelamento TCP de fluxos IPv4 exatamente na marca de 25 pacotes transferidos.
   * **Ajuste Homologado**: No `/usr/lib/sqm/defaults.sh` e `/etc/rc.local`:
     ```sh
     echo 1 > /sys/kernel/debug/ecm/front_end_ipv4_stop
     echo 1 > /sys/kernel/debug/ecm/front_end_ipv6_stop
     echo 1 > /sys/kernel/debug/ecm/ecm_db/defunct_all
     ```
   * **Performance Validada**: Waveform **Nota A+** (Cabo: 748 Mbps Down / 356 Mbps Up / +0ms) e **Nota A** (Wi-Fi 7 6 GHz: 557 Mbps Down / 305 Mbps Up).

---

### Módulo 6: Resolução de Nomes Ultrarrápida e Criptografada (DoH)
**Arquivos Alvo no ARK**: `/etc/config/https-dns-proxy`, `/etc/config/dhcp`, `/usr/sbin/https-dns-proxy`

* **Sem Invasão de Privacidade do Provedor**: Todo tráfego de DNS é encapsulado em HTTPS TLS na porta 443 via Cloudflare (`127.0.0.1:5053`) e Google (`127.0.0.1:5054`).
* **Cache em RAM Instantâneo**: Configurado no `dnsmasq` com `cachesize '5000'` e `allservers '1'` (consulta concorrente dos dois resolvedores). Consultas repetidas respondem em **0.00 ms**.
* **Zero AdBlock Quebrando Aplicações**: Não utiliza filtros agressivos que quebram autenticações bancárias, PIX ou links de compras.

---

### Módulo 7: Acesso Remoto Universal com Tolerância a Falhas
**Arquivos Alvo no ARK**: `/etc/config/dropbear`, `/etc/init.d/telnet`, `/etc/rc.local`

* **SSH (Dropbear)**: Escuta em `0.0.0.0:22` (todas as interfaces locais, protegido pelo firewall na WAN). Senha `root0100` e chave pública autorizada.
* **Telnet com Auto-Respawn via Procd**:
  ```sh
  start_service() {
      procd_open_instance
      procd_set_param command /usr/sbin/telnetd -F -l /bin/ash
      procd_set_param respawn 3600 5 0
      procd_close_instance
  }
  ```
  Mesmo que o daemon seja finalizado acidentalmente, o `procd` o reabre instantaneamente, garantindo acesso de resgate em caso de falhas na rede.

---

### Módulo 8: Painel Visual Inteligente & Blindado de Wi-Fi como WAN (WISP / Repetidor)
**Arquivos Alvo no ARK**:
* `/www/luci-static/resources/view/wifi_wisp.js` (Interface LuCI JS com polling reativo)
* `/usr/sbin/wifi-wisp-tool` (Motor de Borda CLI e Sanitização JSON)
* `/usr/share/luci/menu.d/luci-app-wifi-wisp.json` (Manifesto de Menu LuCI)
* `/usr/share/rpcd/acl.d/luci-app-wifi-wisp.json` (Permissões de Execução RPCD)
* `/usr/lib/lua/luci/controller/wifi_wisp.lua` (Compatibilidade LuCI Legado)

#### Por que o OpenWrt Padrão falha em Repetidor / WISP no Qualcomm QSDK?
1. O LuCI padrão depende de `iwinfo`, que frequentemente entra em timeout em drivers proprietários QCA porque o subsistema SPF utiliza `cfg80211tool` e `wext` ao invés de responder instantaneamente a chamadas genéricas `nl80211`.
2. Se o usuário digitar a senha errada ou a rede externa sair do ar, o `netifd` fica em loop contínuo de reconexão, provocando instabilidade e latência nos rádios locais (AP).
3. Se o usuário tentar conectar o roteador à sua própria rede Wi-Fi (`GAMER_7G`), fecha-se um loop L2/L3 com tempestade de broadcast (*broadcast storm*) que satura a CPU e derruba a rede.
4. Se o IP recebido da rede externa for idêntico à sub-rede LAN (`192.168.76.x`), o roteamento entra em colapso devido à colisão de sub-redes.

#### Arquitetura e Blindagens Anti-Erro Implementadas:
* **Detecção Dinâmica de Própria Rede (Anti-Loopback)**: O backend mapeia dinamicamente todos os SSIDs e endereços MAC (BSSIDs) de todas as interfaces físicas e virtuais (`ath0`, `ath1`, `ath2`). Na interface visual, a própria rede é sinalizada em vermelho com a etiqueta `⚠️ Própria Rede (Loop Bloqueado)` e o botão de conexão é desativado. No backend, qualquer tentativa direta é sumariamente abortada com código de erro fatal.
* **Auto-Rollback com Guardião de 15 Segundos**: Ao disparar a conexão, o script monitora a obtenção do IP via DHCP. Se em 15 segundos a rede externa não responder (senha incorreta, filtro de MAC ou sinal insuficiente), o script aciona rollback instantâneo (`cp -f /tmp/wireless.backup.wisp /etc/config/wireless` e `wifi reload`), mantendo os rádios locais e os clientes 100% online sem travamentos.
* **Detecção e Correção em 1 Clique de Colisão de Sub-rede**: Se a WAN Wi-Fi receber um IP na faixa `192.168.76.x`, o painel exibe um alerta de alta prioridade com o botão `[ 🛠️ Corrigir Conflito Agora ]`, que reconfigura a LAN para `192.168.77.1` automaticamente, instruindo o usuário sobre o novo endereço de acesso.
* **Alocação Inteligente de Rádio Físico por Espectro**:
  * 2.4 GHz -> Rádio `wifi0` (SoC IPQ5332)
  * 5 GHz -> Rádio `wifi1` (QCN9224 PCIe)
  * 6 GHz -> Rádio `wifi2` (QCN9224 PCIe) com imposição mandatória de `sae` (WPA3-SAE, obrigatório pela norma IEEE 802.11be em 6 GHz).
* **Prioridade Automática de Roteamento (Cabo vs Wi-Fi)**: O link WWAN recebe `metric 20`, enquanto a WAN cabeada Ethernet opera em `metric 10`. Ao plugar o cabo de rede de 2.5 Gbps, o tráfego migra instantaneamente para o cabo sem precisar desativar o Wi-Fi; ao desplugar o cabo, o tráfego retorna para o Wi-Fi em milissegundos.
* **Detecção de Captive Portal (Hotspots de Hotel/Aeroporto)**: Testa a conectividade real via ping e curl; caso o rádio esteja associado mas sem internet, alerta o usuário para abrir o navegador no smartphone e aceitar o login no portal.
* **Suporte Completo a Redes Ocultas**: Botão dedicado `[ ➕ Conectar a Rede Oculta (Manual) ]` permitindo inserir SSID, banda, padrão de criptografia e chave.
* **Detecção Confiável de Segurança & Multi-BSSID (Roaming vs Fixação em Ponto Específico)**:
  * *Resolução do bug de varredura*: O script `wifi-wisp-tool` implementa a função `flush_bss()` no BusyBox awk para garantir que flags de RSN/WPA/SAE sejam computadas antes de emitir o registro da rede. Isso elimina falsos-positivos onde redes protegidas (como WPA2-PSK) eram rotuladas erroneamente como "Aberta".
  * *Multi-BSSID e Redes de Mesmo Nome*: Em ambientes com repetidores, nós Mesh ou redes corporativas/residenciais que usam o mesmo SSID em 2.4 GHz e 5 GHz, a tabela lista cada BSSID (endereço MAC) individual com seu canal, frequência em MHz e sinal.
  * *Controle de Roaming Inteligente*: Na janela de conexão, o usuário dispõe do seletor `[x] Fixar conexão neste ponto de acesso específico (BSSID)`.
    * **Marcado (BSSID Lock)**: O T7 crava a conexão no rádio/MAC escolhido via `uci set wireless.wwan_sta.bssid='...'`, impedindo que o roteador caia para frequências lentas de 2.4 GHz.
    * **Desmarcado (Roaming Dinâmico)**: O parâmetro `bssid` é omitido, permitindo que o `wpa_supplicant` transite livremente e de forma inteligente entre múltiplos nós ou bandas da mesma rede, priorizando sempre a melhor relação sinal/qualidade.

---

### Módulo 9: Telemetria Wi-Fi 7 Nativa no LuCI Status Overview & Padronização RFC 1123 de Hostname
**Arquivos Alvo no ARK**:
* `/www/luci-static/resources/view/status/include/60_wifi.js` (Widget moderno para LuCI Status -> Overview)
* `/usr/share/rpcd/acl.d/luci-mod-status-predator.json` (Permissão de leitura para o perfil `luci-access`)
* `/etc/config/system` e `/etc/uci-defaults/99-debloat-v2` (Padronização e persistência de Hostname RFC 1123)

#### Por que o LuCI Status Overview padrão falha no Qualcomm QSDK?
No OpenWrt padrão, a tela de visão geral (`/cgi-bin/luci/admin/status/overview`) carrega `/www/luci-static/resources/view/status/include/60_wifi.js`, que invoca `network.getWifiDevices()` e `iwinfo`. No driver QCA SPF12.2, o `iwinfo` não reconhece a topologia Wi-Fi 7 (canais de 320 MHz, 4096-QAM e dispositivos QCN9224), resultando em caixas vazias, informações corrompidas ou falha silenciosa de renderização.

#### Solução Implementada e Homologada:
1. **Widget Dedicado de Wi-Fi 7**: O arquivo `60_wifi.js` foi reescrito para consultar diretamente o orquestrador `predator.get_status` via RPCD, renderizando cards visuais de telemetria completa para as 3 bandas:
   * **2.4 GHz**: Status Online, SSID ativo, Canal, Largura em MHz, Potência real de TX em dBm e Temperatura do SoC.
   * **5 GHz**: Status Online, SSID ativo, Canal, Largura (160 MHz), Potência real e Temperatura.
   * **6 GHz Wi-Fi 7**: Status Online, SSID ativo, Canal, Largura máxima de 320 MHz, Potência e Temperatura.
   * **Tabela de Clientes Conectados**: Mostra dispositivo/host, endereço MAC, banda (2.4G / 5G / 6G Wi-Fi 7), sinal (dBm + barra de qualidade %) e tempo de conexão.
   * **Atalho Direto**: Botão no topo levando ao painel completo `/cgi-bin/luci/admin/network/predator_wifi`.
2. **Permissão de Acesso Global (RPCD ACL)**: O arquivo `/usr/share/rpcd/acl.d/luci-mod-status-predator.json` adiciona a permissão de leitura de `predator.get_status` ao perfil `luci-access`, garantindo que qualquer usuário autenticado no LuCI visualize os dados na tela inicial.
3. **Hostname Padronizado RFC 1123**: O hostname de fábrica continha espaços (`Predator Connect T7`), o que quebrava conformidade com a RFC 1123, gerava falhas em leases DHCP de operadoras e erros em scripts de terminal. Foi fixado e garantido na primeira inicialização (`99-debloat-v2`) como:
   ```sh
   uci set system.@system[0].hostname='Predator-Connect-T7'
   ```

---

## 4. Pacote Homologado de Restauração

O arquivo master contendo a implementação completa de todos os 9 módulos acima foi empacotado e commitado:
* **Arquivo**: `cfg_restauracao_master_v2.cfg`
* **Localização**: Raiz do repositório
* **Tamanho**: `349 KB` (357.390 bytes)
* **SHA256**: `b135ced45c6d2540a39bfa74c027b0864441f503731d928a992189f17aaecfbf`
* **Padrão de Criação**: `COPYFILE_DISABLE=1 tar --no-mac-metadata -czf`

---

## 5. Roteiro Sugerido para Integração no Repositório ARK Router

Para mesclar esta solução no código-fonte do `luci-app-ark-router`:
1. **Adicionar arquivos estáticos web**: Copiar `/www/luci-static/resources/view/ksmbd.js`, `predator_wifi.js`, `wifi_wisp.js` e `status/include/60_wifi.js` para o diretório de assets do ARK.
2. **Integrar ACLs e Menus**: Incorporar os arquivos de `/usr/share/luci/menu.d/` e `/usr/share/rpcd/acl.d/` (incluindo `luci-mod-status-predator.json`) no pacote IPK do ARK.
3. **Adicionar os Scripts de Borda**:
   * Incluir `/usr/sbin/ksmbd-disk-tool`, `/usr/sbin/predator-wifi-guard` e `/usr/sbin/wifi-wisp-tool` no diretório `/usr/sbin/` do pacote.
   * Adicionar a rotina do `ipset` QUIC no template do `/etc/config/firewall` e `/etc/config/dhcp`.
4. **Incluir as Otimizações no Post-Install Script (`postinst`)**:
   * Configurar o watchdog seguro (`{"stop": false, "frequency": 5}`).
   * Garantir `dp_mlo_reo_rings_map=0` nos arquivos `.ini`.
   * Habilitar o `defaults.sh` com `no-split-gso` para o SQM.
   * Padronizar o hostname sem espaços via `uci set system.@system[0].hostname='Predator-Connect-T7'`.

---
*Documentação gerada com base nos testes e diagnósticos homologados em hardware real do Acer Predator Connect T7.*

