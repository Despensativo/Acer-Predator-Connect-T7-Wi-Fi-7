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

def map_all_firmwares():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req) as resp:
        ts = int(json.loads(resp.read().decode('utf-8'))['timestamp'])

    # Test ranges
    versions_to_probe = []
    # 1.00.xxxxxx
    for i in [1, 2, 5, 8, 9, 10, 12, 15, 18, 20, 24, 25, 27, 30]:
        versions_to_probe.append(f"1.00.{i:06d}")
    # 1.01.xxxxxx
    for i in range(1, 31):
        versions_to_probe.append(f"1.01.{i:06d}")
    # 1.02.xxxxxx
    for i in [1, 5, 10, 15, 20, 25]:
        versions_to_probe.append(f"1.02.{i:06d}")

    # Targets to map: (Project, DeviceID, [SKUs])
    targets = [
        ("T7", "FFG2RTA007439002311L14", ["BR", "US", "WW", "EU", "TW", "PA", "default"]),
        ("W6x", "FFG2TTA007502007801N01", ["GBL", "US", "EU", "TW", "BR", "default"])
    ]

    all_firmwares = {}

    for project, dev_id, skus in targets:
        token = get_token(ts, project, dev_id)
        for sku in skus:
            print(f"\n[*] Scanning {project} [{sku}] across {len(versions_to_probe)} versions...")
            for ver in versions_to_probe:
                body = {
                    "projectName": project,
                    "SKUName": sku,
                    "version": ver,
                    "deviceId": dev_id
                }
                req_up = urllib.request.Request(
                    "https://connect-ota.acervcon.com/updateVersion",
                    data=json.dumps(body).encode('utf-8'),
                    headers={
                        "Content-Type": "application/json;charset=UTF-8",
                        "auth-token": token,
                        "User-Agent": "curl/7.60.0"
                    }
                )
                try:
                    with urllib.request.urlopen(req_up, timeout=2.5) as r:
                        resp_data = r.read().decode('utf-8').strip()
                        if "firmwareUrl" in resp_data:
                            data = json.loads(resp_data).get("firmware", {})
                            key = f"{project}_{sku}_{data.get('version')}"
                            if key not in all_firmwares:
                                all_firmwares[key] = {
                                    "project": project,
                                    "sku": sku,
                                    "target_version": data.get("version"),
                                    "filename": data.get("FirmwareName"),
                                    "releaseDate": data.get("releaseDate"),
                                    "size": data.get("size"),
                                    "checksum": data.get("checksum"),
                                    "changeNotes": data.get("changeNotes"),
                                    "triggered_by": [ver]
                                }
                                print(f"\n  [NEW FIRMWARE DISCOVERED!]")
                                print(f"  Model: {project} | SKU: {sku} | Target Version: {data.get('version')}")
                                print(f"  File: {data.get('FirmwareName')} ({data.get('size')} bytes)")
                                print(f"  Release Date: {data.get('releaseDate')}")
                                print(f"  MD5: {data.get('checksum')}")
                                print(f"  Notes: {data.get('changeNotes')}\n")
                            else:
                                if ver not in all_firmwares[key]["triggered_by"]:
                                    all_firmwares[key]["triggered_by"].append(ver)
                            print("H", end="", flush=True)
                        else:
                            print(".", end="", flush=True)
                except Exception as e:
                    pass

    print("\n\n=======================================================")
    print("      RELATÓRIO COMPLETO DE TODAS AS VERSÕES EXISTENTES")
    print("=======================================================")
    with open("Backups_MTD/catalogo_completo_firmwares_acer.json", "w") as f:
        json.dump(all_firmwares, f, indent=2)

    for k, fw in all_firmwares.items():
        print(f"\nDispositivo: Acer Predator Connect {fw['project']}")
        print(f"  SKU / Região:      {fw['sku']}")
        print(f"  Versão:            {fw['target_version']}")
        print(f"  Data de Release:   {fw['releaseDate']}")
        print(f"  Nome do Arquivo:   {fw['filename']}")
        print(f"  Tamanho:           {fw['size']} bytes ({fw['size']/1024/1024:.2f} MB)")
        print(f"  Checksum (MD5):    {fw['checksum']}")
        print(f"  Notas da Versão:   {fw['changeNotes']}")
        print(f"  Versões de Origem: {', '.join(fw['triggered_by'][:5])}...")

if __name__ == "__main__":
    map_all_firmwares()
