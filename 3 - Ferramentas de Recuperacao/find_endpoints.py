import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
with urllib.request.urlopen(url) as r:
    content = r.read().decode('utf-8', errors='ignore')

endpoints = set(re.findall(r'[\"\'`]([a-zA-Z0-9_\-\.\/]+\.html\?[^\"\'`]+)[\"\'`]', content))
for ep in sorted(endpoints):
    print(ep)

apis = set(re.findall(r'[\"\'`](/api/[a-zA-Z0-9_\-\.\/]+)[\"\'`]', content))
for a in sorted(apis):
    print(a)

cgi = set(re.findall(r'[\"\'`](/cgi-bin/[a-zA-Z0-9_\-\.\/]+)[\"\'`]', content))
for c in sorted(cgi):
    print(c)
