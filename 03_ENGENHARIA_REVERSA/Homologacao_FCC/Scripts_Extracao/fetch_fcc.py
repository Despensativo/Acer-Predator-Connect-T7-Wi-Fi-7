import urllib.request
import re

req = urllib.request.Request(
    "https://fccid.io/HLZT7",
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Status:", resp.status)
        content = resp.read().decode("utf-8", errors="replace")
        print("Length:", len(content))
        with open("fcc_hlzt7.html", "w", encoding="utf-8") as f:
            f.write(content)
        # Find document links and tables
        links = re.findall(r'href="([^"]+)"', content)
        for l in links:
            if "HLZT7" in l or "fcc.gov" in l:
                print("Link:", l)
except Exception as e:
    print("Error:", e)
