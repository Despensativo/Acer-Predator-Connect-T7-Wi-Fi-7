#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
CENTRAL DE PUBLICAÇÃO 100% AUTOMATIZADA - SEM COPIAR/COLAR NADA!
Publica os tópicos e artigos diretamente via API nos fóruns e comunidades.
=============================================================================
"""

import sys
import io
import os
import getpass
import argparse

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from autoposter_openwrt import extrair_cookies_firefox, obter_usuario_e_csrf, publicar_topico as pub_openwrt
from autoposter_tabnews import autenticar, publicar_conteudo as pub_tabnews

def postar_openwrt_auto():
    print("\n" + "="*60)
    print("🌐 [1/2] PUBLICANDO NO FÓRUM OPENWRT...")
    print("="*60)
    cookies = extrair_cookies_firefox()
    if not cookies or '_t' not in cookies:
        print("[-] Sessão do Firefox não encontrada para forum.openwrt.org.")
        return False
        
    import requests
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    })
    session.cookies.update(cookies)
    username, csrf = obter_usuario_e_csrf(session)
    if not username or not csrf:
        print("[-] Falha ao autenticar sessão do OpenWrt.")
        return False
        
    print(f"[+] Sessão ativa detectada: @{username}")
    link = pub_openwrt(session, csrf)
    return bool(link)

def postar_tabnews_auto(email=None, password=None, token=None):
    print("\n" + "="*60)
    print("📰 [2/2] PUBLICANDO NO TABNEWS...")
    print("="*60)
    import requests
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 TabNewsAutoPoster/1.0"
    })
    
    if not token and not (email and password):
        print("\nPara postar no TabNews via API oficial, informe suas credenciais:")
        email = input("E-mail do TabNews: ").strip()
        password = getpass.getpass("Senha do TabNews: ").strip()
        
    if email and password:
        session, token = autenticar(email, password)
        if not session:
            return False
    elif token:
        session.cookies.set("session_id", token, domain="tabnews.com.br")
        
    link = pub_tabnews(session, token)
    return bool(link)

def main():
    parser = argparse.ArgumentParser(description="Central de Publicação Automatizada")
    parser.add_argument("--target", choices=["openwrt", "tabnews", "all"], default=None, help="Alvo de publicação")
    parser.add_argument("--tabnews-email", help="E-mail TabNews")
    parser.add_argument("--tabnews-pass", help="Senha TabNews")
    parser.add_argument("--tabnews-token", help="Token TabNews")
    args = parser.parse_args()

    print("\n" + "█"*65)
    print("   🚀 ROBÔ DE PUBLICAÇÃO AUTOMATIZADA DE DESCOBERTAS")
    print("   Zero cópia/cola. Publicação direta via API oficial!")
    print("█"*65)

    target = args.target
    if not target:
        print("\nEscolha onde deseja publicar automaticamente agora:")
        print("1. Fórum OpenWrt (Usa sua sessão existente @despensativo do Firefox - 1 clique)")
        print("2. TabNews (Via API REST - requer login 1x)")
        print("3. Publicar em AMBOS (OpenWrt + TabNews)")
        print("0. Sair")
        
        escolha = input("\nOpção [1, 2, 3 ou 0]: ").strip()
        if escolha == "1":
            target = "openwrt"
        elif escolha == "2":
            target = "tabnews"
        elif escolha == "3":
            target = "all"
        else:
            print("Saindo...")
            return

    if target in ["openwrt", "all"]:
        postar_openwrt_auto()
        
    if target in ["tabnews", "all"]:
        postar_tabnews_auto(args.tabnews_email, args.tabnews_pass, args.tabnews_token)

if __name__ == "__main__":
    main()
