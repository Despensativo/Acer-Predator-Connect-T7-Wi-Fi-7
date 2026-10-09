import urllib.request
import re
import json

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

m = re.search(r'(\{392:\"[0-9a-f]+\"[^}]+\})', data)
raw_map = m.group(1)
json_map_str = re.sub(r'(\d+):', r'"\1":', raw_map)
chunk_map = json.loads(json_map_str)

all_tables = set()
all_objs = set()

for cid, chash in chunk_map.items():
    chunk_name = f"{cid}.{chash}.js"
    cur_url = f"http://192.168.73.2/pub/dist/js/{chunk_name}"
    try:
        cdata = urllib.request.urlopen(cur_url, timeout=3).read().decode('utf-8', errors='ignore')
        tables = re.findall(r'["\']([a-zA-Z0-9_]*Table)["\']', cdata)
        objs = re.findall(r'["\']([a-zA-Z0-9_]*Obj(?:ect)?)["\']', cdata)
        all_tables.update(tables)
        all_objs.update(objs)
    except Exception as e:
        pass

print("Tables found:", sorted(all_tables))
print("Objects found:", sorted(all_objs))
