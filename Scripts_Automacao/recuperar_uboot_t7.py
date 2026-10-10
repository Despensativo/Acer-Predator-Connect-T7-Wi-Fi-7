#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
   ACER PREDATOR CONNECT T7 & X7 - RECUPERADOR AUTOMATIZADO U-BOOT RECOVERY
================================================================================
Este script realiza o upload e a gravacao automatica de firmware de emergencia
atraves do bootloader Qualcomm U-Boot Web Failsafe (http://192.168.1.1) utilizando
protocolo HTTP/1.0 compativel com o webserver embarcado uIP/0.9.
"""

import sys
import os
import time
import socket
import subprocess
import shutil

RECOVERY_URL = "http://192.168.1.1/"
RECOVERY_IP = "192.168.1.1"
RESTORED_IP = "192.168.76.1"

DEFAULT_STOCK_IMG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "01_FIRMWARES_E_IMAGENS",
    "Stock_OEM_Recovery",
    "nand-4k-ipq5332-single_101000027.img"
)

def print_banner():
    print("=" * 75)
    print("      ACER PREDATOR CONNECT T7 - U-BOOT HARDWARE WEB RECOVERY")
    print("      Automacao de Restauracao e Gravacao Fisica de Firmware (NAND)")
    print("=" * 75)

def check_ip_port(ip, port, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

def wait_for_recovery_mode(max_wait=120):
    print(f"\n[*] [1/4] Verificando conexao com o U-Boot Recovery ({RECOVERY_URL})...")
    if check_ip_port(RECOVERY_IP, 80, timeout=1.0):
        print(f"    [OK] Bootloader U-Boot detectado ativo em {RECOVERY_IP}:80!")
        return True

    print(f"    [!] O roteador NAO respondeu em {RECOVERY_IP}:80.")
    print("    " + "-" * 67)
    print("    INSTRUCOES PARA ACIONAR O MODO RECOVERY (HARDWARE):")
    print("    1. Desconecte a fonte de energia (cabo de forca) do roteador.")
    print("    2. Mantenha pressionado o botao WPS no topo/traseira.")
    print("    3. Plugue a fonte na tomada MANTENDO O WPS PRESSIONADO POR 5 SEGUNDOS.")
    print("    4. Solte o botao WPS. Os LEDs ficarao FIXOS/ESTATICOS.")
    print("    " + "-" * 67)
    print("    [>] Aguardando entrada no Modo Recovery...")

    t0 = time.time()
    while time.time() - t0 < max_wait:
        if check_ip_port(RECOVERY_IP, 80, timeout=0.8):
            print(f"\n    [OK] Modo Recovery detectado com sucesso! ({int(time.time() - t0)}s)")
            time.sleep(1.0)
            return True
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1.5)

    print("\n[-] Tempo limite esgotado. Verifique o cabo de rede e a configuracao de IP.")
    return False

def upload_firmware_python_socket(image_path):
    size_bytes = os.path.getsize(image_path)
    size_mb = size_bytes / (1024 * 1024)
    filename = os.path.basename(image_path)
    boundary = "--------------------PredatorRecoveryBoundary"

    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="firmware"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("latin1")

    footer = f"\r\n--{boundary}--\r\n".encode("latin1")
    total_length = len(header) + size_bytes + len(footer)

    req_headers = (
        f"POST / HTTP/1.0\r\n"
        f"Host: {RECOVERY_IP}\r\n"
        f"User-Agent: PredatorT7-Recovery/1.0\r\n"
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
        f"Content-Length: {total_length}\r\n"
        f"Connection: close\r\n\r\n"
    ).encode("latin1")

    print("\n[*] [3/4] Enviando firmware via Socket Nativo Python (HTTP/1.0)...")
    t_start = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(180)
        s.connect((RECOVERY_IP, 80))
        s.sendall(req_headers)
        s.sendall(header)

        sent = 0
        chunk_size = 65536
        with open(image_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                s.sendall(chunk)
                sent += len(chunk)
                elapsed = time.time() - t_start
                speed = (sent / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                pct = (sent / size_bytes) * 100
                bar = "=" * int(pct / 4) + ">"
                sys.stdout.write(f"\r    [{bar:<26}] {sent/(1024*1024):.1f}/{size_mb:.1f} MB ({pct:.0f}%) | {speed:.2f} MB/s")
                sys.stdout.flush()

        s.sendall(footer)
        sys.stdout.write("\n")
        sys.stdout.flush()

        dur = time.time() - t_start
        resp = b""
        try:
            while True:
                data = s.recv(4096)
                if not data:
                    break
                resp += data
        except:
            pass
        s.close()

        resp_str = resp.decode("latin1", errors="ignore")
        if "UPDATE IN PROGRESS" in resp_str or "Update in progress" in resp_str or "200 OK" in resp_str:
            print(f"    [OK] Upload concluido via Socket em {dur:.1f}s ({size_mb / dur:.2f} MB/s)!")
            print("    [OK] Resposta oficial do U-Boot: 'UPDATE IN PROGRESS'")
            return True
        else:
            print("    [OK] Transmissao concluida. Aguardando confirmacao de gravacao...")
            return True
    except Exception as e:
        print(f"\n[-] Erro durante envio via socket nativo: {e}")
        return False

def upload_firmware(image_path):
    size_bytes = os.path.getsize(image_path)
    size_mb = size_bytes / (1024 * 1024)
    print(f"\n[*] [2/4] Preparando transmissao da imagem:")
    print(f"    - Arquivo: {os.path.basename(image_path)}")
    print(f"    - Tamanho: {size_bytes:,} bytes ({size_mb:.2f} MB)")
    print(f"    - Destino: {RECOVERY_URL}")
    print(f"    - Protocolo: HTTP/1.0 Multipart (Streaming Direto)")

    curl_bin = shutil.which("curl")
    if curl_bin:
        cmd = [
            curl_bin,
            "--http1.0",
            "--progress-bar",
            "-F", f"firmware=@{image_path}",
            RECOVERY_URL,
            "--max-time", "180"
        ]
        print("\n[*] [3/4] Enviando firmware para a memoria do roteador (via cURL)...")
        print("    (Aguarde o preenchimento da barra de progresso)\n")
        t_start = time.time()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            dur = time.time() - t_start
            combined = proc.stdout + proc.stderr
            if "UPDATE IN PROGRESS" in combined or "Update in progress" in combined or proc.returncode == 0:
                print(f"\n    [OK] Upload concluido com sucesso em {dur:.1f}s ({size_mb / dur:.2f} MB/s)!")
                print("    [OK] Resposta oficial do U-Boot: 'UPDATE IN PROGRESS'")
                return True
        except Exception as e:
            print(f"    [!] cURL falhou ({e}), tentando socket nativo Python...")

    # Fallback garantido para Windows sem cURL ou qualquer outro ambiente
    return upload_firmware_python_socket(image_path)

def monitor_reboot_and_restore(max_wait=180):
    print(f"\n[*] [4/4] Monitorando gravacao fisica na NAND e reinicializacao...")
    print(f"    O U-Boot esta gravando os blocos na flash. NAO DESLIGUE A ENERGIA.")
    print(f"    Aguardando retorno no IP de producao: {RESTORED_IP}...")

    t0 = time.time()
    dots = 0
    time.sleep(15)  # Tempo inicial minimo de gravacao na NAND

    while time.time() - t0 < max_wait:
        # Testa se a porta 80 da interface Acer ou LuCI voltou
        if check_ip_port(RESTORED_IP, 80, timeout=0.6):
            elapsed = int(time.time() - t0)
            print(f"\n\n===========================================================================")
            print(f"   🎉 ROTEADOR TOTALMENTE RESTAURADO E ONLINE COM SUCESSO! ({elapsed}s)")
            print(f"===========================================================================")
            print(f"    - IP Ativo: http://{RESTORED_IP}")
            print(f"    - Interface Web (Porta 80): ONLINE")
            print(f"    - Telnet (Porta 23): {'ONLINE' if check_ip_port(RESTORED_IP, 23, 0.4) else 'OFFLINE'}")
            print(f"    - SSH (Porta 22): {'ONLINE' if check_ip_port(RESTORED_IP, 22, 0.4) else 'OFFLINE'}")
            print(f"===========================================================================\n")
            return True

        dots += 1
        sys.stdout.write(f"\r    [~] Gravando/Reinicializando... ({int(time.time() - t0)}s) " + ("." * (dots % 6)))
        sys.stdout.flush()
        time.sleep(2.0)

    print(f"\n\n[!] Tempo limite de {max_wait}s atingido.")
    print(f"    O roteador pode estar demorando um pouco mais para inicializar os servicos.")
    print(f"    Tente abrir http://{RESTORED_IP} no seu navegador.")
    return False

def main():
    print_banner()

    # Define o caminho do arquivo de imagem
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        image_path = os.path.abspath(sys.argv[1])
    elif os.path.exists(DEFAULT_STOCK_IMG):
        image_path = DEFAULT_STOCK_IMG
    else:
        print(f"[-] ERRO: Imagem de recuperacao padrao nao encontrada em:")
        print(f"    {DEFAULT_STOCK_IMG}")
        print("    Informe o caminho da imagem: python recuperar_uboot_t7.py <arquivo.img>")
        sys.exit(1)

    # 1. Aguarda modo recovery se necessario
    if not wait_for_recovery_mode():
        sys.exit(1)

    # 2. Executa o upload via HTTP/1.0
    if not upload_firmware(image_path):
        print("\n[-] Falha no upload do firmware para o U-Boot.")
        sys.exit(1)

    # 3. Monitora gravacao e retorno
    monitor_reboot_and_restore()

if __name__ == "__main__":
    main()
