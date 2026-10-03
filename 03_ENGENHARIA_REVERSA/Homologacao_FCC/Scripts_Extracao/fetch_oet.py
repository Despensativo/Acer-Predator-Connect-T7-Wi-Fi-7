import urllib.request

url = "https://apps.fcc.gov/oetcf/eas/reports/ViewExhibitReport.cfm?mode=Exhibits&RequestTimeout=500&calledFromFrame=N&fcc_id=HLZT7"
req = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode("utf-8", errors="replace")
        print("FCC OET Status:", resp.status)
        print("Length:", len(content))
        with open("fcc_oet_exhibits.html", "w", encoding="utf-8") as f:
            f.write(content)
except Exception as e:
    print("FCC OET Error:", e)
