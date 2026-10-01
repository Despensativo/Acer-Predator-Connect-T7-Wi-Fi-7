import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

# Search for url strings, paths, post/get calls
paths = set(re.findall(r'["\'](/[^"\'\s<>]+)["\']', data))
api_paths = [p for p in paths if not p.endswith(('.js', '.css', '.png', '.svg', '.jpg', '.ico', '.woff', '.ttf'))]
print("API-like paths found in app.js:")
for p in sorted(api_paths)[:30]:
    print(" ", p)
