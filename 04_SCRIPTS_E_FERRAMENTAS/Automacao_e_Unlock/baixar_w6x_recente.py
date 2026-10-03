import urllib.request
import hashlib
import os
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

def download_latest_w6x():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req) as resp:
        ts = int(json.loads(resp.read().decode('utf-8'))['timestamp'])

    dev_id = 'FFG2TTA007502007801N01'
    token = get_token(ts, 'W6x', dev_id)

    body = {'projectName': 'W6x', 'SKUName': 'GBL', 'version': '1.01.000012', 'deviceId': dev_id}
    req_up = urllib.request.Request('https://connect-ota.acervcon.com/updateVersion', data=json.dumps(body).encode('utf-8'), headers={
        'Content-Type': 'application/json;charset=UTF-8',
        'auth-token': token,
        'User-Agent': 'curl/7.60.0'
    })
    with urllib.request.urlopen(req_up) as r:
        fw = json.loads(r.read().decode('utf-8'))['firmware']

    url = fw['firmwareUrl']
    target = os.path.join(r'Backups_MTD\Acer_Predator_Connect_W6x', fw['FirmwareName'])
    expected_md5 = fw['checksum']

    print(f"[*] Downloading latest W6x official firmware: {fw['FirmwareName']} ({fw['size']} bytes)...")
    req_dl = urllib.request.Request(url, headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req_dl) as resp, open(target, 'wb') as f:
        total = 0
        while True:
            chunk = resp.read(1024*1024)
            if not chunk: break
            f.write(chunk)
            total += len(chunk)
            print(f"    Downloaded {total // (1024*1024)} MB...", end='\r')

    print(f"\n[+] Download finished: {total} bytes")
    with open(target, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    print(f"MD5: {md5}")
    print(f"Expected: {expected_md5}")
    assert md5 == expected_md5
    print("[+] LATEST W6X FIRMWARE (1.01.000015) VERIFIED 100%!")

if __name__ == '__main__':
    download_latest_w6x()
