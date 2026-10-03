import os
import json
import urllib.request
import hashlib
import time
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

KEY = bytes.fromhex('4532374633324537464633303444374339463139443130303333423030333031')
IV = bytes.fromhex('38316331326462313565346563316236')

def get_token(ts, project, dev_id):
    plaintext = f'{{\n "project":"{project}",\n "deviceId":"{dev_id}",\n "time":{ts}\n}}\n'
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV))
    enc = cipher.encryptor()
    return base64.b64encode(enc.update(padded) + enc.finalize()).decode('ascii')

def get_server_ts():
    req = urllib.request.Request('https://connect-ota.acervcon.com/now', headers={'User-Agent': 'curl/7.60.0'})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return int(json.loads(resp.read().decode('utf-8'))['timestamp'])

def get_fresh_url(project, sku, trigger_version, dev_id):
    ts = get_server_ts()
    token = get_token(ts, project, dev_id)
    body = {
        "projectName": project,
        "SKUName": sku,
        "version": trigger_version,
        "deviceId": dev_id
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
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        fw = data.get("firmware", {})
        return fw.get("firmwareUrl"), fw.get("checksum"), fw.get("size")

def md5_file(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def main():
    catalog_path = "Backups_MTD/catalogo_completo_firmwares_acer.json"
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # Device IDs
    dev_ids = {
        "T7": "FFG2RTA007439002311L14",
        "W6x": "FFG2TTA007502007801N01",
        "X7": "FFG2RTA007439002311L14"
    }

    # Dest dirs
    dest_dirs = {
        "T7": "Backups_MTD",
        "W6x": "Backups_MTD/Acer_Predator_Connect_W6x",
        "X7": "Backups_MTD/Acer_Predator_Connect_X7"
    }

    for d in dest_dirs.values():
        os.makedirs(d, exist_ok=True)

    print("=" * 70)
    print("      DOWNLOAD E ARQUIVAMENTO DE TODOS OS FIRMWARES OFICIAIS ACER")
    print("=" * 70)

    # Let's filter T7 and W6x firmwares
    targets = [item for item in catalog.values() if item["project"] in ["T7", "W6x"]]

    print(f"Total de firmwares catalogados para T7 e W6x: {len(targets)}\n")

    for item in targets:
        project = item["project"]
        target_version = item["target_version"]
        filename = item["filename"]
        expected_md5 = item["checksum"]
        expected_size = item["size"]
        sku = item["skus"][0]
        trigger_ver = item["source_versions_trigger"][0]
        dev_id = dev_ids[project]
        dest_dir = dest_dirs[project]
        dest_file = os.path.join(dest_dir, filename)

        print(f"\n[>] Processando: {project} | Versao: {target_version} ({filename})")
        print(f"    Destino: {dest_file}")

        # Verifica se já existe e se o MD5 confere
        if os.path.exists(dest_file):
            current_md5 = md5_file(dest_file)
            if current_md5 == expected_md5:
                print(f"    [JA EXISTE E VALIDO] MD5: {current_md5} (OK)")
                continue
            else:
                print(f"    [ARQUIVO CORROMPIDO] MD5 atual: {current_md5} != esperado: {expected_md5}. Rebaixando...")

        # Baixa arquivo com URL fresca
        print(f"    Solicitando URL pré-assinada atualizada do S3 (via {sku} / {trigger_ver})...")
        fresh_url, chk, size = get_fresh_url(project, sku, trigger_ver, dev_id)
        if not fresh_url:
            print(f"    [ERRO] Não foi possível obter URL do S3 para {filename}!")
            continue

        print(f"    Baixando {size} bytes ({size/1024/1024:.2f} MB)...")
        req_dl = urllib.request.Request(fresh_url, headers={'User-Agent': 'curl/7.60.0'})
        tmp_file = dest_file + ".tmp"
        with urllib.request.urlopen(req_dl) as resp, open(tmp_file, 'wb') as out_f:
            downloaded = 0
            while True:
                buf = resp.read(1024 * 1024)
                if not buf:
                    break
                out_f.write(buf)
                downloaded += len(buf)
                print(f"\r    Progresso: {downloaded/1024/1024:.1f} MB / {size/1024/1024:.1f} MB", end="", flush=True)

        print()
        actual_md5 = md5_file(tmp_file)
        if actual_md5 == expected_md5:
            if os.path.exists(dest_file):
                os.remove(dest_file)
            os.rename(tmp_file, dest_file)
            print(f"    [SUCESSO 100%] Salvo com integridade verificada! MD5: {actual_md5}")
        else:
            print(f"    [FALHA DE CHECKSUM] Baixado: {actual_md5} != Esperado: {expected_md5}")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

    print("\n" + "=" * 70)
    print("      CONCLUÍDO: TODOS OS FIRMWARES DISPONÍVEIS FORAM ARQUIVADOS!")
    print("=" * 70)

if __name__ == "__main__":
    main()
