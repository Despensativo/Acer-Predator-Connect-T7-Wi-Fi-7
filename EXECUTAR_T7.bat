@echo off
cd /d "%~dp0"
title ACER PREDATOR CONNECT T7 E X7 MANAGEMENT SUITE
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" %*
if %errorlevel% neq 0 (
    echo.
    echo Execution error / Ocorreu um erro durante a execucao.
    pause
)