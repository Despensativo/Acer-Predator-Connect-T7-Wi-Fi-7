#!/usr/bin/env python3
"""
=============================================================================
EXTRATOR DA CAIXA-PRETA RAMOOPS - ACER PREDATOR CONNECT T7
=============================================================================
Conecta ao roteador via Telnet e faz o dump da regiao de memoria fisica
0x4CC00000 (1 MB reservado para Ramoops/Pstore) usando o dumper nativo mmap.
Decodifica o buffer do console kernel, printk e kernel panics da inicializacao.
=============================================================================
"""

import sys
import time
import os
import socket
import threading
import telnetlib
import re

ROUTER_IP = sys.argv[1] if len(sys.argv) > 1 else "192.168.73.2"
PC_IP = "192.168.73.90"
TRANSFER_PORT = 9998
HTTP_PORT = 8089

BASE_DIR = r"h:\FEITOS COM IA\Acer-Predator-Connect-T7"
LOG_DIR = os.path.join(BASE_DIR, "Logs_Diagnostico")
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts_Automacao")
DUMP_BIN_LOCAL = os.path.join(SCRIPTS_DIR, "dump_mem")
RAW_OUTPUT = os.path.join(LOG_DIR, "ramoops_raw.bin")
TEXT_OUTPUT = os.path.join(LOG_DIR, "ramoops_extracted_log.txt")

def start_tcp_receiver(output_file, expected_size=1048576, timeout=15):
    """Abre um socket TCP no PC para receber os dados binarios do dump"""
    received_data = bytearray()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((PC_IP, TRANSFER_PORT))
    server.listen(1)
    server.settimeout(timeout)

    def worker():
        nonlocal received_data
        try:
            conn, addr = server.accept()
            conn.settimeout(10)
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                received_data.extend(chunk)
            conn.close()
        except Exception as e:
            pass
        finally:
            server.close()

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t, lambda: received_data

def extract_strings(raw_bytes, min_len=4):
    """Extrai strings legíveis de um bloco de memoria binario"""
    result = []
    current = bytearray()
    for b in raw_bytes:
        if 32 <= b <= 126 or b in (10, 13, 9): # Imprimivel ASCII ou newline/tab
            current.append(b)
        else:
            if len(current) >= min_len:
                try:
                    result.append(current.decode("utf-8", errors="replace"))
                except:
                    pass
            current = bytearray()
    if len(current) >= min_len:
        try:
            result.append(current.decode("utf-8", errors="replace"))
        except:
            pass
    return result

def main():
    print("=" * 70)
    print("EXTRATOR DE CAIXA-PRETA RAMOOPS (0x4CC00000) - ACER PREDATOR T7")
    print(f"Roteador: {ROUTER_IP} | PC Receptor: {PC_IP}:{TRANSFER_PORT}")
    print("=" * 70)

    os.makedirs(LOG_DIR, exist_ok=True)

    # 1. Iniciar servidor TCP receptor
    print(f"[*] Preparando receptor TCP em {PC_IP}:{TRANSFER_PORT}...")
    recv_thread, get_data = start_tcp_receiver(RAW_OUTPUT)

    # 2. Conectar Telnet ao roteador
    print(f"[*] Conectando ao roteador em {ROUTER_IP}...")
    try:
        tn = telnetlib.Telnet(ROUTER_IP, 23, timeout=10)
        tn.read_until(b"/ # ", timeout=5)
    except Exception as e:
        print(f"[-] Erro ao conectar via Telnet: {e}")
        return 1

    # 3. Garantir presenca do utilitario dump_mem no roteador
    print("[*] Verificando /tmp/dump_mem no roteador...")
    tn.write(b"ls -l /tmp/dump_mem\n")
    time.sleep(0.5)
    out_ls = tn.read_very_eager().decode("ascii", errors="ignore")
    
    if "No such file" in out_ls or "not found" in out_ls:
        print("    -> Enviando binario nativo dump_mem para o roteador...")
        import http.server, socketserver
        class H(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=SCRIPTS_DIR, **kwargs)
            def log_message(self, *args): pass
        httpd = socketserver.TCPServer((PC_IP, HTTP_PORT), H)
        httpd.allow_reuse_address = True
        th = threading.Thread(target=httpd.serve_forever, daemon=True)
        th.start()
        
        tn.write(f"curl -fsSL http://{PC_IP}:{HTTP_PORT}/dump_mem -o /tmp/dump_mem && chmod +x /tmp/dump_mem\n".encode("ascii"))
        time.sleep(2)
        tn.read_until(b"/ # ", timeout=5)
        httpd.shutdown()

    # 4. Executar o dump fisico e transmitir via TCP
    print("[*] Mapeando 1 MB de memoria fisica (0x4CC00000) e transmitindo ao PC...")
    cmd_dump = f"/tmp/dump_mem 0x4cc00000 1048576 | nc {PC_IP} {TRANSFER_PORT}\n"
    tn.write(cmd_dump.encode("ascii"))
    time.sleep(1)
    tn.read_until(b"/ # ", timeout=10)
    tn.close()

    # 5. Aguardar recepcao dos dados
    recv_thread.join(timeout=5)
    raw_data = get_data()

    print(f"[+] Total de bytes recebidos: {len(raw_data)} bytes ({len(raw_data)/1024:.1f} KB)")

    if len(raw_data) == 0:
        print("[-] Nenhum byte foi recebido. Verifique o firewall do Windows para a porta 9998.")
        return 1

    # 6. Salvar dump binario bruto
    with open(RAW_OUTPUT, "wb") as f:
        f.write(raw_data)
    print(f"[OK] Dump binario salvo em: {RAW_OUTPUT}")

    # 7. Analisar conteudo
    all_zeros = all(b == 0 for b in raw_data)
    all_ffs = all(b == 0xFF for b in raw_data)
    
    # Checar se contem o marcador de teste
    has_deadbeef = b"\xef\xbe\xad\xde" in raw_data[:16]
    has_test_1234 = b"\x78\x56\x34\x12" in raw_data[:16]

    extracted_strings = extract_strings(raw_data, min_len=4)
    full_text = "\n".join(extracted_strings)

    # Identificar se ha marcadores de kernel Linux
    linux_markers = ["Linux version", "Kernel command line", "Booting Linux on physical CPU", "Call trace:", "Kernel panic", "Internal error:", "CPU:"]
    found_markers = [m for m in linux_markers if m in full_text]

    with open(TEXT_OUTPUT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("RELATORIO DE EXTRACAO DA CAIXA-PRETA RAMOOPS - ACER PREDATOR CONNECT T7\n")
        f.write(f"Data: {time.ctime()}\n")
        f.write(f"Tamanho Analisado: {len(raw_data)} bytes\n")
        f.write("=" * 80 + "\n\n")

        f.write("[DIAGNOSTICO PRELIMINAR]\n")
        if all_zeros:
            f.write("[-] A regiao de memoria esta completamente ZERADA (0x00).\n")
        elif all_ffs:
            f.write("[-] A regiao de memoria esta vazia/nao-inicializada (0xFF).\n")
        elif has_deadbeef:
            f.write("[!] ALERTA: O marcador de teste 0xDEADBEEF permaneceu intacto.\n")
            f.write("    Isso significa que o novo kernel nao alcancou a inicializacao do Ramoops.\n")
        elif has_test_1234:
            f.write("[!] ALERTA: O marcador previo 0x12345678 ainda esta no cabecalho.\n")
        else:
            f.write("[+] SUCESSO: A regiao de memoria foi sobrescrita pelo sistema!\n")

        if found_markers:
            f.write(f"[+] Marcadores de Kernel Linux Encontrados: {', '.join(found_markers)}\n")
        else:
            f.write("[-] Nenhum marcador formal de console Linux encontrado no buffer decodificado.\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("STRINGS EXTRAIDAS DA MEMORIA RAM (0x4CC00000 - 0x4CD00000):\n")
        f.write("=" * 80 + "\n\n")
        f.write(full_text)
        f.write("\n\n" + "=" * 80 + "\nFIM DO RELATORIO\n")

    print(f"[OK] Relatorio em texto decodificado salvo em: {TEXT_OUTPUT}")
    print("\n--- RESUMO DA ANALISE ---")
    if found_markers:
        print(f"[!!!] SUCESSO ABSOLUTO! MARCADORES DO KERNEL ENCONTRADOS: {found_markers}")
    elif has_deadbeef:
        print("[!] Marcador 0xDEADBEEF intacto - o kernel nao tocou nessa area antes de reiniciar.")
    else:
        print(f"[i] Strings extraidas: {len(extracted_strings)} blocos encontrados.")
        if extracted_strings:
            print("Amostra:")
            for s in extracted_strings[:10]:
                print(f"  > {s[:80]}")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
