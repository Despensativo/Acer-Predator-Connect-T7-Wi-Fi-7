# Como Editar o Arquivo .cfg e Destravar SOMENTE o SSH / Telnet

Este guia ensina como funciona o arquivo de configuração (`.cfg`) do **Acer Predator Connect T7**, como extraí-lo e editá-lo manualmente, e **exatamente quais são as únicas alterações necessárias** caso você queira **apenas liberar o acesso Root (SSH / Telnet)** sem mexer em nenhuma configuração de rede, Wi-Fi ou IP do roteador.

---

## 1. O que é o arquivo `.cfg` do Acer?

O arquivo `.cfg` exportado pelo painel (**System $\rightarrow$ Backup and restore**) não é um arquivo proprietário criptografado. Ele é simplesmente um pacote compactado em **`tar.gz`** padrão do Linux/OpenWrt.

Ele contém:
* `/etc/config/*` (todas as configurações de rede, Wi-Fi e sistema)
* `/etc/passwd` e `/etc/shadow` (usuários e senhas)
* `/etc/rc.local` (comandos executados ao ligar o roteador)
* `/etc/crontabs/*` (tarefas agendadas do sistema)

> [!WARNING]
> **Cuidado Crítico no Windows:**
> Ao descompactar e editar no Windows com programas como Bloco de Notas ou WinRAR:
> 1. As quebras de linha podem ser convertidas de **LF (Unix)** para **CRLF (Windows)**, o que faz os scripts do roteador falharem.
> 2. O WinRAR/7-Zip descarta as **permissões de arquivo POSIX** (como `0775` para executáveis e `0600` para senhas e chaves SSH).
> **Recomendação:** Use o script Python fornecido abaixo ou edite garantindo finais de linha LF e permissões preservadas.

---

## 2. As Únicas Alterações Necessárias para Destravar SSH e Telnet

Se você não quer alterar o modo de operação do roteador (quer mantê-lo como roteador padrão, com suas redes Wi-Fi atuais e seu IP de fábrica) e quer **apenas o terminal Root**, você precisa modificar cirurgicamente apenas **3 arquivos**:

### 🛠️ Alteração 1: `etc/rc.local` (Permissão: `0775`)
A Acer bloqueia o serviço Dropbear no arquivo de configuração padrão. Para contornar isso, adicionamos a chamada direta dos binários antes da linha `exit 0`:

```sh
# --- ATIVACAO DO TERMINAL (SSH + TELNET) ---
uci set dropbear.@dropbear[0].enable='1' 2>/dev/null
uci commit dropbear 2>/dev/null

# Inicia o Dropbear diretamente passando a chave RSA e flag -R
DROPBEAR=$(command -v dropbear || echo "/usr/sbin/dropbear")
[ -x "$DROPBEAR" ] && $DROPBEAR -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B

# Inicia o Telnet na porta 23
TELNETD=$(command -v telnetd || echo "/usr/sbin/telnetd")
[ -x "$TELNETD" ] && $TELNETD -l /bin/ash

/etc/init.d/cron restart 2>/dev/null
# -------------------------------------------

exit 0
```

---

### 🛠️ Alteração 2: `etc/crontabs/Admin` (Permissão: `0644`)
O daemon do painel da Acer pode tentar derrubar processos não autorizados. Para garantir que o SSH e o Telnet permaneçam sempre abertos, adicionamos duas linhas no final do agendador (`crontab`):

```cron
* * * * * pgrep dropbear || (dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B || /usr/sbin/dropbear -R -r /etc/dropbear/dropbear_rsa_host_key -p 22 -B)
* * * * * pgrep telnetd || (telnetd -l /bin/ash || /usr/sbin/telnetd -l /bin/ash)
```
*A cada 60 segundos, o roteador verifica se o SSH ou o Telnet estão rodando. Se não estiverem, ele os reinicia na hora.*

---

### 🛠️ Alteração 3: `etc/passwd` e `etc/shadow` (Permissão: `0644` e `0600`)
De fábrica, a Acer **removeu o usuário `root`** e renomeou o superusuário para `Admin`. Para permitir o login tradicional com `root`:

1. No arquivo **`etc/passwd`**, adicione esta linha no topo:
   ```text
   root:x:0:0:root:/root:/bin/ash
   ```
2. No arquivo **`etc/shadow`**, localize a linha do `Admin` (que contém o hash da sua senha):
   ```text
   Admin:$1$xyz...:20725:0:99999:7:::
   ```
   E adicione uma cópia idêntica para o `root` logo acima dela:
   ```text
   root:$1$xyz...:20725:0:99999:7:::
   ```
*(Agora você poderá conectar tanto como `Admin` quanto como `root`, usando a mesma senha).*

---

## 3. Método 100% Automático (Recomendado)

Para evitar erros manuais com permissões ou compactação, disponibilizamos o script Python:
📁 **`Scripts_Automacao/unlock_only_ssh.py`**

### Como Usar em 1 Passo:

1. Baixe o backup atual do seu roteador pelo navegador (**System $\rightarrow$ Backup and restore $\rightarrow$ Backup**). Ele será salvo como `config.cfg`.
2. Abra o terminal na pasta deste repositório e execute:
   ```bash
   python Scripts_Automacao/unlock_only_ssh.py "Caminho/Para/Seu/config.cfg"
   ```
3. O script criará o arquivo **`config_ssh_unlocked.cfg`**.
4. Vá no painel do roteador em **System $\rightarrow$ Backup and restore $\rightarrow$ Restore**, selecione esse arquivo novo e confirme.
5. Aguarde o roteador reiniciar (2 minutos).

---

## 4. Como Conectar após o Desbloqueio

### Opção A: Telnet (Mais fácil e instantâneo)
No Prompt de Comando ou PowerShell:
```powershell
telnet 192.168.73.2
```
*(Se o seu roteador estiver com o IP de fábrica, use `telnet 192.168.76.1`).*
Você cairá direto no terminal com privilégios máximos (`/ #`).

### Opção B: SSH Criptografado
```powershell
ssh -o HostKeyAlgorithms=+ssh-rsa Admin@192.168.73.2
```
*(ou `ssh -o HostKeyAlgorithms=+ssh-rsa root@192.168.73.2`)*
Digite a mesma senha do seu usuário `Admin` do painel web.
