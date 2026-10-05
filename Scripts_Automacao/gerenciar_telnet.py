#!/usr/bin/env python3
"""
gerenciar_telnet.py
Gerenciador de Acesso Telnet e SSH (Hardening de Seguranca) para Acer Predator Connect T7
Permite verificar status, desativar ou reativar o servico Telnet (porta 23) e
importar chaves SSH publicas para login 100% sem senha no Dropbear (/etc/dropbear/authorized_keys).
Compativel com Windows, macOS e Linux (Python 3.8 ate 3.14+).
"""

import sys
import os
import platform
import socket
import time
import subprocess
import glob

# Ativar cores ANSI no Windows (PowerShell / CMD)
if platform.system() == "Windows":
    try:
        os.system("")
    except Exception:
        pass

# Import universal de Telnet
try:
    from telnet_compat import Telnet
except ImportError:
    try:
        from Scripts_Automacao.telnet_compat import Telnet
    except ImportError:
        import telnetlib
        Telnet = telnetlib.Telnet

# Paleta de Cores ANSI
C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_RED    = "\033[91m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_CYAN   = "\033[96m"
C_WHITE  = "\033[97m"

def test_port(ip, port, timeout=1.5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False

def detect_router_ip(explicit_ip=None):
    if explicit_ip:
        return explicit_ip
    for cand in ["192.168.73.2", "192.168.76.1", "192.168.1.1"]:
        if test_port(cand, 23):
            return cand
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        my_ip = s.getsockname()[0]
        s.close()
        parts = my_ip.split(".")
        guess = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
        if test_port(guess, 23):
            return guess
    except Exception:
        pass
    for cand in ["192.168.76.1", "192.168.73.2", "192.168.1.1"]:
        if test_port(cand, 80) or test_port(cand, 22):
            return cand
    return "192.168.76.1"

def run_telnet_cmd(tn, cmd, timeout=5):
    tn.write(cmd + "\n")
    time.sleep(0.3)
    return tn.read_until("/ # ", timeout=timeout).decode(errors="replace")

def safe_input(prompt=""):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return None

def status_remoto(ip):
    active_telnet = test_port(ip, 23, timeout=1.2)
    active_ssh    = test_port(ip, 22, timeout=1.2)
    active_http   = test_port(ip, 80, timeout=1.2)

    print(f"\n[*] Status de Acesso Remoto em {C_CYAN}{ip}{C_RESET}:")
    t_tag = f"{C_GREEN}[ATIVO / ABERTO]{C_RESET}" if active_telnet else f"{C_WHITE}[DESATIVADO / FECHADO]{C_RESET}"
    s_tag = f"{C_GREEN}[ATIVO / ABERTO]{C_RESET}" if active_ssh else f"{C_RED}[DESATIVADO / FECHADO]{C_RESET}"
    h_tag = f"{C_GREEN}[ATIVO / ABERTO]{C_RESET}" if active_http else f"{C_WHITE}[INATIVO]{C_RESET}"
    print(f"    - Telnet (Porta 23) : {t_tag}")
    print(f"    - SSH    (Porta 22) : {s_tag}")
    print(f"    - Web    (Porta 80) : {h_tag}")

    if active_telnet:
        print(f"\n{C_YELLOW}{C_BOLD}[!] ALERTA DE SEGURANCA:{C_RESET}")
        print(f"{C_YELLOW}    Sua porta Telnet (23) esta ATIVA na sua rede local!{C_RESET}")
        print(f"{C_YELLOW}    A porta Telnet permite acesso root imediato sem senha.{C_RESET}")
        print(f"{C_YELLOW}    Se voce ja fez tudo que precisava, DESATIVE-A na opcao [1] (Hardening)!{C_RESET}")
    else:
        print(f"\n{C_GREEN}[OK] HARDENING DE SEGURANCA ATIVO:{C_RESET}")
        print(f"{C_GREEN}    A porta Telnet (23) esta fechada e segura.{C_RESET}")
        print(f"{C_GREEN}    O acesso administrativo e restrito exclusivamente ao SSH (porta 22).{C_RESET}")

    return {"telnet": active_telnet, "ssh": active_ssh, "http": active_http}

def desativar_telnet(ip):
    print(f"\n[*] Conectando em {ip}:23 para desativar Telnet...")
    if not test_port(ip, 23):
        print(f"{C_YELLOW}[-] A porta Telnet (23) ja esta fechada ou inacessivel!{C_RESET}")
        return

    try:
        tn = Telnet(ip, 23, timeout=5)
        tn.read_until("/ # ", timeout=3)
        print("    [+] Conectado como root.")
        print("    [*] Removendo inicializacao do Telnet de /etc/rc.local e crontabs...")
        run_telnet_cmd(tn, "sed -i '/telnetd/d' /etc/rc.local /etc/crontabs/Admin /etc/crontabs/root 2>/dev/null")
        run_telnet_cmd(tn, "sync")
        print("    [*] Finalizando processos telnetd em execucao...")
        run_telnet_cmd(tn, "killall -9 telnetd 2>/dev/null")
        tn.close()
    except Exception as e:
        print(f"{C_RED}[-] Erro ao executar desativacao via Telnet: {e}{C_RESET}")
        return

    time.sleep(1.2)
    if not test_port(ip, 23):
        print(f"\n{C_GREEN}[OK] Telnet DESATIVADO com sucesso!{C_RESET}")
        print(f"     A porta 23 foi fechada. Seu roteador agora responde exclusivamente via SSH (porta 22).")
    else:
        print(f"\n{C_YELLOW}[!] Aviso: A porta 23 ainda parece responder. Verifique se o processo foi reiniciado pelo watchdog.{C_RESET}")

def reativar_telnet_ssh(ip):
    print(f"\n[*] Solicitacao de Reativacao do Telnet em {ip}...")
    if test_port(ip, 23):
        print(f"{C_GREEN}[OK] A porta Telnet (23) JA ESTA ATIVA e respondendo! Nenhuma acao necessaria.{C_RESET}")
        return

    if not test_port(ip, 22):
        print(f"{C_RED}[-] A porta SSH (22) nao esta respondendo em {ip}! Impossivel conectar remotamente.{C_RESET}")
        return

    print(f"    Como deseja reativar o Telnet?")
    print(f"    [1] Temporario (Ativo agora ate o proximo reboot)")
    print(f"    [2] Permanente (Ativo agora e adicionado ao boot em /etc/rc.local)")
    print(f"    [0] Cancelar")

    escolha = None
    while escolha not in ["1", "2", "0"]:
        escolha = safe_input("    Escolha [1/2/0]: ")
        if escolha not in ["1", "2", "0"]:
            print(f"    {C_YELLOW}[!] Digite 1 para Temporario, 2 para Permanente ou 0 para Cancelar.{C_RESET}")

    if escolha == "0":
        print("    [*] Operacao cancelada.")
        return

    if escolha == "1":
        remote_cmd = "/usr/sbin/telnetd -l /bin/ash"
        print(f"\n    [*] Executando ativacao temporaria via SSH...")
    else:
        remote_cmd = "grep -q telnetd /etc/rc.local || sed -i '/exit 0/i /usr/sbin/telnetd -l /bin/ash &' /etc/rc.local; sync; /usr/sbin/telnetd -l /bin/ash"
        print(f"\n    [*] Executando ativacao permanente no boot via SSH...")

    print(f"    {C_CYAN}[Dica] Se for solicitada senha no terminal, a senha padrao e: root{C_RESET}")
    ssh_cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"root@{ip}",
        remote_cmd
    ]

    try:
        res = subprocess.run(ssh_cmd, timeout=20)
        time.sleep(1.5)
        if test_port(ip, 23):
            print(f"\n{C_GREEN}[OK] Porta Telnet (23) REATIVADA COM SUCESSO!{C_RESET}")
            print(f"     Voce pode agora conectar no roteador via: telnet {ip}")
        else:
            print(f"\n{C_YELLOW}[!] O comando SSH foi executado, mas a porta 23 ainda nao respondeu.{C_RESET}")
    except subprocess.TimeoutExpired:
        print(f"{C_RED}[-] Tempo limite esgotado ao executar comando SSH.{C_RESET}")
    except Exception as e:
        print(f"{C_RED}[-] Erro ao invocar cliente SSH do sistema: {e}{C_RESET}")

def encontrar_ou_gerar_chave_ssh():
    ssh_dir = os.path.expanduser("~/.ssh")
    os.makedirs(ssh_dir, exist_ok=True)

    candidatas = [
        os.path.join(ssh_dir, "id_ed25519.pub"),
        os.path.join(ssh_dir, "id_rsa.pub"),
        os.path.join(ssh_dir, "id_ecdsa.pub")
    ]
    outras = glob.glob(os.path.join(ssh_dir, "*.pub"))
    for o in outras:
        if o not in candidatas:
            candidatas.append(o)

    existentes = [p for p in candidatas if os.path.isfile(p)]

    if existentes:
        print(f"\n[*] Chaves publicas encontradas no seu PC:")
        for idx, k in enumerate(existentes, 1):
            print(f"    [{idx}] {k}")
        print(f"    [N] Gerar uma nova chave Ed25519 dedicada para o roteador")

        while True:
            sel = safe_input(f"    Selecione a chave a ser usada [1-{len(existentes)} ou N]: ")
            if not sel:
                print(f"    {C_YELLOW}[!] Por favor, selecione uma opcao.{C_RESET}")
                continue
            if sel.lower() == "n":
                break
            if sel.isdigit() and 1 <= int(sel) <= len(existentes):
                chosen_pub = existentes[int(sel) - 1]
                with open(chosen_pub, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read().strip(), chosen_pub
            print(f"    {C_YELLOW}[!] Opcao invalida. Digite um numero de 1 a {len(existentes)} ou N.{C_RESET}")

    # Gerar nova chave Ed25519
    new_key = os.path.join(ssh_dir, "id_ed25519")
    if os.path.isfile(new_key):
        new_key = os.path.join(ssh_dir, "predator_t7_ed25519")

    print(f"\n[*] Gerando nova chave Ed25519 de alta seguranca em: {new_key}...")
    keygen_cmd = ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", new_key, "-C", f"predator-t7-admin@{platform.node()}"]
    try:
        subprocess.run(keygen_cmd, check=True)
    except Exception as e:
        print(f"{C_RED}[-] Falha ao gerar chave com ssh-keygen: {e}{C_RESET}")
        return None, None

    pub_file = new_key + ".pub"
    if os.path.isfile(pub_file):
        with open(pub_file, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip(), pub_file
    return None, None

def importar_chave_ssh(ip):
    print(f"\n" + "=" * 65)
    print("  IMPORTAR CHAVE PUBLICA SSH PARA O ROTEADOR (LOGIN SEM SENHA)")
    print("=" * 65)
    print("  Como funciona:")
    print("  - O Dropbear (servidor SSH do OpenWrt) valida chaves em /etc/dropbear/authorized_keys.")
    print("  - Quando a sua chave publica estiver gravada la, o seu PC conecta")
    print("    instantaneamente via terminal SSH sem pedir senha.")
    print("  - Se a porta 23 (Telnet) estiver ativa agora, a injecao e 100% automatica!")

    pub_content, pub_path = encontrar_ou_gerar_chave_ssh()
    if not pub_content:
        print(f"{C_RED}[-] Nenhuma chave publica disponivel para importacao.{C_RESET}")
        return

    print(f"\n[+] Chave selecionada: {C_CYAN}{pub_path}{C_RESET}")
    print(f"    Previa da chave: {pub_content[:60]}... {pub_content.split()[-1] if len(pub_content.split()) > 2 else ''}")

    conf = ""
    while conf not in ["s", "n"]:
        conf = safe_input(f"\n[?] Confirma injetar esta chave publica em /etc/dropbear/authorized_keys no roteador ({ip})? [S/N]: ").lower()
        if conf not in ["s", "n"]:
            print(f"{C_YELLOW}[!] Por favor, digite S para confirmar ou N para cancelar.{C_RESET}")

    if conf == "n":
        print("[*] Operacao cancelada pelo usuario.")
        return

    # Injetar via Telnet (se disponivel - 0 prompts de senha)
    if test_port(ip, 23):
        print(f"\n[*] Injetando chave via Telnet na porta 23 (Conexao root direta)...")
        try:
            tn = Telnet(ip, 23, timeout=5)
            tn.read_until("/ # ", timeout=3)
            run_telnet_cmd(tn, "mkdir -p /etc/dropbear && chmod 700 /etc/dropbear")
            # Adicionar chave evitando duplicatas
            sanitized_key = pub_content.replace("'", "'\\''")
            cmd_inject = (
                f"grep -q -F '{sanitized_key}' /etc/dropbear/authorized_keys 2>/dev/null || "
                f"echo '{sanitized_key}' >> /etc/dropbear/authorized_keys"
            )
            run_telnet_cmd(tn, cmd_inject)
            run_telnet_cmd(tn, "chmod 600 /etc/dropbear/authorized_keys")
            run_telnet_cmd(tn, "sync")
            tn.close()
            print(f"{C_GREEN}[OK] Chave gravada com sucesso em /etc/dropbear/authorized_keys!{C_RESET}")
        except Exception as e:
            print(f"{C_RED}[-] Falha na gravacao via Telnet: {e}{C_RESET}")
            return
    elif test_port(ip, 22):
        print(f"\n[*] Telnet fechado. Injetando chave via conexao SSH na porta 22...")
        print(f"    {C_CYAN}[Dica] Se o SSH pedir senha para autorizar o envio, digite: root{C_RESET}")
        sanitized_key = pub_content.replace("'", "'\\''")
        remote_script = (
            f"mkdir -p /etc/dropbear && chmod 700 /etc/dropbear && "
            f"(grep -q -F '{sanitized_key}' /etc/dropbear/authorized_keys 2>/dev/null || "
            f"echo '{sanitized_key}' >> /etc/dropbear/authorized_keys) && "
            f"chmod 600 /etc/dropbear/authorized_keys && sync"
        )
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            f"root@{ip}",
            remote_script
        ]
        try:
            subprocess.run(ssh_cmd, check=True)
            print(f"{C_GREEN}[OK] Chave gravada com sucesso via SSH!{C_RESET}")
        except Exception as e:
            print(f"{C_RED}[-] Falha ao enviar chave via SSH: {e}{C_RESET}")
            return
    else:
        print(f"{C_RED}[-] Nem Telnet (23) nem SSH (22) estao acessiveis no roteador ({ip}).{C_RESET}")
        return

    # Testar login SSH com chave
    print(f"\n[*] Testando login SSH autenticado por chave (sem requisicao de senha)...")
    test_ssh_cmd = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=4",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"root@{ip}",
        "echo AUTH_KEY_SUCCESS"
    ]
    try:
        proc = subprocess.run(test_ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
        if "AUTH_KEY_SUCCESS" in proc.stdout:
            print(f"{C_GREEN}{C_BOLD}[SUCESSO ABSOLUTO] Login por chave SSH confirmado!{C_RESET}")
            print(f"                  Voce agora acessa o terminal digitando: ssh root@{ip} (sem senha)!")
        else:
            print(f"{C_YELLOW}[!] A chave foi gravada. Teste o acesso manual digitando: ssh root@{ip}{C_RESET}")
    except Exception:
        print(f"{C_YELLOW}[!] A chave foi gravada no roteador. Teste manualmente com: ssh root@{ip}{C_RESET}")

def main():
    explicit_ip = None
    action = None
    for arg in sys.argv[1:]:
        if arg in ["status", "desativar", "ativar"]:
            action = arg
        elif "." in arg or arg.startswith("--ip="):
            explicit_ip = arg.replace("--ip=", "").strip()

    router_ip = detect_router_ip(explicit_ip)

    print("=" * 65)
    print("  GERENCIADOR DE ACESSO TELNET & SSH - HARDENING DE SEGURANCA")
    print(f"  Roteador Alvo: {C_CYAN}{router_ip}{C_RESET}")
    print("=" * 65)

    if action:
        if action == "status":
            status_remoto(router_ip)
        elif action == "desativar":
            desativar_telnet(router_ip)
        elif action == "ativar":
            reativar_telnet_ssh(router_ip)
        return

    while True:
        status_info = status_remoto(router_ip)
        is_active = status_info["telnet"]

        print(f"\n{C_BOLD}Escolha uma opcao:{C_RESET}")
        if is_active:
            print(f"  [1] {C_YELLOW}Desativar Telnet agora (Hardening - fechar porta 23 e manter apenas SSH){C_RESET}")
        else:
            print(f"  [1] Telnet ja esta DESATIVADO (Hardening Ativo)")
        print(f"  [2] Reativar Telnet via SSH (executar telnetd remotamente)")
        print(f"  [3] Importar Chave SSH do seu PC para o Roteador (Login sem senha)")
        print(f"  [4] Re-testar e atualizar status das portas (Telnet / SSH)")
        print(f"  [0] Sair / Voltar ao menu principal")

        opt = None
        while opt not in ["1", "2", "3", "4", "0"]:
            opt = safe_input(f"\nOpcao [0-4]: ")
            if opt not in ["1", "2", "3", "4", "0"]:
                print(f"{C_YELLOW}[!] Opcao invalida. Digite 1, 2, 3, 4 ou 0 para prosseguir.{C_RESET}")

        if opt == "1":
            if is_active:
                conf = ""
                while conf not in ["s", "n"]:
                    conf = safe_input(f"\n[?] Confirma fechar a porta 23 (Telnet) e manter apenas SSH em {router_ip}? [S/N]: ").lower()
                    if conf not in ["s", "n"]:
                        print(f"{C_YELLOW}[!] Por favor, digite S para SIM ou N para NAO.{C_RESET}")
                if conf == "s":
                    desativar_telnet(router_ip)
                else:
                    print("[*] Operacao cancelada pelo usuario.")
            else:
                print(f"\n{C_GREEN}[OK] O servico Telnet ja esta desativado no roteador ({router_ip}). Nenhuma acao necessaria.{C_RESET}")
            safe_input("\nPressione ENTER para voltar ao menu...")
        elif opt == "2":
            reativar_telnet_ssh(router_ip)
            safe_input("\nPressione ENTER para voltar ao menu...")
        elif opt == "3":
            importar_chave_ssh(router_ip)
            safe_input("\nPressione ENTER para voltar ao menu...")
        elif opt == "4":
            print(f"\n[*] Re-testando conexoes em {router_ip}...")
            time.sleep(0.4)
            continue
        elif opt == "0":
            print("\n[*] Retornando ao menu principal...")
            break

if __name__ == "__main__":
    main()
