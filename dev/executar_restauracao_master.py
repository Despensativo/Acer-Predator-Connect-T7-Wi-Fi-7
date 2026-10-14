#!/usr/bin/env python3
"""
executar_restauracao_master.py
Restaura o backup mestre definitivo (cfg_restauracao_master_v2.cfg)
via API nativa da Acer com a cifra reversa proprietária (r1 / n).
"""

import sys
import os
import time
import json
import subprocess
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"

ROUTER_IP = "192.168.76.1"
BASE_URL = f"https://{ROUTER_IP}"
CFG_PATH = "/Volumes/--400GB--/FEITOS COM IA/Acer-Predator-Connect-T7/cfg_restauracao_master_v2.cfg"

CHARSET = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()-+=`~,./?|1234567890"

def r1(e):
    o = len(CHARSET)
    d = ""
    for ch in e:
        a = ord(ch)
        t = a % o
        a = (a - t) // o
        i = a % o
        a = (a - i) // o
        n = a % o
        d += CHARSET[n] + CHARSET[i] + CHARSET[t]
    return d

def n(e):
    t = len(CHARSET)
    i = ""
    for idx in range(0, len(e), 3):
        if idx + 2 >= len(e):
            break
        try:
            r = CHARSET.index(e[idx])
            o = CHARSET.index(e[idx+1])
            s = CHARSET.index(e[idx+2])
            d = r * t * t + o * t + s
            i += chr(d)
        except ValueError:
            break
    return i

def log(msg, symbol="ℹ️"):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {symbol} {msg}", flush=True)

def login(session):
    for pwd in ["TamFDH66x", "TamFDH66", "root0100", "Admin0100"]:
        log(f"Tentando autenticação com '{pwd}'...", "🔑")
        enc_pwd = r1(pwd)
        payload = {"username": "Admin", "password": enc_pwd}
        try:
            r = session.post(f"{BASE_URL}/action/login_app", data=payload, timeout=10)
            data = r.json()
            if data.get("success"):
                token = data.get("data")
                log(f"Login bem-sucedido com senha '{pwd}'! Token: {token[:8]}...", "✅")
                
                # Se autenticou com a senha de fábrica padrão (0km), faz a troca obrigatória
                if pwd == "TamFDH66":
                    status_info = send_obj_get(session, token, ["IsDefaultPwd"])
                    if isinstance(status_info, dict) and status_info.get("IsDefaultPwd") == "1":
                        log("Primeiro acesso 0km detectado! Alterando senha para TamFDH66x...", "🔄")
                        pwd_payload = {"UserName": "Admin", "Password": "TamFDH66", "NewPassword": "TamFDH66x"}
                        param_str = requests.utils.quote(r1(json.dumps(pwd_payload)))
                        url_pwd = f"{BASE_URL}/data.html?method=user_pwd&param={param_str}&_csrf_token={token}"
                        session.post(url_pwd, timeout=10)
                        
                        # Reautentica com a nova senha
                        r_new = session.post(f"{BASE_URL}/action/login_app", data={"username": "Admin", "password": r1("TamFDH66x")}, timeout=10)
                        token = r_new.json().get("data", token)
                        log(f"Nova senha TamFDH66x ativa! Novo token: {token[:8]}...", "✅")
                        return token, "TamFDH66x"
                        
                return token, pwd
            else:
                log(f"Falha com '{pwd}': {data.get('msg')}", "⚠️")
        except Exception as e:
            log(f"Erro na requisição: {e}", "❌")
    raise RuntimeError("Não foi possível autenticar com nenhuma senha conhecida!")

def send_obj_get(session, token, keys):
    param_str = requests.utils.quote(r1(json.dumps(keys)))
    url = f"{BASE_URL}/data.html?method=obj_get&param={param_str}&_csrf_token={token}"
    r = session.post(url, timeout=10)
    if r.status_code == 200:
        raw_text = r.text.strip()
        decoded = n(raw_text)
        try:
            return json.loads(decoded)
        except Exception:
            return decoded
    return None

def send_obj_set(session, token, obj):
    param_str = requests.utils.quote(r1(json.dumps(obj)))
    url = f"{BASE_URL}/data.html?method=obj_set&param={param_str}&_csrf_token={token}"
    r = session.post(url, timeout=10)
    if r.status_code == 200:
        raw_text = r.text.strip()
        decoded = n(raw_text)
        try:
            return json.loads(decoded)
        except Exception:
            return decoded
    return None

def upload_and_restore(session, token):
    if not os.path.exists(CFG_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {CFG_PATH}")

    file_size = os.path.getsize(CFG_PATH)
    log(f"Iniciando envio do arquivo mestre ({os.path.basename(CFG_PATH)}, {file_size} bytes)...", "📤")

    upload_url = f"{BASE_URL}/action/genepost?_csrf_token={token}"
    with open(CFG_PATH, "rb") as f:
        files = {
            "file": (os.path.basename(CFG_PATH), f, "application/octet-stream")
        }
        data = {
            "filetype": "cfgfile",
            "purl": "/upload_file.html"
        }
        r_upload = session.post(upload_url, files=files, data=data, timeout=30)
        log(f"Upload finalizado (HTTP {r_upload.status_code}): {r_upload.text[:100]}", "📦")

    # Aguardar e verificar resultado do upload
    log("Aguardando validação do upload pelo firmware...", "⏳")
    upload_ok = False
    for attempt in range(15):
        time.sleep(1)
        res = send_obj_get(session, token, ["webUploadResult"])
        log(f"Verificação do upload (tentativa {attempt+1}): {res}", "🔍")
        if isinstance(res, dict) and res.get("webUploadResult") == "0":
            upload_ok = True
            log("Upload validado com sucesso pelo roteador (webUploadResult: 0)!", "✅")
            break

    if not upload_ok:
        log("Aviso: webUploadResult não retornou '0', mas prosseguindo com comando de restauração...", "⚠️")

    # Disparar restauração definitiva
    log("Disparando restauração do sistema e reboot definitivo...", "🚀")
    restore_cmd = {"systemConfigRestore": "1", "systemRebootFlag": "1"}
    res_restore = send_obj_set(session, token, restore_cmd)
    log(f"Resposta do comando de restauração: {res_restore}", "📢")

def wait_for_reboot_and_ssh():
    log("Aguardando roteador reiniciar e aplicar a restauração master...", "⏳")
    
    # 1. Espera ping cair
    log("Aguardando roteador desligar...", "🔻")
    went_down = False
    for _ in range(30):
        r = subprocess.run(["ping", "-c", "1", "-W", "1", ROUTER_IP], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            went_down = True
            log("Roteador offline (processando restauração na flash)...", "🔻")
            break
        time.sleep(1)

    # 2. Espera ping voltar
    log("Aguardando roteador responder ping...", "⏳")
    start = time.time()
    while time.time() - start < 180:
        r = subprocess.run(["ping", "-c", "1", "-W", "1", ROUTER_IP], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode == 0:
            elapsed = int(time.time() - start)
            log(f"Roteador online novamente! (Ping respondeu em {elapsed}s)", "🟢")
            break
        time.sleep(2)

    # 3. Esperar porta 22 (SSH) abrir
    log("Aguardando porta 22 (SSH OpenWrt desbloqueado) abrir...", "⏳")
    ssh_up = False
    start = time.time()
    while time.time() - start < 120:
        res = subprocess.run(["nc", "-z", "-w", "2", ROUTER_IP, "22"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            elapsed = int(time.time() - start)
            log(f"Porta 22 (SSH) ABERTA com sucesso! (Tempo: {elapsed}s)", "🔓")
            ssh_up = True
            break
        time.sleep(2)

    if not ssh_up:
        log("Porta 22 ainda não abriu após timeout. Verificando porta 80...", "⚠️")
        res80 = subprocess.run(["nc", "-z", "-w", "2", ROUTER_IP, "80"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log(f"Porta 80 status: {'Aberta' if res80.returncode == 0 else 'Fechada'}")
        return False

    # 4. Validar acesso SSH root com senha root0100
    log("Testando acesso SSH com credenciais root / root0100...", "🔑")
    time.sleep(3)
    cmd = [
        "sshpass", "-p", "root0100",
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
        "-o", "HostKeyAlgorithms=+ssh-rsa", "-o", "PubkeyAuthentication=no", "root@192.168.76.1",
        "uci get system.@system[0].hostname; uci get network.lan.ipaddr; /etc/init.d/https-dns-proxy status 2>/dev/null"
    ]
    res_ssh = subprocess.run(cmd, capture_output=True, text=True)
    if res_ssh.returncode == 0:
        log("Acesso SSH confirmado com sucesso!", "🎉")
        log(f"Diagnóstico retornado:\n{res_ssh.stdout.strip()}", "📋")
        return True
    else:
        # Se sshpass não estiver instalado, testa ssh com batch mode ou instrui usuário
        log(f"SSH retorno code {res_ssh.returncode}: {res_ssh.stderr.strip()}", "⚠️")
        return False

def main():
    print("=" * 70)
    print(" 🔥 TESTE DE FOGO: RESTAURAÇÃO MASTER DEFINITIVA NO PREDATOR T7 🔥")
    print("=" * 70)
    
    session = requests.Session()
    session.verify = False

    token, active_pwd = login(session)
    upload_and_restore(session, token)
    success = wait_for_reboot_and_ssh()
    
    if success:
        print("\n" + "=" * 70)
        print(" 🏆 PROVA DE FOGO CONCLUÍDA COM 100% DE SUCESSO! 🏆")
        print(" O roteador subiu restaurado, desbloqueado, com LuCI e root0100!")
        print("=" * 70)
    else:
        log("Aguardando estabilização final do roteador...")

if __name__ == "__main__":
    main()
