# luci-app-predator-wifi & predator-wifi-guard

Módulo de Gestão Avançada de Wi-Fi 7 e Sistema Antiburro de Autoproteção RF para o **Acer Predator Connect T7 (Qualcomm IPQ5332 Tri-Band)**.

---

## 🛡️ Camadas do Sistema Antiburro (Predator Guard)

O sistema opera em 4 camadas complementares para impedir travamentos de RF, loops do hostapd e inconsistências de segurança:

### 1. Interface Web LuCI (`predator_wifi.js`)
- **Validação de SSID**: Bloqueia nomes vazios, nomes com mais de 32 bytes (limite IEEE 802.11) e caracteres de escape que quebram scripts shell (`' " \` ; \\`).
- **Autopreenchimento de Senha Existente**: Se o usuário editar uma rede existente e deixar o campo de senha em branco, o sistema automaticamente reutiliza a senha atual configurada.
- **Validação de Senha**: Redes com criptografia exigem no mínimo 8 e no máximo 63 caracteres.
- **Aviso de Desconexão**: Alerta dinâmico na troca de topologia indicando o número de dispositivos conectados e seus hostnames que serão temporariamente desconectados.
- **Banner de Auto-Rollback**: Notifica visualmente caso o guardião tenha realizado uma reversão automática de configuração ou reinício limpo de emergência.

### 2. Backend RPCD (`/usr/libexec/rpcd/predator`)
- Métodos `apply_topology`, `edit_vif` e `add_vif` validam parâmetros antes de gravar no UCI.
- Se a senha vier em branco no `edit_vif`, recupera do UCI (`wireless.$SEC.key`).
- Aciona `/usr/sbin/predator-wifi-guard fix` pré-aplicação e dispara o cão de guarda `verify` em background.

### 3. Sanitizador Pré-Aplicação (`/usr/sbin/predator-wifi-guard fix` e `/sbin/wifi`)
- Gancho obrigatório chamado antes de qualquer `wifi reload` ou `wifi up` (cobre CLI, LuCI padrão e Central Predator).
- **2.4 GHz**: Força largura máxima de 40 MHz e canais válidos (1–13).
- **5 GHz**: Limita 160 MHz aos blocos compatíveis (canais 36–64 e 100–128). Canais 132+ revertem para 80 MHz e canal 165 para 20 MHz.
- **6 GHz**: Exige WPA3-SAE (ou OWE). Proíbe redes abertas puras e WPA2.
- **Blindagem MLO (IPQ5332)**: O chipset Qualcomm IPQ5332 rejeita MBSSID com MLO na banda de 5 GHz. O guardião remove a flag `mld` de qualquer VAP secundário, permitindo criação de redes de convidados/secundárias com roaming 802.11k/v padrão.
- **Sincronização SAE**: Garante que `sae_password` seja idêntico a `key`, evitando descompasso entre clientes WPA2 e WPA3.

### 4. Cão de Guarda e Auto-Rollback (`/usr/sbin/predator-wifi-guard verify`)
- Aguarda a inicialização do subsistema de RF e sonda o socket global `/var/run/hostapd/global` e cada rádio individual.
- Se os rádios atingirem `state=ENABLED` ou `DFS`, atualiza `/etc/predator/wireless.lastgood`.
- Se os rádios não responderem dentro do tempo limite (15 sondagens) e a configuração divergir da última boa, restaura automaticamente `/etc/predator/wireless.lastgood`, salva o arquivo defeituoso em `/etc/predator/wireless.failed` e executa um reinício limpo do hostapd.
- Registra a causa da reversão para exibição no painel LuCI.

---

## 📁 Estrutura de Arquivos

```
dev/luci-app-predator-wifi/
├── README.md
└── root/
    ├── sbin/
    │   └── wifi                                   # Wrapper do /sbin/wifi com gancho do guardião
    ├── usr/
    │   ├── libexec/
    │   │   └── rpcd/
    │   │       └── predator                       # Backend RPCD com validações defensivas
    │   ├── sbin/
    │   │   └── predator-wifi-guard                # Daemon/script de validação, saúde e rollback
    │   └── share/
    │       ├── luci/menu.d/
    │       │   └── luci-app-predator-wifi.json    # Entrada de menu LuCI
    │       └── rpcd/acl.d/
    │           └── luci-app-predator-wifi.json    # Permissões ACL para o RPCD
    └── www/
        └── luci-static/resources/view/
            └── predator_wifi.js                   # Interface visual LuCI com i18n e validação
```
