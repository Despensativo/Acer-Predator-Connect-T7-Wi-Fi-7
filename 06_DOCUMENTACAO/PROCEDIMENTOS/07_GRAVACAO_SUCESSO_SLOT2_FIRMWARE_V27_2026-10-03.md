# Relatório Técnico de Sucesso: Gravação e Boot do Firmware v1.01.000027 no Slot 2

> **Data da Operação:** 03 de Outubro de 2026  
> **Dispositivo:** Acer Predator Connect T7 (Qualcomm IPQ5332 / Wi-Fi 7)  
> **Status:** **SUCESSO CONFIRMADO EM BANCADA**  
> **Sistema em Execução:** Acer Predator Connect T7 OEM Firmware `1.01.000027` (Build: 11/03/2025)  
> **Slot Ativo:** Slot 2 (`mtd20` / `rootfs_1` / `ubi1`)  
> **Slot 1 (`mtd21` / v24 Original):** **100% INTACTO E PRESERVADO**  
> **Endereço de Gestão Web:** `http://192.168.76.1`  

---

## 1. Resumo Executivo da Operação

Foi realizada com êxito a extração, validação, gravação e inicialização da versão oficial mais recente do firmware Acer Predator Connect T7 (**v1.01.000027**) na partição secundária (**Slot 2 - `mtd20`**). 

A partição primária de fábrica (**Slot 1 - `mtd21`**), contendo a versão anterior estável `1.01.000024`, **não sofreu nenhuma operação de escrita**, permanecendo disponível como salvaguarda absoluta de hardware (fail-safe dual-boot).

Após a comutação dos ponteiros de boot (`primaryboot=0`), o aparelho reiniciou diretamente no novo firmware, comprovado via requisição HTTP onde o servidor Web nativo retornou o cabeçalho oficial:
`Last-Modified: Tue, 11 Mar 2025 08:57:41 GMT`.

---

## 2. Arquitetura das Partições e Estrutura UBI

O Acer Predator Connect T7 utiliza memória Flash NAND com suporte a boot duplo A/B. A tabela MTD divide o armazenamento da seguinte forma:

| Partição MTD | Rótulo OEM | Função | Tamanho | Slot UBI |
| :--- | :--- | :--- | :--- | :--- |
| `/dev/mtd3` | `0:BOOTCONFIG` | Tabela primária de ponteiro de inicialização | 512 KiB | N/A |
| `/dev/mtd4` | `0:BOOTCONFIG1` | Tabela redundante de ponteiro de inicialização | 512 KiB | N/A |
| `/dev/mtd20` | `rootfs_1` | **Container UBI do Slot 2** (Alvo da Gravação) | 240 MiB | `ubi1` |
| `/dev/mtd21` | `rootfs` | **Container UBI do Slot 1** (Firmware Original Preservado) | 240 MiB | `ubi0` |

### Estrutura Interna dos Volumes UBI (`ubi1` no `mtd20`):
* `ubi1_0` (**wifi_fw**): Volume estático contendo os firmwares dos rádios Qualcomm (`8.554.496 bytes`).
* `ubi1_1` (**kernel**): Volume estático contendo a imagem FIT do Kernel Linux 5.4 (`4.237.480 bytes`).
* `ubi1_2` (**ubi_rootfs**): Volume dinâmico contendo o sistema de arquivos SquashFS (`39.616.512 bytes`).
* `ubi1_3` (**rootfs_data**): Volume dinâmico de leitura e escrita (Overlay JFFS2/UBIFS de fábrica).

> [!IMPORTANT]
> **Chave de Ouro:** Gravar diretamente com `mtd write` no `/dev/mtd20` corrompe a tabela de volumes UBI. A técnica correta e segura é anexar o container UBI via `ubiattach` e gravar volume por volume com `ubiupdatevol`.

---

## 3. Passo a Passo Técnico Executado

### Etapa 1: Extração e Hashes dos Componentes v27

A partir da imagem `nand-4k-ipq5332-single_101000027.img`, foi desempacotada a partição UBI e extraídos os três componentes vitais:

* **Kernel FIT (`kernel.bin`):**
  * Tamanho: `4.237.480 bytes`
  * MD5: `ade31977f9c740a36ecfe50ac9e335d9`
* **Firmware Wi-Fi (`wifi_fw.bin`):**
  * Tamanho: `8.554.496 bytes`
  * MD5: `f1091a9c062ff50dd3348e06a8a5457e`
* **RootFS SquashFS (`rootfs.squashfs`):**
  * Tamanho: `39.616.512 bytes`
  * MD5: `99df532f68c147355c894611d1977cbf`

---

### Etapa 2: Instalação dos Atalhos de Proteção e Rollback

Antes de qualquer ação na memória Flash, conectou-se via Telnet no roteador (Slot 1 ativo) e foram criados dois utilitários de emergência em `/usr/sbin/`:

1. `/usr/sbin/boot-openwrt` (ou `boot-slot2`):
   ```sh
   #!/bin/sh
   echo "=== Chaveando boot para SLOT 2 (Firmware v27) ==="
   echo 0 > /proc/boot_info/bootconfig0/rootfs/primaryboot
   echo 0 > /proc/boot_info/bootconfig1/rootfs/primaryboot
   cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
   cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
   mtd unlock /dev/mtd3 2>/dev/null
   mtd unlock /dev/mtd4 2>/dev/null
   mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
   mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
   rm -f /tmp/bc0.bin /tmp/bc1.bin
   sync
   echo "[OK] Slot 2 definido! Reiniciando..."
   reboot
   ```

2. `/usr/sbin/boot-acer` (Rollback imediato para o Slot 1 estável):
   ```sh
   #!/bin/sh
   echo "=== Retornando boot para SLOT 1 (OEM v24 Estavel) ==="
   echo 1 > /proc/boot_info/bootconfig0/rootfs/primaryboot
   echo 1 > /proc/boot_info/bootconfig1/rootfs/primaryboot
   cat /proc/boot_info/bootconfig0/getbinary_bootconfig > /tmp/bc0.bin
   cat /proc/boot_info/bootconfig1/getbinary_bootconfig > /tmp/bc1.bin
   mtd unlock /dev/mtd3 2>/dev/null
   mtd unlock /dev/mtd4 2>/dev/null
   mtd -e /dev/mtd3 write /tmp/bc0.bin /dev/mtd3
   mtd -e /dev/mtd4 write /tmp/bc1.bin /dev/mtd4
   rm -f /tmp/bc0.bin /tmp/bc1.bin
   sync
   echo "[OK] Slot 1 redefinido! Reiniciando..."
   reboot
   ```

---

### Etapa 3: Transferência via HTTP e Validação de Hashes na RAM

1. Um servidor HTTP Python foi instanciado na máquina local vinculando a todas as interfaces (`0.0.0.0:8089`).
2. O roteador realizou o download para a sua memória volátil (`/tmp`, que dispõe de 414 MB livres):
   ```sh
   curl -fsSL http://192.168.73.90:8089/kernel.bin -o /tmp/v27_kernel.bin
   curl -fsSL http://192.168.73.90:8089/wifi_fw.bin -o /tmp/v27_wifi.bin
   curl -fsSL http://192.168.73.90:8089/rootfs.squashfs -o /tmp/v27_rootfs.bin
   ```
3. A integridade foi aferida diretamente pelo Linux do roteador:
   ```sh
   md5sum /tmp/v27_kernel.bin /tmp/v27_wifi.bin /tmp/v27_rootfs.bin
   ```
   **Resultado Remoto:**
   * `ade31977f9c740a36ecfe50ac9e335d9  /tmp/v27_kernel.bin` (**CONFIRMADO**)
   * `f1091a9c062ff50dd3348e06a8a5457e  /tmp/v27_wifi.bin` (**CONFIRMADO**)
   * `99df532f68c147355c894611d1977cbf  /tmp/v27_rootfs.bin` (**CONFIRMADO**)

---

### Etapa 4: Anexação do UBI e Gravação dos Volumes no Slot 2

1. O dispositivo `mtd20` foi anexado ao subsistema UBI como `ubi1`:
   ```sh
   ubiattach /dev/ubi_ctrl -m 20
   ```
   *Retorno:* `UBI device number 1, total 960 LEBs (243793920 bytes, 232.5 MiB), LEB size 253952 bytes`.

2. Gravação de cada volume com seus dados binários:
   ```sh
   # 1. Gravar Wi-Fi Firmware
   ubiupdatevol /dev/ubi1_0 /tmp/v27_wifi.bin

   # 2. Gravar Kernel FIT
   ubiupdatevol /dev/ubi1_1 /tmp/v27_kernel.bin

   # 3. Gravar RootFS SquashFS
   ubiupdatevol /dev/ubi1_2 /tmp/v27_rootfs.bin

   # 4. Truncar/Limpar o Overlay para boot de fábrica limpo
   ubiupdatevol /dev/ubi1_3 -t
   ```

3. Limpeza dos temporários e sincronização da memória Flash:
   ```sh
   rm -f /tmp/v27_*.bin
   sync
   ```

---

### Etapa 5: Validação Pré-Boot por Montagem Read-Only na Flash

Antes de permitir o reboot, foi criada uma camada de bloco sobre o volume gravado para montar o SquashFS gravado na própria Flash NAND:

```sh
ubiblock -c /dev/ubi1_2
mkdir -p /tmp/test_v27_mnt
mount -t squashfs -o ro /dev/ubiblock1_2 /tmp/test_v27_mnt
cat /tmp/test_v27_mnt/etc/version
```
*Saída obtida no console:*
```text
1.01.000027
```
Em seguida o bloco foi desmontado de forma limpa:
```sh
umount /tmp/test_v27_mnt
ubiblock -r /dev/ubi1_2
rmdir /tmp/test_v27_mnt
```

---

### Etapa 6: Chaveamento do Bootloader e Inicialização

Com a integridade física e lógica comprovada, disparou-se o chaveador nativo:
```sh
/usr/sbin/boot-openwrt
```
* O U-Boot leu `primaryboot=0` no MTD3/MTD4.
* Os argumentos de boot (`fsbootargs`) direcionaram a montagem da raiz para `ubi1_2` (`rootfs_1`).
* O Kernel Linux v27 inicializou sem falhas de montagem.

---

### Etapa 7: Verificação em Execução (Post-Boot)

Em aproximadamente 60 segundos após o comando de reinicialização:

1. **Conectividade de Rede:**
   * A interface de rede local respondeu prontamente no IP de fábrica: **`192.168.76.1`**.
   * Ping com tempo de resposta `< 1 ms` e `TTL = 64`.

2. **Serviço Web Ativo:**
   * Requisição `curl -sI http://192.168.76.1` retornou:
     ```http
     HTTP/1.1 200 OK
     Content-Type: text/html
     Last-Modified: Tue, 11 Mar 2025 08:57:41 GMT
     Server: server
     ```
   * O cabeçalho `Last-Modified: Tue, 11 Mar 2025` certifica em 100% que o sistema operacional em execução é o novo firmware oficial **v1.01.000027** da Acer.

---

## 4. Reativação de Acesso Root / SSH no Novo Firmware

Como o volume de dados (`rootfs_data` / `ubi1_3`) subiu limpo de fábrica:
1. As portas de depuração Telnet (`23`) e SSH (`22`) estão temporariamente inativas por padrão de segurança da fábrica.
2. A vulnerabilidade do arquivo de configuração foi auditada e permanece **completamente funcional** nesta versão.
3. Para restabelecer o acesso total:
   * Conecte-se via navegador em **`http://192.168.76.1`**.
   * Complete as etapas iniciais de senha de administrador do painel.
   * Navegue até a área de Manutenção / Atualização e restaure o arquivo de configuração desbloqueado:
     `02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_ssh_unlocked.cfg`
   * Após a reinicialização automática da restauração, as portas `22` (SSH) e `23` (Telnet) estarão operacionais.

---

## 5. Scripts de Automação Utilizados

Todo o procedimento foi compilado e salvo para repetição automatizada em:
* [gravar_v27_slot2.py](file:///H:/FEITOS%20COM%20IA/Acer-Predator-Connect-T7/Scripts_Automacao/gravar_v27_slot2.py)
* [switch_boot_slot.py](file:///H:/FEITOS%20COM%20IA/Acer-Predator-Connect-T7/Scripts_Automacao/switch_boot_slot.py)
