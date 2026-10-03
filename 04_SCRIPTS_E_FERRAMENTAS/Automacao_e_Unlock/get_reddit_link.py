import sqlite3
import shutil
import os
import tempfile
from playwright.sync_api import sync_playwright

src = r'C:\Users\User\AppData\Roaming\Mozilla\Firefox\Profiles\bn45djuk.default-release\cookies.sqlite'
tmp = os.path.join(tempfile.gettempdir(), 'ff_reddit_link.sqlite')
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
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    )
    context.add_cookies(playwright_cookies)
    page = context.new_page()
    page.goto('https://www.reddit.com/user/me/submitted/', wait_until='domcontentloaded')
    page.wait_for_timeout(4000)
    print('User profile URL:', page.url)
    
    links = page.query_selector_all('a[href*="/comments/"]')
    for l in links[:10]:
        href = l.get_attribute('href')
        text = l.inner_text().strip()
        full = 'https://www.reddit.com' + href if href.startswith('/') else href
        print(f"Found post: {full} | Title: {text}")
            
    browser.close()
