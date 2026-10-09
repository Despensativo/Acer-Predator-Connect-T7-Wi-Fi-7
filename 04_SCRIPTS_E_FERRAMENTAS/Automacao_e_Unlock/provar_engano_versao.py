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

def run_tests():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req) as resp:
        ts = int(json.loads(resp.read().decode('utf-8'))['timestamp'])

    token = get_token(ts, 'T7')

    tests = [
        # Variations for T7
        {'projectName': 'T7', 'SKUName': 'BR', 'version': '1.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        {'projectName': 'T7', 'SKUName': 'BR', 'version': '0.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        {'projectName': 'T7', 'SKUName': 'BR', 'version': '1.01.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        {'projectName': 'T7', 'SKUName': 'BR', 'version': 'T7_BR_1.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        {'projectName': 'T7', 'SKUName': 'WW', 'version': '1.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        {'projectName': 'T7', 'SKUName': 'US', 'version': '1.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        {'projectName': 'T7', 'SKUName': 'GL', 'version': '1.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        # Other projects from the same ODM family
        {'projectName': 'X7', 'SKUName': 'WW', 'version': '1.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        {'projectName': 'X7', 'SKUName': 'BR', 'version': '1.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        {'projectName': 'GX3000', 'SKUName': 'BR', 'version': '1.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
        {'projectName': 'IH3000', 'SKUName': 'WW', 'version': '1.00.000000', 'deviceId': 'FFG2RTA007439002311L14'},
    ]

    for t in tests:
        body = json.dumps(t).encode('utf-8')
        req = urllib.request.Request('https://connect-ota.acervcon.com/updateVersion', data=body, headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'auth-token': token,
            'User-Agent': 'curl/7.60.0'
        })
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read().decode('utf-8')
                print(f"Project: {t['projectName']:6s} | SKU: {t['SKUName']:3s} | Ver: {t['version']:18s} -> {data.strip()}", flush=True)
        except Exception as e:
            print(f"Error {t}: {e}", flush=True)

if __name__ == '__main__':
    run_tests()
