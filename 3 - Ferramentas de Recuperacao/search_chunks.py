import urllib.request
import re
import json

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

# Extract chunk map
m = re.search(r'(\{392:\"[0-9a-f]+\"[^}]+\})', data)
if not m:
    print("Chunk map not found")
    exit(1)

raw_map = m.group(1)
# convert to valid json: {392:"5b3a7a3e",...} -> {"392":"5b3a7a3e",...}
json_map_str = re.sub(r'(\d+):', r'"\1":', raw_map)
chunk_map = json.loads(json_map_str)
print(f"Total chunks: {len(chunk_map)}")

keywords = ['ssh', 'dropbear', 'telnet', 'debug', 'developer', 'factory', 'uart', 'terminal', 'shell', 'console']

for cid, chash in chunk_map.items():
    chunk_name = f"{cid}.{chash}.js"
    cur_url = f"http://192.168.73.2/pub/dist/js/{chunk_name}"
    try:
        cdata = urllib.request.urlopen(cur_url, timeout=3).read().decode('utf-8', errors='ignore')
        matches = [k for k in keywords if re.search(r'\b' + k + r'\b', cdata, re.I)]
        if matches:
            print(f"[{chunk_name}] Matches: {matches}")
            for k in matches:
                for match in re.finditer(re.escape(k), cdata, re.I):
                    start = max(0, match.start() - 60)
                    end = min(len(cdata), match.end() + 60)
                    print(f"   Context for '{k}': ...{cdata[start:end]}...")
                    break
    except Exception as e:
        pass
