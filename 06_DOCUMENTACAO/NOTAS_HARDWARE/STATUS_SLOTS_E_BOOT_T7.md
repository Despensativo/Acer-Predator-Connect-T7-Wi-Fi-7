# Status dos Slots, Bootloader e Procedimentos de Teste — Acer Predator Connect T7

> **Resumo Técnico Consolidado**: Este documento unifica as análises e testes realizados sobre o chaveamento de partições (Dual Slot A/B), boot em RAM via TFTP e integração com o bootloader Qualcomm IPQ5332 do Acer T7.

---

## 1. Arquitetura Dual-Boot (Slot 1 vs Slot 2)

O Acer Predator Connect T7 utiliza um esquema de redundância A/B gerenciado via U-Boot e partições `BOOTCONFIG`.

| Slot | Partição RootFS | MTD | Status Atual | Finalidade |
| :--- | :--- | :--- | :--- | :--- |
| **Slot 1 (A)** | `rootfs` | `mtd21` | **ATIVO** (Primário OEM) | Firmware original Acer (Seguro / Fallback) |
| **Slot 2 (B)** | `rootfs_1` | `mtd20` | **INATIVO** (Secundário) | Alvo para testes de customização / OpenWrt |

*Nota: O kernel OEM 5.4 é compartilhado entre os slots. A separação ocorre no RootFS e nos argumentos de montagem UBI.*

---

## 2. Mecanismo de Chaveamento entre Slots

O sistema possui scripts utilitários em `/usr/sbin/` para controle do slot de inicialização:

### Alternar para o Slot 2 (OpenWrt / Teste): `/usr/sbin/boot-openwrt`
1. Define a variável de ambiente U-Boot:
   ```sh
   fw_setenv fsbootargs "ubi.mtd=rootfs_1 root=mtd:ubi_rootfs rootfstype=squashfs"
   ```
2. Altera o parâmetro `primaryboot=0` nos procfs `bootconfig0` e `bootconfig1`.
3. Exporta o binário atualizado via `getbinary_bootconfig` para `/tmp`.
4. Desbloqueia e regrava as partições de bootconfig:
   ```sh
   mtd unlock /dev/mtd3 && mtd write /tmp/bootconfig.bin /dev/mtd3
   mtd unlock /dev/mtd4 && mtd write /tmp/bootconfig.bin /dev/mtd4
   ```
5. Executa `reboot`.

### Retornar para o Slot 1 (OEM): `/usr/sbin/boot-acer`
1. Remove a variável `fsbootargs`:
   ```sh
   fw_setenv fsbootargs
   ```
2. Define `primaryboot=1` nos objetos procfs.
3. Regrava as partições `mtd3` (`BOOTCONFIG`) e `mtd4` (`BOOTCONFIG1`).
4. Executa `reboot`.

> [!WARNING]
> **Risco de Gravação**: Os scripts OEM executam a gravação MTD sequencial sem verificação pós-gravação (sem checagem SHA-256 pós-flash) e reiniciam imediatamente. É **obrigatório** ter backup local dos MTDs 3 e 4 antes de qualquer chaveamento persistente.

---

## 3. Boot em RAM via TFTP (Sem Modificação da Flash)

Para ensaios seguros sem risco de brick permanente, a inicialização em RAM via TFTP utiliza imagens FIT (`.itb`).

### Parâmetros de Rede TFTP:
- **IP do Servidor TFTP (PC)**: `192.168.1.66` (padrão de recuperação Qualcomm) ou `192.168.1.254`
- **IP do Roteador (T7)**: `192.168.1.1`
- **Endereço de Carga RAM (Load Address)**: `0x41000000` (teto seguro testado até `0x41b20000`)

### Estrutura do FIT de Diagnóstico em RAM:
- **Kernel Base**: Linux ARM64 (6.18.52 ou 5.4 OEM).
- **Initramfs**: Mínimo embutido, estático, com heartbeat UDP e netconsole ativado.
- **Linha de Comando (Cmdline)**: Forçada para RAM (`maxcpus=1`, sem montagem de MTDs, `ubi.mtd` desativado para evitar escrita acidental).

---

## 4. Requisitos para Compilação de Imagens SquashFS

Para que uma imagem RootFS seja reconhecida e montada com sucesso pelo kernel e U-Boot:
1. **Ferramenta**: Utilizar o `mksquashfs-qsdk` (disponível em `COMPILADOR-OFICIAL-SQUASHFS-T7/`).
2. **Tamanho do Bloco**: `-b 256k` (262.144 bytes).
3. **Compressor**: `-comp xz` com opções de compactação padrão QSDK.
4. **Metadados e Mtime**: Preservar o timestamp fixo e permissões corretas de symlinks para evitar rejeição no hash de verificação.

---

## 5. Rádio Wi-Fi e TrustZone (Q6 / WCSS)

- **SoC**: Qualcomm IPQ5332 (Quad-Core ARM Cortex-A53).
- **Arquitetura de Segurança**: A inicialização do subsistema sem fio (WCSS/Q6) exige autenticação via Qualcomm TrustZone SCM.
- **Driver Necessário**: `qcom,ipq5332-wcss-sec-pil` utilizando PAS ID `0xd`.
- **Implicação**: Um kernel genérico sem os patches SCM da Qualcomm não consegue inicializar os rádios Wi-Fi 7 sem autorização da TrustZone da Acer.

---

*Para histórico bruto de mensagens das sessões anteriores de chat, consulte a pasta `_archive_historico/`.*
