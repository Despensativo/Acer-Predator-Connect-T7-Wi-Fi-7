# Guia de Recuperação de Desastre e Restauração (Unbrick)

Este guia contém as instruções passo a passo para recuperar o **Acer Predator Connect T7** em caso de falhas de configuração, perda de acesso, redefinições acidentais ou problemas de inicialização.

---

## Cenário 1: Redefinição Acidental / Reset de Fábrica

Se você pressionar o botão físico **RESET** na traseira do aparelho por 10 segundos, o roteador voltará às configurações de fábrica:
* IP padrão de fábrica: `192.168.76.1`
* Servidor DHCP voltará a ficar ativo (causará duplo NAT temporário).
* O terminal (SSH / Telnet) voltará a ficar bloqueado.

### Como Restaurar Tudo em Menos de 2 Minutos:
1. Conecte o cabo de rede do seu PC na porta **LAN 1** do Predator.
2. Acesse pelo navegador: **`http://192.168.76.1`** (ou `http://acer-connect.com`).
3. Conclua a configuração inicial rápida (Quick Setup) com qualquer senha provisória.
4. Vá em **System** $\rightarrow$ **Backup and restore** $\rightarrow$ **Restore**.
5. Selecione o arquivo definitivo salvo nesta pasta:
   * **`Configuracoes_Roteador/config_ap_ssh_unlocked.cfg`**
6. Clique em **Restore** e aguarde 2 minutos.
7. O roteador voltará imediatamente para `192.168.73.2`, como AP 2.5G sem duplo NAT, com Wi-Fi 7 MLO, canais travados e SSH/Telnet liberados!

---

## Cenário 2: Perda de Acesso ao Painel Web mas com Acesso ao Terminal

Se a interface web travar ou apresentar erro, mas o terminal continuar respondendo:
1. Abra o Prompt de Comando ou PowerShell:
   ```powershell
   telnet 192.168.73.2
   ```
2. Para reiniciar a interface web (lighttpd):
   ```sh
   /etc/init.d/lighttpd/lighttpd.init restart
   ```
3. Para reiniciar os rádios Wi-Fi:
   ```sh
   wifi
   ```
4. Para reiniciar o roteador com segurança:
   ```sh
   reboot
   ```

---

## Cenário 3: Restauração da Partição de Calibração ART (Perda de Alcance Wi-Fi)

Caso em alguma atualização futura ou teste de firmware o sinal Wi-Fi fique fraco ou as potências sejam perdidas:

1. Transfira o arquivo de calibração salvo neste repositório (`Backups_MTD/backup_predator_t7_art.bin`) para o diretório `/tmp/` do roteador via SCP:
   ```powershell
   scp -O "H:\FEITOS COM IA\Acer-Predator-Connect-T7\Backups_MTD\backup_predator_t7_art.bin" Admin@192.168.73.2:/tmp/art.bin
   ```
2. Acesse o terminal:
   ```powershell
   telnet 192.168.73.2
   ```
3. Grave a partição ART de volta na Flash (`mtd18`):
   ```sh
   dd if=/tmp/art.bin of=/dev/mtdblock18 bs=64k
   sync
   reboot
   ```
*Após reiniciar, a calibração de fábrica de todos os rádios Wi-Fi estará 100% restaurada.*

---

## Cenário 4: Recuperação Crítica de Bootloader (TFTP Recovery)

Conforme revelado no arquivo `backup_predator_t7_uboot_env.bin`, o bootloader U-Boot do Predator T7 escuta por um servidor de recuperação por rede:

* **IP do Roteador no Bootloader:** `192.168.10.1`
* **IP do Servidor TFTP esperado:** `192.168.10.10`
* **Velocidade da Porta Serial (UART):** `115200 bps, 8N1` (no conector serial interno `ttyMSM0`)

### Procedimento de Recuperação via TFTP:
1. Configure a placa de rede do seu computador com IP estático:
   * **Endereço IP:** `192.168.10.10`
   * **Máscara:** `255.255.255.0`
   * **Gateway:** `192.168.10.1`
2. Conecte um cabo de rede direto da placa do PC na porta **LAN 1** do roteador.
3. Inicie um software de servidor TFTP no Windows (como o *Tftpd64*).
4. O bootloader procurará pela imagem de recuperação oficial da Acer/Qualcomm e efetuará o flash automaticamente em caso de corrupção total do sistema operacional.

---

## Regras de Ouro de Segurança

1. **NUNCA conecte dois cabos de rede simultâneos** entre o roteador mestre e o Predator T7 (isso causa um loop de camada 2 que derruba toda a internet da casa). Apenas um único cabo na porta de 2.5 Gbps é suficiente.
2. **NUNCA desligue o roteador da tomada** enquanto uma restauração de backup ou gravação de flash estiver em andamento.
3. **Mantenha os arquivos desta pasta salvos em cópia externa** (Google Drive ou nuvem) para garantir acesso mesmo que o HD externo não esteja conectado.
