import urllib.request
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def get_token(ts, project, dev_id='FFG2RTA007439002311L14'):
    key = bytes.fromhex('4532374633324537464633303444374339463139443130303333423030333031')
    iv = bytes.fromhex('38316331326462313565346563316236')
    plaintext = f'{{\n "project":"{project}",\n "deviceId":"{dev_id}",\n "time":{ts}\n}}\n'
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    enc = cipher.encryptor()
    return base64.b64encode(enc.update(padded) + enc.finalize()).decode('ascii')

def probe_models():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req) as resp:
        ts = int(json.loads(resp.read().decode('utf-8'))['timestamp'])

    # Models / Projects to test
    projects = [
        # Predator series
        'T7',
        'X7',
        'W6',
        'W6m',
        'W6x',
        'Predator W6',
        'Predator X7',
        # ODM models
        'GX3000',
        'IH3000',
        'FG18'
    ]

    skus = ['WW', 'US', 'EU', 'BR', 'TW', 'GL', 'default']
    # Common previous versions
    versions = [
        '1.00.000001', '1.00.000010', '1.00.000020',
        '1.01.000001', '1.01.000010', '1.01.000012', '1.01.000020',
        '2.00.000001', '1.0.0', '1.0'
    ]

    hits = []
    print("[*] Probing multiple models on Acer FOTA server...", flush=True)

    for p in projects:
        token = get_token(ts, p)
        for s in ['WW', 'US', 'EU', 'BR', 'TW']:
            for v in ['1.01.000012', '1.01.000020', '1.00.000010', '1.00.000020']:
                body = {
                    'projectName': p,
                    'SKUName': s,
                    'version': v,
                    'deviceId': 'FFG2RTA007439002311L14'
                }
                b_data = json.dumps(body).encode('utf-8')
                req_up = urllib.request.Request('https://connect-ota.acervcon.com/updateVersion', data=b_data, headers={
                    'Content-Type': 'application/json;charset=UTF-8',
                    'auth-token': token,
                    'User-Agent': 'curl/7.60.0'
                })
                try:
                    with urllib.request.urlopen(req_up, timeout=3) as r:
                        resp_data = r.read().decode('utf-8').strip()
                        if 'firmwareUrl' in resp_data:
                            print(f"\n[!!!] HIT: Project {p} | SKU {s} | Ver {v}:")
                            info = json.loads(resp_data).get('firmware', {})
                            print(f"      Version: {info.get('version')}")
                            print(f"      File: {info.get('FirmwareName')}")
                            print(f"      Size: {info.get('size')} bytes")
                            print(f"      URL: {info.get('firmwareUrl')[:80]}...")
                            hits.append((p, s, info))
                        else:
                            print('.', end='', flush=True)
                except Exception as e:
                    pass

    print(f"\n\n[+] Probing finished! Found {len(hits)} available models/firmwares on Acer AWS.")
    for p, s, info in hits:
        print(f"-> {p} [{s}]: {info.get('FirmwareName')} ({info.get('version')}) - {info.get('size')} bytes")

if __name__ == '__main__':
    probe_models()
