#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
OPENWRT FORUM AUTO-POSTER - 100% AUTOMATIZADO
Publica automaticamente no forum.openwrt.org aproveitando sua sessão ativa
do Firefox (usuário despensativo), sem você ter que copiar ou colar nada.
=============================================================================
"""

import os
import sys
import io
import glob
import shutil
import sqlite3
import tempfile
import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

FORUM_URL = "https://forum.openwrt.org"

TITULO_OPENWRT = "Reverse-Engineered Acer FOTA & Stock Firmware Extractor — Predator Connect T7 (IPQ5332) & W6x (MT7986)"
# Categoria 8 = "For Developers" (devel)
CATEGORIA_ID = 8 

CONTEUDO_OPENWRT = """Hey everyone,

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

**Prerequisites:** Python 3.8+ and `pip`.

```bash
# Clone the repository
git clone https://github.com/Despensativo/acer-predator-fota-extractor.git
cd acer-predator-fota-extractor

# Install dependencies (requests, pycryptodome)
pip install -r requirements.txt

# Run the interactive wizard
python acer_fota_extractor.py
```

**Single-line CLI Batch Download Example:**
```bash
python acer_fota_extractor.py --model "Acer Predator Connect T7" --version "1.00.000007" --download
```

---

### 6. Repository & Collaboration

The project is released under the MIT License on GitHub:  
👉 **https://github.com/Despensativo/acer-predator-fota-extractor**

If you have other Acer routers (e.g., Predator Connect W6, X5, or generic Acer gateways), feel free to run the tool with your model and serial number from the sticker, open issues, or submit PRs with newly discovered version strings to expand the matrix!
"""

def extrair_cookies_firefox():
    appdata = os.environ.get('APPDATA', '')
    profiles = glob.glob(os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles', '*'))
    
    cookies = {}
    for prof in profiles:
        src = os.path.join(prof, 'cookies.sqlite')
        if not os.path.exists(src):
            continue
        try:
            tmp = os.path.join(tempfile.gettempdir(), f"ff_openwrt_{os.path.basename(prof)}.sqlite")
            shutil.copy2(src, tmp)
            conn = sqlite3.connect(tmp)
            c = conn.cursor()
            c.execute("SELECT name, value FROM moz_cookies WHERE host LIKE '%openwrt.org%'")
            for name, val in c.fetchall():
                cookies[name] = val
            conn.close()
            os.remove(tmp)
            if '_t' in cookies:
                return cookies
        except Exception:
            continue
    return cookies

def obter_usuario_e_csrf(session):
    print("[*] Verificando sessão no forum.openwrt.org...")
    r = session.get(f"{FORUM_URL}/session/current.json")
    if r.status_code != 200:
        return None, None
    user_data = r.json().get("current_user", {})
    username = user_data.get("username")
    
    r_csrf = session.get(f"{FORUM_URL}/session/csrf.json")
    csrf = r_csrf.json().get("csrf") if r_csrf.status_code == 200 else None
    
    return username, csrf

def publicar_topico(session, csrf, titulo=TITULO_OPENWRT, corpo=CONTEUDO_OPENWRT, categoria=CATEGORIA_ID):
    print(f"[*] Publicando tópico na categoria {categoria} ('For Developers')...")
    url = f"{FORUM_URL}/posts.json"
    headers = {
        "X-CSRF-Token": csrf,
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    payload = {
        "title": titulo,
        "raw": corpo,
        "category": categoria
    }
    res = session.post(url, json=payload, headers=headers)
    if res.status_code == 200:
        data = res.json()
        topic_slug = data.get("topic_slug")
        topic_id = data.get("topic_id")
        link = f"{FORUM_URL}/t/{topic_slug}/{topic_id}"
        print("\n" + "="*65)
        print("🎉 SUCESSO ABSOLUTO! Tópico publicado no Fórum OpenWrt!")
        print(f"🔗 Link direto: {link}")
        print("="*65 + "\n")
        return link
    else:
        print(f"[-] Erro na publicação (Status {res.status_code}): {res.text}")
        return None

def atualizar_topico(session, csrf, post_id=1342854, titulo=TITULO_OPENWRT, corpo=CONTEUDO_OPENWRT):
    print(f"[*] Atualizando tópico/post ID {post_id} no Fórum OpenWrt...")
    headers = {
        "X-CSRF-Token": csrf,
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    # Atualiza o corpo do post
    res = session.put(f"{FORUM_URL}/posts/{post_id}.json", json={"post": {"raw": corpo}}, headers=headers)
    if res.status_code == 200:
        print("[+] Conteúdo detalhado atualizado com sucesso!")
    else:
        print(f"[-] Erro ao atualizar conteúdo (Status {res.status_code}): {res.text}")
        
    # Atualiza o título do tópico (tópico 254115)
    res_title = session.put(f"{FORUM_URL}/t/254115.json", json={"title": titulo}, headers=headers)
    if res_title.status_code == 200:
        print("[+] Título do tópico atualizado com sucesso!")
        print("\n" + "="*65)
        print("🎉 Tópico OpenWrt atualizado com sucesso!")
        print(f"🔗 Link: https://forum.openwrt.org/t/254115")
        print("="*65 + "\n")
        return True
    else:
        print(f"[-] Erro ao atualizar título (Status {res_title.status_code}): {res_title.text}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Publicador automático no Fórum OpenWrt")
    parser.add_argument("--yes", "-y", action="store_true", help="Publica direto sem pedir confirmação")
    parser.add_argument("--update", "-u", action="store_true", help="Atualiza o tópico existente com o novo texto completo")
    args = parser.parse_args()

    print("="*65)
    print("🚀 PUBLICADOR 100% AUTOMÁTICO - FÓRUM OPENWRT")
    print("="*65)
    
    cookies = extrair_cookies_firefox()
    if not cookies or '_t' not in cookies:
        print("[-] Não foi possível encontrar a sessão ativa do OpenWrt no Firefox.")
        sys.exit(1)
        
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    })
    session.cookies.update(cookies)
    
    username, csrf = obter_usuario_e_csrf(session)
    if not username or not csrf:
        print("[-] Sessão expirada ou não autenticado no fórum.")
        sys.exit(1)
        
    print(f"[+] Autenticado com sucesso como: @{username}")
    print(f"[+] Token CSRF obtido com sucesso.")
    
    if args.update:
        atualizar_topico(session, csrf)
        return

    if args.yes:
        publicar_topico(session, csrf)
    else:
        confirm = input(f"\nDeseja publicar o tópico agora como @{username}? [S/n]: ").strip().lower()
        if confirm in ['', 's', 'sim', 'y', 'yes']:
            publicar_topico(session, csrf)
        else:
            print("[*] Publicação cancelada pelo usuário.")

if __name__ == "__main__":
    main()
