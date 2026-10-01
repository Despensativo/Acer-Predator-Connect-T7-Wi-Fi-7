import urllib.request
import urllib.parse
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
with urllib.request.urlopen(url) as r:
    content = r.read().decode('utf-8', errors='ignore')

for m in re.finditer(r'method=obj_get&param=([^\"\'& ]+)', content):
    p = urllib.parse.unquote(m.group(1))
    if any(k in p.lower() for k in ['mlo', 'wifi', 'band', 'psc']):
        print(p)
