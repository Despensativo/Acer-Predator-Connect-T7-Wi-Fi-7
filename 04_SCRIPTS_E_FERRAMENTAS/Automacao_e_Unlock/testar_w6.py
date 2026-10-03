import urllib.request
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def get_token(ts, project='W6'):
    key = bytes.fromhex('4532374633324537464633303444374339463139443130303333423030333031')
    iv = bytes.fromhex('38316331326462313565346563316236')
    plaintext = f'{{\n "project":"{project}",\n "deviceId":"FFG2RTA007439002311L14",\n "time":{ts}\n}}\n'
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    enc = cipher.encryptor()
    return base64.b64encode(enc.update(padded) + enc.finalize()).decode('ascii')

def run():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req) as resp:
        ts = int(json.loads(resp.read().decode('utf-8'))['timestamp'])

    token = get_token(ts, 'W6')

    for v in ['1.30.308516', '1.20.000000', '1.00.000000', '1.10.000000']:
        for s in ['WW', 'US', 'default']:
            body = {'projectName': 'W6', 'SKUName': s, 'version': v, 'deviceId': 'FFG2RTA007439002311L14'}
            req_up = urllib.request.Request('https://connect-ota.acervcon.com/updateVersion', data=json.dumps(body).encode('utf-8'), headers={
                'Content-Type': 'application/json;charset=UTF-8',
                'auth-token': token,
                'User-Agent': 'curl/7.60.0'
            })
            try:
                with urllib.request.urlopen(req_up) as r:
                    data = r.read().decode('utf-8')
                    print(f"W6 {s} {v} -> {data[:100]}", flush=True)
            except Exception as e:
                print(f"Error: {e}", flush=True)

if __name__ == '__main__':
    run()
