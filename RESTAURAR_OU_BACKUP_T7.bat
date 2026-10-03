@echo off
chcp 65001 >nul
title CENTRAL DE BACKUP E RESTAURAÇÃO - ACER PREDATOR CONNECT T7
color 0B

:MENU
cls
echo ===========================================================================
echo       CENTRAL DE BACKUP E RESTAURAÇÃO - ACER PREDATOR CONNECT T7
echo             Firmware v27 (Slot 2) - Wi-Fi 7 + LuCI Porta 80
echo ===========================================================================
echo.
echo   [1] RESTAURAR VIA SCRIPT INTELIGENTE (Recomendado)
echo       - Reaplica Wi-Fi 7 (CASA_ARK_7G / 320MHz), 5GHz, Modo AP (192.168.73.2)
echo       - Desativa DHCP e integra portas em Switch L2 em 5 segundos
echo.
echo   [2] RESTAURAR CLONE COMPLETO DO OVERLAY (.tar.gz)
echo       - Restaura 100%% da memoria Flash NAND (senhas, LuCI, sysctl, scripts)
echo       - Ideal se o roteador foi resetado pelo botao fisico Reset
echo.
echo   [3] GERAR NOVO BACKUP DO ROTEADOR PARA O COMPUTADOR
echo       - Baixa automaticamente o snapshot do Overlay e Sysupgrade atualizados
echo.
echo   [4] ABRIR PAINEL LUCI NO NAVEGADOR (http://192.168.73.2)
echo.
echo   [5] ABRIR TERMINAL TELNET NO ROTEADOR (root / admin0100)
echo.
echo   [0] SAIR
echo.
echo ===========================================================================
set /p OPCAO="Escolha uma opção (0-5): "

if "%OPCAO%"=="1" goto OPCAO1
if "%OPCAO%"=="2" goto OPCAO2
if "%OPCAO%"=="3" goto OPCAO3
if "%OPCAO%"=="4" goto OPCAO4
if "%OPCAO%"=="5" goto OPCAO5
if "%OPCAO%"=="0" goto SAIR
goto MENU

:OPCAO1
cls
echo.
echo [*] Executando Aplicador de Configuracao Pessoal...
echo.
python "%~dp004_SCRIPTS_E_FERRAMENTAS\Automacao_e_Unlock\aplicar_configuracao_pessoal_ap_t7.py"
echo.
pause
goto MENU

:OPCAO2
cls
echo.
echo [*] Executando Restauracao de Snapshot do Overlay...
echo.
python "%~dp004_SCRIPTS_E_FERRAMENTAS\Automacao_e_Unlock\restaurar_backup_pessoal.py"
echo.
pause
goto MENU

:OPCAO3
cls
echo.
echo [*] Gerando e Baixando Backup Atualizado...
echo.
python "%~dp004_SCRIPTS_E_FERRAMENTAS\Automacao_e_Unlock\gerar_backup_pessoal.py"
echo.
pause
goto MENU

:OPCAO4
start http://192.168.73.2
goto MENU

:OPCAO5
cls
echo Conectando via Telnet no roteador (IP 192.168.73.2)...
telnet 192.168.73.2 23
pause
goto MENU

:SAIR
exit
