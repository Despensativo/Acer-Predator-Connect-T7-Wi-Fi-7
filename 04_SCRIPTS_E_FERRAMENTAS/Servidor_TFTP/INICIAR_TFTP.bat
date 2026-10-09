@echo off
title Servidor TFTP - Acer Predator Connect T7
cd /d "%~dp0"
echo ========================================================
echo   INICIANDO SERVIDOR TFTP PARA O ACER PREDATOR CONNECT T7
echo ========================================================
echo.
python tftp_server.py
if %errorlevel% neq 0 (
    echo.
    echo Tentando com 'py'...
    py tftp_server.py
)
pause
