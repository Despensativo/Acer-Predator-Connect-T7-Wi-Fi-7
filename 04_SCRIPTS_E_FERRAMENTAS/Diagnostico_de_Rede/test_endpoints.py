import urllib.request
import urllib.error

urls = [
    'http://192.168.73.2/cgi-bin/web_cgi',
    'http://192.168.73.2/action/genepost',
    'http://192.168.73.2/action/login_app',
    'http://192.168.73.2/cgi-bin/luci',
    'http://192.168.73.2/ubus',
]

for u in urls:
    req = urllib.request.Request(u, data=b'{"test":1}', headers={'Content-Type': 'application/json'})
    try:
        resp = urllib.request.urlopen(req, timeout=3)
        print(f"[OK {resp.status}] {u} -> {resp.read()[:100]}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {u} -> {e.read()[:100]}")
    except Exception as ex:
        print(f"[ERR] {u} -> {ex}")
