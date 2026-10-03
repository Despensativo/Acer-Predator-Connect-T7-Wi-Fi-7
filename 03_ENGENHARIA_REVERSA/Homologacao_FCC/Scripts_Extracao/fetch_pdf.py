import urllib.request

url = "https://fccid.io/HLZT7/Internal-Photos/9-Internal-Photos-Part1-7455750.pdf"
req = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Status:", resp.status)
        data = resp.read()
        print("PDF Length:", len(data))
        with open("internal_photos_part1.pdf", "wb") as f:
            f.write(data)
except Exception as e:
    print("Error:", e)
