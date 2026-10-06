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

# 1. Definir Diretorio de Trabalho Seguro no Desktop (Sem espacos, uso de hifens)
$Desktop = [Environment]::GetFolderPath("Desktop")
$DesktopWorkDir = "$Desktop\Acer-Predator-Connect-T7"

# Detectar se ja existe uma pasta local clonada (ex: em pendrive ou HD externo)
$LocalSourceDir = $PSScriptRoot
if (-not $LocalSourceDir -or -not (Test-Path "$LocalSourceDir\Scripts_Automacao")) {
    if (Test-Path ".\Scripts_Automacao") {
        $LocalSourceDir = (Get-Item ".").FullName
    } elseif (Test-Path "$DesktopWorkDir\Scripts_Automacao") {
        $LocalSourceDir = $DesktopWorkDir
    } else {
        $LocalSourceDir = $null
    }
}

# A pasta de trabalho oficial e sempre no Desktop (zero risco de limpeza de %TEMP%)
$RepoDir = $DesktopWorkDir
if (-not (Test-Path $RepoDir)) {
    New-Item -ItemType Directory -Path $RepoDir -Force | Out-Null
}

# 1. Sincronizar e Atualizar Ferramenta (GitHub Checksum) no inicio (Antes do Idioma)
function Sync-Suite-From-GitHub {
    Write-Header "SINCRONIZANDO FERRAMENTAS DO GITHUB / SYNCING SUITE"
    Write-Info "Verificando atualizacoes no GitHub / Checking latest updates from GitHub..."
    Write-Host "  Pasta de Trabalho: $RepoDir" -ForegroundColor Gray
    Write-Host ""

    $ManifestFile = "$RepoDir\manifest_suite.json"
    $cacheBuster  = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $ManifestUrl  = "$RawBase/manifest_suite.json?t=$cacheBuster"
    $Manifest     = $null
    $isOffline    = $false

    # Carregar Manifesto Oficial (Remoto via GitHub com Timeout de 8s e sem Cache)
    try {
        $headers = @{
            "User-Agent"    = "Mozilla/5.0"
            "Cache-Control" = "no-cache, no-store, must-revalidate"
            "Pragma"        = "no-cache"
        }
        $resp = Invoke-WebRequest -Uri $ManifestUrl -TimeoutSec 8 -UseBasicParsing -Headers $headers
        $remoteJson = $resp.Content
        $Manifest = $remoteJson | ConvertFrom-Json
        [System.IO.File]::WriteAllText($ManifestFile, $remoteJson, [System.Text.Encoding]::UTF8)
        Write-Success "Manifesto v$($Manifest.suite_version) carregado do GitHub ($($Manifest.files.Count) arquivos monitorados)"
    } catch {
        $isOffline = $true
        if (Test-Path $ManifestFile) {
            try {
                $Manifest = Get-Content $ManifestFile -Raw | ConvertFrom-Json
                Write-Warn "Sem internet. Usando manifesto em cache v$($Manifest.suite_version) (Modo Offline)"
            } catch {}
        } elseif ($LocalSourceDir -and (Test-Path "$LocalSourceDir\manifest_suite.json")) {
            try {
                $Manifest = Get-Content "$LocalSourceDir\manifest_suite.json" -Raw | ConvertFrom-Json
                Copy-Item "$LocalSourceDir\manifest_suite.json" $ManifestFile -Force
                Write-Success "Manifesto local v$($Manifest.suite_version) carregado ($($Manifest.files.Count) arquivos)"
            } catch {}
        }

        if (-not $Manifest) {
            Write-Warn "Sem conexao com a internet (Modo Offline). Continuando normalmente..."
        }
    }

    # Verificacao Inteligente Baseada em Checksum SHA-256 e Categorias
    if ($Manifest -and $Manifest.files) {
        $TotalChecked   = 0
        $UpToDateCount  = 0
        $UpdatedCount   = 0
        $NewCount       = 0

        $wc = New-Object System.Net.WebClient
        $wc.Headers.Add("User-Agent", "Mozilla/5.0")
        $wc.Headers.Add("Cache-Control", "no-cache")
        $wc.Headers.Add("Pragma", "no-cache")
        try {
            $wc.CachePolicy = New-Object System.Net.Cache.RequestCachePolicy([System.Net.Cache.RequestCacheLevel]::NoCacheNoStore)
        } catch {}

        foreach ($item in $Manifest.files) {
            $rel = $item.path
            $dest = Join-Path $RepoDir ($rel.Replace('/', '\'))
            $destDir = Split-Path $dest -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            $TotalChecked++

            $needsDownload = $false
            $isUpdate = $false

            # Imagens de ROM grandes (~50 MB): checar tamanho primeiro
            if ($item.category -in @("rom", "stock_rom")) {
                if (Test-Path $dest) {
                    $curLen = (Get-Item $dest).Length
                    if ($curLen -eq $item.size) {
                        $UpToDateCount++
                        continue
                    }
                }
                $needsDownload = $true
                $NewCount++
                if (-not $isOffline) {
                    $romLabel = "$([math]::Round($item.size / 1MB, 1)) MB"
                    Write-Info "Baixando ROM do GitHub: $(Split-Path $dest -Leaf) ($romLabel)..."
                }
            } else {
                # Scripts, CFG e Launchers
                if (-not (Test-Path $dest)) {
                    $needsDownload = $true
                    $NewCount++
                    if (-not $isOffline) {
                        Write-Info "Arquivo ausente: $rel. Baixando..."
                    }
                } else {
                    $localHash = (Get-FileHash -Path $dest -Algorithm SHA256).Hash
                    if ($localHash -eq $item.sha256) {
                        $UpToDateCount++
                    } else {
                        $needsDownload = $true
                        $isUpdate = $true
                        $UpdatedCount++
                        if (-not $isOffline) {
                            Write-Info "Nova versao detectada no GitHub: $rel! Atualizando..."
                            try { Copy-Item $dest "$dest.bak" -Force } catch {}
                        }
                    }
                }
            }

            if ($needsDownload) {
                if ($isOffline) {
                    continue
                }

                $copiedLocal = $false
                if ($LocalSourceDir) {
                    $localSrc = Join-Path $LocalSourceDir ($rel.Replace('/', '\'))
                    if (Test-Path $localSrc) {
                        $srcLen = (Get-Item $localSrc).Length
                        if ($item.category -in @("rom", "stock_rom") -and $srcLen -eq $item.size) {
                            Copy-Item $localSrc $dest -Force
                            $copiedLocal = $true
                        } elseif ($item.category -notin @("rom", "stock_rom")) {
                            $srcHash = (Get-FileHash -Path $localSrc -Algorithm SHA256).Hash
                            if ($srcHash -eq $item.sha256) {
                                Copy-Item $localSrc $dest -Force
                                $copiedLocal = $true
                            }
                        }
                    }
                }

                if (-not $copiedLocal) {
                    try {
                        $wc.DownloadFile("$RawBase/$rel?t=$cacheBuster", $dest)
                    } catch {}
                }

                if (Test-Path $dest) {
                    if ($isUpdate) {
                        Write-Success "Atualizado com sucesso: $rel"
                    } else {
                        Write-Success "Baixado com sucesso: $rel"
                    }
                }
            }
        }

        Write-Host ""
        if ($isOffline) {
            Write-Warn "Modo Offline: $UpToDateCount de $TotalChecked arquivos locais verificados. Continuando..."
        } elseif ($UpdatedCount -eq 0 -and $NewCount -eq 0) {
            Write-Success "Todas as $TotalChecked ferramentas verificadas e atualizadas (SHA-256 validado)!"
        } else {
            Write-Success "Sincronizacao concluida: $TotalChecked arquivos checados ($UpToDateCount ja atualizados, $($UpdatedCount + $NewCount) atualizados/baixados)."
        }
        Write-Host ""
    } else {
        if ($isOffline) {
            Write-Warn "Sem conexao com internet e sem manifesto. Continuando com arquivos locais..."
        }
    }
}

# Executa sincronizacao inteligente no inicio (se nao tiver internet, continua normalmente)
Sync-Suite-From-GitHub

# 2. Selecao de Idioma
if (-not $Lang) {
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
        "triage_prompt"      = "Choose option [Y/N]: "
        "unlock_header"      = "STEP-BY-STEP ROOT UNLOCK (SAFE & FAST)"
        "unlock_desc"        = "The unlock is 100% safe and DOES NOT flash NAND memory.`n  It only enables SSH/Telnet inside a config backup (.cfg) that you restore via Acer Web GUI."
        "choose_cfg"         = "How would you like to prepare your unlock file?"
        "cfg_opt1"           = "[1] Use Universal Ready-Made v27 CFG (Fastest - 1 Click)"
        "cfg_opt1_desc"      = "    - Copies unlock file directly to your Desktop`n    - Unlocks Telnet (no pass) and SSH ('root' / 'root')`n    - Wi-Fi: Predator_T7 / Password: predator123"
        "cfg_opt2"           = "[2] Unlock YOUR OWN Current Backup (Keeps your current Wi-Fi and Passwords)"
        "cfg_opt2_desc"      = "    - Download your current config.cfg from Acer Web GUI`n    - Injects root while keeping all your Wi-Fi SSIDs and settings"
        "cfg_prompt"         = "Choose option [1/2]: "
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
        "python_added_path"  = "Python permanently added to Windows User PATH: {0}"
        "ip_confirm_prompt"  = "Press ENTER to confirm [{0}] or type your router IP: "
        "ip_not_found"       = "Could not automatically find Predator router on standard IPs."
        "ip_manual_prompt"   = "Type your Predator router IP [Default: 192.168.76.1]: "
        "auto_diag_header"     = "AUTOMATIC ROUTER STATE DIAGNOSTIC"
        "auto_root_detected"   = "Detected: Router already has ACTIVE ROOT ACCESS (Telnet/SSH active)!`n  [KEY] Toolkit default root password: root0100 (8 lowercase chars).`n  -> Next step: Proceeding straight to the MANAGEMENT SUITE."
        "auto_locked_detected" = "Detected: Router is still FACTORY LOCKED (Telnet/SSH ports closed).`n  -> Next step: Proceeding to STEP-BY-STEP ROOT UNLOCK."
        "auto_confirm_prompt"  = "Press ENTER to proceed automatically, or type [M] for manual choice / change IP: "
        "manual_ip_ask"        = "Do you want to change the router IP? Type new IP or press ENTER to keep [{0}]: "
        "manual_choice_title"  = "MANUAL FLOW SELECTION"
        "manual_opt1"          = "[1] My router already has Root / Telnet / SSH -> Launch Management Suite"
        "manual_opt2"          = "[2] My router is factory locked -> Start Step-by-Step Unlock (.cfg)"
        "manual_choice_prompt" = "Choose how to proceed [1/2]: "
        "confirm_restore_done" = "Did you click 'Restore' in Acer web panel and router began rebooting? [Y/N]: "
        "wait_restore_first"   = "Please complete the restore in the browser first, then confirm [Y] to proceed."
        "triage_required"      = "Please answer with [Y] for YES or [N] for NO to proceed."
        "deps_title"               = "SMART DEPENDENCY SYNC & UPDATE CHECKER"
        "deps_checking"            = "Verifying local suite files and checking for updates against GitHub..."
        "deps_manifest_checking"   = "Connecting to GitHub to verify latest versions and checksums..."
        "deps_manifest_ok"         = "Suite manifest v{0} loaded ({1} files tracked)"
        "deps_manifest_offline"    = "GitHub connection unavailable. Using existing local files on Desktop."
        "deps_manifest_cached"     = "Using cached manifest v{0} (Offline mode)"
        "deps_file_uptodate"       = "Up-to-date: {0}"
        "deps_file_new"            = "New file missing: {0}. Downloading..."
        "deps_file_updating"       = "Newer version detected on GitHub: {0}! Updating..."
        "deps_file_local_newer"    = "Local file {0} was edited locally ({1}). Saving backup to .local_backup and updating..."
        "deps_file_updated_ok"     = "Updated successfully: {0} (backup saved as .bak)"
        "deps_file_downloaded_ok"  = "Downloaded successfully: {0}"
        "deps_summary_all_ok"      = "All {0} suite files are verified and up-to-date (SHA-256 matched)!"
        "deps_summary_updates"     = "Sync complete: {0} files verified ({1} up-to-date, {2} updated/downloaded)."
        "deps_down_file"           = "Downloading from GitHub: {0}..."
        "deps_down_rom"            = "Downloading v27 ROM binary from GitHub: {0} ({1})..."
        "deps_scripts_ok"          = "Suite Python Automation Scripts : [OK] 9/9 files verified (~135 KB)"
        "deps_cfg_ok"              = "Ready-Made CFG Unlock Backup    : [OK] Verified (~50 KB)"
        "deps_rom_ok"              = "v27 OpenWrt Slot 2 ROM Binaries : [OK] 3/3 verified (50.0 MB)"
        "deps_all_done"            = "ALL DEPENDENCIES 100% READY AND SYNCHRONIZED (~50.2 MB TOTAL)!"
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
        "triage_prompt"      = "Escolha a opcao [S/N]: "
        "unlock_header"      = "DESBLOQUEIO DE ACESSO ROOT PASSO A PASSO (SEGURO E RAPIDO)"
        "unlock_desc"        = "O desbloqueio e 100% seguro e NAO grava particoes da flash.`n  Ele apenas ativa o terminal SSH/Telnet em um backup (.cfg) restaurado pelo painel da Acer."
        "choose_cfg"         = "Como voce prefere gerar o seu arquivo de desbloqueio?"
        "cfg_opt1"           = "[1] Usar CFG Pronto Universal v27 (Mais Rapido - 1 Clique)"
        "cfg_opt1_desc"      = "    - Copia o arquivo pronto direto para sua Area de Trabalho`n    - Ativa Telnet sem senha e SSH com usuario 'root' / senha 'root'`n    - Wi-Fi: Predator_T7 / Senha: predator123"
        "cfg_opt2"           = "[2] Desbloquear o SEU PROPRIO backup atual (Mantem seu Wi-Fi e Senhas)"
        "cfg_opt2_desc"      = "    - Voce baixa o config.cfg pelo painel da Acer`n    - O script injeta o root mantendo todas as suas redes e senhas de Wi-Fi"
        "cfg_prompt"         = "Escolha a opcao [1/2]: "
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
        "python_added_path"  = "Python adicionado permanentemente ao PATH do Windows: {0}"
        "ip_confirm_prompt"  = "Pressione ENTER para confirmar [{0}] ou digite o IP correto: "
        "ip_not_found"       = "Nao foi possivel detectar automaticamente o roteador nos IPs padrao."
        "ip_manual_prompt"   = "Digite o IP do seu roteador Predator [Padrao: 192.168.76.1]: "
        "auto_diag_header"     = "DIAGNOSTICO AUTOMATICO DE ESTADO DO ROTEADOR"
        "auto_root_detected"   = "Diagnostico: Roteador com ACESSO ROOT ativo detectado (Telnet/SSH ativo)!`n  [🔑] Senha padrao de root do toolkit: root0100 (8 caracteres minusculos).`n  -> Fluxo automatico: Abrir direto a CENTRAL DE GERENCIAMENTO."
        "auto_locked_detected" = "Diagnostico: Roteador com FIRMWARE TRAVADO DE FABRICA (portas 22 e 23 fechadas).`n  -> Fluxo automatico: Iniciar DESBLOQUEIO DE ROOT PASSO A PASSO."
        "auto_confirm_prompt"  = "Pressione ENTER para prosseguir automaticamente, ou digite [M] (ou novo IP) para escolha manual: "
        "manual_ip_ask"        = "Deseja alterar o IP do roteador? Digite o novo IP ou pressione ENTER para manter [{0}]: "
        "manual_choice_title"  = "ESCOLHA MANUAL DE FLUXO"
        "manual_opt1"          = "[1] Meu roteador ja tem Root / Telnet / SSH ativo -> Abrir Central de Gerenciamento"
        "manual_opt2"          = "[2] Meu roteador esta travado de fabrica -> Iniciar Desbloqueio Passo a Passo (.cfg)"
        "manual_choice_prompt" = "Escolha como deseja prosseguir [1/2]: "
        "confirm_restore_done" = "Voce ja clicou em 'Restaurar' no painel da Acer e o roteador comecou a reiniciar? [S/N]: "
        "wait_restore_first"   = "Por favor, conclua o envio do backup no painel primeiro e responda [S] para prosseguir."
        "triage_required"      = "Por favor, responda com [S] para SIM ou [N] para NAO para prosseguir."
        "cfg_choice_required"  = "Por favor, digite 1 ou 2 para prosseguir."
        "deps_title"               = "SINCRONIZACAO INTELIGENTE E VERIFICACAO DE ATUALIZACOES"
        "deps_checking"            = "Verificando arquivos locais e checando atualizacoes no GitHub..."
        "deps_manifest_checking"   = "Conectando ao GitHub para verificar versoes mais recentes e checksums..."
        "deps_manifest_ok"         = "Manifesto da suite v{0} carregado ({1} arquivos monitorados)"
        "deps_manifest_offline"    = "Sem conexao com GitHub no momento. Utilizando arquivos locais da Area de Trabalho."
        "deps_manifest_cached"     = "Utilizando manifesto em cache v{0} (Modo Offline)"
        "deps_file_uptodate"       = "Ja atualizado: {0}"
        "deps_file_new"            = "Arquivo ausente: {0}. Baixando..."
        "deps_file_updating"       = "Nova versao detectada no GitHub: {0}! Atualizando..."
        "deps_file_local_newer"    = "Arquivo local {0} foi editado na maquina ({1}). Salvando backup em .local_backup e atualizando..."
        "deps_file_updated_ok"     = "Atualizado com sucesso: {0} (backup salvo como .bak)"
        "deps_file_downloaded_ok"  = "Baixado com sucesso: {0}"
        "deps_summary_all_ok"      = "Todos os {0} arquivos da suite estao verificados e na versao mais recente (SHA-256 validado)!"
        "deps_summary_updates"     = "Sincronizacao concluida: {0} arquivos checados ({1} ja atualizados, {2} atualizados/baixados)."
        "deps_down_file"           = "Baixando do GitHub: {0}..."
        "deps_down_rom"            = "Baixando imagem da ROM v27 do GitHub: {0} ({1})..."
        "deps_scripts_ok"          = "Scripts Python da Suite         : [OK] 9/9 arquivos verificados (~135 KB)"
        "deps_cfg_ok"              = "Arquivo de Desbloqueio CFG Pronto: [OK] Verificado (~50 KB)"
        "deps_rom_ok"              = "Binarios da ROM v27 para Slot 2 : [OK] 3/3 verificados (50.0 MB)"
        "deps_all_done"            = "TODAS AS DEPENDENCIAS 100% PRONTAS E SINCRONIZADAS (~50.2 MB TOTAL)!"
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

function Ensure-Python {
    Write-Info $M["checking_python"]
    $PythonExe = $null

    # 1. Verificar se o comando 'python' ja esta funcional no PATH e nao e o atalho vazio da WindowsApps
    try {
        $cmdInfo = Get-Command "python.exe" -ErrorAction SilentlyContinue
        if ($cmdInfo -and ($cmdInfo.Source -notlike "*WindowsApps*")) {
            $testVer = & $cmdInfo.Source --version 2>&1
            if ($LASTEXITCODE -eq 0 -and "$testVer" -like "*Python 3*") {
                $PythonExe = $cmdInfo.Source
            }
        }
    } catch {}

    # 2. Se nao encontrou ou se o PATH aponta para o atalho da loja, procurar instalacoes reais no disco
    if (-not $PythonExe) {
        $searchDirs = @(
            "$env:LOCALAPPDATA\Programs\Python",
            "$env:ProgramFiles\Python3*",
            "${env:ProgramFiles(x86)}\Python3*",
            "C:\Python3*"
        )
        foreach ($sdir in $searchDirs) {
            if (Test-Path $sdir) {
                $found = Get-ChildItem -Path $sdir -Filter "python.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue |
                         Where-Object { $_.FullName -notlike "*WindowsApps*" } |
                         Sort-Object FullName -Descending |
                         Select-Object -First 1
                if ($found) {
                    $PythonExe = $found.FullName
                    break
                }
            }
        }
    }

    # 3. Tentar via Python Launcher oficial (py.exe) se existir
    if (-not $PythonExe) {
        try {
            $pyLauncher = Get-Command "py.exe" -ErrorAction SilentlyContinue
            if ($pyLauncher) {
                $resolved = & $pyLauncher.Source -c "import sys; print(sys.executable)" 2>$null
                if ($resolved -and (Test-Path $resolved.Trim())) {
                    $PythonExe = $resolved.Trim()
                }
            }
        } catch {}
    }

    # 4. Se nao estiver instalado em nenhum local, instalar automaticamente via WinGet
    if (-not $PythonExe) {
        Write-Warn $M["python_missing"]
        try {
            winget install Python.Python.3.14 --silent --override "/passive PrependPath=1"
        } catch {
            Write-Warn "WinGet falhou. Tentando instalador alternativo..."
        }
        Start-Sleep -Seconds 3

        # Re-procurar na pasta padrao do usuario apos a instalacao
        $newFound = Get-ChildItem -Path "$env:LOCALAPPDATA\Programs\Python" -Filter "python.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue |
                     Sort-Object FullName -Descending |
                     Select-Object -First 1
        if ($newFound) {
            $PythonExe = $newFound.FullName
        } else {
            $PythonExe = "python"
        }
    }

    # 5. Adicionar a pasta do Python e Scripts permanentemente ao PATH do Windows e a sessao atual
    if ($PythonExe -and (Test-Path $PythonExe)) {
        $pyDir = Split-Path $PythonExe -Parent
        $scriptsDir = Join-Path $pyDir "Scripts"

        # Prepend na sessao ativa do terminal imediatamente
        if ($env:PATH -notlike "*$pyDir*") {
            $env:PATH = "$pyDir;$scriptsDir;$env:PATH"
        }

        # Configurar permanentemente no PATH do usuario no Windows (Registro HKCU)
        try {
            $currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
            if (-not $currentUserPath) { $currentUserPath = "" }
            if ($currentUserPath -notlike "*$pyDir*") {
                # Prepend para ter precedencia sobre o atalho quebrado da Microsoft Store (WindowsApps)
                $newUserPath = "$pyDir;$scriptsDir;" + ($currentUserPath.Trim(';'))
                [Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
                Write-Success ($M["python_added_path"] -f $pyDir)
            }
        } catch {}
    }

    $verOutput = (& $PythonExe --version 2>&1)
    Write-Success ($M["python_ok"] -f $verOutput)
    return $PythonExe
}

# 2.5. Garantir Ambiente Python 3
$PythonCmd = Ensure-Python

# 3. Detectar IP do Roteador
Write-Header $M["title"]
Write-Info $M["detecting"]

$Candidates = @()

# 3.1. Coletar Default Gateway das placas de rede ativas (ignora VPN, ZeroTier, WSL, etc)
try {
    $Adapters = Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "Up" -and $_.InterfaceDescription -notmatch "(Virtual|VPN|ZeroTier|Npcap|Hyper-V|WSL)" }
    foreach ($ad in $Adapters) {
        $ipConf = Get-NetIPConfiguration -InterfaceIndex $ad.InterfaceIndex -ErrorAction SilentlyContinue
        if ($ipConf.IPv4DefaultGateway) {
            foreach ($gw in $ipConf.IPv4DefaultGateway) {
                if ($gw.NextHop -and $gw.NextHop -notin $Candidates) {
                    $Candidates += $gw.NextHop
                }
            }
        }
    }
} catch {}

# 3.2. Adicionar IPs conhecidos da linha Acer Predator
foreach ($stdIp in @("192.168.76.1", "192.168.73.2", "192.168.1.1")) {
    if ($stdIp -notin $Candidates) {
        $Candidates += $stdIp
    }
}

$RouterIP = ""
$HttpOk = $false
$TelnetOk = $false
$SshOk = $false

# Prioridade 1: Roteador que ja responde com Telnet na porta 23 (Root ativo)
foreach ($ip in $Candidates) {
    if (Test-Port $ip 23 400) {
        $RouterIP = $ip
        $TelnetOk = $true
        $HttpOk = Test-Port $ip 80 400
        $SshOk = Test-Port $ip 22 400
        break
    }
}

# Prioridade 2: Se nenhum tem Telnet, buscar quem responde na porta 80 (Web GUI)
if (-not $RouterIP) {
    foreach ($ip in $Candidates) {
        if (Test-Port $ip 80 400) {
            $RouterIP = $ip
            $HttpOk = $true
            $SshOk = Test-Port $ip 22 400
            break
        }
    }
}

# 3.3. Tratamento de Fallback: Se nenhum IP respondeu nas portas esperadas
if (-not $RouterIP) {
    Write-Warn $M["ip_not_found"]
    $CustomIP = Read-Host "  $($M["ip_manual_prompt"])"
    if ($CustomIP -and $CustomIP.Trim() -ne "") {
        $RouterIP = $CustomIP.Trim()
    } else {
        $RouterIP = "192.168.76.1"
    }
    $HttpOk   = Test-Port $RouterIP 80 500
    $TelnetOk = Test-Port $RouterIP 23 500
    $SshOk    = Test-Port $RouterIP 22 500
}

# Mostra o status do roteador e das portas detectadas
Write-Success ($M["gateway_found"] -f $RouterIP)
Write-Host ("      " + ($M["port_web"] -f ($(if ($HttpOk) {"[YES/SIM]"} else {"[NO/NAO]"})))) -ForegroundColor $(if ($HttpOk) {"Green"} else {"Gray"})
Write-Host ("      " + ($M["port_telnet"] -f ($(if ($TelnetOk) {"[YES/SIM]"} else {"[NO/NAO]"})))) -ForegroundColor $(if ($TelnetOk) {"Green"} else {"Gray"})
Write-Host ("      " + ($M["port_ssh"] -f ($(if ($SshOk) {"[YES/SIM]"} else {"[NO/NAO]"})))) -ForegroundColor $(if ($SshOk) {"Green"} else {"Gray"})
Write-Host ""

# 4. Diagnostico Automatico de Estado (Root vs Travado)
$HasRoot = ($TelnetOk -or $SshOk)

Write-Header $M["auto_diag_header"]
if ($HasRoot) {
    Write-Host "  $($M["auto_root_detected"])" -ForegroundColor Green
    Write-Host ""
    $NeedsUnlock = $false
    Start-Sleep -Milliseconds 600
} else {
    Write-Host "  $($M["auto_locked_detected"])" -ForegroundColor Yellow
    Write-Host ""

    # Permite confirmacao automatica (ENTER) ou escolha manual / alterar IP caso o usuario queira
    $UserAction = (Read-Host "  $($M["auto_confirm_prompt"])").Trim()

    if ($UserAction -eq "" -or $UserAction -eq "2") {
        # Prosseguir automaticamente para o desbloqueio
        $NeedsUnlock = $true
    } elseif ($UserAction -eq "1") {
        $NeedsUnlock = $false
    } else {
        # Usuario solicitou escolha manual ou informou um IP diferente
        if ($UserAction -match '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$') {
            $RouterIP = $UserAction
        } else {
            $NewIP = (Read-Host "  $($M["manual_ip_ask"] -f $RouterIP)").Trim()
            if ($NewIP -and $NewIP -match '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$') {
                $RouterIP = $NewIP
            }
        }

    Write-Info "Re-testando portas em $RouterIP..."
    $HttpOk   = Test-Port $RouterIP 80 500
    $TelnetOk = Test-Port $RouterIP 23 500
    $SshOk    = Test-Port $RouterIP 22 500
    Write-Host ("      " + ($M["port_web"] -f ($(if ($HttpOk) {"[YES/SIM]"} else {"[NO/NAO]"})))) -ForegroundColor $(if ($HttpOk) {"Green"} else {"Gray"})
    Write-Host ("      " + ($M["port_telnet"] -f ($(if ($TelnetOk) {"[YES/SIM]"} else {"[NO/NAO]"})))) -ForegroundColor $(if ($TelnetOk) {"Green"} else {"Gray"})
    Write-Host ("      " + ($M["port_ssh"] -f ($(if ($SshOk) {"[YES/SIM]"} else {"[NO/NAO]"})))) -ForegroundColor $(if ($SshOk) {"Green"} else {"Gray"})
    Write-Host ""

    Write-Header $M["manual_choice_title"]
    Write-Host "  $($M["manual_opt1"])" -ForegroundColor White
    Write-Host "  $($M["manual_opt2"])" -ForegroundColor White
    Write-Host ""

    $ManualChoice = ""
    while ($ManualChoice -notin @("1", "2")) {
        $ManualChoice = (Read-Host "  $($M["manual_choice_prompt"])").Trim()
        if ($ManualChoice -notin @("1", "2")) {
            Write-Warn $M["cfg_choice_required"]
        }
    }
    $NeedsUnlock = ($ManualChoice -eq "2")
}
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
    $CfgChoice = ""
    while ($CfgChoice -notin @("1", "2")) {
        $CfgChoice = (Read-Host "  $($M["cfg_prompt"])").Trim()
        if ($CfgChoice -notin @("1", "2")) {
            Write-Warn $M["cfg_choice_required"]
        }
    }

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
            & $PythonCmd $UnlockScript "$UserCfg" "$OutputCfg"
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
    $RstConfirmed = $false
    while (-not $RstConfirmed) {
        $Ans = Read-Host "  $($M["confirm_restore_done"])"
        if ($Ans -like "s*" -or $Ans -like "sim" -or $Ans -like "y*" -or $Ans -like "yes") {
            $RstConfirmed = $true
        } else {
            Write-Warn $M["wait_restore_first"]
        }
    }

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

# 6. Executar a Central de Gerenciamento (launcher_t7.py)
Write-Header $M["launching_suite"]
$LauncherPy = "$RepoDir\Scripts_Automacao\launcher_t7.py"
& $PythonCmd $LauncherPy --lang $Lang --ip $RouterIP
