# Procedimento 03: Ativação do LuCI, Fix de Autenticação e Debloat

> **Status:** [VALIDADO EM BANCADA]  
> **Nível de Risco:** [BAIXO - Modificações em `/etc` e Daemons em Execução]  
> **Objetivo:** Ativar a interface nativa OpenWrt (LuCI) na porta 8080, corrigir autenticação RPC e desativar serviços pesados de telemetria e FOTA da Acer.

---

## 1. Ativação do LuCI (Porta 8080)

O firmware original contém o `uhttpd` e os pacotes LuCI pré-instalados em `/www`, mas desativados para evitar conflito com o `lighttpd` (porta 80).

### Iniciar o LuCI na porta 8080:
```sh
/usr/sbin/uhttpd -p 8080 -h /www -x /cgi-bin
```

---

## 2. Correção de Autenticação LuCI (`rpcd` e `shadow`)

O LuCI falha ao logar com `Admin` porque o `rpcd` só autoriza `root`.

### A. Autorizar `Admin` no `rpcd`:
```sh
uci add rpcd login
uci set rpcd.@login[-1].username='Admin'
uci set rpcd.@login[-1].password='$p$Admin'
uci add_list rpcd.@login[-1].read='*'
uci add_list rpcd.@login[-1].write='*'
uci commit rpcd
/etc/init.d/rpcd restart
```

### B. Sincronizar Senhas em `/etc/shadow`:
Defina a mesma hash de senha para `root` e `Admin` (Senha padrão: `root`):
```sh
# Define a senha 'root' para ambos os usuários:
sed -i "s|^root:.*|root:\$1\$ARKroot1\$RxlP7OYmB1xLe1obY775A/:20729:0:99999:7:::|" /etc/shadow
sed -i "s|^Admin:.*|Admin:\$1\$ARKroot1\$RxlP7OYmB1xLe1obY775A/:20729:0:99999:7:::|" /etc/shadow
sync
```

> [!CAUTION]
> **Regra de Ouro:** NUNCA apague nem renomeie os usuários `root` ou `Admin`. Se for alterar a senha no terminal pelo comando `passwd`, altere sempre os dois (`passwd root` e `passwd Admin`) para mantê-los sincronizados.

---

## 3. Debloat de Segurança e Desativação do FOTA

Para evitar que atualizações automáticas silenciosas da Acer sobrescrevam a customização:

```sh
# 1. Desativar scripts de atualização automática da Acer
chmod -x /lib/functions/silent-reboot.sh 2>/dev/null
chmod -x /lib/functions/download_img.sh 2>/dev/null
chmod -x /lib/functions/update_img.sh 2>/dev/null
chmod -x /usr/sbin/fota 2>/dev/null

# 2. Desativar daemons de telemetria pesada e modem inexistente
for svc in modem-monitor at_ril ril monitord sodd cwmp mqtt_client breakpad; do
    /etc/init.d/$svc stop 2>/dev/null
    /etc/init.d/$svc disable 2>/dev/null
done
```

---

## 4. Persistência no Boot (`/etc/rc.local`)

Adicione ao final de `/etc/rc.local` (antes de `exit 0`):
```sh
# Manter LuCI ativo na porta 8080
/usr/sbin/uhttpd -p 8080 -h /www -x /cgi-bin &
```
