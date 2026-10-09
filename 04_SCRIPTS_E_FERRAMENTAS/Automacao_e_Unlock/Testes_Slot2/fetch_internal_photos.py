import urllib.request
import re

url = "https://fccid.io/HLZT7/Internal-Photos/9-Internal-Photos-Part1-7455750"
req = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode("utf-8", errors="replace")
        pdf_urls = re.findall(r'href="([^"]+\.pdf[^"]*)"', content)
        print("PDF URLs:", pdf_urls)
        # also search for iframe or embed
        embeds = re.findall(r'src="([^"]+\.pdf[^"]*)"', content)
        print("Embeds:", embeds)
        direct = re.findall(r'https://[^"]+\.pdf', content)
        print("Direct PDFs:", direct)
except Exception as e:
    print("Error:", e)
