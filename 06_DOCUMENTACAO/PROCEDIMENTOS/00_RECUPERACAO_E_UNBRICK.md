# Procedimento 00: Recuperação de Desastre e Unbrick

> **Status:** [VALIDADO EM BANCADA]  
> **Nível de Risco:** [MÉDIO A ALTO - Recuperação de Sistema / Gravação de MTD]  
> **Objetivo:** Recuperar o roteador Acer Predator Connect T7 em casos de perda de acesso, reset de fábrica, corrupção de sistema ou perda de calibração Wi-Fi.

---

## Cenário 1: Redefinição Acidental / Reset de Fábrica

Se o botão físico **RESET** for pressionado por 10 segundos:
* IP volta para `192.168.76.1` (ou `192.168.1.1`).
* SSH/Telnet voltam a ficar bloqueados.

### Passos de Restauração:
1. Conecte o cabo de rede na porta **LAN 1**.
2. Acesse no navegador `http://192.168.76.1` (ou `http://acer-connect.com`).
3. Conclua o Quick Setup provisório.
4. Acesse: **System** $\rightarrow$ **Backup and restore** $\rightarrow$ **Restore**.
5. Selecione o arquivo de desbloqueio oficial:
   ```text
   02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_ssh_unlocked.cfg
   ```
6. Clique em **Restore** e aguarde 2 minutos. O roteador reinicia com SSH/Telnet liberados.

---

## Cenário 2: Perda de Acesso Web com Terminal Respondendo

Se a interface web travar, mas houver resposta via Telnet/SSH:
```sh
# Reiniciar o servidor web
/etc/init.d/lighttpd/lighttpd.init restart

# Reiniciar os subsistemas de rádio Wi-Fi
wifi

# Reiniciar com segurança
sync && reboot
```

---

## Cenário 3: Restauração da Partição de Calibração ART (Rádio Wi-Fi)

> [!CAUTION]
> A partição ART contém a calibração de fábrica e os endereços MAC exclusivos do hardware. Nunca inicialize sem conferir o tamanho da imagem antes da gravação. (Arquivo de backup preservado localmente em `_FORA DO GitHub/02_FIRMWARES_E_DUMPS_PESADOS/MTD_Full_Dumps/backup_predator_t7_art.bin`).

1. Envie o backup de calibração para `/tmp/`:
   ```sh
   scp -O "_FORA DO GitHub/02_FIRMWARES_E_DUMPS_PESADOS/MTD_Full_Dumps/backup_predator_t7_art.bin" Admin@192.168.73.2:/tmp/art.bin
   ```
2. No terminal do roteador, grave de volta na flash:
   ```sh
   dd if=/tmp/art.bin of=/dev/mtdblock18 bs=64k
   sync
   reboot
   ```

---

## Cenário 4: Recuperação Crítica de Bootloader (TFTP Recovery)

Se o sistema operacional não inicializar e entrar em modo de recuperação:
- **IP do Roteador no Bootloader:** `192.168.10.1` (ou `192.168.1.1`)
- **IP do Servidor TFTP (PC):** `192.168.10.10` (ou `192.168.1.66`)
- **Serial UART:** `115200 8N1` em `ttyMSM0`

### Passos:
1. Fixe o IP do PC como estático em `192.168.10.10` (máscara `255.255.255.0`).
2. Conecte o cabo direto na porta **LAN 1**.
3. Inicie o servidor TFTP (ex: Tftpd64) apontando para a pasta com o firmware oficial assinado.
4. Ligue o roteador mantendo o botão reset pressionado para forçar a solicitação TFTP do U-Boot.
