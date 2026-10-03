#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
REDDIT AUTO-POSTER - 100% AUTOMATIZADO
Publica automaticamente no r/openwrt via Playwright usando a sessão ativa
do seu navegador, sem precisar clicar ou copiar/colar nada.
=============================================================================
"""

import sys
import io
import os
import sqlite3
import shutil
import tempfile
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SUBREDDIT = "openwrt"
TITULO_REDDIT = "Reverse-Engineered Acer FOTA & Stock Firmware Extractor — Predator Connect T7 (IPQ5332) & W6x (MT7986)"

CONTEUDO_REDDIT = """Hey everyone,

Unlike router vendors that provide standalone recovery firmware `.bin` files on their consumer support pages, **Acer does not provide offline factory firmware recovery files for their modern routers**. If you brick an Acer unit, need to revert back to stock, or need pristine factory squashfs rootfs, device-tree blobs (DTBs), kernel configs, or proprietary wireless blobs/drivers for OpenWrt porting, you are usually completely stuck.

To solve this while working on OpenWrt support for the **Acer Predator Connect T7** (Qualcomm IPQ5332 Wi-Fi 7 BE11000) and **Predator Connect W6x** (MediaTek MT7986 Filogic 830), I reverse-engineered the native `/usr/bin/fota` daemon from the router's stock squashfs rootfs and extracted the cloud update handshake.

I packaged this into a 100% standalone, open-source Python tool that queries Acer's update gateway and pulls official stock firmware images straight from their pre-signed AWS S3 buckets:

🔗 **GitHub Repository:** https://github.com/Despensativo/acer-predator-fota-extractor

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

Rather than requiring a physical router connected or setting up intercepting proxies, the tool is a completely self-contained Python 3 application:

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

def extrair_cookies_reddit():
    appdata = os.environ.get('APPDATA', '')
    src = os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles', 'bn45djuk.default-release', 'cookies.sqlite')
    if not os.path.exists(src):
        return []
    tmp = os.path.join(tempfile.gettempdir(), 'ff_reddit_pub.sqlite')
    shutil.copy2(src, tmp)
    conn = sqlite3.connect(tmp)
    c = conn.cursor()
    c.execute("SELECT host, name, value, path, expiry FROM moz_cookies WHERE host LIKE '%reddit.com%'")
    rows = c.fetchall()
    conn.close()
    os.remove(tmp)

    playwright_cookies = []
    for host, name, value, path, expiry in rows:
        cookie = {'name': name, 'value': value, 'domain': host, 'path': path or '/'}
        try:
            exp = float(expiry)
            cookie['expires'] = exp / 1000.0 if exp > 1e11 else exp
        except Exception:
            cookie['expires'] = -1
        playwright_cookies.append(cookie)
    return playwright_cookies

def publicar_reddit():
    print("="*65)
    print(f"🚀 PUBLICADOR AUTOMÁTICO - REDDIT (r/{SUBREDDIT})")
    print("="*65)
    
    cookies = extrair_cookies_reddit()
    if not cookies:
        print("[-] Não foi possível carregar os cookies do Reddit.")
        return None
        
    print(f"[+] {len(cookies)} cookies de autenticação carregados.")
    print(f"[*] Abrindo navegador para publicar em r/{SUBREDDIT}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
            permissions=['clipboard-read', 'clipboard-write']
        )
        context.add_cookies(cookies)
        page = context.new_page()
        
        url = f"https://www.reddit.com/r/{SUBREDDIT}/submit"
        page.goto(url, wait_until='domcontentloaded')
        page.wait_for_timeout(4000)
        
        print("[*] Injetando título...")
        page.fill('textarea[name="title"]', TITULO_REDDIT)
        page.wait_for_timeout(500)
        
        print("[*] Injetando corpo do artigo...")
        body_div = page.locator('div[role="textbox"]').nth(1)
        body_div.click()
        page.wait_for_timeout(500)
        
        # Insere o texto completo via clipboard no editor
        page.evaluate("text => navigator.clipboard.writeText(text)", CONTEUDO_REDDIT)
        page.keyboard.press('Control+v')
        page.wait_for_timeout(2000)
        
        post_btn = page.locator('button:has-text("Postar"), button:has-text("Post")').first
        if post_btn.is_disabled():
            print("[-] Botão Postar ainda está desabilitado. Tentando ajuste...")
            page.wait_for_timeout(2000)
            
        print("[*] Clicando no botão Postar...")
        post_btn.click()
        
        # Aguarda redirecionamento para o post criado
        print("[*] Aguardando confirmação do Reddit...")
        for _ in range(15):
            page.wait_for_timeout(1000)
            curr = page.url
            if "/comments/" in curr:
                print("\n" + "="*65)
                print("🎉 SUCESSO! Post publicado no Reddit r/openwrt!")
                print(f"🔗 Link direto: {curr}")
                print("="*65 + "\n")
                browser.close()
                return curr
                
        print(f"[*] Finalizado. URL atual: {page.url}")
        page.screenshot(path="reddit_final_status.png")
        browser.close()
        return page.url

if __name__ == "__main__":
    publicar_reddit()
