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

- **IP Web Stock (Fábrica / LuCI):** `192.168.76.1` (Porta 80)
- **IP do Servidor TFTP de Recuperação (PC):** `192.168.1.66` (ou `192.168.10.10`)
- **Porta Serial UART:** `115200 8N1` (`ttyMSM0`), 3.3V

---

## 3. Tabela Resumo de Partições MTD Críticas

| MTD | Nome da Partição | Papel no Sistema | Risco |
| :--- | :--- | :--- | :--- |
| `mtd18` | `0:ART` | Calibração de rádio e MAC Address | **CRÍTICO - Nunca apagar sem backup** |
| `mtd11` | `0:APPSBL` | Bootloader U-Boot oficial | **CRÍTICO - 100% Intacto de Fábrica** |
| `mtd3` / `mtd4` | `BOOTCONFIG` / `1` | Seletor de Slot A/B (`primaryboot`) | Chaveador de inicialização |
| `mtd21` | `rootfs` | **Slot 1 (Reserva / Fallback OEM)** | **Preservado 100% intacto de fábrica** |
| `mtd20` | `rootfs_1` | **Slot 2 (Ativo / Otimizado v27)** | **ATIVO - LuCI Porta 80 + Wi-Fi 7** |

---

## 4. Mapa da Arquitetura do Repositório

### 📁 [Scripts_Automacao/](Scripts_Automacao/) — Central Ativa da Suite
- `launcher_t7.py`: Gerenciador central interativo (menus 0 a 8).
- `gravar_v27_slot2.py`, `otimizar_e_ativar_luci_slot2.py`: Gravação, debloat e LuCI na porta 80.
- `switch_boot_slot.py`, `unlock_only_ssh.py`, `instalar_ark_router.py`: Dual-boot, desbloqueio e temas.
- `telnet_compat.py`, `logger_t7.py`: Bibliotecas universais de comunicação e logging.

### 📁 [01_FIRMWARES_E_IMAGENS/](01_FIRMWARES_E_IMAGENS/)
- `Official_v27_Componentes/`: Kernel, rootfs e wifi_fw da ROM oficial v27 para Slot 2.
- `Stock_OEM_Recovery/`: Imagem completa de fábrica v27 (`nand-4k-...`) e binários U-Boot para unbrick físico WPS 5s.
- `Ark_Router/`: Cache local do painel (pacote baixado sob demanda direto do GitHub Releases pela Opção [5]).
- `Custom_SquashFS/`: Imagem consolidada de RootFS otimizado.

### 📁 [02_BACKUPS_E_DUMPS/](02_BACKUPS_E_DUMPS/)
- `Configuracoes_CFG/`: Arquivo canônico oficial de desbloqueio (`config_v27_ssh_unlocked.cfg`).
- `Backups_Configuracao_Pessoal/`: Snapshots locais de overlay e backups pessoais do roteador.
- `Imagens_Recuperacao_WPS_Failsafe/`: Imagens auxiliares de emergência para U-Boot.

### 📁 [04_SCRIPTS_E_FERRAMENTAS/](04_SCRIPTS_E_FERRAMENTAS/)
- `Servidor_TFTP/`: Servidor TFTP RFC 1350/2348 nativo para recuperação de baixo nível em rede.
- `Diagnostico_de_Rede/`: Utilitários forenses, sniffers e decodificadores de tráfego.

### 📁 [06_DOCUMENTACAO/](06_DOCUMENTACAO/)
- [**`PROCEDIMENTOS/`**](06_DOCUMENTACAO/PROCEDIMENTOS/): Runbooks operacionais passo a passo (`00` a `09`).
- [**`NOTAS_HARDWARE/`**](06_DOCUMENTACAO/NOTAS_HARDWARE/): Estudos técnicos de hardware, MTD, FOTA e Wi-Fi TrustZone.
- [**`logs_e_rascunhos/`**](06_DOCUMENTACAO/logs_e_rascunhos/): Relatórios de auditoria e históricos técnicos.

---

## 5. Acervo Histórico e Pesquisa Local (`_FORA DO GitHub/`)

O material de pesquisa pesada, compilações intermediárias e dumps brutos foi preservado localmente fora do controle de versão em `_FORA DO GitHub/`:
- `01_ARTEFATOS_BUILD_WSL/`: Kernels experimentais compilados em WSL e logs brutos de compilação.
- `02_FIRMWARES_E_DUMPS_PESADOS/`: Dumps brutos MTD de todas as partições da flash e imagens de fábrica legadas.
- `03_DOCUMENTOS_PESADOS_FCC/`: Documentação e PDFs completos da homologação FCC dos modelos T7 e X7.
- `06_OPENWRT_IMAGENS_DESENVOLVIMENTO/`: Compilações do kernel OpenWrt 6.18 em RAM.
- `07_ENGENHARIA_REVERSA_HISTORICA/`: Desmontagens de U-Boot, módulos de kernel QSDK e pinouts.
- `08_COMPILADORES_E_FONTES_HISTORICAS/`: Ferramenta e código-fonte em C do `mksquashfs-qsdk`.

