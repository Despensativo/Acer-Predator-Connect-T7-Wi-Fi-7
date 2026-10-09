import urllib.request
import json
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

KEY = bytes.fromhex('4532374633324537464633303444374339463139443130303333423030333031')
IV = bytes.fromhex('38316331326462313565346563316236')

_cached_ts = 0
_cached_time_local = 0

def get_server_timestamp():
    global _cached_ts, _cached_time_local
    now = time.time()
    if now - _cached_time_local < 45 and _cached_ts > 0:
        return _cached_ts + int(now - _cached_time_local)
    try:
        req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            _cached_ts = int(data['timestamp'])
            _cached_time_local = now
            return _cached_ts
    except Exception:
        return int(time.time())

def generate_auth_token(project, device_id):
    ts = get_server_timestamp()
    plaintext = f'{{\n "project":"{project}",\n "deviceId":"{device_id}",\n "time":{ts}\n}}\n'
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV))
    enc = cipher.encryptor()
    return base64.b64encode(enc.update(padded) + enc.finalize()).decode('ascii')

def check_firmware(project, sku, version, device_id):
    token = generate_auth_token(project, device_id)
    body = {
        "projectName": project,
        "SKUName": sku,
        "version": version,
        "deviceId": device_id
    }
    req = urllib.request.Request(
        "https://connect-ota.acervcon.com/updateVersion",
        data=json.dumps(body).encode('utf-8'),
        headers={
            "Content-Type": "application/json;charset=UTF-8",
            "auth-token": token,
            "User-Agent": "curl/7.60.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("success") and "firmware" in data and isinstance(data["firmware"], dict):
                fw = data["firmware"]
                if fw.get("firmwareUrl"):
                    return {
                        "project": project,
                        "sku": sku,
                        "queried_version": version,
                        "target_version": fw.get("version"),
                        "filename": fw.get("FirmwareName"),
                        "url": fw.get("firmwareUrl"),
                        "releaseDate": fw.get("releaseDate"),
                        "size": fw.get("size"),
                        "checksum": fw.get("checksum"),
                        "changeNotes": fw.get("changeNotes")
                    }
    except Exception:
        pass
    return None

def main():
    print("=" * 60)
    print("     SCANNER DE FIRMWARES OFICIAIS ACER CLOUD FOTA")
    print("=" * 60)

    # Models and device IDs
    targets = [
        ("T7", "FFG2RTA007439002311L14", ["BR", "US", "EU", "TW", "WW", "PA", "GBL", "default"]),
        ("W6x", "FFG2TTA007502007801N01", ["GBL", "US", "EU", "TW", "BR", "default"]),
        ("W6", "FFG2RTA007439002311L14", ["GBL", "US", "EU", "TW", "BR", "default"]),
        ("W6m", "FFG2RTA007439002311L14", ["GBL", "US", "EU", "TW", "BR", "default"]),
        ("X5", "FFG2RTA007439002311L14", ["GBL", "EU", "default"]),
        ("X7", "FFG2RTA007439002311L14", ["GBL", "US", "EU", "TW", "BR", "default"])
    ]

    # Probed versions
    versions = []
    for i in range(1, 31):
        versions.append(f"1.00.{i:06d}")
    for i in range(1, 31):
        versions.append(f"1.01.{i:06d}")
    for i in [1, 2, 5, 10, 15, 20]:
        versions.append(f"1.02.{i:06d}")

    # Build work items
    tasks = []
    for project, dev_id, skus in targets:
        for sku in skus:
            for v in versions:
                tasks.append((project, sku, v, dev_id))

    print(f"Total de consultas planejadas: {len(tasks)} requisições.")
    print("Iniciando varredura paralela acelerada...\n")

    catalog = {}
    completed = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_firmware, p, s, v, d): (p, s, v) for p, s, v, d in tasks}
        for future in as_completed(futures):
            completed += 1
            if completed % 100 == 0:
                print(f"Progresso: {completed}/{len(tasks)} consultas concluídas...")
            result = future.result()
            if result:
                unique_key = f"{result['project']}_{result['target_version']}_{result['checksum']}"
                if unique_key not in catalog:
                    catalog[unique_key] = {
                        "project": result["project"],
                        "target_version": result["target_version"],
                        "filename": result["filename"],
                        "url": result["url"],
                        "releaseDate": result["releaseDate"],
                        "size": result["size"],
                        "checksum": result["checksum"],
                        "changeNotes": result["changeNotes"],
                        "skus": [result["sku"]],
                        "source_versions_trigger": [result["queried_version"]]
                    }
                    print(f"\n[NOVO FIRMWARE ENCONTRADO!]")
                    print(f"  Modelo:   Acer Predator Connect {result['project']}")
                    print(f"  Versao:   {result['target_version']}")
                    print(f"  SKU:      {result['sku']}")
                    print(f"  Arquivo:  {result['filename']} ({result['size']} bytes)")
                    print(f"  Data:     {result['releaseDate']}")
                    print(f"  MD5:      {result['checksum']}")
                    print(f"  Origem:   {result['queried_version']}\n")
                else:
                    if result["sku"] not in catalog[unique_key]["skus"]:
                        catalog[unique_key]["skus"].append(result["sku"])
                    if result["queried_version"] not in catalog[unique_key]["source_versions_trigger"]:
                        catalog[unique_key]["source_versions_trigger"].append(result["queried_version"])

    # Salva catálogo completo em JSON
    with open("Backups_MTD/catalogo_completo_firmwares_acer.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("           RESUMO DO CATÁLOGO DE FIRMWARES OFICIAIS ACER ENCONTRADOS")
    print("=" * 80)
    for k, item in sorted(catalog.items(), key=lambda x: (x[1]['project'], x[1]['target_version'])):
        print(f"\nDispositivo: Acer Predator Connect {item['project']}")
        print(f"  Versão Final:      {item['target_version']}")
        print(f"  SKUs Compatíveis:  {', '.join(item['skus'])}")
        print(f"  Arquivo:           {item['filename']}")
        print(f"  Tamanho:           {item['size']} bytes ({item['size']/1024/1024:.2f} MB)")
        print(f"  Data de Release:   {item['releaseDate']}")
        print(f"  Checksum (MD5):    {item['checksum']}")
        print(f"  Notas de Release:  {item['changeNotes']}")
        print(f"  URL S3:            {item['url']}")

if __name__ == "__main__":
    main()
