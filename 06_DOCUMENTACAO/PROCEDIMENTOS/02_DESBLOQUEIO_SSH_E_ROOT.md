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

### 🔐 Qual senha vai ficar no roteador?
1. **Se você usou o seu próprio backup (`config.cfg`):**
   - **SSH (Porta 22) e LuCI Web:** A senha das contas `Admin` e `root` é **EXATAMENTE A MESMA SENHA** que você já usava para entrar na página web da Acer! O script não altera a sua senha.
   - **Telnet (Porta 23):** Conexão direta ao shell `ash` com privilégios de `root` **sem pedir senha** (útil se você esquecer sua senha ou precisar de acesso de emergência).
   - **Redes Wi-Fi:** Suas redes Wi-Fi (SSIDs, frequências e senhas) continuam **100% inalteradas**.

2. **Se você restaurou um arquivo de template ou exemplo pronto do repositório:**
   - A senha padrão de fábrica das contas `Admin` e `root` é **`admin0100`**.

```powershell
# Conectar via Telnet (acesso direto root sem senha):
telnet 192.168.76.1 23
# (ou 192.168.73.2 se configurado como AP)

# Conectar via SSH (com suporte a RSA legado):
ssh -o HostKeyAlgorithms=+ssh-rsa Admin@192.168.76.1
# ou
ssh -o HostKeyAlgorithms=+ssh-rsa root@192.168.76.1
# (Senha: a mesma senha que voce usa na pagina da Acer, ou admin0100)
```

---

## 5. Arquivos de Referência Arquivados no Repositório

* `02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_stock_original.cfg`: Backup virgem de fábrica da versão v1.01.000027.
* `02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_ssh_unlocked.cfg`: Backup pronto com SSH/Telnet e script `/usr/sbin/boot-acer` injetados.
* `04_SCRIPTS_E_FERRAMENTAS/Automacao_e_Unlock/unlock_only_ssh.py`: Script automatizado para geração de qualquer pacote desbloqueado.
