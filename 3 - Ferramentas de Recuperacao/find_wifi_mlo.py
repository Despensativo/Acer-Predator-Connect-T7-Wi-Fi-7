import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
with urllib.request.urlopen(url) as r:
    content = r.read().decode('utf-8', errors='ignore')

matches = [m.start() for m in re.finditer(r'wifi.*mlo|mlo.*wifi', content, re.IGNORECASE)]
for p in matches[:10]:
    print(content[max(0, p-100):min(len(content), p+200)])
    print('='*50)
