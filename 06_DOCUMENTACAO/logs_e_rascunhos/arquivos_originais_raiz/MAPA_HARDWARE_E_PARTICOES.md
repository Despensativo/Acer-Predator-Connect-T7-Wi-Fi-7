# Mapa de Hardware, Partições MTD e U-Boot

Este documento descreve as especificações de hardware de baixo nível, a tabela de partições de memória Flash (MTD) e os parâmetros do bootloader U-Boot do **Acer Predator Connect T7**.

---

## 1. Especificações Técnicas de Hardware

| Componente | Especificação |
| :--- | :--- |
| **Processador (SoC)** | Qualcomm IPQ5332 (Quad-Core ARM Cortex-A53 @ 1.5 GHz, arquitetura ARMv7l) |
| **Kernel do Sistema** | Linux `5.4.213 #0 SMP PREEMPT` |
| **Memória RAM** | 1.0 GB DDR4 (aprox. 885 MB utilizáveis, >520 MB livres) |
| **Armazenamento Flash** | SPI NAND Flash com sistema UBI / OverlayFS (153.3 MB graváveis em `/overlay`) |
| **Controlador Ethernet 2.5G** | Aquantia / Qualcomm PHY dedicado (porta WAN `eth0`) |
| **Switch Gigabit Integrado** | QCA NSS DP Switch (`eth1.1` Game Port, `eth1.2` LAN 1) |
| **Rádios Wi-Fi** | Tri-Band Wi-Fi 7 (802.11be): 2.4 GHz (2x2), 5 GHz (2x2), 6 GHz (2x2) |

---

## 2. Tabela de Partições MTD (`/proc/mtd`)

O Predator T7 utiliza um sistema de **Dual Boot redundante (A/B)** para permitir atualizações seguras de firmware.

```text
dev:    size   erasesize  name
mtd0: 00180000 00040000 "0:SBL1"          -> Secondary Boot Loader (Slot A) [DUMP COMPLETO]
mtd1: 00180000 00040000 "0:SBL1_1"        -> Secondary Boot Loader (Slot B)
mtd2: 00100000 00040000 "0:MIBIB"         -> Master Information Block (Partições) [DUMP COMPLETO]
mtd3: 00080000 00040000 "0:BOOTCONFIG"    -> Configuração de Inicialização
mtd4: 00080000 00040000 "0:BOOTCONFIG1"   -> Configuração de Inicialização (Backup)
mtd5: 00380000 00040000 "0:QSEE"          -> Qualcomm Secure Execution Environment (TrustZone) [DUMP COMPLETO]
mtd6: 00380000 00040000 "0:QSEE_1"        -> Qualcomm Secure Execution Environment (Slot B)
mtd7: 00080000 00040000 "0:DEVCFG_1"      -> Device Configuration (Slot B)
mtd8: 00080000 00040000 "0:DEVCFG"        -> Device Configuration (Slot A) [DUMP COMPLETO]
mtd9: 00080000 00040000 "0:TME"           -> Trusted Management Engine
mtd10: 00080000 00040000 "0:TME_1"        -> Trusted Management Engine (Backup)
mtd11: 00080000 00040000 "0:CDT_1"        -> Platform Configuration Data (Slot B)
mtd12: 00080000 00040000 "0:CDT"          -> Platform Configuration Data (Slot A) [DUMP COMPLETO]
mtd13: 00080000 00040000 "0:APPSBLENV"    -> Variáveis de Ambiente do U-Boot [DUMP COMPLETO]
mtd14: 00180000 00040000 "0:APPSBL_1"     -> U-Boot Bootloader (Slot B) [DUMP COMPLETO]
mtd15: 00180000 00040000 "0:APPSBL"       -> U-Boot Bootloader (Slot A) [DUMP COMPLETO]
mtd16: 00100000 00040000 "0:ETHPHYFW"     -> Firmware do chip 2.5 Gbps Ethernet [DUMP COMPLETO]
mtd17: 00080000 00040000 "0:TRAINING"     -> Dados de Treinamento de Memória DDR
mtd18: 00200000 00040000 "0:ART"          -> Atheros Radio Test (Calibração Wi-Fi) [CRÍTICO - DUMP COMPLETO]
mtd19: 00040000 00040000 "0:LICENSE"      -> Licenças e números de série [DUMP COMPLETO]
mtd20: 0f000000 00040000 "rootfs_1"       -> Imagem do Sistema Operacional (Slot B - 240 MB)
mtd21: 0f000000 00040000 "rootfs"         -> Imagem do Sistema Operacional (Slot A - 240 MB)
mtd22: 00600000 00040000 "0:TRAFFIC"      -> Dados de Estatísticas de Tráfego
mtd23: 00080000 00040000 "0:SYSTRACE"     -> Rastreamento de Sistema
mtd24: 00300000 00040000 "0:TRAFFIC_DAY"  -> Histórico Diário de Tráfego
mtd25: 00828800 0003e000 "wifi_fw"        -> Firmware Binário Wi-Fi 7 Qualcomm IPQ5332 (8.3 MB) [DUMP COMPLETO]
mtd26: 0040ad48 0003e000 "kernel"         -> Imagem do Kernel Linux montada (4.04 MB) [DUMP COMPLETO]
mtd27: 02606000 0003e000 "ubi_rootfs"     -> Sistema Base /rom (SquashFS 38 MB) [DUMP COMPLETO]
mtd28: 0a71c000 0003e000 "rootfs_data"    -> Camada gravável de personalizações (/overlay)
```

---

## 3. Variáveis do Bootloader U-Boot (`mtd13` - `APPSBLENV`)

Abaixo estão os parâmetros nativos extraídos da partição de boot:

```text
baudrate=115200
bootargs=console=ttyMSM0,115200n8
bootcmd=bootipq
bootdelay=3
ipaddr=192.168.10.1
serverip=192.168.10.10
netmask=255.255.255.0
ethaddr=70:5a:6f:5d:7c:b1       (Porta WAN 2.5G)
eth1addr=70:5a:6f:5d:80:71      (Game Port)
eth2addr=70:5a:6f:5d:84:31      (LAN 1)
soc_hw_version=201a0101
soc_version_major=1
soc_version_minor=1
fdt_high=0x48500000
fdtcontroladdr=4a4f4004
```

---

## 4. Arquivos de Backup Preservados na Pasta `Backups_MTD/`

1. **`backup_predator_t7_art.bin` (2.0 MB)**:
   * Contém a calibração física dos amplificadores de potência (FEMs) dos rádios de 2.4 GHz, 5 GHz e 6 GHz. Este arquivo é único por placa física e insubstituível.
2. **`backup_predator_t7_uboot_env.bin` (512 KB)**:
   * As variáveis de inicialização para emergência via TFTP.
3. **`backup_predator_t7_ethphy_fw.bin` (1.0 MB)**:
   * O microcódigo da porta física 2.5 Gbps.
4. **`backup_predator_t7_license.bin` (256 KB)**:
   * Registro de licença original do equipamento.
5. **`backup_predator_t7_devcfg.bin` (512 KB)** & **`backup_predator_t7_cdt.bin` (512 KB)**:
   * Parâmetros de clock, voltagem e barramentos da placa-mãe.
