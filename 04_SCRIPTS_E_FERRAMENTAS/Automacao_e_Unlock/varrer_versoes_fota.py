import urllib.request
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def get_token(ts, project='T7', dev_id='FFG2RTA007439002311L14'):
    key = bytes.fromhex('4532374633324537464633303444374339463139443130303333423030333031')
    iv = bytes.fromhex('38316331326462313565346563316236')
    plaintext = f'{{\n "project":"{project}",\n "deviceId":"{dev_id}",\n "time":{ts}\n}}\n'
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    enc = cipher.encryptor()
    return base64.b64encode(enc.update(padded) + enc.finalize()).decode('ascii')

def test_versions():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req) as resp:
        ts = int(json.loads(resp.read().decode('utf-8'))['timestamp'])

    token = get_token(ts, 'T7')

    # Generate range of possible previous versions:
    versions_to_test = []
    # 1.00.000001 .. 1.00.000025
    for i in range(1, 26):
        versions_to_test.append(f"1.00.{i:06d}")
    # 1.01.000001 .. 1.01.000023
    for i in range(1, 24):
        versions_to_test.append(f"1.01.{i:06d}")

    print(f"[*] Testing {len(versions_to_test)} versions on Acer FOTA server...", flush=True)

    found = []
    for ver in versions_to_test:
        body = {
            'projectName': 'T7',
            'SKUName': 'BR',
            'version': ver,
            'deviceId': 'FFG2RTA007439002311L14'
        }
        b_data = json.dumps(body).encode('utf-8')
        req = urllib.request.Request('https://connect-ota.acervcon.com/updateVersion', data=b_data, headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'auth-token': token,
            'User-Agent': 'curl/7.60.0'
        })
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                res = resp.read().decode('utf-8').strip()
                if res != '{"success":true,"firmware":""}' and 'Current is the latest' not in res and res != '{\n  "success": true,\n  "firmware": ""\n}':
                    print(f"!!! HIT FOUND !!! Version: {ver} -> {res}", flush=True)
                    found.append((ver, res))
                else:
                    # print dot to show progress
                    print(f".", end="", flush=True)
        except Exception as e:
            print(f"\n[!] Error on {ver}: {e}", flush=True)

    print("\n[+] Done testing.", flush=True)
    if found:
        print("[!] SUCCESSFUL HITS:")
        for v, r in found:
            print(f"  {v}: {r}")
    else:
        print("[-] No hits with firmware != empty in the 1.00/1.01 series for SKU BR.")

if __name__ == '__main__':
    test_versions()
