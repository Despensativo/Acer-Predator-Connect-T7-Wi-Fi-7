import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

# Webpack chunk mapping
# usually something like {8233:"53cf7f63",...}
matches = re.findall(r'(\{[0-9]+:\"[0-9a-f]+\"[^}]+\})', data)
print(f"Found {len(matches)} chunk maps")
for m in matches[:5]:
    print(m[:100])
