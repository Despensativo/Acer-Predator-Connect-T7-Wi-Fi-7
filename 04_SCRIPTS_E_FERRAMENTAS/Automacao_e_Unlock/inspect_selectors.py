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
    
    # Title
    inputs = page.query_selector_all('textarea, input[type="text"], faceplate-textarea-input')
    for i, el in enumerate(inputs):
        print(f"Input {i}: {el.evaluate('el => ({tag: el.tagName, name: el.name, placeholder: el.placeholder, text: el.innerText})')}")
        
    # Editable
    divs = page.query_selector_all('div[contenteditable="true"], [role="textbox"]')
    for i, el in enumerate(divs):
        print(f"Editable {i}: {el.evaluate('el => ({tag: el.tagName, role: el.getAttribute(\"role\"), ariaPlaceholder: el.getAttribute(\"aria-placeholder\"), class: el.className})')}")
        
    # Buttons
    btns = page.query_selector_all('button')
    for b in btns:
        t = b.inner_text().strip()
        if any(w in t.lower() for w in ['post', 'postar', 'publicar']):
            print(f"Post button found: '{t}' -> disabled={b.is_disabled()}")
            
    browser.close()
