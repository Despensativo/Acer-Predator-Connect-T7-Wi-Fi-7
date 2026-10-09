import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
with urllib.request.urlopen(url) as r:
    content = r.read().decode('utf-8', errors='ignore')

# Find where data.html?method=obj_get is called
for m in re.finditer(r'data\.html\?method=obj_get', content):
    p = m.start()
    print(content[max(0, p-120):min(len(content), p+200)])
    print('='*50)
