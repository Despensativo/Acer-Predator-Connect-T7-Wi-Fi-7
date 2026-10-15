# Procedimento 02: Desbloqueio de Acesso SSH e Root

> **Status:** [VALIDADO EM BANCADA NAS VERSÕES v1.01.000024 E v1.01.000027 - 03/10/2026]  
> **Nível de Risco:** [BAIXO - Modificação via Web Restore de Backup `.cfg`]  
> **Objetivo:** Liberar acesso de superusuário (Root) e terminal persistente (SSH / Telnet) no firmware oficial da Acer sem alterar partições da flash.

---

## 1. Princípio de Funcionamento

O backup `.cfg` exportado pelo painel da Acer (**System $\rightarrow$ Backup and restore**) é um arquivo `tar.gz` padrão contendo as configurações de `/etc`. Ao injetar a ativação do Dropbear e Telnet no `/etc/rc.local`, o roteador reinicia com portas 22 e 23 abertas e persistentes.

---

## 2. Método Oficial (Restauração Direta ou Gerador Personalizado)

1. **Restauração Direta (1 Minuto):** No painel web OEM (**System $\rightarrow$ Backup and restore $\rightarrow$ Restore**), envie diretamente o pacote mestre [`cfg_restauracao_master_v2.cfg`](../cfg_restauracao_master_v2.cfg) localizado na raiz do repositório.
2. **Gerador Personalizado (Opcional):** Caso deseje gerar um `.cfg` já com seu próprio SSID e senhas antes de aplicar:
   ```bash
   python3 dev/gerar_cfg_personalizado.py
   ```
   *(Nota histórica: o script minimalista `unlock_only_ssh.py` da fase inicial foi arquivado fora do Git em `_FORA DO GitHub/10_LEGADO_E_DESENVOLVIMENTO_PRE_MASTER_V2/`).*
3. Aguarde o roteador reiniciar (aproximadamente 40 a 60 segundos no padrão de 80 MHz non-DFS).

---

## 3. Alterações Manuais no `.cfg` (Referência Técnica)

Se desejar inspecionar a estrutura em ambiente Linux/macOS/WSL:

### A. `etc/rc.local` (Permissão `0755`)
Garante a inicialização do Dropbear e Telnet no boot:
```sh
# Garantir SSH (Dropbear) e Telnet ativos em todas as interfaces LAN
/etc/init.d/dropbear start >/dev/null 2>&1
/etc/init.d/telnet start >/dev/null 2>&1
pgrep telnetd >/dev/null || /usr/sbin/telnetd -l /bin/ash
```

### B. `etc/crontabs/Admin` (Permissão `0644`)
Garante que o daemon da Acer não derrube os serviços de acesso:
```cron
* * * * * pgrep dropbear || /usr/sbin/dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B
* * * * * pgrep telnetd || /usr/sbin/telnetd -l /bin/ash
```

### C. `etc/passwd` e `etc/shadow`
Contas de superusuário sincronizadas com UID `0:0` (`root`, `admin` e `Admin`):
- Em `etc/passwd`: `root:x:0:0:root:/root:/bin/ash`, `admin:x:0:0:Admin:/root:/bin/ash` e `Admin:x:0:0:Admin:/root:/bin/ash`.
- Em `etc/shadow`: o mesmo hash MD5-Crypt (`root0100`) replicado nas 3 contas.

---

## 4. Conexão ao Terminal e Credenciais de Acesso

### 🔑 Credenciais Padrão Unificadas:
* **Usuário:** `root` (ou `admin` / `Admin`)
* **Senha no `cfg_restauracao_master_v2.cfg`:** `root0100`
* **LuCI Web (Porta 80):** `http://192.168.76.1` | Usuário: `root` | Senha: `root0100`
* **SSH (Porta 22):**
  ```bash
  ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa root@192.168.76.1
  # (Senha: root0100)
  ```
* **Telnet de Emergência (Porta 23):** Conexão direta ao shell `ash` com privilégios de `root` **sem pedir senha** (gerenciado com auto-respawn pelo `procd`):
  ```bash
  telnet 192.168.76.1 23
  ```

> [!CAUTION]
> ### 🛡️ Regra de Ouro ao Alterar Senhas
> 1. **NUNCA apague ou renomeie as contas `root`, `admin` ou `Admin`.** Todas compartilham UID 0. Tarefas agendadas do cron (`/etc/crontabs/Admin`) e binários nativos da Acer dependem de `Admin`, enquanto o OpenWrt/LuCI utiliza `root` e `admin`.
> 2. **Se você for alterar a senha pelo terminal, atualize SEMPRE AS TRÊS contas para mantê-las sincronizadas:**
>    ```sh
>    passwd root
>    passwd admin
>    passwd Admin
>    ```

---

## 5. Pacote Mestre Oficial e Arquivos

* [`cfg_restauracao_master_v2.cfg`](../cfg_restauracao_master_v2.cfg): Pacote Mestre consolidado (na raiz do repositório, `364.312 bytes`, SHA-256 `82e77ac839d45d28056b155a380fd99f3a70be2537c8ab4494d1ee36799dbae9`) pronto com LuCI, Central Wi-Fi com blindagem de deadlocks (`predator-wifi-guard`), Painel WISP, NAS `ksmbd`, DoH, SSH/Telnet liberados e scripts `/usr/sbin/boot-acer` e `/usr/sbin/boot-openwrt` integrados.
* Backups históricos e scripts preliminares de desenvolvimento foram arquivados fora do controle de versão Git em `_FORA DO GitHub/10_LEGADO_E_DESENVOLVIMENTO_PRE_MASTER_V2/`.
