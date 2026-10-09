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

def test():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req) as resp:
        ts = int(json.loads(resp.read().decode('utf-8'))['timestamp'])

    token = get_token(ts, 'T7')

    test_values = [
        "01", "0.1", "0.01", "001", "0001", "000001",
        "01.00", "01.00.00", "01.00.04", "01.00.05",
        "1.01.000001", "1.00.000001", "0.01.000001"
    ]

    print("Testando variações de '01' no servidor da Acer:")
    for v in test_values:
        body = {'projectName': 'T7', 'SKUName': 'BR', 'version': v, 'deviceId': 'FFG2RTA007439002311L14'}
        req_up = urllib.request.Request('https://connect-ota.acervcon.com/updateVersion', data=json.dumps(body).encode('utf-8'), headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'auth-token': token,
            'User-Agent': 'curl/7.60.0'
        })
        try:
            with urllib.request.urlopen(req_up, timeout=3) as r:
                data = r.read().decode('utf-8').strip()
                if "firmwareUrl" in data:
                    print(f"Versao={repr(v):16s} -> [HIT!] Liberou download do firmware!")
                else:
                    print(f"Versao={repr(v):16s} -> {data.replace(chr(10), ' ')}")
        except Exception as e:
            print(f"Versao={repr(v):16s} -> Erro: {e}")

if __name__ == '__main__':
    test()
