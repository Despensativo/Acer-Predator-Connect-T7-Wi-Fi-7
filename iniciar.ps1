# ===========================================================================
# iniciar.ps1 - Assistente Interativo Universal & One-Liner do GitHub
# Acer Predator Connect T7 (IPQ5332) & X7 (Pesquisa)
# Suporte: Local (.ps1 / .bat) e Remoto via 'irm https://... | iex'
# ===========================================================================

param(
    [string]$Lang = ""
)

$ErrorActionPreference = "Continue"

# Cores e Formatacao
function Write-Header($text) {
    Write-Host ""
    Write-Host "===========================================================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor Cyan
}

function Write-Info($text)    { Write-Host "  [*] $text" -ForegroundColor Cyan }
function Write-Success($text) { Write-Host "  [OK] $text" -ForegroundColor Green }
function Write-Warn($text)    { Write-Host "  [!] $text" -ForegroundColor Yellow }
function Write-Err($text)     { Write-Host "  [-] $text" -ForegroundColor Red }

$RawBase = "https://raw.githubusercontent.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/main"

# 1. Resolver Diretorio Base (Local vs Web One-Liner)
$RepoDir = $PSScriptRoot
if (-not $RepoDir -or -not (Test-Path "$RepoDir\Scripts_Automacao")) {
    if (Test-Path ".\Scripts_Automacao") {
        $RepoDir = (Get-Item ".").FullName
    } elseif (Test-Path ".\04_SCRIPTS_E_FERRAMENTAS\Automacao_e_Unlock") {
        $RepoDir = (Get-Item ".").FullName
    } else {
        # Executado via One-Liner do GitHub
        $TargetDir = "$env:USERPROFILE\Acer-Predator-Connect-T7"
        if (-not (Test-Path $TargetDir)) {
            New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
        }
        $RepoDir = $TargetDir
    }
}

# 2. Selecao de Idioma
if (-not $Lang) {
    Clear-Host
    Write-Host "===========================================================================" -ForegroundColor Cyan
    Write-Host "             ACER PREDATOR CONNECT T7 & X7 - WIZARD & SUITE                " -ForegroundColor White
    Write-Host "===========================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Select Language / Selecione o Idioma:" -ForegroundColor Gray
    Write-Host "  [1] English (Default - Press ENTER)" -ForegroundColor White
    Write-Host "  [2] Portugues (Brasil)" -ForegroundColor White
    Write-Host ""
    $LangChoice = Read-Host "  Choice / Escolha [1/2] (Default: 1)"
    if ($LangChoice -eq "2" -or $LangChoice -like "pt*") {
        $Lang = "pt"
    } else {
        $Lang = "en"
    }
}

# Dicionario Bilingue
$T = @{
    "en" = @{
        "title"              = "ACER PREDATOR CONNECT T7 & X7 - INTERACTIVE WIZARD"
        "detecting"          = "Detecting local network and router..."
        "gateway_found"      = "Router detected at IP: {0}"
        "port_web"           = "Web GUI (Port 80) : {0}"
        "port_telnet"        = "Telnet  (Port 23) : {0}"
        "port_ssh"           = "SSH     (Port 22) : {0}"
        "triage_title"       = "CURRENT STEP: DO YOU ALREADY HAVE ROOT ACCESS?"
        "triage_q"           = "Do you already have root / SSH access unlocked on this router?"
        "triage_yes"         = "[Y] YES - I already restored .cfg and Telnet/SSH is active"
        "triage_no"          = "[N] NO  - My router is still factory locked (I need to unlock)"
        "triage_prompt"      = "Your choice [Y/N] (Default: {0})"
        "unlock_header"      = "STEP-BY-STEP ROOT UNLOCK (SAFE & FAST)"
        "unlock_desc"        = "The unlock is 100% safe and DOES NOT flash NAND memory.`n  It only enables SSH/Telnet inside a config backup (.cfg) that you restore via Acer Web GUI."
        "choose_cfg"         = "How would you like to prepare your unlock file?"
        "cfg_opt1"           = "[1] Use Universal Ready-Made v27 CFG (Fastest - 1 Click)"
        "cfg_opt1_desc"      = "    - Copies unlock file directly to your Desktop`n    - Unlocks Telnet (no pass) and SSH ('root' / 'root')`n    - Wi-Fi: Predator_T7 / Password: predator123"
        "cfg_opt2"           = "[2] Unlock YOUR OWN Current Backup (Keeps your current Wi-Fi and Passwords)"
        "cfg_opt2_desc"      = "    - Download your current config.cfg from Acer Web GUI`n    - Injects root while keeping all your Wi-Fi SSIDs and settings"
        "cfg_prompt"         = "Choose option [1/2] (Default: 1)"
        "wifi_info_header"   = "DEFAULT WI-FI CREDENTIALS AFTER UNLOCK"
        "wifi_info_desc"     = "When your router reboots, reconnect to your Wi-Fi using:`n    - Networks: Predator_T7_2.4GHz / Predator_T7_5GHz / Predator_T7_6GHz`n    - Password: predator123`n    - Web / Root Password: root"
        "copying_cfg"        = "Preparing unlock config for your Desktop..."
        "cfg_copied"         = "Unlock file saved at: {0}"
        "own_cfg_prompt"     = "Drag & Drop or type the path to your downloaded config.cfg: "
        "step_download_backup" = "To download your current backup: open http://{0} in your browser and go to: System -> Backup and restore."
        "patching_cfg"       = "Injecting root & Telnet into your backup..."
        "instructions"       = "STEPS TO RESTORE AND ACTIVATE ROOT:"
        "step1"              = "1. In your browser, open the Acer Web GUI: http://{0}"
        "step2"              = "2. Log in and go to: System -> Backup and restore"
        "step3"              = "3. Under 'Restore backup', click 'Browse' and select:"
        "step4"              = "4. Click 'Restore' and confirm."
        "press_enter_rst"    = "Press ENTER AFTER you clicked 'Restore' in your browser..."
        "waiting_reboot"     = "Waiting for router to reboot and open Telnet root port (takes ~60-90s)..."
        "attempt"            = "Testing connection to {0}:23 [Attempt {1}/{2}]..."
        "reboot_success"     = "TELNET PORT 23 CONNECTED! ROUTER SUCCESSFULLY UNLOCKED WITH ROOT!"
        "reboot_timeout"     = "Timeout waiting for port 23. If the router is still booting, please wait a moment."
        "launching_suite"    = "Launching Master Management Suite..."
        "checking_python"    = "Checking Python 3 environment..."
        "python_ok"          = "Python 3 detected: {0}"
        "python_missing"     = "Python 3 not found. Installing Python 3.14 via WinGet..."
    }
    "pt" = @{
        "title"              = "ACER PREDATOR CONNECT T7 & X7 - ASSISTENTE INTERATIVO"
        "detecting"          = "Detectando rede local e roteador..."
        "gateway_found"      = "Roteador detectado no IP: {0}"
        "port_web"           = "Painel Web (Porta 80) : {0}"
        "port_telnet"        = "Telnet     (Porta 23) : {0}"
        "port_ssh"           = "SSH        (Porta 22) : {0}"
        "triage_title"       = "ETAPA ATUAL: VOCE JA TEM ACESSO ROOT?"
        "triage_q"           = "Voce ja possui acesso ROOT / SSH liberado no roteador?"
        "triage_yes"         = "[S] SIM - Ja restaurei o .cfg e o Telnet/SSH esta ativo"
        "triage_no"          = "[N] NAO - Meu roteador ainda esta com o firmware original travado de fabrica"
        "triage_prompt"      = "Escolha [S/N] (Padrao: {0})"
        "unlock_header"      = "DESBLOQUEIO DE ACESSO ROOT PASSO A PASSO (SEGURO E RAPIDO)"
        "unlock_desc"        = "O desbloqueio e 100% seguro e NAO grava particoes da flash.`n  Ele apenas ativa o terminal SSH/Telnet em um backup (.cfg) restaurado pelo painel da Acer."
        "choose_cfg"         = "Como voce prefere gerar o seu arquivo de desbloqueio?"
        "cfg_opt1"           = "[1] Usar CFG Pronto Universal v27 (Mais Rapido - 1 Clique)"
        "cfg_opt1_desc"      = "    - Copia o arquivo pronto direto para sua Area de Trabalho`n    - Ativa Telnet sem senha e SSH com usuario 'root' / senha 'root'`n    - Wi-Fi: Predator_T7 / Senha: predator123"
        "cfg_opt2"           = "[2] Desbloquear o SEU PROPRIO backup atual (Mantem seu Wi-Fi e Senhas)"
        "cfg_opt2_desc"      = "    - Voce baixa o config.cfg pelo painel da Acer`n    - O script injeta o root mantendo todas as suas redes e senhas de Wi-Fi"
        "cfg_prompt"         = "Escolha a opcao [1/2] (Padrao: 1)"
        "wifi_info_header"   = "CREDENCIAIS DO WI-FI APOS O DESBLOQUEIO"
        "wifi_info_desc"     = "Quando o roteador reiniciar, reconecte no seu Wi-Fi com:`n    - Redes:    Predator_T7_2.4GHz / Predator_T7_5GHz / Predator_T7_6GHz`n    - Senha:    predator123`n    - Senha do Painel (Root): root"
        "copying_cfg"        = "Preparando arquivo de desbloqueio para sua Area de Trabalho..."
        "cfg_copied"         = "Arquivo de desbloqueio salvo em: {0}"
        "own_cfg_prompt"     = "Arraste e solte ou digite o caminho do seu config.cfg baixado: "
        "step_download_backup" = "Para baixar seu backup atual: abra http://{0} no navegador e acesse: System -> Backup and restore."
        "patching_cfg"       = "Injetando root e Telnet no seu backup..."
        "instructions"       = "PASSO A PASSO PARA RESTAURAR E ATIVAR O ROOT:"
        "step1"              = "1. No seu navegador, abra o painel da Acer: http://{0}"
        "step2"              = "2. Faca login e acesse: System -> Backup and restore"
        "step3"              = "3. Na opcao 'Restore backup', clique em 'Procurar' e selecione:"
        "step4"              = "4. Clique no botao 'Restore' / 'Restaurar'."
        "press_enter_rst"    = "Pressione ENTER DEPOIS que tiver clicado em Restaurar no navegador..."
        "waiting_reboot"     = "Aguardando o roteador reiniciar e abrir a porta de root (Telnet) (~60-90s)..."
        "attempt"            = "Testando conexao em {0}:23 [Tentativa {1}/{2}]..."
        "reboot_success"     = "PORTA 23 (TELNET) CONECTADA! ROTEADOR DESBLOQUEADO COM SUCESSO!"
        "reboot_timeout"     = "Tempo limite esgotado. Se o roteador ainda estiver reiniciando, aguarde mais um instante."
        "launching_suite"    = "Iniciando Central de Gerenciamento do Predator T7..."
        "checking_python"    = "Verificando ambiente Python 3..."
        "python_ok"          = "Python 3 detectado: {0}"
        "python_missing"     = "Python 3 nao encontrado. Instalando Python 3.14 via WinGet..."
    }
}

$M = $T[$Lang]

# Funcao de Teste de Porta TCP
function Test-Port($ip, $port, $timeoutMs = 800) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect($ip, $port, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne($timeoutMs, $false)
        if ($wait -and $tcp.Connected) {
            $tcp.EndConnect($iar)
            $tcp.Close()
            return $true
        }
        $tcp.Close()
        return $false
    } catch {
        return $false
    }
}

# 3. Detectar IP do Roteador
Clear-Host
Write-Header $M["title"]
Write-Info $M["detecting"]

$Candidates = @("192.168.76.1", "192.168.73.2", "192.168.1.1")
try {
    $gw = (Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue | Select-Object -First 1).NextHop
    if ($gw -and $gw -notin $Candidates) {
        $Candidates = @($gw) + $Candidates
    }
} catch {}

$RouterIP = "192.168.76.1"
$HttpOk = $false
$TelnetOk = $false
$SshOk = $false

foreach ($ip in $Candidates) {
    if (Test-Port $ip 23 400) {
        $RouterIP = $ip
        $TelnetOk = $true
        break
    }
    if (Test-Port $ip 80 400) {
        $RouterIP = $ip
        $HttpOk = $true
    }
}

if (-not $TelnetOk) {
    $TelnetOk = Test-Port $RouterIP 23 500
}
$HttpOk = Test-Port $RouterIP 80 500
$SshOk  = Test-Port $RouterIP 22 500

Write-Success ($M["gateway_found"] -f $RouterIP)
Write-Host ("      " + ($M["port_web"] -f ($(if ($HttpOk) {"[YES/SIM]"} else {"[NO/NAO]"})))) -ForegroundColor $(if ($HttpOk) {"Green"} else {"Gray"})
Write-Host ("      " + ($M["port_telnet"] -f ($(if ($TelnetOk) {"[YES/SIM]"} else {"[NO/NAO]"})))) -ForegroundColor $(if ($TelnetOk) {"Green"} else {"Gray"})
Write-Host ("      " + ($M["port_ssh"] -f ($(if ($SshOk) {"[YES/SIM]"} else {"[NO/NAO]"})))) -ForegroundColor $(if ($SshOk) {"Green"} else {"Gray"})

function Ensure-Python {
    Write-Info $M["checking_python"]
    $PythonCmd = ""
    if (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe") {
        $PythonCmd = "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"
    } elseif (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe") {
        $PythonCmd = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    } elseif (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe") {
        $PythonCmd = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    } else {
        try {
            $ver = & python --version 2>$null
            if ($LASTEXITCODE -eq 0) { $PythonCmd = "python" }
        } catch {}
    }

    if (-not $PythonCmd) {
        Write-Warn $M["python_missing"]
        winget install Python.Python.3.14 --silent --override "/passive PrependPath=1"
        Start-Sleep -Seconds 2
        if (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe") {
            $PythonCmd = "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"
        } else {
            $PythonCmd = "python"
        }
    }

    Write-Success ($M["python_ok"] -f (& $PythonCmd --version 2>&1))
    return $PythonCmd
}

function Ensure-Scripts {
    $scriptDir = "$RepoDir\Scripts_Automacao"
    if (-not (Test-Path "$scriptDir\launcher_t7.py")) {
        New-Item -ItemType Directory -Path $scriptDir -Force | Out-Null
        $scriptFiles = @(
            "launcher_t7.py", "telnet_compat.py", "gerenciar_telnet.py",
            "otimizar_e_ativar_luci_slot2.py", "gravar_v27_slot2.py",
            "switch_boot_slot.py", "diagnostico_x7.py", "unlock_only_ssh.py",
            "aplicar_configuracao_pessoal_ap_t7.py"
        )
        Write-Info "Sincronizando scripts da suite / Syncing suite scripts..."
        foreach ($s in $scriptFiles) {
            $dest = "$scriptDir\$s"
            if (-not (Test-Path $dest)) {
                try {
                    Invoke-WebRequest -Uri "$RawBase/Scripts_Automacao/$s" -OutFile $dest -UseBasicParsing
                } catch {
                    Invoke-WebRequest -Uri "$RawBase/04_SCRIPTS_E_FERRAMENTAS/Automacao_e_Unlock/$s" -OutFile $dest -UseBasicParsing
                }
            }
        }
        Write-Success "Scripts prontos."
    }
}

# 4. Pergunta de Triagem: Voce ja tem acesso root?
Write-Header $M["triage_title"]
Write-Host "  $($M["triage_q"])" -ForegroundColor Yellow
Write-Host ""
Write-Host "  $($M["triage_yes"])" -ForegroundColor White
Write-Host "  $($M["triage_no"])" -ForegroundColor White
Write-Host ""

$DefaultTriage = if ($TelnetOk) { "S" } else { "N" }
if ($Lang -eq "en") {
    $DefaultTriage = if ($TelnetOk) { "Y" } else { "N" }
}

$TriageChoice = Read-Host "  $($M["triage_prompt"] -f $DefaultTriage)"
if (-not $TriageChoice) { $TriageChoice = $DefaultTriage }

$NeedsUnlock = $false
if ($TriageChoice -like "n*" -or $TriageChoice -like "N*") {
    $NeedsUnlock = $true
}

# 5. Fluxo de Desbloqueio se NAO tiver root
if ($NeedsUnlock) {
    Write-Header $M["unlock_header"]
    Write-Host "  $($M["unlock_desc"])" -ForegroundColor Gray
    Write-Host ""
    Write-Header $M["choose_cfg"]
    Write-Host "  $($M["cfg_opt1"])" -ForegroundColor White
    Write-Host "$($M["cfg_opt1_desc"])" -ForegroundColor Gray
    Write-Host "  $($M["cfg_opt2"])" -ForegroundColor White
    Write-Host "$($M["cfg_opt2_desc"])" -ForegroundColor Gray
    Write-Host ""
    $CfgChoice = Read-Host "  $($M["cfg_prompt"])"
    if (-not $CfgChoice) { $CfgChoice = "1" }

    $Desktop = [Environment]::GetFolderPath("Desktop")
    $OutputCfg = "$Desktop\config_desbloqueio_t7.cfg"
    $UnlockScript = "$RepoDir\Scripts_Automacao\unlock_only_ssh.py"

    # Informar credenciais de Wi-Fi que ficarao ativas
    Write-Header $M["wifi_info_header"]
    Write-Host "  $($M["wifi_info_desc"])" -ForegroundColor Yellow
    Write-Host ""

    if ($CfgChoice -eq "2") {
        # Opcao 2: Desbloquear backup proprio
        Write-Info ($M["step_download_backup"] -f $RouterIP)
        Write-Host ""
        $UserCfg = Read-Host "  $($M["own_cfg_prompt"])"
        $UserCfg = $UserCfg.Trim('"').Trim("'")

        if (Test-Path $UserCfg) {
            Write-Info $M["patching_cfg"]
            $PythonExe = Ensure-Python
            Ensure-Scripts
            & $PythonExe $UnlockScript "$UserCfg" "$OutputCfg"
            Write-Success ($M["cfg_copied"] -f $OutputCfg)
        } else {
            Write-Warn "Arquivo nao encontrado. Usando CFG universal padrao..."
            $SrcCfg = "$RepoDir\02_BACKUPS_E_DUMPS\Configuracoes_CFG\config_v27_ssh_unlocked.cfg"
            if (Test-Path $SrcCfg) {
                Copy-Item $SrcCfg $OutputCfg -Force
            } else {
                $RawCfg = "$RawBase/02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_ssh_unlocked.cfg"
                Invoke-WebRequest -Uri $RawCfg -OutFile $OutputCfg -UseBasicParsing
            }
            Write-Success ($M["cfg_copied"] -f $OutputCfg)
        }
    } else {
        # Opcao 1: CFG Universal v27
        Write-Info $M["copying_cfg"]
        $SrcCfg = "$RepoDir\02_BACKUPS_E_DUMPS\Configuracoes_CFG\config_v27_ssh_unlocked.cfg"
        if (Test-Path $SrcCfg) {
            Copy-Item $SrcCfg $OutputCfg -Force
        } else {
            $RawCfg = "$RawBase/02_BACKUPS_E_DUMPS/Configuracoes_CFG/config_v27_ssh_unlocked.cfg"
            Invoke-WebRequest -Uri $RawCfg -OutFile $OutputCfg -UseBasicParsing
        }
        Write-Success ($M["cfg_copied"] -f $OutputCfg)
    }

    # Instrucoes na tela
    Write-Header $M["instructions"]
    Write-Host "  $($M["step1"] -f $RouterIP)" -ForegroundColor Yellow
    Write-Host "  $($M["step2"])" -ForegroundColor Yellow
    Write-Host "  $($M["step3"])" -ForegroundColor Yellow
    Write-Host "     ==> $OutputCfg" -ForegroundColor White
    Write-Host "  $($M["step4"])" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "  $($M["press_enter_rst"])"

    # Polling ativo de reinicializacao
    Write-Header $M["waiting_reboot"]
    $RebootOk = $false
    for ($i = 1; $i -le 45; $i++) {
        Write-Host ($M["attempt"] -f $RouterIP, $i, 45) -ForegroundColor Gray
        Start-Sleep -Seconds 2
        if (Test-Port $RouterIP 23 700) {
            $RebootOk = $true
            break
        }
    }

    if ($RebootOk) {
        Write-Success $M["reboot_success"]
        Start-Sleep -Seconds 2
    } else {
        Write-Warn $M["reboot_timeout"]
    }
}

# 6. Garantir Python e Scripts para a Central
$PythonCmd = Ensure-Python
Ensure-Scripts

# 7. Executar a Central de Gerenciamento (launcher_t7.py)
Write-Header $M["launching_suite"]
$LauncherPy = "$RepoDir\Scripts_Automacao\launcher_t7.py"
& $PythonCmd $LauncherPy --lang $Lang
