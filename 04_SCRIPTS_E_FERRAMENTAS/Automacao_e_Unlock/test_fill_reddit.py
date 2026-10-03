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
        viewport={'width': 1280, 'height': 800}
    )
    context.add_cookies(playwright_cookies)
    page = context.new_page()
    page.goto('https://www.reddit.com/r/openwrt/submit', wait_until='domcontentloaded')
    page.wait_for_timeout(4000)
    
    # Preenche título
    title = "Reverse-Engineered Acer FOTA & Stock Firmware Extractor — Predator Connect T7 (IPQ5332) & W6x (MT7986)"
    page.fill('textarea[name="title"]', title)
    print("Título preenchido!")
    
    # Foca no corpo e insere texto
    body_div = page.locator('div[role="textbox"]').nth(1)
    body_div.click()
    page.keyboard.insert_text("This is a test post for Acer FOTA Extractor.")
    print("Corpo preenchido!")
    
    page.wait_for_timeout(2000)
    
    # Verifica o botão Postar
    post_btn = page.locator('button:has-text("Postar"), button:has-text("Post")').first
    is_disabled = post_btn.is_disabled()
    print(f"Botão Postar habilitado: {not is_disabled}")
    
    page.screenshot(path="reddit_filled_test.png")
    browser.close()
