import urllib.request
import re
import json

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

m = re.search(r'(\{392:\"[0-9a-f]+\"[^}]+\})', data)
raw_map = m.group(1)
json_map_str = re.sub(r'(\d+):', r'"\1":', raw_map)
chunk_map = json.loads(json_map_str)

for cid, chash in chunk_map.items():
    chunk_name = f"{cid}.{chash}.js"
    cur_url = f"http://192.168.73.2/pub/dist/js/{chunk_name}"
    try:
        cdata = urllib.request.urlopen(cur_url, timeout=3).read().decode('utf-8', errors='ignore')
        if 'obj_get' in cdata:
            print(f"[{chunk_name}] found obj_get:")
            for match in re.finditer(r'obj_get', cdata):
                start = max(0, match.start() - 100)
                end = min(len(cdata), match.end() + 150)
                print("   ...", cdata[start:end], "...")
    except Exception as e:
        pass
