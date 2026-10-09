#!/bin/bash
# -*- coding: utf-8 -*-
# ==============================================================================
# monitorar_t7.sh - Painel de Telemetria e Monitoria ao Vivo (HUD)
# Acer Predator Connect T7 (Qualcomm IPQ5332 + QCN9224 Wi-Fi 7)
# ==============================================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="/Users/user/.antigravity-tools-env/bin/python3"

if [ ! -x "$PYTHON" ]; then
    PYTHON=$(command -v python3 || echo "python3")
fi

echo "=================================================================="
echo "    INICIANDO PAINEL DE TELEMETRIA AO VIVO - PREDATOR T7"
echo "=================================================================="
echo " Conectando a 192.168.76.1 via OpenSSH Multiplexado..."
echo " Pressione Ctrl+C a qualquer momento para sair."
echo "=================================================================="

exec "$PYTHON" "$DIR/04_SCRIPTS_E_FERRAMENTAS/monitorar_t7_live.py" "$@"
