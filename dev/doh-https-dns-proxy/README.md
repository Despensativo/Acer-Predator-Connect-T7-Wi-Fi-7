# Pacote DoH (DNS-over-HTTPS) para Acer Predator Connect T7

Implementação nativa de DNS-over-HTTPS (DoH) utilizando o daemon `https-dns-proxy` portado do QSDK OpenWrt (SPF 12.4), integrado diretamente com o `dnsmasq` do sistema.

## Características da Implementação

1. **DNS 100% Livre e Sem Bloqueios**:
   - Zero vínculo com AdGuard, Shiild ou serviços pagos/filtrados.
   - Resolução via **Cloudflare** (`https://cloudflare-dns.com/dns-query`) e **Google** (`https://dns.google/dns-query`).

2. **Alta Disponibilidade e Redundância Ativa**:
   - Duas instâncias independentes rodando sob controle do `procd`:
     - **Instância Cloudflare**: porta local `127.0.0.1:5053`
     - **Instância Google**: porta local `127.0.0.1:5054`
   - O `dnsmasq` roda com `option allservers '1'`, consultando ambos os servidores em paralelo e aproveitando a resposta mais veloz em tempo real.
   - Caso um servidor falhe ou sofra degradação de rota internacional, o outro responde instantaneamente sem qualquer queda para os clientes da LAN.

3. **Cache em Memória RAM Ultra-Rápido**:
   - O `dnsmasq` opera com `cachesize '5000'`.
   - Primeira consulta: ~20 ms (ida e volta HTTPS criptografada).
   - Consultas repetidas: **0.00s** (resposta instantânea do cache local).

4. **Privacidade e Criptografia Total contra o Provedor (ISP)**:
   - Todo tráfego de saída na WAN ocorre exclusivamente via TLS (TCP 443).
   - Bloqueio de vazamentos unencrypted UDP 53 (`option noresolv '1'`).
   - Totalmente compatível com a regra anti-QUIC (`REJECT udp --dport 443`), pois o DoH trafega em **TCP 443**.

## Arquivos do Pacote

- `https-dns-proxy`: Binário compilado para arquitetura ARM64 (Qualcomm IPQ5332).
- `libev.so.4.0.0`: Biblioteca de loop de eventos assíncrona libev.
- `https-dns-proxy.config`: Configuração UCI para `/etc/config/https-dns-proxy`.
- `https-dns-proxy.init`: Script de inicialização procd para `/etc/init.d/https-dns-proxy`.
- `install.sh`: Script de instalação automática via SSH/SCP.
