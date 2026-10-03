import urllib.request
import json
import base64
import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def get_token(ts, project='T7'):
    key = bytes.fromhex('4532374633324537464633303444374339463139443130303333423030333031')
    iv = bytes.fromhex('38316331326462313565346563316236')
    plaintext = f'{{\n "project":"{project}",\n "deviceId":"FFG2RTA007439002311L14",\n "time":{ts}\n}}\n'
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    enc = cipher.encryptor()
    return base64.b64encode(enc.update(padded) + enc.finalize()).decode('ascii')

def download_t7_us():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req) as resp:
        ts = int(json.loads(resp.read().decode('utf-8'))['timestamp'])

    token = get_token(ts, 'T7')
    body = {
        'projectName': 'T7',
        'SKUName': 'US',
        'version': '1.01.000020',
        'deviceId': 'FFG2RTA007439002311L14'
    }
    req_up = urllib.request.Request('https://connect-ota.acervcon.com/updateVersion', data=json.dumps(body).encode('utf-8'), headers={
        'Content-Type': 'application/json;charset=UTF-8',
        'auth-token': token,
        'User-Agent': 'curl/7.60.0'
    })
    with urllib.request.urlopen(req_up) as r:
        data = json.loads(r.read().decode('utf-8'))
        fw = data.get('firmware', {})
        print("Fetched Firmware Metadata:")
        print(json.dumps(fw, indent=2))

    url = fw.get('firmwareUrl')
    fname = fw.get('FirmwareName')
    expected_md5 = fw.get('checksum')
    target_path = os.path.join('Backups_MTD', fname)

    print(f"\n[*] Starting download of {fname} ({fw.get('size')} bytes)...")
    req_dl = urllib.request.Request(url, headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req_dl) as resp, open(target_path, 'wb') as f:
        total = 0
        while True:
            chunk = resp.read(1024*1024)
            if not chunk: break
            f.write(chunk)
            total += len(chunk)
            print(f"Downloaded {total // (1024*1024)} MB...", end='\r')

    print(f"\n[+] Download finished: {total} bytes")
    with open(target_path, 'rb') as f:
        dl_md5 = hashlib.md5(f.read()).hexdigest()
    print(f"MD5: {dl_md5}")
    print(f"Expected MD5: {expected_md5}")
    if dl_md5.lower() == expected_md5.lower():
        print("[+] VERIFIED 100% PERFECT MATCH!")
    else:
        print("[-] MD5 mismatch!")

if __name__ == '__main__':
    download_t7_us()
