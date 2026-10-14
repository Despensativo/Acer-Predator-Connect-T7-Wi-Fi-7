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
                      ┌──────────────────────────────────────────────┐
                      │          ARK ROUTER MASTER SUITE             │
                      └──────────────────────┬───────────────────────┘
                                             │
      ┌──────────────────┬───────────────────┼───────────────────┬──────────────────┐
      ▼                  ▼                   ▼                   ▼                  ▼
┌───────────┐      ┌───────────┐       ┌───────────┐       ┌───────────┐      ┌───────────┐
│  MÓDULO 1 │      │  MÓDULO 2 │       │  MÓDULO 3 │       │  MÓDULO 4 │      │  MÓDULO 5 │
│ Estabiliz.│      │  Wi-Fi 7  │       │   KSMBD   │       │ QUIC IPSet│      │ SQM CAKE  │
│ Hardware  │      │ Tri-Band  │       │  Kernel   │       │ Seletivo  │      │ Coexist.  │
│ Watchdog  │      │ Orquestr. │       │  SMB 3.1  │       │  RFC 8899 │      │ PPPoE Fix │
└───────────┘      └───────────┘       └───────────┘       └───────────┘      └───────────┘
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

## 4. Pacote Homologado de Restauração

O arquivo master contendo a implementação completa de todos os módulos acima foi empacotado e commitado:
* **Arquivo**: `cfg_restauracao_master_v2.cfg`
* **Localização**: Raiz do repositório
* **Tamanho**: `328 KB` (335.630 bytes)
* **SHA256**: `422b1cb49f8f9aef44ba56f6aae8a173ec40eb2b99c5a536dc23cd8884618c51`
* **Padrão de Criação**: `COPYFILE_DISABLE=1 tar --no-mac-metadata -czf`

---

## 5. Roteiro Sugerido para Integração no Repositório ARK Router

Para mesclar esta solução no código-fonte do `luci-app-ark-router`:
1. **Adicionar arquivos estáticos web**: Copiar `/www/luci-static/resources/view/ksmbd.js` e `predator_wifi.js` para o diretório de assets do ARK.
2. **Integrar ACLs e Menus**: Incorporar os arquivos de `/usr/share/luci/menu.d/` e `/usr/share/rpcd/acl.d/` no pacote IPK do ARK.
3. **Adicionar os Scripts de Borda**:
   * Incluir `/usr/sbin/ksmbd-disk-tool` e `/usr/sbin/predator-wifi-guard` no diretório `/usr/sbin/` do pacote.
   * Adicionar a rotina do `ipset` QUIC no template do `/etc/config/firewall` e `/etc/config/dhcp`.
4. **Incluir as Otimizações no Post-Install Script (`postinst`)**:
   * Configurar o watchdog seguro (`{"stop": false, "frequency": 5}`).
   * Garantir `dp_mlo_reo_rings_map=0` nos arquivos `.ini`.
   * Habilitar o `defaults.sh` com `no-split-gso` para o SQM.

---
*Documentação gerada com base nos testes e diagnósticos homologados em hardware real do Acer Predator Connect T7.*
