# 📋 Inventário de Arquivos Modificados — Candidatos ao CFG Master
> **Acer Predator Connect T7 (IPQ5332 + QCN9224 DualMAC)**  
> **Status:** Em processo de validação técnica gradual.  
> **Regra Mandatória:** Somente incorporar ao `cfg_restauracao_master_v2.cfg` após 100% de validação em produção, estabilidade térmica e confirmação de clientes sem regressão.

---

## 1. Arquivos Modificados (Fase 1 — 100% Validados no Roteador)

Estes arquivos já passaram por validação no sistema físico, estão ativos e estáveis:

| Arquivo no Roteador | Arquivo no Repositório Git | Descrição do Ajuste Realizado | Status de Validação |
| :--- | :--- | :--- | :--- |
| `/usr/libexec/rpcd/predator` | `dev/luci-app-predator-wifi/root/usr/libexec/rpcd/predator` | • Correção do comando `iw set txpower fixed` para **mBm** (`$((TX * 100))`), evitando clamping e potência atenuada.<br>• Extração da temperatura real do silício e do `current level` de duty cycle via `thermaltool -i wifiX -get -g`.<br>• Suporte a parâmetro `zone` em `do_add_vif` para vincular redes às bridges corretas (`lan`, `guest`, `iot`). | **100% Validado** (`ubus call predator get_status` online, limpo, temp real 86/89 °C) |
| `/www/luci-static/resources/view/predator_wifi.js` | `dev/luci-app-predator-wifi/root/www/luci-static/resources/view/predator_wifi.js` | • Topologia corrigida: `wifi0` como SoC IPQ5332 (AHB) e `wifi1`/`wifi2` compartilhando o endpoint PCIe `0001:01:00.0` (QCN9224 DualMAC).<br>• Rótulos claros diferenciando **TxPower Conduzido** (medição `iw`) de **EIRP Estimado**.<br>• Expansão do espectro de 6 GHz até o canal 233 (5955–7115 MHz) incluindo todos os PSCs.<br>• Seletor de rede/bridge de destino (`br-lan`, `br-guest`, `br-iot`) na modal de criação.<br>• Esclarecimento técnico de que 4096-QAM inativo rebaixa para Wi-Fi 6E (HT160) e que MBSSID+MLO é restrição de profile QSDK. | **100% Validado** (Interface Web LuCI renderizando HTTP 200, sem erros JS de console) |
| `/etc/config/predator` | `dev/luci-app-predator-wifi/root/etc/config/predator` | Configurações do painel do Predator, Single-SSID Tri-band por padrão, portas e flags de aceleração. | **100% Validado** |

---

## 2. Arquivos de Userspace Candidatos (Fase 2 — Ensaio e Diagnóstico Realizado)

Estes binários e scripts provêm da engenharia reversa do Cudy WR11000 release 2.5.34 (Qualcomm SPF 12.4 / hostapd v2.11-devel ARM32). Foram ensaiados no hardware com backup e rollback automático:

| Arquivo no Roteador | Fonte de Origem (Cudy 2.5.34) | Descrição do Ajuste / Upgrade | Status de Validação |
| :--- | :--- | :--- | :--- |
| `/usr/sbin/qca-hapd-supp` | `versions/2.5.34/rootfs/usr/sbin/qca-hapd-supp` | Binário multicall ARM32 moderno. **Executa 100% no T7 via CLI** (560 símbolos resolvidos).<br>**Resultado em Produção**: O parser de configuração rejeitou 2 itens do script Acer (`noauth_pasn_activated` e `puncture_bitmap`). **Não deve ser aplicado em produção sem portar o `/lib/wifi/hostapd.sh` correspondente.** | **Auditado e Bloqueado por Dependência de Script** (Rollback executado para original v2.10) |
| `/usr/sbin/hostapd` | `dev/cudy-hostapd-upgrade/hostapd` | Wrapper que garante invocação correta via `exec -a hostapd`. | **Em Staging Local** (Armazenado em `dev/cudy-hostapd-upgrade/`) |
| `/usr/sbin/wpa_supplicant` | `dev/cudy-hostapd-upgrade/wpa_supplicant` | Wrapper que garante invocação correta via `exec -a wpa_supplicant`. | **Em Staging Local** (Armazenado em `dev/cudy-hostapd-upgrade/`) |
| `/usr/sbin/hostapd_cli` | `dev/cudy-hostapd-upgrade/hostapd_cli` | Cliente de controle v2.11-devel. | **Em Staging Local** |


---

## 3. Arquivos Estritamente Protegidos (NÃO ALTERAR)

Confirmado pelos estudos de ABI e RF:

1. `/lib/firmware/qcn9224/bdwlan.b1015` e `b16`: Calibração analógica de fábrica inviolável. Não copiar de outros roteadores.
2. Módulos de Kernel `.ko` do Cudy (`umac.ko`, `qca_ol.ko`): Incompatíveis em tempo de link com o kernel atual do Acer por falta de símbolos exportados (`__netdev_alloc_skb_fast`, `pcie_parf_read`).

---

## 4. Procedimento para Cópia / Incorporação no `cfg_restauracao_master_v2.cfg`

Quando todas as etapas forem 100% validadas e aprovadas pelo usuário:

1. **Backup prévio do CFG Master:**
   ```bash
   cp cfg_restauracao_master_v2.cfg cfg_restauracao_master_v2.cfg.bak.$(date +%Y%m%d_%H%M%S)
   ```
2. **Extração, inserção dos arquivos validados e remontagem:**
   O arquivo `.cfg` é um tarball gzipado (`.tar.gz`).
   ```bash
   mkdir -p /tmp/cfg_repack && cd /tmp/cfg_repack
   tar -xzf /Volumes/--400GB--/FEITOS\ COM\ IA/Acer-Predator-Connect-T7/cfg_restauracao_master_v2.cfg
   # Copiar arquivos homologados para a árvore etc/ correspondente
   COPYFILE_DISABLE=1 tar --no-mac-metadata -czf /Volumes/--400GB--/FEITOS\ COM\ IA/Acer-Predator-Connect-T7/cfg_restauracao_master_v2.cfg *
   ```
3. **Commit e Tag no Git.**
