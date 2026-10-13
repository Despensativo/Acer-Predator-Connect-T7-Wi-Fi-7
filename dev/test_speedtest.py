import time
import sys
import re
from playwright.sync_api import sync_playwright

def run_speedtest(tag="wifi_6ghz"):
    print(f"\n==================================================")
    print(f"[{tag.upper()}] INICIANDO TESTE OOKLA SPEEDTEST.NET VIA NAVEGADOR")
    print(f"==================================================")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 900}
        )
        page = context.new_page()
        
        print(f"[{tag.upper()}] Acessando https://www.speedtest.net/ ...")
        page.goto("https://www.speedtest.net/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(5000)
        
        # Fechar banner de privacidade/cookies se existir
        try:
            accept_btn = page.locator("#onetrust-accept-btn-handler, button:has-text('Accept'), button:has-text('Aceitar'), button:has-text('Continue')").first
            if accept_btn.is_visible(timeout=2000):
                accept_btn.click()
                page.wait_for_timeout(1000)
        except Exception:
            pass
            
        print(f"[{tag.upper()}] Clicando no botao 'GO'...")
        # Novo UI React/MUI do Speedtest usa .animate-start-ring dentro do botao GO
        go_btn = page.locator("button:has(.animate-start-ring), .animate-start-ring, a.js-start-test, [aria-label*='start' i]").first
        go_btn.click(force=True)
        print(f"[{tag.upper()}] Teste Speedtest.net iniciado! Medindo Ping, Download e Upload...")
        
        start_time = time.time()
        while time.time() - start_time < 90:
            url = page.url
            if "/result/" in url:
                print(f"[{tag.upper()}] Teste concluido! URL de resultado detectada: {url}")
                break
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0 and elapsed > 0:
                print(f"[{tag.upper()}] Executando Speedtest.net... ({elapsed}s)")
            time.sleep(2)
            
        page.wait_for_timeout(5000)
        
        screenshot_path = f"/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/assets/speedtest_{tag}.png"
        page.screenshot(path=screenshot_path, full_page=False)
        print(f"[{tag.upper()}] Screenshot salvo em: {screenshot_path}")
        
        body_text = page.locator("body").inner_text()
        print(f"\n[{tag.upper()}] === RESULTADO EXTRAIDO SPEEDTEST.NET ===")
        print(f"[{tag.upper()}] URL: {page.url}")
        for line in body_text.splitlines():
            line_s = line.strip()
            if any(k in line_s.lower() for k in ["download", "upload", "ping", "mbps", "ms", "result id"]) and len(line_s) < 60:
                print(f"  {line_s}")
            
        browser.close()

if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "wifi_6ghz"
    run_speedtest(tag)
