# Acer Predator Connect T7 — Índice Mestre (Ground Truth)

> **Context Priming para IA e Desenvolvedores**: Documento de verdade absoluta e mapa arquitetural do roteador Acer Predator Connect T7 (SoC Qualcomm IPQ5332 / Wi-Fi 7).

---

## 1. Especificações Técnicas Fundamentais

| Componente | Especificação | Observações |
| :--- | :--- | :--- |
| **SoC** | Qualcomm IPQ5332 (Miami) | Quad-Core ARM Cortex-A53 @ 1.5 GHz, 64-bit |
| **RAM** | 1 GB DDR4 | Base U-Boot: `0x41000000` |
| **Flash** | 1 GB SPI NAND | Esquema A/B UBI + SquashFS 256k XZ |
| **Wi-Fi** | Tri-Band BE11000 (QCN6432) | Exige driver PIL seguro + TrustZone SCM (PAS ID `0xd`) |
| **Portas LAN** | 1x 2.5G WAN + 1x 2.5G LAN + 2x 1G LAN | Aceleração via hardware PPE/NSS nativa no kernel 5.4 |

---

## 2. Parâmetros de Conexão e Rede

- **IP Web Stock (Fábrica):** `192.168.76.1` (Porta 80)
- **IP Atual do Laboratório (Modo AP Wi-Fi 7):** `192.168.73.2` (LuCI Porta 80)
- **IP do Servidor TFTP de Recuperação (PC):** `192.168.1.66` (ou `192.168.10.10`)
- **Porta Serial UART:** `115200 8N1` (`ttyMSM0`), 3.3V

---

## 3. Tabela Resumo de Partições MTD Críticas

| MTD | Nome da Partição | Papel no Sistema | Risco |
| :--- | :--- | :--- | :--- |
| `mtd18` | `0:ART` | Calibração de rádio e MAC Address | **CRÍTICO - Nunca apagar sem backup** |
| `mtd11` | `0:APPSBL` | Bootloader U-Boot oficial | **CRÍTICO - Não sobrescrever** |
| `mtd3` / `mtd4` | `BOOTCONFIG` / `1` | Seletor de Slot A/B (`primaryboot`) | Chaveador de inicialização |
| `mtd21` | `rootfs` | **Slot 1 (Reserva / Fallback v24)** | **Preservado 100% intacto** |
| `mtd20` | `rootfs_1` | **Slot 2 (Ativo / Otimizado v27)** | **ATIVO - LuCI Porta 80 + Wi-Fi 7 + IPv6 Híbrido** |

---

## 4. Mapa da Arquitetura em 7 Módulos

### 📁 [01_FIRMWARES_E_IMAGENS/](01_FIRMWARES_E_IMAGENS/)
- `OpenWrt_Imagens/`: Imagens FIT `.itb`, sysupgrade e initramfs.
- `Custom_SquashFS/`: Imagens compiladas e modificadas de RootFS.

### 📁 [02_BACKUPS_E_DUMPS/](02_BACKUPS_E_DUMPS/)
- `MTD_Full_Dumps/`: Cópias 1:1 de todas as partições MTD da SPI NAND (`ART`, U-Boot, Kernel).
- `Backups_Configuracao_Pessoal/`: Snapshot do Overlay (`backup_overlay_completo_2026-10-03.tar.gz`) e Sysupgrade do LuCI.
- `Configuracoes_CFG/`: Backups `.cfg` da interface Web OEM.

### 📁 [03_ENGENHARIA_REVERSA/](03_ENGENHARIA_REVERSA/)
- `DeviceTree_DTS/`: Árvores de dispositivos `.dts` e `.dtb` descompiladas.
- `Modulos_Kernel_QSDK/`: Drivers de aceleração proprietários (PPE, NSS, ECM).
- `Modem_5G_Fibocom_X7/`: Engenharia reversa dos binários celulares e barramento MHI.
- `Homologacao_FCC/`: Documentos oficiais e fotos forenses do circuito PCB.
- `Desmontagem_U-Boot/`: Scripts de engenharia reversa e análise estática do bootloader.

### 📁 [04_SCRIPTS_E_FERRAMENTAS/](04_SCRIPTS_E_FERRAMENTAS/)
- `Automacao_e_Unlock/`: Scripts Python de debloat, liberação de SSH, AP pessoal e restauração rápida (`restaurar_backup_pessoal.py`).
- `Diagnostico_de_Rede/`: Ferramentas de escuta DHCP, sniffers ARP e monitoramento.
- `Servidor_TFTP/`: Utilitários e binários do servidor TFTP para Windows.

### 📁 [05_COMPILADORES/](05_COMPILADORES/)
- `SquashFS_QSDK_T7/`: Ferramenta `mksquashfs-qsdk` validada para empacotamento 256k XZ.

### 📁 [06_DOCUMENTACAO/](06_DOCUMENTACAO/)
- [**`PROCEDIMENTOS/`**](06_DOCUMENTACAO/PROCEDIMENTOS/): Runbooks operacionais passo a passo (`00` a `08`).
- [**`NOTAS_HARDWARE/`**](06_DOCUMENTACAO/NOTAS_HARDWARE/): Estudos técnicos de hardware, MTD, FOTA e Wi-Fi TrustZone.
- [**`logs_e_rascunhos/`**](06_DOCUMENTACAO/logs_e_rascunhos/): Arquivo histórico e quarentena de logs de testes.

### 📁 [07_ARTEFATOS_BUILD_WSL/](07_ARTEFATOS_BUILD_WSL/)
- Ambiente de compilação cruzada do kernel ARM64 Linux, manifestos e imagens experimentais.
