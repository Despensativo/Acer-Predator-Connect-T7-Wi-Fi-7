#!/usr/bin/env python3
"""
Servidor TFTP RFC 1350 / RFC 2348 de Alta Performance para Windows
Desenvolvido para boot do Acer Predator Connect T7 (U-Boot IPQ5332)
Suporta Transferencias Padrao (512b) e Otimizadas (blksize / OACK ate 1468b)
"""

import os
import socket
import struct
import sys
import time

TFTP_DIR = os.path.dirname(os.path.abspath(__file__))

OP_RRQ = 1
OP_WRQ = 2
OP_DATA = 3
OP_ACK = 4
OP_ERROR = 5
OP_OACK = 6

def handle_rrq(sock, client_addr, data):
    parts = data[2:].split(b'\x00')
    if len(parts) < 2:
        return
    
    filename = parts[0].decode('latin1', errors='ignore')
    mode = parts[1].decode('latin1', errors='ignore').lower()
    
    # Parse options (blksize, timeout, etc.)
    options = {}
    idx = 2
    while idx + 1 < len(parts):
        opt_name = parts[idx].decode('latin1', errors='ignore').lower()
        opt_val = parts[idx+1].decode('latin1', errors='ignore')
        if opt_name:
            options[opt_name] = opt_val
        idx += 2
        
    blksize = 512
    if 'blksize' in options:
        try:
            blksize = min(int(options['blksize']), 1468)
        except ValueError:
            blksize = 512

    # Local file resolution
    clean_name = os.path.basename(filename)
    filepath = os.path.join(TFTP_DIR, clean_name)
    
    # Also fallback to openwrt.itb if requested name not found
    if not os.path.exists(filepath):
        alt = os.path.join(TFTP_DIR, "openwrt.itb")
        if os.path.exists(alt):
            filepath = alt
        else:
            print(f"[-] Arquivo nao encontrado: {clean_name}")
            err = struct.pack("!HH", OP_ERROR, 1) + b"File not found\x00"
            sock.sendto(err, client_addr)
            return

    filesize = os.path.getsize(filepath)
    print(f"\n[+] Conexao de {client_addr[0]}:{client_addr[1]}")
    print(f"    Arquivo: {os.path.basename(filepath)} ({filesize:,} bytes)")
    print(f"    Tamanho do bloco: {blksize} bytes (Opcoes: {options})")

    # Worker socket on ephemeral port
    worker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    worker.settimeout(5.0)

    try:
        with open(filepath, "rb") as f:
            block_num = 0
            
            # Send OACK if options negotiated
            if options:
                oack = struct.pack("!H", OP_OACK)
                if 'blksize' in options:
                    oack += b"blksize\x00" + str(blksize).encode('ascii') + b"\x00"
                if 'tsize' in options:
                    oack += b"tsize\x00" + str(filesize).encode('ascii') + b"\x00"
                    
                worker.sendto(oack, client_addr)
                
                # Wait for ACK 0
                resp, _ = worker.recvfrom(512)
                op, ack_num = struct.unpack("!HH", resp[:4])
                if op != OP_ACK or ack_num != 0:
                    print("[-] Falha na negociacao OACK")
                    return
                block_num = 1
            else:
                block_num = 1

            start_time = time.time()
            bytes_sent = 0
            
            while True:
                chunk = f.read(blksize)
                data_pkt = struct.pack("!HH", OP_DATA, block_num) + chunk
                
                # Send and retry up to 3 times
                acked = False
                for _ in range(3):
                    worker.sendto(data_pkt, client_addr)
                    try:
                        resp, _ = worker.recvfrom(512)
                        if len(resp) >= 4:
                            op, ack_num = struct.unpack("!HH", resp[:4])
                            if op == OP_ACK and ack_num == block_num:
                                acked = True
                                break
                    except socket.timeout:
                        pass
                
                if not acked:
                    print(f"[-] Timeout no bloco {block_num}")
                    break
                    
                bytes_sent += len(chunk)
                block_num = (block_num + 1) & 0xFFFF
                
                if len(chunk) < blksize:
                    elapsed = max(time.time() - start_time, 0.001)
                    speed = (bytes_sent / 1024 / 1024) / elapsed
                    print(f"[OK] Transferencia CONCLUIDA! {bytes_sent:,} bytes em {elapsed:.2f}s ({speed:.2f} MB/s)")
                    break

    except Exception as e:
        print(f"[-] Erro durante transferencia: {e}")
    finally:
        worker.close()

def main():
    print("=" * 65)
    print("   SERVIDOR TFTP WINDOWS - ACER PREDATOR CONNECT T7")
    print("=" * 65)
    print(f"Pasta raiz TFTP: {TFTP_DIR}")
    print("Arquivos disponiveis:")
    for f in os.listdir(TFTP_DIR):
        if f.endswith(('.itb', '.bin', '.txt')):
            sz = os.path.getsize(os.path.join(TFTP_DIR, f))
            print(f"  * {f} ({sz:,} bytes)")
            
    print("\nEscutando conexoes em UDP 0.0.0.0:69...")
    print("Pressione Ctrl+C para encerrar o servidor.\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('0.0.0.0', 69))
    except Exception as e:
        print(f"[-] Erro ao abrir porta 69: {e}")
        input("Pressione Enter para fechar...")
        return

    while True:
        try:
            data, client_addr = server.recvfrom(2048)
            if len(data) >= 2:
                op = struct.unpack("!H", data[:2])[0]
                if op == OP_RRQ:
                    handle_rrq(server, client_addr, data)
        except KeyboardInterrupt:
            print("\nServidor encerrado pelo usuario.")
            break
        except Exception as e:
            print(f"[-] Erro: {e}")

if __name__ == '__main__':
    main()
