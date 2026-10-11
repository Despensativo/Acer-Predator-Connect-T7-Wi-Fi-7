# Procedimento 02: Desbloqueio de Acesso SSH e Root

> **Status:** [VALIDADO EM BANCADA NAS VERSÕES v1.01.000024 E v1.01.000027 - 03/10/2026]  
> **Nível de Risco:** [BAIXO - Modificação via Web Restore de Backup `.cfg`]  
> **Objetivo:** Liberar acesso de superusuário (Root) e terminal persistente (SSH / Telnet) no firmware oficial da Acer sem alterar partições da flash.

---

## 1. Princípio de Funcionamento

O backup `.cfg` exportado pelo painel da Acer (**System $\rightarrow$ Backup and restore**) é um arquivo `tar.gz` padrão contendo as configurações de `/etc`. Ao injetar a ativação do Dropbear e Telnet no `/etc/rc.local`, o roteador reinicia com portas 22 e 23 abertas e persistentes.

---

## 2. Método Automático (Recomendado via Script Python)

1. Baixe o backup atual do roteador pelo painel web (`config.cfg`).
2. Execute o injetor automatizado:
   ```bash
   python 04_SCRIPTS_E_FERRAMENTAS/Automacao_e_Unlock/unlock_only_ssh.py "caminho/para/config.cfg"
   ```
3. O script gera o arquivo `config_ssh_unlocked.cfg`.
4. No painel web (**System $\rightarrow$ Backup and restore $\rightarrow$ Restore**), envie o novo arquivo gerado.
5. Aguarde o roteador reiniciar (aproximadamente 2 minutos).

---

## 3. Alterações Manuais no `.cfg` (Referência Técnica)

Se desejar aplicar manualmente em ambiente Linux/WSL:

### A. `etc/rc.local` (Permissão `0775`)
Adicione antes da linha `exit 0`:
```sh
# Ativar Dropbear
uci set dropbear.@dropbear[0].enable='1' 2>/dev/null
uci commit dropbear 2>/dev/null
DROPBEAR=$(command -v dropbear || echo "/usr/sbin/dropbear")
[ -x "$DROPBEAR" ] && $DROPBEAR -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B

# Ativar Telnet
TELNETD=$(command -v telnetd || echo "/usr/sbin/telnetd")
[ -x "$TELNETD" ] && $TELNETD -l /bin/ash
```

### B. `etc/crontabs/Admin` (Permissão `0644`)
Garante que o daemon da Acer não mate o processo:
```cron
* * * * * pgrep dropbear || /usr/sbin/dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B
* * * * * pgrep telnetd || /usr/sbin/telnetd -l /bin/ash
```

### C. `etc/passwd` e `etc/shadow`
Restaurar a conta de superusuário `root` (id `0:0`):
- Em `etc/passwd`: `root:x:0:0:root:/root:/bin/ash`
- Em `etc/shadow`: clonar a linha do usuário `Admin` atribuindo para `root`.

---

## 4. Conexão ao Terminal e Credenciais de Acesso

### 🔑 Credenciais Padrão Unificadas:
* **Usuário:** `root` (ou `Admin`)
* **Senha:** `root`
* **LuCI Web (Porta 80):** `http://192.168.76.1` (ou `192.168.73.2`) | Usuário: `root` | Senha: `root`
* **SSH (Porta 22):**
  ```powershell
  ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.76.1
  # (Senha: root)
  ```
* **Telnet de Emergência (Porta 23):** Conexão direta ao shell `ash` com privilégios de `root` **sem pedir senha**:
  ```powershell
  telnet 192.168.76.1 23
  ```

> [!CAUTION]
> ### 🛡️ Regra de Ouro ao Alterar Senhas
> 1. **NUNCA apague ou renomeie as contas `root` ou `Admin`.** Ambos compartilham UID 0. Tarefas agendadas do cron (`/etc/crontabs/Admin`) e scripts nativos da Acer dependem de `Admin`, enquanto o OpenWrt/LuCI espera `root`.
> 2. **Se você for alterar a senha pelo terminal, atualize SEMPRE OS DOIS usuários para mantê-los sincronizados:**
>    ```sh
>    passwd root
>    passwd Admin
>    ```

---

## 5. Arquivos de Referência Arquivados no Repositório

* `02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_stock_original.cfg`: Backup virgem de fábrica da versão v1.01.000027.
* `02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_ssh_unlocked.cfg`: Backup pronto com SSH/Telnet e script `/usr/sbin/boot-acer` injetados.
* `04_SCRIPTS_E_FERRAMENTAS/Automacao_e_Unlock/unlock_only_ssh.py`: Script automatizado para geração de qualquer pacote desbloqueado.
