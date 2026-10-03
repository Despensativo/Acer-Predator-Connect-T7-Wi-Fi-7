import urllib.request
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def encrypt_auth_token(ts, project="T7", device_id="FFG2RTA007439002311L14"):
    key_hex = '4532374633324537464633303444374339463139443130303333423030333031'
    iv_hex = '38316331326462313565346563316236'
    
    key = bytes.fromhex(key_hex)
    iv = bytes.fromhex(iv_hex)

    # In /usr/bin/fota, fota_enc.txt is formatted with exact newlines and spaces:
    # {
    #  "project":"T7",
    #  "deviceId":"FFG2RTA007439002311L14",
    #  "time":1790965660
    # }
    plaintext = f'{{\n "project":"{project}",\n "deviceId":"{device_id}",\n "time":{ts}\n}}'
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(ciphertext).decode('ascii')

def query_acer_fota():
    req = urllib.request.Request(
        'https://connect-ota.acervcon.com/now',
        headers={'User-Agent': 'curl/7.60.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        ts = int(data.get('timestamp', data))
    print(f"[+] Server timestamp: {ts}")

    auth_token = encrypt_auth_token(ts)
    print(f"[+] Generated auth-token: {auth_token}")

    versions = [
        "1.00.000000",
        "1.00.000020",
        "1.01.000000",
        "0.00.000000",
        "0.01.000000"
    ]
    skus = ["BR", "WW", "US", "EU", "TW", "PA", "default", "GL", "CN"]

    for sku in skus:
        for ver in versions:
            body = {
                "projectName": "T7",
                "SKUName": sku,
                "version": ver,
                "deviceId": "FFG2RTA007439002311L14"
            }
            body_bytes = json.dumps(body).encode('utf-8')
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
                    if "Current is the latest" not in res and "Parameter error" not in res:
                        print(f"!!! FOUND UPDATE !!! SKU={sku} VER={ver} -> {res}")
                    else:
                        print(f"[>] SKU={sku:7s} VER={ver:12s} -> {res.strip()}")
            except Exception as ex:
                print(f"[!] SKU={sku:7s} VER={ver:12s} -> ERROR: {ex}")

if __name__ == '__main__':
    query_acer_fota()
