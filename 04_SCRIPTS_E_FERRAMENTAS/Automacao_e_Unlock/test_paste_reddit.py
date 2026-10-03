import sqlite3
import shutil
import os
import tempfile
from playwright.sync_api import sync_playwright

src = r'C:\Users\User\AppData\Roaming\Mozilla\Firefox\Profiles\bn45djuk.default-release\cookies.sqlite'
tmp = os.path.join(tempfile.gettempdir(), 'ff_reddit_test.sqlite')
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

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        viewport={'width': 1280, 'height': 800},
        permissions=['clipboard-read', 'clipboard-write']
    )
    context.add_cookies(playwright_cookies)
    page = context.new_page()
    page.goto('https://www.reddit.com/r/openwrt/submit', wait_until='domcontentloaded')
    page.wait_for_timeout(4000)
    
    title = "Reverse-Engineered Acer FOTA & Stock Firmware Extractor — Predator Connect T7 (IPQ5332) & W6x (MT7986)"
    page.fill('textarea[name="title"]', title)
    
    sample_md = """### 1. Reverse-Engineering Acer FOTA

* **Timestamp:** `GET https://connect-ota.acervcon.com/now`
* **Encryption:** AES-256-CBC

Check repo: https://github.com/Despensativo/acer-predator-fota-extractor"""

    body_div = page.locator('div[role="textbox"]').nth(1)
    body_div.click()
    
    # Testa colar via clipboard
    page.evaluate("text => navigator.clipboard.writeText(text)", sample_md)
    page.keyboard.press('Control+v')
    page.wait_for_timeout(2000)
    
    page.screenshot(path="reddit_paste_test.png")
    browser.close()
