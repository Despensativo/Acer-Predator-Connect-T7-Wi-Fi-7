import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
with urllib.request.urlopen(url) as r:
    content = r.read().decode('utf-8', errors='ignore')

matches = [m.start() for m in re.finditer(r'mloConfig|mloSetting|wifiMlo|wifi_mlo', content, re.IGNORECASE)]
print('Matches:', len(matches))
for p in matches:
    s = content[max(0, p-80):min(len(content), p+200)].encode('ascii', errors='replace').decode('ascii')
    print(s)
    print('='*50)
