import urllib.request
import re
import json

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

m = re.search(r'(\{392:\"[0-9a-f]+\"[^}]+\})', data)
raw_map = m.group(1)
json_map_str = re.sub(r'(\d+):', r'"\1":', raw_map)
chunk_map = json.loads(json_map_str)

params = set()

for cid, chash in chunk_map.items():
    chunk_name = f"{cid}.{chash}.js"
    cur_url = f"http://192.168.73.2/pub/dist/js/{chunk_name}"
    try:
        cdata = urllib.request.urlopen(cur_url, timeout=3).read().decode('utf-8', errors='ignore')
        matches = re.findall(r'param=([a-zA-Z0-9_%]+)', cdata)
        params.update(matches)
        matches2 = re.findall(r'param["\']?\s*:\s*["\']([^"\']+)["\']', cdata)
        params.update(matches2)
    except Exception as e:
        pass

print("Unique param patterns found:")
for p in sorted(params):
    print(" ", p)
