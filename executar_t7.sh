#!/bin/sh
# ===========================================================================
# executar_t7.sh - Launcher Inteligente para macOS e Linux
# Acer Predator Connect T7 & X7
# ===========================================================================

# 1. Fixar o diretorio de trabalho na pasta deste script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 2. Detectar se o Python 3 esta instalado
PYTHON_CMD=""

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    # Confere se 'python' e versao 3
    if python -c "import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)" >/dev/null 2>&1; then
        PYTHON_CMD="python"
    fi
fi

# 3. Se nao encontrar Python 3, orientar de forma didatica
if [ -z "$PYTHON_CMD" ]; then
    echo "==========================================================================="
    echo " [-] ERROR: PYTHON 3 NOT DETECTED / NÃO FOI ENCONTRADO!"
    echo "==========================================================================="
    echo ""
    echo " Please install Python 3 to run the Predator Connect T7/X7 suite:"
    echo ""
    if [ "$(uname)" = "Darwin" ]; then
        echo " -> macOS (Terminal with Homebrew):"
        echo "    brew install python3"
        echo "    Official installer: https://www.python.org/downloads/macos/"
    else
        echo " -> Linux (Ubuntu / Debian / Mint):"
        echo "    sudo apt update && sudo apt install -y python3"
        echo " -> Linux (Fedora / RHEL):"
        echo "    sudo dnf install -y python3"
        echo " -> Linux (Arch):"
        echo "    sudo pacman -S python"
    fi
    echo ""
    echo "==========================================================================="
    exit 1
fi

# 4. Selecao de Idioma se nao passado por argumento
LANG_PARAM="en"
ENTRY_SCRIPT="$SCRIPT_DIR/iniciar.py"
if [ ! -f "$ENTRY_SCRIPT" ]; then
    ENTRY_SCRIPT="$SCRIPT_DIR/Scripts_Automacao/launcher_t7.py"
fi

if [ $# -eq 0 ]; then
    echo "==========================================================================="
    echo "              ACER PREDATOR CONNECT T7 & X7 MANAGEMENT SUITE"
    echo "==========================================================================="
    echo ""
    echo "  Select Language / Selecione o Idioma:"
    echo "  [1] English (Default - Press ENTER)"
    echo "  [2] Português (Brasil)"
    echo ""
    printf "  Choice / Escolha [1/2] (Default: 1): "
    read -r LANG_INPUT
    if [ "$LANG_INPUT" = "2" ] || [ "$LANG_INPUT" = "pt" ] || [ "$LANG_INPUT" = "pt-br" ]; then
        LANG_PARAM="pt"
    fi
    exec "$PYTHON_CMD" "$ENTRY_SCRIPT" --lang "$LANG_PARAM"
else
    exec "$PYTHON_CMD" "$ENTRY_SCRIPT" "$@"
fi
