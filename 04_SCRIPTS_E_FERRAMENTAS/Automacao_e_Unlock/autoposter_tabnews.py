#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TABNEWS AUTO-POSTER - 100% AUTOMATIZADO
Posta automaticamente no TabNews via API oficial (sem copiar/colar nada).
=============================================================================
"""

import sys
import io
import getpass
import argparse
import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

TABNEWS_API = "https://www.tabnews.com.br/api/v1"

TITULO = "Reverse-Engineered Acer FOTA & Stock Firmware Extractor: Como extraí firmwares oficiais de fábrica direto da AWS S3"
SOURCE_URL = "https://github.com/Despensativo/acer-predator-fota-extractor"

CONTEUDO_TABNEWS = """Fala pessoal do TabNews!

Recentemente comecei a trabalhar no porte do **OpenWrt** para o roteador **Acer Predator Connect T7** (um dos primeiros roteadores Wi-Fi 7 BE11000 com o SoC Qualcomm IPQ5332 lançados no mercado nacional). Durante o projeto, também analisei o seu antecessor, o **Predator Connect W6x** (baseado no chip MediaTek MT7986 Filogic 830).

Rapidamente esbarrei em um problema crônico e bem frustrante da Acer: **a fabricante não disponibiliza arquivos de firmware (.bin / .img) para download no seu site de suporte**.

Se um usuário brickar o aparelho tentando instalar um sistema customizado, precisar restaurar o roteador para o padrão de fábrica, ou se desenvolvedores precisarem extrair as partições SquashFS, arquivos Device Tree (DTB) e blobs binários de Wi-Fi, eles ficam completamente no escuro.

Para resolver isso, decidi investigar como o roteador se atualizava sozinho. Fiz a engenharia reversa no cliente de atualização OTA (`/usr/bin/fota`) presente na partição SquashFS e mapeei todo o ecossistema na nuvem da Acer.

O resultado foi a criação de uma ferramenta em Python 100% autônoma, de código aberto, chamada **`acer_fota_extractor.py`**, que permite consultar a nuvem da Acer e baixar qualquer ROM oficial diretamente de buckets pré-assinados da **Amazon AWS S3**.

Abaixo compartilho todos os detalhes técnicos da descoberta, como o protocolo funciona e o que o script faz por baixo dos panos.

---

### 1. Como funciona a Nuvem de Atualização da Acer (Engenharia Reversa)

Ao decompilar o binário `/usr/bin/fota` e analisar as chamadas de rede e rotinas criptográficas, o fluxo revelou-se bastante metódico:

1. **Sincronização de Relógio do Servidor:**  
   O binário faz um `GET https://connect-ota.acervcon.com/now` para obter o timestamp Unix oficial em segundos. Qualquer descompasso no relógio invalida a requisição.
   
2. **Criptografia do Token de Autorização (`auth-token`):**  
   Todas as requisições para a API exigem um header HTTP chamado `auth-token`.  
   * **Algoritmo:** AES-256 no modo CBC com preenchimento (padding) PKCS#7.
   * **Payload interno:** Um JSON serializado contendo `{"project": "<codigo_modelo>", "sn": "<numero_serie>", "time": <timestamp_unix>}`.
   * **Chaves:** A chave simétrica de 256 bits e o vetor de inicialização (IV) de 16 bytes estavam compilados diretamente no binário.

3. **Matriz Estrita de Transição de Versões (`POST https://connect-ota.acervcon.com/fota/query`):**  
   O backend da Acer **não aceita consultas abertas, nem wildcards (`*`) ou listagens globais**.  
   Ele funciona como um autômato finito / grafo dirigido de atualizações: você precisa enviar a versão exata de origem que está rodando no roteador (por exemplo, `1.00.000007`).  
   O servidor consulta sua tabela de transições e devolve:
   * A nova versão de destino disponível (ex: `1.00.000010`).
   * Tamanho exato em bytes.
   * Hash MD5 oficial gerado na compilação da Acer.
   * **Uma URL pré-assinada da Amazon AWS S3 com validade temporária de 300 segundos**.
   * Notas de versão e changelogs reais registrados pelos engenheiros da Acer.

---

### 2. O que o Script (`acer_fota_extractor.py`) faz na prática

Em vez de exigir que a pessoa tenha o roteador conectado na rede ou configure interceptadores de proxy, o script é uma ferramenta CLI completamente autônoma desenvolvida em Python 3:

* **100% Standalone:** Roda em qualquer máquina com Windows, Linux ou macOS. Não precisa estar conectado ao roteador e nem mesmo ter o roteador em mãos para baixar as ROMs.
* **Dois Modos de Operação:**
  1. **Assistente Interativo no Terminal:** Apresenta um menu guiado em ASCII onde você escolhe o modelo (Predator T7, W6x, X7 ou Qualquer Modelo Customizado), seleciona a região e o serial.
  2. **Modo CLI / Automação:** Permite passar flags diretas (`--model`, `--version`, `--sn`, `--download`, `--all`) para ser integrado em pipelines ou scripts em lote.
* **Download em Chunks com Barra de Progresso:** Conecta no link pré-assinado da AWS S3 e baixa arquivos de dezenas de megabytes com tratamento de interrupção e progresso em tempo real.
* **Verificação Automática de Integridade (MD5):** Ao término do download, o script calcula o hash MD5 do arquivo baixado e compara byte a byte com o hash fornecido pela Acer, garantindo que o arquivo não venha corrompido.
* **Organização Inteligente de Pastas:** Cria automaticamente a estrutura de diretórios organizada por modelo e região: `./downloads/<Nome_Do_Modelo>/...`.
* **Extração de Changelogs Ocultos:** Revela notas de versão oficiais que muitas vezes não aparecem nas interfaces web (por exemplo, descobrimos que a versão `1.01.000015` do W6x implementou suporte a VLAN ID de operadoras).

---

### 3. Estrutura das ROMs da Acer (FIT Images)

Os arquivos `.bin` baixados são imagens no padrão **U-Boot FIT (Flattened Image Tree)**. Dentro de cada imagem encontramos:

* `kernel@1`: O kernel Linux oficial ARM64 compilado pela fabricante.
* `fdt@1`: O Device Tree Blob (`.dtb`) compilado, contendo todo o mapeamento de pinos, portas Ethernet e partições de memória.
* `rootfs@1`: Sistema de arquivos SquashFS original com scripts de inicialização e drivers proprietários de Wi-Fi 7 e Wi-Fi 6.

Para quem quiser inspecionar ou extrair componentes da imagem:
```bash
# Extrair o kernel
dumpimage -T flat_dt -p 0 -o kernel.bin firmware_oficial.bin

# Extrair a árvore de dispositivos (Device Tree)
dumpimage -T flat_dt -p 1 -o devicetree.dtb firmware_oficial.bin

# Ou extrair todo o sistema com binwalk
binwalk -e firmware_oficial.bin
```

---

### 4. Modelos e Versões já Mapeados e Testados

| Modelo | Chipset | Região | Versão Base | Versão Baixada | Status / Observações |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Acer Predator Connect T7** | Qualcomm IPQ5332 (Wi-Fi 7 BE11000) | BR / Global | `1.00.000007` | `1.00.000010` | Validado e baixado via AWS |
| **Acer Predator Connect T7** | Qualcomm IPQ5332 (Wi-Fi 7 BE11000) | Região US | `1.00.000003` | `1.00.000010` | Validado e baixado via AWS |
| **Acer Predator Connect W6x** | MediaTek MT7986 (Filogic 830 Wi-Fi 6) | Global | `1.00.000008` | `1.01.000015` | Validado (adicionou VLAN ID) |
| **Acer Predator Connect X7** | Qualcomm IPQ5332 + 5G CPE | Global | Base de fábrica | Ativo na nuvem | Handshake validado |
| **Outros Modelos Acer** | Qualquer modelo | Qualquer região | Info da etiqueta | Consulta na nuvem | Suporte via código e serial |

---

### 5. Como Executar no seu Computador

```bash
# 1. Clonar o repositório
git clone https://github.com/Despensativo/acer-predator-fota-extractor.git
cd acer-predator-fota-extractor

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar o assistente
python acer_fota_extractor.py
```

Ou baixar diretamente via linha de comando:
```bash
python acer_fota_extractor.py --model "Acer Predator Connect T7" --version "1.00.000007" --download
```

---

### 6. Repositório Aberto e Contribuições

O projeto está disponível sob a licença MIT no GitHub:  
👉 **https://github.com/Despensativo/acer-predator-fota-extractor**

Se você tem algum roteador da Acer (como o Predator W6 clássico, o X5 5G ou roteadores corporativos da marca), basta olhar a etiqueta na parte inferior do aparelho, pegar o código de modelo e serial e testar no script. Pull requests com novas versões e testes de hardware são muito bem-vindos!
"""

def autenticar(email, password):
    print(f"[*] Autenticando usuário {email} no TabNews...")
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TabNewsAutoPoster/1.0"
    })
    
    url = f"{TABNEWS_API}/sessions"
    payload = {"email": email, "password": password}
    
    res = session.post(url, json=payload)
    if res.status_code == 201:
        data = res.json()
        token = data.get("token") or res.cookies.get("session_id")
        print(f"[+] Autenticação realizada com sucesso!")
        return session, token
    else:
        try:
            err = res.json()
            msg = err.get("message", res.text)
        except Exception:
            msg = res.text
        print(f"[-] Erro ao autenticar: {msg}")
        return None, None

def publicar_conteudo(session, token, titulo=TITULO, corpo=CONTEUDO_TABNEWS, source_url=SOURCE_URL):
    print(f"[*] Publicando artigo no TabNews...")
    url = f"{TABNEWS_API}/contents"
    
    payload = {
        "title": titulo,
        "body": corpo,
        "status": "published",
        "source_url": source_url
    }
    
    # Injeta cookie de sessão se necessário
    if token:
        session.cookies.set("session_id", token, domain="tabnews.com.br")
    
    res = session.post(url, json=payload)
    if res.status_code == 201:
        data = res.json()
        owner = data.get("owner_username")
        slug = data.get("slug")
        link = f"https://www.tabnews.com.br/{owner}/{slug}"
        print(f"\n" + "="*60)
        print(f"🎉 SUCESSO! Artigo publicado automaticamente!")
        print(f"🔗 Link direto: {link}")
        print("="*60 + "\n")
        return link
    else:
        try:
            err = res.json()
            msg = err.get("message", res.text)
        except Exception:
            msg = res.text
        print(f"[-] Falha na publicação (Status {res.status_code}): {msg}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Publicador automático no TabNews")
    parser.add_argument("--email", "-e", help="E-mail da conta TabNews")
    parser.add_argument("--password", "-p", help="Senha da conta TabNews")
    parser.add_argument("--token", "-t", help="Token ou session_id do TabNews caso já possua")
    args = parser.parse_args()
    
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TabNewsAutoPoster/1.0"
    })
    
    token = args.token
    if token:
        session.cookies.set("session_id", token, domain="tabnews.com.br")
    elif args.email and args.password:
        session, token = autenticar(args.email, args.password)
        if not session:
            sys.exit(1)
    else:
        print("\n=== PUBLICADOR AUTOMÁTICO TABNEWS ===")
        print("Digite suas credenciais do TabNews (sua senha não será exibida na tela):")
        email = input("E-mail: ").strip()
        password = getpass.getpass("Senha: ").strip()
        
        session, token = autenticar(email, password)
        if not session:
            sys.exit(1)
            
    publicar_conteudo(session, token)

if __name__ == "__main__":
    main()
