# 🛠️ ÁREA DEV: Chaveadores de Slot de Boot (.BIN)

> ⚠️ **AVISO EXCLUSIVO PARA DESENVOLVEDORES:**  
> Estes arquivos são destinados exclusivamente a desenvolvedores e usuários avançados que necessitam alternar manualmente as partições de boot para testes, depuração ou análise de ROMs.  
> **Usuários comuns não precisam utilizar estes arquivos.**

---

## 📦 Arquivos Binários de Chaveamento (512 KB):

* **`chaveador_slot1_acer_oem.bin`** (ou `bootconfig_slot1_acer_oem.bin`):  
  Força a inicialização no **Slot 1 (`rootfs` / `mtd21`)**, que contém o Firmware Original OEM da Acer de fábrica.
* **`chaveador_slot2_openwrt.bin`** (ou `bootconfig_slot2_openwrt.bin`):  
  Força a inicialização no **Slot 2 (`rootfs_1` / `mtd20`)**, que contém a ROM OpenWrt Customizada com LuCI na porta 80 e Wi-Fi 7.

---

## 🚀 Como Fazer a Alternância pelo U-Boot Web Failsafe (`http://192.168.1.1`):

1. Desligue o roteador da tomada.
2. Ligue mantendo o botão físico **WPS pressionado por 8 a 10 segundos** até o LED piscar em ritmo de recovery.
3. No seu computador (conectado via cabo de rede na LAN), defina o IP estático:  
   * **IP:** `192.168.1.50` | **Máscara:** `255.255.255.0` | **Gateway:** `192.168.1.1`
4. Abra o navegador em modo anônimo e acesse `http://192.168.1.1`.
5. No campo de upload de firmware da tela de emergência:
   * Selecione o arquivo `.bin` desejado:  
     👉 **`chaveador_slot1_acer_oem.bin`** (para iniciar no Slot 1 OEM de fábrica)  
     👉 **`chaveador_slot2_openwrt.bin`** (para iniciar no Slot 2 OpenWrt)
6. Clique em **Upload / Upgrade** e aguarde o roteador reiniciar automaticamente no slot escolhido.

---

## 💡 Dica para Sistema Desbloqueado (SSH / Telnet):

Se o roteador já estiver desbloqueado e você tiver acesso via terminal (SSH na porta 22 ou Telnet na porta 23), **não é necessário fazer upload de arquivos nem digitar comandos complexos de partição**. O sistema já possui comandos nativos integrados:

* **Para alternar para o Slot 1 (OEM de Fábrica):**
  ```sh
  /usr/sbin/boot-acer
  ```
* **Para alternar para o Slot 2 (OpenWrt Custom):**
  ```sh
  /usr/sbin/boot-openwrt
  ```
*O comando grava automaticamente o bootconfig na flash e reinicia o roteador no slot desejado.*
