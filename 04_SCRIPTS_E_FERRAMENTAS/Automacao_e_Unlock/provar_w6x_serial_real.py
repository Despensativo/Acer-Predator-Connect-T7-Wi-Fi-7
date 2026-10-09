import urllib.request
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def get_token(ts, project, dev_id):
    key = bytes.fromhex('4532374633324537464633303444374339463139443130303333423030333031')
    iv = bytes.fromhex('38316331326462313565346563316236')
    plaintext = f'{{\n "project":"{project}",\n "deviceId":"{dev_id}",\n "time":{ts}\n}}\n'
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    enc = cipher.encryptor()
    return base64.b64encode(enc.update(padded) + enc.finalize()).decode('ascii')

def probe():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req) as resp:
        ts = int(json.loads(resp.read().decode('utf-8'))['timestamp'])

    dev_id = 'FFG2TTA007502007801N01'
    print(f"[*] Probing Acer FOTA with genuine W6x Serial: {dev_id} (SKU: GBL)")

    versions = [
        '1.00.000001', '1.00.000010', '1.00.000020',
        '1.01.000001', '1.01.000010', '1.01.000012', '1.01.000018', '1.01.000020', '1.01.000024',
        '1.02.000001', '1.02.000010', '1.02.000020',
        '0.01.000001', '0.01.000010', '1.0.0', '1.1.0'
    ]

    for proj in ['W6x', 'W6']:
        token = get_token(ts, proj, dev_id)
        for v in versions:
            body = {'projectName': proj, 'SKUName': 'GBL', 'version': v, 'deviceId': dev_id}
            req_up = urllib.request.Request('https://connect-ota.acervcon.com/updateVersion', data=json.dumps(body).encode('utf-8'), headers={
                'Content-Type': 'application/json;charset=UTF-8',
                'auth-token': token,
                'User-Agent': 'curl/7.60.0'
            })
            try:
                with urllib.request.urlopen(req_up, timeout=3) as r:
                    data = r.read().decode('utf-8').strip()
                    if 'firmwareUrl' in data:
                        print(f"\n[!!!] HIT on {proj} {v}: {data}\n")
                    else:
                        print('.', end='', flush=True)
            except Exception as e:
                pass

    print("\n[+] Finished probe.")

if __name__ == '__main__':
    probe()
