# Kit de Engenharia Reversa para Portabilidade do OpenWrt Oficial

> **Finalidade**: Este diretório reúne todos os arquivos de baixo nível, a Árvore de Dispositivos descompilada (`.dts`), os microcódigos proprietários, módulos de kernel e os mapas de pinos necessários para criar o suporte oficial (**Target Port**) do **Acer Predator Connect T7** dentro da árvore de código-fonte do **OpenWrt Oficial**.

---

## 1. Conteúdo Deste Kit de Portabilidade

| Arquivo | Tamanho | Descrição Técnica |
| :--- | :--- | :--- |
| **`acer_predator_t7.dts`** | 100 KB | **Árvore de Dispositivos (DTS) Descompilada**: Código-fonte C legível de todos os barramentos, registradores, interrupções, PCIe e memória do SoC Qualcomm IPQ5332. |
| **`acer_predator_t7.dtb`** | 61.4 KB | **Device Tree Blob (DTB)**: O binário original extraído de `/sys/firmware/fdt` montado pelo kernel oficial. |
| **`kernel_modules_5.4.213.tar.gz`**| 8.3 MB | **Drivers do Kernel Qualcomm**: Todos os módulos `.ko` compilados para Linux 5.4.213 (NSS/PPE aceleração de 2.5 Gbps, ECM, drivers Wi-Fi 7 `ath12k`/`qca_ol`). |
| **`webapps_acer_oem.tar.gz`** | 3.4 MB | **Binários e Daemons Acer**: Binários do painel web, APIs de controle de LED, acelerador de jogos (Killer QoS/Game Priority) e scripts CGI. |
| **`etc_factory_tree.tar.gz`** | 435 KB | **Árvore `/etc` Original de Fábrica**: Todos os scripts de inicialização `/etc/init.d/`, regras udev/hotplug e padrões UCI intactos. |
| **`qualcomm_ini_and_sawf.tar.gz`**| 8.2 KB | **Parâmetros de Hardware Qualcomm**: Arquivos `QCA5332.ini`, `global.ini` e perfis de classes de QoS de baixa latência SAWF. |
| **`ipq5332_wifi_fw.tar.gz`** | 4.3 MB | **Pacote de Firmware Wi-Fi 7 (Qualcomm)**: Contém `q6_fw0.*`, `q6_fw1.*`, `iu_fw.*`, `regdb.bin`, `caldata.bin` e todos os arquivos BDF (`bdwlan.*`). |
| **`gpio_table.txt`** | 2.1 KB | **Tabela de Pinos GPIO**: Mapa completo de pinos digitais do processador (`platform/1000000.pinctrl`), voltagens, direções (in/out) e resistores pull-up/down. |
| **`board.json`** | 323 B | Definição padrão OpenWrt do modelo (`qcom,ipq5332-ap-mi01.6`) e interfaces de rede. |
| **`switch_config.txt`** | 6.9 KB | Dump da configuração do switch integrado Gigabit (`switch1` / QCA NSS DP). |
| **`network_interfaces.txt`** | 7.0 KB | Tabela de interfaces de rede ativas, rotas e mapeamento MAC. |
| **`loaded_modules.txt`** | 14.0 KB | Lista de todos os módulos de kernel carregados (`lsmod`): aceleradores `qca-nss-ppe`, `ecm`, `emesh-sp` e drivers Wi-Fi. |
| **`ledd_config.txt`** | 164 B | Configuração do daemon de iluminação RGB dos LEDs do Predator. |
| **`buttons_config.txt`** | 94 B | Mapeamento dos botões físicos (Reset e WPS). |

---

## 2. A Device Tree (`acer_predator_t7.dts`)

O arquivo **`acer_predator_t7.dts`** é o artefato mais valioso para qualquer desenvolvedor de kernel ou mantenedor do OpenWrt.

### Identificação da Placa:
* **Modelo**: `Qualcomm Technologies, Inc. IPQ5332/AP-MI01.6`
* **Compatibilidade**: `"qcom,ipq5332-ap-mi01.6"`, `"qcom,ipq5332"`
* **Plataforma Base**: Placa de referência oficial Qualcomm **"Miami" (AP-MI01.6)**.
* **Memória Reservada do Bootloader**: `0x484ef000 0xf000`

### Principais Barramentos Mapeados no DTS:
1. **PCIe dos Rádios Wi-Fi:**
   * `pcie3x2_phy_pipe_clk` e `pcie3x1_0_phy_pipe_clk` (barramentos de alta velocidade que comunicam com os rádios de 5 GHz e 6 GHz).
2. **USB 3.0 / USB 2.0:**
   * `usb3phy_0_cc_pipe_clk` (controlador USB host).
3. **Controlador de Pinos e Interrupções (Pin Controller):**
   * `pinctrl@1000000` gerenciando os 53 pinos de GPIO.

---

## 3. Como o OpenWrt Oficial Usa esses Arquivos

Para adicionar o Acer Predator Connect T7 no repositório oficial do OpenWrt (`git clone https://github.com/openwrt/openwrt.git`):

### Passo 1: Inserir a Device Tree no Target
Copiar o arquivo para a pasta do target Qualcomm Wi-Fi 7:
```text
target/linux/qualcommax/files/arch/arm/boot/dts/qcom-ipq5332-acer-predator-t7.dts
```

### Passo 2: Criar a Definição de Imagem em `target/linux/qualcommax/image/ipq53xx.mk`
```makefile
define Device/acer_predator-t7
	$(call Device/FitImage)
	DEVICE_VENDOR := Acer
	DEVICE_MODEL := Predator Connect T7
	SOC := ipq5332
	DEVICE_DTS := qcom-ipq5332-acer-predator-t7
	DEVICE_PACKAGES := ath12k-firmware-ipq5332 kmod-ath12k
	IMAGE_SIZE := 245760k
endef
TARGET_DEVICES += acer_predator-t7
```

### Passo 3: Mapeamento de Calibração de Rádio (`ath12k`)
No arquivo `target/linux/qualcommax/base-files/etc/hotplug.d/firmware/11-ath12k-caldata`:
Adicionar a instrução para extrair o BDF diretamente da partição **`0:ART`** (`mtd18`), cujo backup já temos em `Backups_MTD/backup_predator_t7_art.bin`.

### Passo 4: Firmware de Rede 2.5G
Utilizar o microcódigo extraído em `Backups_MTD/backup_predator_t7_ethphy_fw.bin` para o carregador de firmware da porta física Aquantia/Qualcomm.

---

## 4. Conclusão

Com todos esses arquivos preservados, **a engenharia reversa do hardware está 100% concluída**. Não existe nenhuma "caixa preta" restante no equipamento: sabemos a pinagem, os barramentos, os binários de calibração, os drivers de aceleração NSS/PPE, o mapa de memória e os microcódigos de rede.
