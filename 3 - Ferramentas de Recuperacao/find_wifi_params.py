import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
with urllib.request.urlopen(url) as r:
    content = r.read().decode('utf-8', errors='ignore')

p = content.find('wifi6gHtmode')
print(content[max(0, p-500):min(len(content), p+1200)])
