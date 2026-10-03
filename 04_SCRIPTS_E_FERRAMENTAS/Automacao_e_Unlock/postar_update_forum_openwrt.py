#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postar_update_forum_openwrt.py
Publica automaticamente a resposta de atualizacao de desenvolvimento na thread 254042 do Forum OpenWrt.
Thread: https://forum.openwrt.org/t/research-guide-acer-predator-connect-t7-qualcomm-ipq5332-wi-fi-7-root-shell-unlock-2-5gbps-ap-mode-mtd-backups/254042
"""

import os
import sys
import io
import requests

from autoposter_openwrt import extrair_cookies_firefox, obter_usuario_e_csrf

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

FORUM_URL = "https://forum.openwrt.org"
TOPIC_ID = 254042
DOC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "06_DOCUMENTACAO", "PROCEDIMENTOS", "09_POST_ATUALIZACAO_FORUM_OPENWRT_2026-10-03.md"))

def extrair_corpo_post():
    if not os.path.isfile(DOC_PATH):
        print(f"[-] Erro: Arquivo {DOC_PATH} nao encontrado!")
        sys.exit(1)
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Pula os metadados do cabecalho (linhas 1 a 6)
    return "".join(lines[7:]).strip()

def publicar_resposta(session, csrf, topic_id=TOPIC_ID):
    corpo = extrair_corpo_post()
    print(f"[*] Preparando envio de resposta na thread {topic_id} ({len(corpo)} caracteres)...")
    
    headers = {
        "X-CSRF-Token": csrf,
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    payload = {
        "topic_id": topic_id,
        "raw": corpo
    }
    
    res = session.post(f"{FORUM_URL}/posts.json", json=payload, headers=headers)
    if res.status_code == 200:
        data = res.json()
        post_id = data.get("id")
        post_number = data.get("post_number")
        topic_slug = data.get("topic_slug", "research-guide-acer-predator-connect-t7")
        link = f"{FORUM_URL}/t/{topic_slug}/{topic_id}/{post_number}"
        print("\n" + "=" * 70)
        print("🎉 SUCESSO! Resposta de atualizacao publicada na thread do OpenWrt!")
        print(f"🔗 Post #{post_number}: {link}")
        print("=" * 70 + "\n")
        return link
    else:
        print(f"[-] Erro na publicacao (Status {res.status_code}): {res.text}")
        return None

def main():
    print("=" * 70)
    print("🚀 PUBLICADOR DE ATUALIZACAO - THREAD OPENWRT #254042")
    print("=" * 70)
    
    cookies = extrair_cookies_firefox()
    if not cookies or '_t' not in cookies:
        print("[-] Nao foi possivel encontrar a sessao ativa do OpenWrt no Firefox.")
        sys.exit(1)
        
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    })
    session.cookies.update(cookies)
    
    username, csrf = obter_usuario_e_csrf(session)
    if not username or not csrf:
        print("[-] Sessao expirada ou nao autenticado no forum.")
        sys.exit(1)
        
    print(f"[+] Autenticado com sucesso como: @{username}")
    
    # Se passado --yes ou -y via argumento
    if len(sys.argv) > 1 and sys.argv[1] in ["--yes", "-y"]:
        publicar_resposta(session, csrf)
    else:
        confirm = input(f"\nDeseja publicar a resposta agora na thread 254042 como @{username}? [S/n]: ").strip().lower()
        if confirm in ['', 's', 'sim', 'y', 'yes']:
            publicar_resposta(session, csrf)
        else:
            print("[*] Publicacao cancelada.")

if __name__ == "__main__":
    main()
