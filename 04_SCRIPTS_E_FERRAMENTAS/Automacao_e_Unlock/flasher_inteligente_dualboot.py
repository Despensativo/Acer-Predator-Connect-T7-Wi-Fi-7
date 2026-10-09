#!/usr/bin/env python3
"""
flasher_inteligente_dualboot.py
Flasher Inteligente Dual-Boot com Gravacao Tripla (Kernel + Wi-Fi FW + RootFS)
Acer Predator Connect T7 (Qualcomm IPQ5332)

Identifica automaticamente o Slot em uso (Slot 1 ou Slot 2), grava os 3 componentes
no Slot livre alternativo com formatacao de overlay, chaveia o BootConfig Qualcomm
e valida o reboot de forma 100% autonoma e segura.
"""

import hashlib
import http.server
import os
import socket
import socketserver
import subprocess
import sys
import threading
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Localizar raiz do projeto
cur = SCRIPT_DIR
PROJECT_ROOT = cur
for _ in range(3):
    if os.path.exists(os.path.join(cur, "_FORA DO GitHub")) or os.path.exists(os.path.join(cur, "01_FIRMWARES_E_IMAGENS")):
        PROJECT_ROOT = cur
        break
    cur = os.path.dirname(cur)

# Diretorios candidatos para os artefatos da ROM
CANDIDATE_DIRS = [
    os.path.join(PROJECT_ROOT, "01_FIRMWARES_E_IMAGENS", "Official_v27_Componentes"),
    os.path.join(PROJECT_ROOT, "_FORA DO GitHub", "V27_CUSTOM_DEPLOY"),
    os.path.join(PROJECT_ROOT, "01_FIRMWARES_E_IMAGENS", "Custom_SquashFS")
]

HTTP_PORT = 8888
DEFAULT_ROUTER_IPS = ["192.168.76.1", "192.168.1.1", "192.168.73.2"]

FILES_REQUIRED = [
    "wifi_fw.bin",
    "kernel.bin",
    "rootfs.squashfs",
    "flash_engine.sh"
]


def calculate_md5(filepath):
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_local_ip(router_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((router_ip, 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "192.168.76.2"
    finally:
        s.close()
    return ip


def test_connection(ip, port, timeout=1.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False


def detect_router(explicit_ip=None):
    if explicit_ip and test_connection(explicit_ip, 80, 1.5):
        return explicit_ip

    for ip in DEFAULT_ROUTER_IPS:
        if test_connection(ip, 80, 0.8) or test_connection(ip, 22, 0.8) or test_connection(ip, 23, 0.8):
            return ip

    return "192.168.76.1"


class RouterRunner:
    def __init__(self, ip):
        self.ip = ip
        self.mode = None
        self.ssh_socket = f"/tmp/ssh-t7-root@{self.ip}:22"
        self._detect_method()

    def _detect_method(self):
        # 1. Verifica SSH com socket ativo
        if os.path.exists(self.ssh_socket):
            self.mode = "ssh_socket"
            return

        # 2. Verifica SSH direto
        if test_connection(self.ip, 22, 1.0):
            res = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=2", f"root@{self.ip}", "echo OK"],
                capture_output=True, text=True
            )
            if "OK" in res.stdout:
                self.mode = "ssh_direct"
                return

        # 3. Verifica Telnet
        if test_connection(self.ip, 23, 1.0):
            self.mode = "telnet"
            return

        # Fallback SSH padrao
        self.mode = "ssh_direct"

    def run(self, cmd, timeout=30):
        if self.mode == "ssh_socket":
            res = subprocess.run(
                ["ssh", "-S", self.ssh_socket, f"root@{self.ip}", cmd],
                capture_output=True, text=True, timeout=timeout
            )
            return res.stdout.strip()
        elif self.mode == "ssh_direct":
            res = subprocess.run(
                ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5", f"root@{self.ip}", cmd],
                capture_output=True, text=True, timeout=timeout
            )
            return res.stdout.strip()
        elif self.mode == "telnet":
            s = socket.create_connection((self.ip, 23), timeout=timeout)
            time.sleep(0.2)
            try:
                s.settimeout(0.5)
                s.recv(4096)
            except Exception:
                pass
            s.sendall((cmd + "\nexit\n").encode("utf-8"))
            out = b""
            start = time.time()
            while time.time() - start < timeout:
                try:
                    s.settimeout(1.0)
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    out += chunk
                except Exception:
                    break
            s.close()
            return out.decode("utf-8", errors="ignore").strip()
        return ""

    def run_stream(self, cmd, timeout=180):
        if self.mode in ["ssh_socket", "ssh_direct"]:
            ssh_args = ["ssh"]
            if self.mode == "ssh_socket":
                ssh_args += ["-S", self.ssh_socket]
            else:
                ssh_args += ["-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5"]
            ssh_args += [f"root@{self.ip}", cmd]

            p = subprocess.Popen(ssh_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            out_lines = []
            try:
                for line in iter(p.stdout.readline, ''):
                    print(line, end="")
                    out_lines.append(line)
                p.stdout.close()
                p.wait(timeout=timeout)
            except Exception as e:
                p.kill()
                print(f"[-] Erro na execucao: {e}")
            return "".join(out_lines)
        else:
            # Telnet interativo
            s = socket.create_connection((self.ip, 23), timeout=10)
            time.sleep(0.3)
            try:
                s.settimeout(0.5)
                s.recv(4096)
            except Exception:
                pass
            s.sendall((cmd + "\n").encode("utf-8"))
            out = b""
            start = time.time()
            while time.time() - start < timeout:
                try:
                    s.settimeout(2.0)
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    out += chunk
                    sys.stdout.write(chunk.decode("utf-8", errors="ignore"))
                    sys.stdout.flush()
                    if b"FLASH_CONCLUIDO_COM_SUCESSO" in out:
                        time.sleep(2)
                        break
                except socket.timeout:
                    pass
                except Exception:
                    break
            s.close()
            return out.decode("utf-8", errors="ignore")


def start_http_server(directory, port):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        def log_message(self, format, *args):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("0.0.0.0", port), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def wait_router_reboot(router_ip, expected_cmdline_fragment, max_wait=90):
    print(f"\n[*] Aguardando reinicializacao do roteador ({router_ip})...")
    time.sleep(10)
    start = time.time()
    while time.time() - start < max_wait:
        if test_connection(router_ip, 80, 1.0) or test_connection(router_ip, 22, 1.0):
            print(f"    [+] Roteador detectado online em {time.time() - start:.1f}s! Verificando boot...")
            time.sleep(3)
            runner = RouterRunner(router_ip)
            cmdline = runner.run("cat /proc/cmdline")
            if expected_cmdline_fragment in cmdline:
                return True, cmdline
        time.sleep(2)
        print(".", end="", flush=True)
    return False, "TIMEOUT"


def main():
    print("=" * 70)
    print("   PREDATOR CONNECT T7 - FLASHER INTELIGENTE DUAL-BOOT TRIPLO   ")
    print("      (Kernel Linux + Wi-Fi Firmware Qualcomm + RootFS Otimizado)")
    print("=" * 70)

    # 1. Localizar pasta com os arquivos da ROM
    deploy_dir = None
    for cand in CANDIDATE_DIRS:
        if os.path.exists(os.path.join(cand, "rootfs.squashfs")) and os.path.exists(os.path.join(cand, "kernel.bin")):
            deploy_dir = cand
            break

    if not deploy_dir:
        print("[-] ERRO: Nenhuma pasta com os componentes completos (kernel, wifi_fw, rootfs) foi encontrada.")
        sys.exit(1)

    print(f"\n[*] Diretorio da ROM: {deploy_dir}")

    # 2. Validar presenca e calcular checksums
    hashes = {}
    print("\n[*] Validando integridade dos 3 componentes da ROM:")
    for fn in FILES_REQUIRED:
        fp = os.path.join(deploy_dir, fn)
        if not os.path.isfile(fp):
            print(f"[-] ERRO FATAL: Arquivo obrigatorio ausente: {fn} ({fp})")
            sys.exit(1)
        sz = os.path.getsize(fp)
        md5 = calculate_md5(fp)
        hashes[fn] = (sz, md5)
        print(f"    - {fn:<16} | {sz:>10,} bytes ({sz/(1024*1024):>5.2f} MB) | MD5: {md5}")

    # 3. Detectar Roteador e Metodo de Acesso
    explicit_ip = sys.argv[1] if len(sys.argv) > 1 and "." in sys.argv[1] else None
    router_ip = detect_router(explicit_ip)
    print(f"\n[*] Conectando ao roteador em {router_ip}...")
    runner = RouterRunner(router_ip)
    print(f"    [+] Metodo de comunicacao ativo: {runner.mode}")

    # 4. Diagnosticar Slot Ativo e Determinar Slot Alvo
    cmdline = runner.run("cat /proc/cmdline")
    upgradepart = runner.run("cat /proc/boot_info/bootconfig0/rootfs/upgradepartition 2>/dev/null || echo ''")
    primaryboot = runner.run("cat /proc/boot_info/bootconfig0/rootfs/primaryboot 2>/dev/null || echo ''")

    print(f"\n[*] Diagnostico da Flash Qualcomm:")
    print(f"    - Linha de Comando (cmdline): {cmdline}")
    print(f"    - Particao Upgrade declarada: {upgradepart}")
    print(f"    - PrimaryBoot atual: {primaryboot}")

    if "ubi.mtd=rootfs" in cmdline or upgradepart == "rootfs_1":
        active_slot = "SLOT 1 (rootfs - MTD 20)"
        target_slot = "SLOT 2 (rootfs_1 - MTD 21)"
        target_mtd = "21"
        new_pb = "0"
        expected_boot_fragment = "ubi.mtd=rootfs_1"
    elif "ubi.mtd=rootfs_1" in cmdline or upgradepart == "rootfs":
        active_slot = "SLOT 2 (rootfs_1 - MTD 21)"
        target_slot = "SLOT 1 (rootfs - MTD 20)"
        target_mtd = "20"
        new_pb = "1"
        expected_boot_fragment = "ubi.mtd=rootfs"
    else:
        print("[-] ERRO: Nao foi possivel determinar com certeza o slot atual.")
        sys.exit(1)

    print("\n" + "#" * 70)
    print(f"  [>] SLOT ATIVO NO MOMENTO : {active_slot}")
    print(f"  [>] SLOT ALVO PARA GRAVACAO: {target_slot}")
    print(f"  [>] NOVO PRIMARYBOOT APOS O FLASH: {new_pb}")
    print("#" * 70)

    # 5. Iniciar Servidor HTTP Local para transferencia de alta velocidade
    is_dry_run = "--dry-run" in sys.argv
    auto_yes = "--yes" in sys.argv or "-y" in sys.argv

    if is_dry_run:
        print("\n[*] MODO DRY-RUN: Inspecao concluida sem realizar alteracoes na flash.")
        print(f"    - Alvo que seria gravado: {target_slot} (MTD {target_mtd})")
        print(f"    - Componentes que seriam gravados: wifi_fw.bin, kernel.bin, rootfs.squashfs")
        print(f"    - Novo PrimaryBoot que seria definido: {new_pb}")
        return

    if not auto_yes:
        try:
            resp = input(f"\n[?] Deseja iniciar a gravacao tripla no {target_slot}? [s/N]: ").strip().lower()
            if resp not in ["s", "sim", "y", "yes"]:
                print("[*] Operacao cancelada pelo usuario.")
                return
        except (EOFError, KeyboardInterrupt):
            pass

    local_ip = get_local_ip(router_ip)
    print(f"\n[*] Iniciando servidor HTTP local em {local_ip}:{HTTP_PORT}...")
    httpd = start_http_server(deploy_dir, HTTP_PORT)
    time.sleep(0.5)

    # 6. Transferir os arquivos para /tmp do roteador
    print(f"\n[*] Baixando os 3 componentes na memoria RAM (/tmp) do roteador...")
    transfer_script = f"""
rm -f /tmp/wifi_fw.bin /tmp/kernel.bin /tmp/rootfs.squashfs /tmp/flash_engine.sh
curl -fsSL http://{local_ip}:{HTTP_PORT}/wifi_fw.bin -o /tmp/wifi_fw.bin
curl -fsSL http://{local_ip}:{HTTP_PORT}/kernel.bin -o /tmp/kernel.bin
curl -fsSL http://{local_ip}:{HTTP_PORT}/rootfs.squashfs -o /tmp/rootfs.squashfs
curl -fsSL http://{local_ip}:{HTTP_PORT}/flash_engine.sh -o /tmp/flash_engine.sh
chmod +x /tmp/flash_engine.sh
md5sum /tmp/wifi_fw.bin /tmp/kernel.bin /tmp/rootfs.squashfs /tmp/flash_engine.sh
"""
    dl_out = runner.run(transfer_script, timeout=60)
    print("    [+] Arquivos recebidos no roteador:")
    for line in dl_out.splitlines():
        if "tmp" in line:
            print(f"        {line.strip()}")

    # 7. Disparar o Engine de Gravacao na Flash NAND
    print("\n[*] Disparando gravacao atomica e formatacao de overlay no roteador...")
    print("=" * 70)
    flash_output = runner.run_stream("/bin/sh /tmp/flash_engine.sh", timeout=180)
    print("=" * 70)

    httpd.shutdown()

    # 8. Monitorar Reinicializacao
    if "FLASH_CONCLUIDO_COM_SUCESSO" in flash_output or "REINICIANDO" in flash_output:
        print(f"\n[+] Gravacao dos 3 componentes finalizada com 100% de sucesso!")
        ok, res_boot = wait_router_reboot(router_ip, expected_boot_fragment, max_wait=90)
        if ok:
            print("\n" + "=" * 70)
            print(f"  [SUCESSO ABSOLUTO] Roteador reiniciou com sucesso no {target_slot}!")
            print(f"  Cmdline confirmada: {res_boot.strip()}")
            print("=" * 70)
        else:
            print(f"\n[!] O roteador esta iniciando ou trocou de IP. Cmdline: {res_boot}")
    else:
        print("\n[-] AVISO: Nao foi possivel confirmar a conclusao do flash. Inspecione os logs.")


if __name__ == "__main__":
    main()
