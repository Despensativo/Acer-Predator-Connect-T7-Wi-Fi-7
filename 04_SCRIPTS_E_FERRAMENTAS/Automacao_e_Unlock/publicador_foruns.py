#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
 Assistente de Publicação nos Fóruns e Comunidades (Automação Assistida)
========================================================================================
 Este script abre a URL exata de criação do tópico no seu navegador e copia
 o Título e o Conteúdo Markdown automaticamente para a sua Área de Transferência (Clipboard).
========================================================================================
"""

import os
import sys
import webbrowser
import subprocess

CANAL_POSTS = {
    "1": {
        "nome": "Fórum Oficial OpenWrt (forum.openwrt.org)",
        "url": "https://forum.openwrt.org/t/254115",
        "titulo": "Reverse-Engineered Acer FOTA & Stock Firmware Extractor — Predator Connect T7 (IPQ5332) & W6x (MT7986)",
        "tags": "acer, firmware, reverse-engineering, ipq53xx, mediatek",
        "conteudo": """Hey everyone,

While working on the OpenWrt port for the **Acer Predator Connect T7** (Qualcomm IPQ5332 Wi-Fi 7 BE11000) and inspecting the **Acer Predator Connect W6x** (MediaTek MT7986 Filogic 830), I hit a major roadblock common to modern Acer routers:

**Acer does not provide offline factory firmware recovery files (.bin/.img) on their public support websites.**

If you brick a unit, need to revert back to stock, or need pristine factory squashfs rootfs, device-tree blobs (DTBs), kernel configs, or proprietary wireless blobs/drivers for OpenWrt porting, you are usually completely stuck.

To solve this, I reverse-engineered the native `/usr/bin/fota` daemon from the router's stock squashfs filesystem and extracted the complete cloud update handshake. I then built a 100% standalone, open-source Python tool that queries Acer's update cloud and pulls official stock firmware images straight from their pre-signed AWS S3 buckets.

Below is an in-depth breakdown of how the protocol was reversed, how the tool operates, and how you can use it.

---

### 1. Reverse-Engineering the Native Acer FOTA Protocol (`/usr/bin/fota`)

Inspecting the disassembled `/usr/bin/fota` binary revealed the entire cloud communication workflow:

1. **Official Server Time Synchronization:**
   The router contacts `GET https://connect-ota.acervcon.com/now` to obtain the official server Unix timestamp.
2. **Encrypted Authentication Header (`auth-token`):**
   Every query to the OTA backend must be signed with an `auth-token` HTTP header:
   * **Algorithm:** AES-256 in CBC mode with standard PKCS#7 padding.
   * **Payload:** Serialized JSON string containing `{"project": "<project_name>", "sn": "<serial_number>", "time": <unix_timestamp>}`.
   * **Key & IV:** Extracted directly from the compiled binary.
3. **Transition-Matrix Query Engine (`POST https://connect-ota.acervcon.com/fota/query`):**
   * The Acer OTA backend does **not** support wildcards (`*`) or bulk listing.
   * Instead, it operates on a strict upgrade transition graph: you must supply a valid known base version (e.g., `1.00.000007`).
   * The server validates the transition and responds with:
     * Target firmware version string.
     * Total binary file size in bytes.
     * Official MD5 checksum.
     * A temporary, pre-signed **Amazon AWS S3** download URL (valid for 300 seconds).
     * Official internal developer changelogs stored in Acer's database.

---

### 2. What the Extractor Tool (`acer_fota_extractor.py`) Does

Rather than requiring you to have a physical router connected or write scripts from scratch, the tool is a completely self-contained Python 3 application:

* **100% Standalone & Cross-Platform:** Runs on any PC running Linux, macOS, or Windows. Zero physical connection to the router required.
* **Dual Operating Modes:**
  1. **Interactive Guided Wizard:** An intuitive console questionnaire that prompts for Model (T7, W6x, X7 or Generic), Region, Serial Number, and scanning preferences.
  2. **Headless CLI / Scripting Mode:** Fully automatable with command-line flags (`--model`, `--version`, `--sn`, `--region`, `--download`, `--all`, `--output`).
* **Automated AWS S3 Streaming:** Downloads multi-megabyte images in chunks with real-time transfer progress.
* **Integrity Validation (MD5):** Automatically computes and checks MD5 hashes on the fly upon download completion against Acer's cloud manifest.
* **Smart Storage Layout:** Creates clean, model-specific subdirectories automatically (`./downloads/<Model_Name>/...`).
* **Release Notes Capture:** Displays the actual engineering release notes found in Acer's cloud (e.g., discovering that W6x version `1.01.000015` introduced ISP VLAN ID support).

---

### 3. Structure of Downloaded Firmware Files (FIT Images)

The downloaded files are standard U-Boot Flattened Image Trees (FIT format / `uImage.FIT`). They can be examined and disassembled using standard tooling:

* `kernel@1`: ARM64 Linux Kernel.
* `fdt@1`: Flattened Device Tree (`.dtb`) containing hardware pinmux, memory mappings, and Ethernet switch layout.
* `rootfs@1`: Compressed SquashFS partition containing the OEM system, configuration scripts, and vendor wireless drivers.

You can inspect the components directly with `dumpimage` or `binwalk`:
```bash
# Extract kernel
dumpimage -T flat_dt -p 0 -o kernel.bin <firmware_file>.bin

# Extract device-tree blob
dumpimage -T flat_dt -p 1 -o devicetree.dtb <firmware_file>.bin

# Or extract all partitions using binwalk
binwalk -e <firmware_file>.bin
```

---

### 4. Verified Models & Firmware Release Matrix

| Model | Chipset | Region | Tested Base | Latest Extracted | Status / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Acer Predator Connect T7** | Qualcomm IPQ5332 (Wi-Fi 7 BE11000) | BR / Global | `1.00.000007` | `1.00.000010` | Verified & Downloaded |
| **Acer Predator Connect T7** | Qualcomm IPQ5332 (Wi-Fi 7 BE11000) | US Region | `1.00.000003` | `1.00.000010` | Verified & Downloaded |
| **Acer Predator Connect W6x** | MediaTek MT7986 (Filogic 830 Wi-Fi 6) | Global | `1.00.000008` | `1.01.000015` | Verified (Added ISP VLAN ID support) |
| **Acer Predator Connect X7** | Qualcomm IPQ5332 + 5G CPE | Global | Factory base | Cloud active | Handshake validated |
| **Generic Acer Routers** | Any | Any | Sticker info | Cloud query | Input model code & serial |

---

### 5. How to Install & Run

```bash
git clone https://github.com/Despensativo/acer-predator-fota-extractor.git
cd acer-predator-fota-extractor
pip install -r requirements.txt
python acer_fota_extractor.py
```

---

### 6. Repository & Collaboration

The project is released under the MIT License on GitHub:  
👉 **https://github.com/Despensativo/acer-predator-fota-extractor**"""
    },
    "2": {
        "nome": "TabNews (tabnews.com.br)",
        "url": "https://www.tabnews.com.br/publicar",
        "titulo": "Reverse-Engineered Acer FOTA & Stock Firmware Extractor: Como extraí firmwares oficiais de fábrica direto da AWS S3",
        "tags": "engenharia-reversa, openwrt, firmware, hardware, python",
        "conteudo": """Fala pessoal do TabNews!

Recentemente comecei a trabalhar no porte do **OpenWrt** para o roteador **Acer Predator Connect T7** (um dos primeiros roteadores Wi-Fi 7 BE11000 com o SoC Qualcomm IPQ5332 lançados no mercado nacional). Durante o projeto, também analisei o seu antecessor, o **Predator Connect W6x** (baseado no chip MediaTek MT7986 Filogic 830).

Rapidamente esbarrei em um problema crônico e bem frustrante da Acer: **a fabricante não disponibiliza arquivos de firmware (.bin / .img) para download no seu site de suporte**.

Se um usuário brickar o aparelho tentando instalar um sistema customizado, precisar restaurar o roteador para o padrão de fábrica, ou se desenvolvedores precisarem extrair as partições SquashFS, arquivos Device Tree (DTB) e blobs binários de Wi-Fi, eles ficam completamente no escuro.

Para resolver isso, decidi investigar como o roteador se atualizava sozinho. Fiz a engenharia reversa no cliente de atualização OTA (`/usr/bin/fota`) presente na partição SquashFS e mapeei todo o ecossistema na nuvem da Acer.

O resultado foi a criação de uma ferramenta em Python 100% autônoma, de código aberto, chamada **`acer_fota_extractor.py`**, que permite consultar a nuvem da Acer e baixar qualquer ROM oficial diretamente de buckets pré-assinados da **Amazon AWS S3**.

Abaixo compartilho todos os detalhes técnicos da descoberta, como o protocolo funciona e o que o script faz por baixo dos panos.

---

### 1. Como funciona a Nuvem de Atualização da Acer (Engenharia Reversa)

Ao decompilar o binário `/usr/bin/fota` e analisar as chamadas de rede e rotinas criptográficas, o fluxo revelou-se bastante metódico:

1. **Sincronização de Relógio do Servidor:**  
   O binário faz um `GET https://connect-ota.acervcon.com/now` para obter o timestamp Unix oficial em segundos. Qualquer descompasso no relógio invalida a requisição.
   
2. **Criptografia do Token de Autorização (`auth-token`):**  
   Todas as requisições para a API exigem um header HTTP chamado `auth-token`.  
   * **Algoritmo:** AES-256 no modo CBC com preenchimento (padding) PKCS#7.
   * **Payload interno:** Um JSON serializado contendo `{"project": "<codigo_modelo>", "sn": "<numero_serie>", "time": <timestamp_unix>}`.
   * **Chaves:** A chave simétrica de 256 bits e o vetor de inicialização (IV) de 16 bytes estavam compilados diretamente no binário.

3. **Matriz Estrita de Transição de Versões (`POST https://connect-ota.acervcon.com/fota/query`):**  
   O backend da Acer **não aceita consultas abertas, nem wildcards (`*`) ou listagens globais**.  
   Ele funciona como um autômato finito / grafo dirigido de atualizações: você precisa enviar a versão exata de origem que está rodando no roteador (por exemplo, `1.00.000007`).  
   O servidor consulta sua tabela de transições e devolve:
   * A nova versão de destino disponível (ex: `1.00.000010`).
   * Tamanho exato em bytes.
   * Hash MD5 oficial gerado na compilação da Acer.
   * **Uma URL pré-assinada da Amazon AWS S3 com validade temporária de 300 segundos**.
   * Notas de versão e changelogs reais registrados pelos engenheiros da Acer.

---

### 2. O que o Script (`acer_fota_extractor.py`) faz na prática

Em vez de exigir que a pessoa tenha o roteador conectado na rede ou configure interceptadores de proxy, o script é uma ferramenta CLI completamente autônoma desenvolvida em Python 3:

* **100% Standalone:** Roda em qualquer máquina com Windows, Linux ou macOS. Não precisa estar conectado ao roteador e nem mesmo ter o roteador em mãos para baixar as ROMs.
* **Dois Modos de Operação:**
  1. **Assistente Interativo no Terminal:** Apresenta um menu guiado em ASCII onde você escolhe o modelo (Predator T7, W6x, X7 ou Qualquer Modelo Customizado), seleciona a região e o serial.
  2. **Modo CLI / Automação:** Permite passar flags diretas (`--model`, `--version`, `--sn`, `--download`, `--all`) para ser integrado em pipelines ou scripts em lote.
* **Download em Chunks com Barra de Progresso:** Conecta no link pré-assinado da AWS S3 e baixa arquivos de dezenas de megabytes com tratamento de interrupção e progresso em tempo real.
* **Verificação Automática de Integridade (MD5):** Ao término do download, o script calcula o hash MD5 do arquivo baixado e compara byte a byte com o hash fornecido pela Acer, garantindo que o arquivo não venha corrompido.
* **Organização Inteligente de Pastas:** Cria automaticamente a estrutura de diretórios organizada por modelo e região: `./downloads/<Nome_Do_Modelo>/...`.
* **Extração de Changelogs Ocultos:** Revela notas de versão oficiais que muitas vezes não aparecem nas interfaces web (por exemplo, descobrimos que a versão `1.01.000015` do W6x implementou suporte a VLAN ID de operadoras).

---

### 3. Estrutura das ROMs da Acer (FIT Images)

Os arquivos `.bin` baixados são imagens no padrão **U-Boot FIT (Flattened Image Tree)**. Dentro de cada imagem encontramos:

* `kernel@1`: O kernel Linux oficial ARM64 compilado pela fabricante.
* `fdt@1`: O Device Tree Blob (`.dtb`) compilado, contendo todo o mapeamento de pinos, portas Ethernet e partições de memória.
* `rootfs@1`: Sistema de arquivos SquashFS original com scripts de inicialização e drivers proprietários de Wi-Fi 7 e Wi-Fi 6.

Para quem quiser inspecionar ou extrair componentes da imagem:
```bash
# Extrair o kernel
dumpimage -T flat_dt -p 0 -o kernel.bin firmware_oficial.bin

# Extrair a árvore de dispositivos (Device Tree)
dumpimage -T flat_dt -p 1 -o devicetree.dtb firmware_oficial.bin

# Ou extrair todo o sistema com binwalk
binwalk -e firmware_oficial.bin
```

---

### 4. Modelos e Versões já Mapeados e Testados

| Modelo | Chipset | Região | Versão Base | Versão Baixada | Status / Observações |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Acer Predator Connect T7** | Qualcomm IPQ5332 (Wi-Fi 7 BE11000) | BR / Global | `1.00.000007` | `1.00.000010` | Validado e baixado via AWS |
| **Acer Predator Connect T7** | Qualcomm IPQ5332 (Wi-Fi 7 BE11000) | Região US | `1.00.000003` | `1.00.000010` | Validado e baixado via AWS |
| **Acer Predator Connect W6x** | MediaTek MT7986 (Filogic 830 Wi-Fi 6) | Global | `1.00.000008` | `1.01.000015` | Validado (adicionou VLAN ID) |
| **Acer Predator Connect X7** | Qualcomm IPQ5332 + 5G CPE | Global | Base de fábrica | Ativo na nuvem | Handshake validado |
| **Outros Modelos Acer** | Qualquer modelo | Qualquer região | Info da etiqueta | Consulta na nuvem | Suporte via código e serial |

---

### 5. Como Executar no seu Computador

```bash
git clone https://github.com/Despensativo/acer-predator-fota-extractor.git
cd acer-predator-fota-extractor
pip install -r requirements.txt
python acer_fota_extractor.py
```

---

### 6. Repositório Aberto e Contribuições

O projeto está disponível sob a licença MIT no GitHub:  
👉 **https://github.com/Despensativo/acer-predator-fota-extractor**"""
    },
    "3": {
        "nome": "Reddit r/openwrt",
        "url": "https://www.reddit.com/r/openwrt/submit",
        "titulo": "Reverse-Engineered Acer FOTA & Stock Firmware Extractor — Predator Connect T7 (IPQ5332), W6x (MT7986) & Generic Acer Routers",
        "tags": "Firmware, Hardware, Research",
        "conteudo": """Hey everyone,

Unlike brands that provide recovery firmware `.bin` files on their support websites, Acer only distributes updates through an internal cloud FOTA daemon. If you brick an Acer router or need stock blobs, DTBs, or partitions for OpenWrt porting, you are usually out of luck.

I reverse-engineered the native `/usr/bin/fota` binary, extracted the AES-256-CBC authentication keys, and built an open-source standalone Python tool that downloads official factory firmware directly from Acer's AWS S3 buckets:

🔗 **GitHub:** https://github.com/Despensativo/acer-predator-fota-extractor

### How the Protocol Works:
1. **Server Time Sync:** Queries `GET https://connect-ota.acervcon.com/now`.
2. **Encrypted Handshake:** Signs with `auth-token` using AES-256-CBC (PKCS#7) with embedded keys.
3. **Transition-Matrix Query:** Server enforces an upgrade graph (requires exact source versions) and returns pre-signed AWS S3 links (300s TTL) with official MD5 checksums.

### What the Extractor Tool Does:
* **100% Standalone:** Runs on PC, Linux, or macOS. No physical router connection needed.
* **Dual Interface:** Interactive guided CLI wizard + headless scripting flags (`--model`, `--version`, `--download`, `--all`).
* **Automated MD5 Verification:** Automatically verifies image integrity after streaming from S3.
* **FIT Image Structure:** Images contain ARM64 Linux Kernel, Device Tree Blob (`.dtb`), and SquashFS rootfs with vendor Wi-Fi 7/6 blobs.
* **Changelogs Captured:** Extracts official internal engineering release notes.

### Tested Models:
* **Acer Predator Connect T7** (Qualcomm IPQ5332 Wi-Fi 7 BE11000)
* **Acer Predator Connect W6x** (MediaTek MT7986 Filogic 830)
* **Acer Predator Connect X7** (Qualcomm IPQ5332 + 5G CPE)
* **Generic Acer Routers:** Supported by inputting model code & serial number from device sticker.

Hope this helps anyone working on OpenWrt support or looking for clean stock recovery images!"""
    },
    "4": {
        "nome": "Fórum Adrenaline (forum.adrenaline.com.br)",
        "url": "https://forum.adrenaline.com.br/forums/internet-redes.118/post-thread",
        "titulo": "Reverse-Engineered Acer FOTA & Stock Firmware Extractor: Como baixar e recuperar firmwares de fábrica (Predator T7, W6x)",
        "tags": "acer, predator, t7, w6x, firmware, redes",
        "conteudo": """Fala pessoal do Adrenaline!

Muitos membros aqui compraram recentemente os roteadores gamer da Acer (especialmente o **Predator Connect T7 Wi-Fi 7** e o **Predator Connect W6x**). 

Um grande problema desses aparelhos é que a Acer **não disponibiliza o arquivo de firmware de fábrica para download no site de suporte** — as atualizações só acontecem automaticamente pela nuvem. Quem quiser recuperar o aparelho, fazer downgrade ou estudar o sistema fica sem ter de onde baixar a ROM oficial.

Fiz uma engenharia reversa no serviço de atualização da Acer (`/usr/bin/fota`) e criei uma ferramenta gratuita e de código aberto para baixar todas as versões oficiais direto dos servidores da Acer:

🔗 **Repositório GitHub:** https://github.com/Despensativo/acer-predator-fota-extractor

### O que a ferramenta faz:
* **Não precisa de roteador conectado:** O script roda no seu Windows, Mac ou Linux e busca os arquivos originais nos servidores AWS S3 da Acer.
* **Fácil de usar:** Ao abrir, ele faz perguntas simples no terminal (qual o modelo, região e se quer baixar a última versão ou todas).
* **Verificação de Integridade:** Valida o MD5 de cada arquivo baixado contra a assinatura oficial da Acer para garantir que a imagem não está corrompida.
* **Changelogs Ocultos:** Mostra as notas de versão oficiais dos desenvolvedores da Acer (ex: na versão 1.01.000015 do W6x eles adicionaram suporte a VLAN ID de operadoras).
* **Estrutura das ROMs:** Os arquivos baixados são imagens U-Boot FIT contendo o Kernel ARM64, a Device Tree e a partição SquashFS com os drivers de fábrica.

Quem tiver o T7, W6x ou outros modelos (como W6 ou X5), dê uma olhada! É uma segurança excelente para quem quer ter a ROM original salva no PC para eventuais recuperações."""
    },
    "5": {
        "nome": "Hacker News (news.ycombinator.com)",
        "url": "https://news.ycombinator.com/submit",
        "titulo": "Reverse-Engineered Acer FOTA & Stock Firmware Extractor: Fetching factory router images straight from AWS S3",
        "tags": "",
        "conteudo": """https://github.com/Despensativo/acer-predator-fota-extractor

Acer does not distribute offline firmware recovery images for its modern Wi-Fi 7 (Qualcomm IPQ5332) and Wi-Fi 6 (MediaTek MT7986) routers. By reverse-engineering the AES-256-CBC authentication mechanism in `/usr/bin/fota`, this standalone tool queries Acer's update cloud and fetches pre-signed AWS S3 download URLs for stock factory FIT images."""
    }
}

def copy_to_clipboard(text):
    try:
        # Usa o comando do PowerShell para copiar no Windows
        cmd = f"Set-Clipboard -Value @'\n{text}\n'@"
        subprocess.run(["powershell", "-Command", cmd], check=True)
        return True
    except Exception:
        return False

def main():
    print("=" * 75)
    print("   ASSISTENTE DE PUBLICAÇÃO DE TÓPICOS NOS FÓRUNS E COMUNIDADES")
    print("=" * 75)
    print("\nEscolha qual fórum você deseja publicar agora:\n")
    for k, item in CANAL_POSTS.items():
        print(f"  [{k}] {item['nome']}")
    print("  [0] Sair")

    escolha = input("\nOpção [0-5]: ").strip()
    if escolha not in CANAL_POSTS:
        print("Saindo...")
        return

    post = CANAL_POSTS[escolha]
    print("\n" + "-" * 75)
    print(f"Canal Selecionado: {post['nome']}")
    print(f"Título: {post['titulo']}")
    if post['tags']:
        print(f"Tags:   {post['tags']}")
    print("-" * 75)

    print("\n[1] Copiar o CONTEÚDO (Corpo do texto) para a Área de Transferência")
    print("[2] Copiar o TÍTULO para a Área de Transferência")
    print("[3] Abrir a página do fórum no navegador e copiar o CONTEÚDO")
    
    sub = input("\nOpção [1-3] (Padrão: 3): ").strip()
    if not sub:
        sub = "3"

    if sub in ["1", "3"]:
        if copy_to_clipboard(post['conteudo']):
            print("\n[+] Conteúdo copiado com sucesso para o Clipboard (Ctrl+V)!")
        else:
            print("\n[!] Não foi possível copiar automaticamente para o Clipboard.")
    elif sub == "2":
        if copy_to_clipboard(post['titulo']):
            print("\n[+] Título copiado com sucesso para o Clipboard (Ctrl+V)!")

    if sub == "3":
        print(f"[+] Abrindo {post['url']} no navegador...")
        webbrowser.open(post['url'])

    print("\n" + "=" * 75)
    print("Pronto! Cole o conteúdo no campo de postagem com Ctrl+V.")
    print("=" * 75)

if __name__ == "__main__":
    main()
