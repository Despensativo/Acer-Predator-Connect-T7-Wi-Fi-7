#!/usr/bin/env python3
"""
telnet_compat.py
Camada universal de compatibilidade Telnet para Python 3.8 até 3.14+.
Aceita tanto 'bytes' quanto 'str' em write() e read_until().
Utiliza telnetlib nativo se disponível ou cliente socket puro (Python >= 3.13).
Zero bibliotecas de terceiros necessárias (dispensa pip install).
"""

import socket
import time

try:
    import telnetlib
    class Telnet(telnetlib.Telnet):
        def write(self, data):
            if isinstance(data, str):
                data = data.encode("ascii")
            super().write(data)

        def read_until(self, expected, timeout=None):
            if isinstance(expected, str):
                expected = expected.encode("ascii")
            return super().read_until(expected, timeout=timeout)
except ImportError:
    class Telnet:
        def __init__(self, host=None, port=23, timeout=5):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(timeout)
            if host:
                self.connect(host, port, timeout)

        def connect(self, host, port=23, timeout=5):
            self.sock.connect((host, port))
            self.sock.settimeout(timeout)

        def write(self, data):
            if isinstance(data, str):
                data = data.encode("ascii")
            self.sock.sendall(data)

        def read_until(self, expected, timeout=5):
            if isinstance(expected, str):
                expected = expected.encode("ascii")
            self.sock.settimeout(timeout)
            buf = b""
            start = time.time()
            while expected not in buf:
                if timeout is not None and time.time() - start > timeout:
                    break
                try:
                    chunk = self.sock.recv(4096)
                    if not chunk:
                        break
                    # Filtrar comandos IAC (0xFF) do protocolo Telnet
                    filtered = bytearray()
                    i = 0
                    while i < len(chunk):
                        if chunk[i] == 0xFF:
                            i += 3  # Pula 3 bytes (IAC + comando + opcao)
                        else:
                            filtered.append(chunk[i])
                            i += 1
                    buf += bytes(filtered)
                except socket.timeout:
                    break
            return buf

        def read_very_eager(self):
            self.sock.setblocking(False)
            buf = b""
            try:
                while True:
                    c = self.sock.recv(4096)
                    if not c:
                        break
                    buf += c
            except Exception:
                pass
            self.sock.setblocking(True)
            return buf

        def close(self):
            try:
                self.sock.close()
            except Exception:
                pass
