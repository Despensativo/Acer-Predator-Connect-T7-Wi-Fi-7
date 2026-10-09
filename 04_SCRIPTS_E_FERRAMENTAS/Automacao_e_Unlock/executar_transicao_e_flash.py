#!/usr/bin/env python3
import socket
import sys
import time

ROUTER_IP = "192.168.76.1"
TELNET_PORT = 23

def telnet_run_cmd(cmd, wait_after=1, timeout=90):
    out = b""
    try:
        s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=5)
        time.sleep(0.3)
        try:
            s.settimeout(1.0)
            s.recv(4096)
        except Exception:
            pass

        s.sendall(cmd.encode("utf-8") + b"\n")
        time.sleep(wait_after)

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                s.settimeout(2.0)
                chunk = s.recv(4096)
                if not chunk:
                    break
                out += chunk
                if b"=== FLASH_COMPLETO_COM_SUCESSO ===" in out:
                    break
                if b"/ #" in out[-20:] or b"# " in out[-10:]:
                    break
            except socket.timeout:
                if out:
                    break
            except Exception:
                break
        s.close()
    except Exception as e:
        return f"ERROR: {e}"
    return out.decode("utf-8", errors="ignore")

def wait_for_router(expected_version=None, max_retries=75, retry_delay=3):
    print(f"[*] Aguardando roteador responder em {ROUTER_IP}:{TELNET_PORT}...")
    for i in range(max_retries):
        try:
            s = socket.create_connection((ROUTER_IP, TELNET_PORT), timeout=2)
            time.sleep(0.5)
            s.sendall(b"cat /etc/version\n")
            time.sleep(1)
            resp = s.recv(2048).decode("utf-8", errors="ignore")
            s.close()
            for line in resp.splitlines():
                if "1.01." in line or "T7_" in line:
                    ver = line.strip()
                    print(f"    [+] Roteador online! Versao detectada: {ver}")
                    if expected_version is None or expected_version in ver:
                        return True, ver
        except Exception:
            pass
        time.sleep(retry_delay)
        if (i + 1) % 5 == 0:
            print(f"    ... aguardando inicializacao ({(i+1)*retry_delay}s decorridos)")
    return False, "TIMEOUT"

def main():
    print("=" * 70)
    print("  EXECUTANDO PROCESSO REAL DE RE-FLASH A/B NA FLASH NAND")
    print("=" * 70)

    # 1. Comutar para Slot 1
    print("\n[Etapa 1/4] Chaveando ponteiro de boot para Slot 1 (OEM v24)...")
    res = telnet_run_cmd("/usr/sbin/boot-acer", wait_after=2, timeout=5)
    print("    Comando /usr/sbin/boot-acer enviado. Roteador reiniciando...")
    time.sleep(12)

    # 2. Aguardar Slot 1 subir
    print("\n[Etapa 2/4] Aguardando inicializacao do Slot 1 (OEM v24)...")
    ok, ver = wait_for_router(expected_version="000024", max_retries=65, retry_delay=3)
    if not ok:
        print(f"[-] Falha ao aguardar Slot 1: {ver}")
        sys.exit(1)
    print(f"[OK] Slot 1 ativo com sucesso! ({ver})")

    # 3. Disparar auto_flash no Slot 1
    print("\n[Etapa 3/4] Executando /root/auto_flash.sh no Slot 1...")
    flash_out = telnet_run_cmd("/root/auto_flash.sh", wait_after=5, timeout=120)
    print(f"--- Log da gravacao na Flash NAND ---\n{flash_out}\n-------------------------------------")

    if "FLASH_COMPLETO_COM_SUCESSO" not in flash_out and "Volume RootFS gravado com sucesso" not in flash_out:
        print("[-] ALERTA: A gravacao nao confirmou conclusao bem-sucedida!")
        sys.exit(1)

    print("[+] Gravacao no Slot 2 concluida com exito! Roteador reiniciando para o novo firmware...")
    time.sleep(15)

    # 4. Aguardar Slot 2 subir
    print("\n[Etapa 4/4] Aguardando o novo Slot 2 atualizado...")
    ok, ver = wait_for_router(expected_version="000027", max_retries=75, retry_delay=3)
    if not ok:
        print(f"[-] Roteador demorou para responder: {ver}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("  🎉 FLASH REAL E BOOT LIMPO CONCLUÍDOS COM SUCESSO TOTAL!")
    print(f"  Versao ativa: {ver}")
    print(f"  IP LuCI: http://{ROUTER_IP}/")
    print("=" * 70)

if __name__ == "__main__":
    main()
