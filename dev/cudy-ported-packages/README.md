# Pacotes Portados do Cudy WR11000 (OpenWrt 21.02 / QSDK SPF 12.4) para o Acer Predator Connect T7

Coleção de pacotes e correções de alta performance validados e instalados no Predator T7.

## 1. WireGuard (VPN Gigabit em Silício)
- **Status**: Ativo e Homologado no Kernel (`wireguard.ko` carregado).
- **Módulo Kernel**: `/lib/modules/5.4.213/wireguard.ko` (carregado via `/etc/modules.d/wireguard`).
- **CLI**: `/usr/bin/wg` (`wg --version`, `wg genkey`).
- **Protocolo Netifd**: `/lib/netifd/proto/wireguard.sh` (permite criar interfaces `proto 'wireguard'`).
- **Watchdog / Hotplug**: `/usr/bin/wireguard_watchdog` e `/etc/hotplug.d/iface/16-wireguard`.
- **Como Usar**: Basta criar uma interface `network.<nome>=interface` com `proto 'wireguard'`, chave privada e peers via LuCI ou UCI.

## 2. Wake-on-LAN (`etherwake`)
- **Status**: Instalado em `/usr/bin/etherwake`.
- **Como Usar**:
  ```sh
  etherwake -i br-lan 00:11:22:33:44:55
  ```

## 3. IGMP Proxy (`igmpproxy` - IPTV Multicast)
- **Status**: Instalado, **desativado por padrão** (sem consumo de recursos).
- **Configuração**: `/etc/config/igmpproxy`.
- **Como Ativar (se usar IPTV)**:
  ```sh
  /etc/init.d/igmpproxy enable
  /etc/init.d/igmpproxy start
  ```

## 4. Agendador Wi-Fi (`wifi_schedule` - Modo Noturno / Eco)
- **Status**: Instalado, **desativado por padrão** (`option enabled '0'`).
- **Configuração**: `/etc/config/wifi_schedule`.
- **Script**: `/usr/bin/wifi_schedule.sh`.

## 5. Calculador de Conflito de Rede (`network-conflict-calc.sh`)
- **Status**: Instalado em `/bin/network-conflict-calc.sh`.
- **Função**: Previne sobreposição de sub-redes entre conexões WAN, VPN e LAN.

## 6. Correções de Firewall
- **DNS TCP 53**: Liberado nas zonas `guest` e `iot` (`option proto 'tcp udp'`).
- **IPv6 Discovery**: Adicionadas regras para DHCPv6 (UDP 547) e ICMPv6 (Router Solicitation / Neighbor Discovery) nas zonas `guest` e `iot`.
- **WAN DHCPv6**: Removida restrição incorreta de IP `fc00::/6`.
- **Idempotência**: Scripts `/etc/firewall.d/qca-nss-ecm` e `99-predator-fixes` agora usam verificação `-C` para não duplicar regras a cada reload.
