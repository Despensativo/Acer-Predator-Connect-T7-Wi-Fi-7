import time
import sys
import re
from playwright.sync_api import sync_playwright

def run_waveform_test(tag="cable"):
    print(f"\n==================================================")
    print(f"[{tag.upper()}] INICIANDO TESTE WAVEFORM BUFFERBLOAT VIA NAVEGADOR")
    print(f"==================================================")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 900}
        )
        page = context.new_page()
        
        print(f"[{tag.upper()}] Acessando https://www.waveform.com/tools/bufferbloat...")
        page.goto("https://www.waveform.com/tools/bufferbloat", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        
        print(f"[{tag.upper()}] Clicando no botao 'Start Test'...")
        start_btn = page.locator("button:has-text('Start Test')").first
        start_btn.scroll_into_view_if_needed()
        start_btn.click()
        print(f"[{tag.upper()}] Teste iniciado! Medindo Latencia, Download e Upload em tempo real...")
        
        start_time = time.time()
        completed = False
        while time.time() - start_time < 120:
            url = page.url
            if "test-id=" in url:
                completed = True
                print(f"[{tag.upper()}] Teste concluido! ID do teste detectado.")
                break
            
            # Checar se ja apareceu o container de resultado
            if page.locator("text='Results'").count() > 0 and page.locator("text='Grade'").count() > 0:
                completed = True
                print(f"[{tag.upper()}] Resultados renderizados!")
                break
                
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0:
                print(f"[{tag.upper()}] Executando teste... ({elapsed}s)")
            time.sleep(2)
            
        # Esperar 5s para o grafico e scores estabilizarem na tela
        page.wait_for_timeout(5000)
        
        final_url = page.url
        print(f"\n[{tag.upper()}] URL do Resultado: {final_url}")
        
        # Salvar screenshot
        screenshot_path = f"/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/assets/waveform_{tag}.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"[{tag.upper()}] Screenshot completo salvo em: {screenshot_path}")
        
        # Extrair texto
        content = page.locator("body").inner_text()
        
        # Buscar Grade (Nota)
        grade_match = re.search(r"(?:Bufferbloat Grade|Grade)\s*\n*([A-F][+-]?)", content, re.IGNORECASE)
        if not grade_match:
            grade_match = re.search(r"\b([A-F][+-])\b", content)
            
        grade = grade_match.group(1) if grade_match else "N/A"
        print(f"[{tag.upper()}] >>> NOTA BUFFERBLOAT: {grade} <<<")
        
        # Buscar Download e Upload
        down_match = re.search(r"Download\s*\n*([0-9.]+\s*Mbps)", content, re.IGNORECASE)
        up_match = re.search(r"Upload\s*\n*([0-9.]+\s*Mbps)", content, re.IGNORECASE)
        unloaded_match = re.search(r"Unloaded\s*\n*([0-9.]+\s*ms)", content, re.IGNORECASE)
        down_active = re.search(r"Download Active\s*\n*(\+?[0-9.]+\s*ms)", content, re.IGNORECASE)
        up_active = re.search(r"Upload Active\s*\n*(\+?[0-9.]+\s*ms)", content, re.IGNORECASE)
        
        if down_match: print(f"[{tag.upper()}] Velocidade Download: {down_match.group(1)}")
        if up_match: print(f"[{tag.upper()}] Velocidade Upload: {up_match.group(1)}")
        if unloaded_match: print(f"[{tag.upper()}] Latencia Base (Unloaded): {unloaded_match.group(1)}")
        if down_active: print(f"[{tag.upper()}] Aumento de Latencia no Download: {down_active.group(1)}")
        if up_active: print(f"[{tag.upper()}] Aumento de Latencia no Upload: {up_active.group(1)}")
        
        browser.close()
        return final_url

if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "cable"
    run_waveform_test(tag)
