param([string]$InterfaceAlias = 'Ethernet 4')
$ErrorActionPreference = 'Stop'
$base = Split-Path $PSScriptRoot -Parent
$plan = Get-Content -LiteralPath (Join-Path $base 'sessao-teste-v3-PENDENTE.json') -Raw | ConvertFrom-Json
$checks = @()
foreach ($item in $plan.files) {
    $path = Join-Path $base $item.path
    $valid = (Test-Path -LiteralPath $path -PathType Leaf)
    if ($valid) { $valid = ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower() -eq $item.sha256) }
    $checks += [pscustomobject]@{ artifact=$item.path; sha256_matches=$valid }
}
$adapter = Get-NetAdapter -Name $InterfaceAlias -ErrorAction SilentlyContinue
$addresses = @(Get-NetIPAddress -InterfaceAlias $InterfaceAlias -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object IPAddress,PrefixLength)
$ports = @(Get-NetUDPEndpoint -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(69,6666,6667) } | Select-Object LocalAddress,LocalPort)
$result = [ordered]@{
    checked_at = (Get-Date).ToUniversalTime().ToString('o')
    artifacts = $checks
    interface_alias = $InterfaceAlias
    link_status = $(if ($adapter) { [string]$adapter.Status } else { 'NotFound' })
    ipv4 = $addresses
    existing_udp_listeners = $ports
    current_service_ip_reported = $plan.current_service_ip_reported
    current_slot_verified = $false
    kernel_boot_launcher_ready = $false
    router_contacted = $false
    host_configuration_changed = $false
    note = 'Somente leitura do PC. Não faz ping, HTTP, Telnet, reboot, upload, alteração de IP/firewall ou abertura de sockets.'
}
$dir = Join-Path $base 'evidencias'
$path = Join-Path $dir ('preflight-v3-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $path -Encoding UTF8
$result | ConvertTo-Json -Depth 6
Write-Output ('Evidência: ' + $path)
