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
    cookie = {
        'name': name,
        'value': value,
        'domain': host,
        'path': path or '/'
    }
    try:
        exp = float(expiry)
        if exp > 1e11:  # milliseconds
            cookie['expires'] = exp / 1000.0
        elif exp > 0:
            cookie['expires'] = exp
        else:
            cookie['expires'] = -1
    except Exception:
        cookie['expires'] = -1
    playwright_cookies.append(cookie)

print(f"Loaded {len(playwright_cookies)} cookies from Firefox.")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    context.add_cookies(playwright_cookies)
    page = context.new_page()
    page.goto('https://www.reddit.com/r/openwrt/submit', wait_until='domcontentloaded', timeout=30000)
    print('Current URL:', page.url)
    print('Page title:', page.title())
    content = page.content()
    is_logged_in = 'login' not in page.url.lower() and ('hcsskt' in content.lower() or 'logout' in content.lower() or 'submit' in page.url.lower())
    print('Likely logged in:', is_logged_in)
    page.screenshot(path="reddit_test.png")
    browser.close()
