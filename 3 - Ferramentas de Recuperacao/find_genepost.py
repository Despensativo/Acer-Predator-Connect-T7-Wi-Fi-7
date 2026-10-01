import urllib.request
import re

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

# Search around /action/genepost
idx = 0
while True:
    idx = data.find('/action/genepost', idx)
    if idx == -1:
        break
    start = max(0, idx - 150)
    end = min(len(data), idx + 250)
    print("--- CONTEXT ---")
    print(data[start:end])
    idx += len('/action/genepost')
