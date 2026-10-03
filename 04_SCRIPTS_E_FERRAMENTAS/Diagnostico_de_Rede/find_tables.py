import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

tables = set(re.findall(r'["\']table["\']\s*:\s*["\']([a-zA-Z0-9_]+)["\']', data))
objs = set(re.findall(r'obj_get&param=([a-zA-Z0-9_]+)|obj_set&param=([a-zA-Z0-9_]+)', data))
print(f"Total tables: {len(tables)}")
for t in sorted(tables):
    print("  Table:", t)

flat_objs = set()
for o1, o2 in objs:
    if o1: flat_objs.add(o1)
    if o2: flat_objs.add(o2)
print(f"\nTotal objects: {len(flat_objs)}")
for o in sorted(flat_objs):
    print("  Object:", o)
