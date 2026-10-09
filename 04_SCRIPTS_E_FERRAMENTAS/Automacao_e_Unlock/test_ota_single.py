import urllib.request
import json
import base64
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def test_query(sku="BR", version="1.00.000000"):
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        ts = int(data.get('timestamp', data))
    print(f"Timestamp: {ts}", flush=True)

    key_hex = '4532374633324537464633303444374339463139443130303333423030333031'
    iv_hex = '38316331326462313565346563316236'
    key = bytes.fromhex(key_hex)
    iv = bytes.fromhex(iv_hex)

    # In fota binary:
    # {
    #  "project":"T7",
    #  "deviceId":"FFG2RTA007439002311L14",
    #  "time":<timestamp>
    # }
    # Note: openssl enc on the router encrypts /etc/config/fota_enc.txt
    plaintext = f'{{\n "project":"T7",\n "deviceId":"FFG2RTA007439002311L14",\n "time":{ts}\n}}\n'
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    auth_token = base64.b64encode(ciphertext).decode('ascii')
    print(f"Auth token: {auth_token}", flush=True)

    body = {
        "projectName": "T7",
        "SKUName": sku,
        "version": version,
        "deviceId": "FFG2RTA007439002311L14"
    }
    body_bytes = json.dumps(body).encode('utf-8')
    print(f"Sending body: {body}", flush=True)

    req_update = urllib.request.Request(
        'https://connect-ota.acervcon.com/updateVersion',
        data=body_bytes,
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'auth-token': auth_token,
            'User-Agent': 'curl/7.60.0'
        }
    )
    try:
        with urllib.request.urlopen(req_update, timeout=10) as r:
            res = r.read().decode('utf-8')
            print(f"Response: {res}", flush=True)
    except Exception as ex:
        print(f"Error: {ex}", flush=True)

if __name__ == '__main__':
    for s in ["BR", "WW", "US", "TW"]:
        print(f"\n--- Testing SKU {s} with 1.00.000000 ---")
        test_query(sku=s, version="1.00.000000")
