# Relatório Técnico: Acesso ao Acer Predator T7 e Diagnóstico de IPv6 em Modo AP

**Data da Auditoria:** 30/09/2026  
**Equipamentos Auditados:**
1. **Roteador Primário (Gateway):** ARK Router OS • LuCI 25.12.5 (`192.168.73.1`)
2. **Roteador Secundário (AP Sob Teste):** Acer Predator Connect T7 (`192.168.73.2`)

---

## 1. Dados de Acesso ao Segundo Roteador (Acer Predator T7)

O Acer T7 está operando como **Dumb Access Point (Ponte L2)** no endereço IP estático `192.168.73.2`.

| Serviço | Porta | Usuário | Senha | Observações / Parâmetros Necessários |
| :--- | :--- | :--- | :--- | :--- |
| **SSH** | `22` | `root` | `admin0100` | Requer cifras legadas RSA (Dropbear OpenWrt 19.07):<br>`ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedKeyTypes=+ssh-rsa root@192.168.73.2` |
| **Telnet** | `23` | *(sem login)* | *(sem senha)* | Acesso direto ao shell `ash` (útil em caso de emergência):<br>`telnet 192.168.73.2` |
| **LuCI (OpenWrt)** | `8080` | `root` | `admin0100` | Web UI OpenWrt:<br>`http://192.168.73.2:8080` |
| **Web UI Acer (OEM)** | `80` / `443` | `admin` | `admin0100` | Interface gráfica original da Acer:<br>`http://192.168.73.2` |

> [!NOTE]
> Todos os serviços de acesso administrativo (SSH, Telnet, LuCI e Crond de persistência) estão ativos e configurados para inicializar automaticamente em `/etc/rc.local`.

---

## 2. Histórico de Todas as Ações Executadas

### Ações no Acer Predator T7 (`192.168.73.2`)

Para transformar o roteador de fábrica em uma ponte transparente (Dumb AP):
1. **Desativação de Servidores DHCP/IPv6 Concorrentes:**
   - O daemon `odhcpd` foi completamente desativado e finalizado (`/etc/init.d/odhcpd stop; /etc/init.d/odhcpd disable`).
   - Removidas as opções `ra`, `dhcpv6` e `ndp` de `/etc/config/dhcp` para impedir que o T7 dispute anúncios de roteador com o gateway principal.
   - Excluída a interface órfã `wan6`.
2. **Eliminação de Prefixo ULA e Delegação Local:**
   - Removido `network.lan.ip6assign` e limpo o prefixo ULA próprio em `/etc/config/network` para que o T7 não gere endereçamento autônomo na bridge `br-lan`.
3. **Bypass de Netfilter na Bridge Linux:**
   - Desativada a filtragem de pacotes em ponte via sysctl:
     - `net.bridge.bridge-nf-call-ip6tables = 0`
     - `net.bridge.bridge-nf-call-iptables = 0`
     - `net.bridge.bridge-nf-call-arptables = 0`
   - Persistido em `/etc/sysctl.d/qca-nss-ecm.conf` e `/etc/rc.local`.
4. **Desbloqueio de IPv6 no Kernel nas Portas Slaves:**
   - O daemon `netifd` do OpenWrt 19.07 marcava `disable_ipv6 = 1` nas portas da bridge (`eth0`, `eth1.1`, etc.). Foi forçado `disable_ipv6 = 0` em todas as interfaces.
5. **Forçamento de Roteador Multicast na Bridge:**
   - Ajustado `multicast_router = 2` (modo permanente) nas portas `eth0`, `mld0`, `ath01`, `ath11` e `ath21`, obrigando o switch virtual a inundar quadros ICMPv6 (`ff02::1` e `ff02::2`) sem depender de snooping.
6. **Desbloqueio do Bonding MLO (`mld0`):**
   - No driver de agregação proprietário Qualcomm MLO (`mode mlo 7`), o parâmetro `all_slaves_active` estava definido como `0`, fazendo com que o kernel descartasse quadros multicast recebidos nos links secundários. Foi ativado `all_slaves_active = 1`.
   - Removida a flag legada de isolamento `option isiot '1'` das VAPs do `CASA_ARK_7G`.

### Ações no Roteador Principal (`192.168.73.1`)

1. **Remoção de Sub-rede Conflitante da WAN na LAN:**
   - Identificamos que a interface `br-lan` continha o endereço estático `2804:c88:feca:e2a2::1/64`, que pertencia à ponta da WAN (PPPoE). Isso gerava anúncios de roteador com duas faixas globais e quebrava o retorno dos pacotes. O IP foi expurgado da `br-lan`.
2. **Ajuste de Flags de RA para Compatibilidade com iOS/Apple:**
   - O `odhcpd` estava anunciando `ra_flags='managed-config' 'other-config'` (M-bit = 1).
   - O iOS não aceita atribuição de IP via DHCPv6 com estado. Removemos o `managed-config` (`ra_flags='other-config'`), forçando o SLAAC padrão RFC.

---

## 3. Análise Técnica: Por Que o IPv6 Ainda Não Funcionou nos Clientes Wi-Fi?

Apesar de todas as correções acima, a auditoria em tempo real revelou os **motivos de fundo pelos quais os clientes Wi-Fi continuam sem IPv6 funcional**:

### 1. O Bug Estrutural do Driver Proprietário Qualcomm MLO (`mld0`)
- No firmware OEM da Acer (baseado no SDK QCA SPF12.4 de 2021/2022), o Wi-Fi 7 MLO foi construído em cima de um módulo de agregação `bonding.ko` modificado (`mode mlo 7`) somado ao subsistema proprietário `umac.ko` / `qca_ol.ko`.
- **Comportamento com Multicast:** Os quadros de *Router Solicitation* (RS - `ff02::2`) e *Router Advertisement* (RA - `ff02::1` / `33:33:00:00:00:01`) são pacotes de difusão L2. O driver de bonding da Qualcomm não possui regras de hashing para endereços de multicast em enlaces agregados sem que o hardware PPE (Packet Processing Engine) tenha fluxos mapeados previamente.
- O resultado é que os pacotes de solicitação/anúncio do SLAAC são **descartados na fronteira entre a bridge Linux (`br-lan`) e o pseudo-dispositivo `mld0`**.

### 2. Aceleração de Hardware Qualcomm PPE / NSS / ECM em Modo AP
- O processador IPQ5332 possui aceleração de hardware (NSS PPE) acoplada ao módulo ECM (`qca-nss-ecm`).
- Em roteadores originais quando operam como Roteador NAT, o ECM cria conexões no hardware para acelerar tráfego. Porém, quando o roteador é forçado a atuar como **Dumb AP (L2 Bridge)**, o ECM e o subsistema de aceleração de multicast (`qca_mcs`) tentam interceptar e filtrar o tráfego de Neighbor Discovery (NDP / MLD).
- Ao interceptar o NDP sem ter um roteador local ativo, o subsistema de aceleração descarta as respostas de vizinhança IPv6 que deveriam atravessar livremente o cabo Ethernet até o roteador primário.

### 3. Comportamento Específico do iOS (Apple Happy Eyeballs & Captive Portal)
- Dispositivos Apple (iPhone, iPad, Mac) realizam testes rigorosos de conectividade ao associar à rede Wi-Fi.
- Se o iPhone recebe apenas o prefixo local ULA (`fd73:...`) ou se o tempo de resposta do gateway primário para o endereço global (`2804:c88:...`) falha na resolução de vizinhança (*Neighbor Solicitation*), o algoritmo *Happy Eyeballs* (RFC 8305) do iOS:
  1. Marca a rede como sem acesso à Internet IPv6.
  2. Suprime o uso de endereços IPv6 em favor do IPv4.
  3. Relata nos testes de navegador que não há IPv6 disponível.

---

## 4. Conclusão e Próximo Passo Definitivo

Tentamos contornar todas as amarras do firmware de fábrica da Acer, mas esbarramos no limite técnico do software original:
- O firmware OEM foi desenhado pela Acer para funcionar **exclusivamente como Roteador Primário NAT**, mantendo o controle total sobre o firewall e o subsistema de aceleração PPE.
- O driver proprietário da Qualcomm para MLO no Linux 5.4 não foi preparado para atuar de forma transparente em pontes de camada 2 de terceiros.

### A Solução Definitiva: OpenWrt Mainline (Opção B)
No **OpenWrt Mainline** (Linux 6.6+ com drivers de código aberto `ath12k` e `mac80211`):
1. **Sem gambiarras de Bonding:** O MLO do 802.11be é processado nativamente no subsistema de rede sem fio do kernel Linux (`mac80211`).
2. **Ponte L2 Pura:** A bridge `br-lan` opera com código padrão upstream, garantindo transparência total e imediata para SLAAC, DHCPv6, NDP e multicast.
3. **Firmware Moderno:** LuCI atualizado, sem serviços legados da Acer que interferem no tráfego de rede.

O ambiente de build no WSL2 (`/home/builder/openwrt`, branch `acer-t7-port`) já está configurado e pronto para a compilação do arquivo `initramfs.itb`.
