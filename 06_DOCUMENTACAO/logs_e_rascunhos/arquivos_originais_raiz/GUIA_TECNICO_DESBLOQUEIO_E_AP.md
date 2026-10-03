# Guia Técnico de Engenharia Reversa, Desbloqueio e Modo AP 2.5G

Este documento registra em detalhes toda a análise técnica, engenharia reversa e modificações realizadas no firmware do roteador **Acer Predator Connect T7**.

---

## 1. O Desafio Inicial e Objetivos

O Acer Predator Connect T7 é um roteador gamer de ponta equipado com o SoC **Qualcomm IPQ5332 (Wi-Fi 7)** e uma porta de **2.5 Gbps**.

> [!NOTE]
> **Esquema de Endereçamento IP**:
> * **IP Padrão de Fábrica (Stock):** `192.168.76.1` (Modo Roteador com servidor DHCP ativo).
> * **IP Customizado deste Projeto:** `192.168.73.2` (Modificado manualmente para integrar como Access Point à rede do roteador mestre `192.168.73.1`).

O usuário possui uma conexão de internet de **2 Gbps** entregue por um roteador mestre (`192.168.73.1`), mas o firmware de fábrica da Acer impunha limitações severas:

1. **Sem Modo Ponto de Acesso (AP) verdadeiro para 2.5G**: O painel padrão insistia em usar a porta 2.5G como WAN de roteador com NAT duplo ou limitava a operação às portas Gigabit.
2. **Terminal (SSH/Telnet) Bloqueado de Fábrica**: A Acer removeu qualquer opção de habilitar SSH ou acesso ao console Linux no painel web.
3. **Rede MLO Wi-Fi 7 Travada**: A interface web mantinha nomes genéricos de fábrica (`T7_...`) e seleção confusa de bandas.
4. **Quedas e interferências no Wi-Fi**: Dispositivos IoT a 25 metros sofriam com canais dinâmicos em 2.4 GHz, e a banda de 5 GHz corria risco de desativação por radares meteorológicos (DFS).

---

## 2. A Engenharia Reversa do Arquivo de Configuração (`.cfg`)

Ao exportar o backup do roteador via **System $\rightarrow$ Backup and restore**, obtivemos o arquivo `config.cfg`.

### Estrutura Interna
O arquivo `.cfg` é um pacote compactado em **`tar.gz`** contendo a árvore de configurações do OpenWrt:
* `/etc/config/*` (Arquivos UCI: `network`, `wireless`, `dhcp`, `firewall`, `tripleband`, etc.)
* `/etc/passwd`, `/etc/shadow`, `/etc/hosts`
* `/etc/rc.local` e `/etc/crontabs/*`
* `/etc/dropbear/dropbear_rsa_host_key`

Quando o usuário restaura um arquivo `.cfg` pelo painel da Acer, o daemon de restauração descompacta o arquivo diretamente sobre a partição de sobreposição gravável (`/overlay/upper/`), substituindo os arquivos do sistema.

---

## 3. Configurando o Modo AP Puro (Zero Duplo NAT a 2.5 Gbps)

Para garantir que a porta WAN de 2.5 Gbps recebesse os 2 Gbps da internet sem passar pelo processador de NAT:

### No `/etc/config/network`:
Unificamos a interface física da porta 2.5G (`eth0`) e as portas LAN Gigabit (`eth1.1` e `eth1.2`) dentro da mesma ponte de rede (`br-lan`):

```uci
config interface 'lan'
	option type 'bridge'
	option ifname 'eth0 eth1.1 eth1.2'
	option proto 'static'
	option ipaddr '192.168.73.2'
	option gateway '192.168.73.1'
	list dns '192.168.73.1'
	list dns '8.8.8.8'
	option netmask '255.255.255.0'

config interface 'wan'
	option disabled '1'
```

### No `/etc/config/dhcp`:
Desativamos completamente o servidor DHCP interno do Acer:
```uci
config dhcp 'lan'
	option interface 'lan'
	option ignore '1'
	option dhcpv6 'disabled'
	option ra 'disabled'
```
*Com isso, todos os computadores, celulares e TVs conectados ao Predator pegam IP diretamente do roteador mestre (`192.168.73.x`), mantendo a rede plana e sem duplo NAT.*

---

## 4. Engenharia Reversa da Interface Web da Acer (Vue.js)

Ao inspecionar o código-fonte empacotado pelo Webpack no frontend do roteador (`pub/dist/js/app.867e05fe.js` e chunks auxiliares), desvendamos o mapeamento exato que a Acer usa:

1. **Nome da Rede MLO na Tela:**
   A página web lê o valor de `WiFiIotSsidTable[0]`, que corresponde ao primeiro rádio (`wifi0`). Para a caixinha exibir `CASA_ARK_7G`, é necessário que **todos** os blocos de MLO (`wifi0`, `wifi1`, `wifi2`, `tripleband` e `wifi-mld mld0`) estejam sincronizados com o mesmo SSID.
2. **Seleção de Bandas 5G + 6G:**
   No arquivo `8233.53cf7f63.js`, encontramos o mapa:
   ```javascript
   MLOBandLists = [
     { value: "0", label: "5G+6G" },
     { value: "1", label: "2.4G+5G" },
     { value: "2", label: "2.4G+6G" }
   ]
   ```
   Definindo `option mlo_bands '0'` no arquivo `tripleband`, a interface web abre automaticamente selecionada em **5G + 6G**!
3. **Interruptor de PSC (Preferred Scanning Channel):**
   A chavinha no painel consulta `wifi6gPsc`. Ao adicionar `option psc '1'` no bloco do rádio `wifi2`, a chavinha liga nativamente no painel.

---

## 5. O Desbloqueio do Terminal Root (SSH e Telnet)

### A Descoberta da "Pegadinha" no `/etc/passwd`
Ao analisar os logs de sistema (`syslog`), vimos o erro:
`cron.err crond: ignoring file 'root' (no such user)`

Ao inspecionar o `/etc/passwd`, descobrimos que a Acer **removeu o usuário `root`** e renomeou o superusuário (UID 0) para **`Admin`**:
```text
Admin:x:0:0:root:/root:/bin/ash
```
Por isso, qualquer conexão usando `ssh root@...` falhava sumariamente.

### O Bloqueio do Dropbear
A Acer configurou o daemon do painel para injetar `option enable '0'` no arquivo `/etc/config/dropbear`. Quando o script `/etc/init.d/dropbear` rodava no boot, ele lia o `'0'` e abortava a inicialização.

### A Solução Implementada (Bypass Triplo)
No script gerador `build_ssh_unlocked.py`:

1. **Criamos o usuário `root` duplicado:**
   Adicionamos `root:x:0:0:root:/root:/bin/ash` no `/etc/passwd` e duplicamos o hash da senha no `/etc/shadow`. Agora o roteador aceita login tanto como `Admin` quanto como `root`.
2. **Execução Direta do Binário (Bypass do init.d):**
   No `/etc/rc.local`, iniciamos o Dropbear passando a chave RSA e a flag `-R` (geração de chaves automáticas) diretamente:
   ```sh
   /usr/sbin/dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B
   telnetd -l /bin/ash
   ```
3. **Watchdog no Agendador (`crontab`):**
   Adicionamos uma regra no `/etc/crontabs/Admin` para verificar a cada minuto se o SSH e o Telnet estão rodando. Caso sejam finalizados, o sistema os reinicia imediatamente:
   ```cron
   * * * * * pgrep dropbear || dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B
   * * * * * pgrep telnetd || telnetd -l /bin/ash
   ```

---

## 6. Otimização de Rádio e Frequências

Para garantir máxima estabilidade e desempenho:

* **2.4 GHz (`wifi0`):** Cravado no **Canal 1** em **20 MHz (`HT20`)** com potência máxima (**25 dBm**). Reduz ruídos de canais laterais e garante penetração estável através de paredes até os dispositivos inteligentes a 25 metros.
* **5 GHz (`wifi1`):** Cravado no **Canal 36** em **160 MHz (`HT160`)** com DFS desbloqueado (`blockdfslist '0'`). Evita que radares meteorológicos obriguem o roteador a desativar a banda de 5 GHz no meio de jogos ou downloads.
* **6 GHz (`wifi2`):** Cravado no **Canal 37 (PSC)** em **320 MHz (`HT320`)** com PSC ativado. Permite que dispositivos Wi-Fi 7 encontrem o canal imediatamente na varredura passiva.

---

## 7. Análise dos Logs do Sistema

Durante os testes, observamos no syslog:
`user.warn : [WARN][get_users]get user failed(-1) [dw_ioctl.cpp:578]`

* **Causa:** O daemon de monitoramento de QoS e segurança da Trend Micro (`dw` - *Device Watcher*) consulta o kernel a cada 10 segundos procurando conexões passando pelo NAT/WAN.
* **Efeito:** Como o roteador está em Modo AP (Camada 2 pura, sem NAT/WAN), o kernel retorna `-1` (nenhum usuário roteado). É apenas um aviso informativo benigno que não interfere na rede.
