import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

methods = set(re.findall(r'data\.html\?method=([a-zA-Z0-9_]+)', data))
print(f"Total methods in data.html: {len(methods)}")
for m in sorted(methods):
    print("  ", m)
