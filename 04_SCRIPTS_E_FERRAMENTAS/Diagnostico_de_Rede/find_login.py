import urllib.request

url = 'http://192.168.73.2/pub/dist/js/app.867e05fe.js'
data = urllib.request.urlopen(url, timeout=5).read().decode('utf-8', errors='ignore')

idx = 0
while True:
    idx = data.find('login_app', idx)
    if idx == -1:
        break
    start = max(0, idx - 200)
    end = min(len(data), idx + 300)
    print("--- CONTEXT login_app ---")
    print(data[start:end])
    idx += len('login_app')
