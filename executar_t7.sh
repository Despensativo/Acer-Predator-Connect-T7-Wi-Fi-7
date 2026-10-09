#!/bin/sh
# ===========================================================================
# executar_t7.sh - Launcher Inteligente para macOS e Linux
# Acer Predator Connect T7 (IPQ5332) & X7
# Suporta execucao local e remota (curl | bash)
# ===========================================================================

# 1. Localizar ou preparar a pasta de trabalho da Suite
PROJECT_DIR=""
CURRENT_DIR="$(pwd)"
SCRIPT_DIR=""
IS_PIPE=0
SIMULAR_CLIENTE=0

# Detectar se esta sendo executado via pipe (curl | bash)
case "$0" in
    bash|sh|-bash|-sh)
        IS_PIPE=1
        ;;
esac

for arg in "$@"; do
    case "$arg" in
        --simular|--cliente|--fresh|--clean)
            SIMULAR_CLIENTE=1
            ;;
    esac
done

if [ -n "$0" ] && [ -f "$0" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

# Se for execucao via pipe (curl | bash) ou solicitada simulacao de cliente,
# baixa e executa 100% como usuario real na Mesa (Desktop)
if [ "$IS_PIPE" -eq 1 ] || [ "$SIMULAR_CLIENTE" -eq 1 ]; then
    DESKTOP_DIR="$HOME/Desktop/Acer-Predator-Connect-T7"
    echo "==========================================================================="
    echo "  [+] Modo Cliente Real: Configurando suite na Mesa (Desktop)..."
    echo "==========================================================================="
    if [ -d "$DESKTOP_DIR/.git" ]; then
        echo "  [*] Atualizando suite existente na Mesa (Desktop)..."
        git -C "$DESKTOP_DIR" pull --ff-only 2>/dev/null || (cd "$DESKTOP_DIR" && git fetch && git reset --hard origin/main 2>/dev/null) || true
    else
        if [ -d "$DESKTOP_DIR" ]; then
            rm -rf "$DESKTOP_DIR"
        fi
        if command -v git >/dev/null 2>&1; then
            echo "  [*] Baixando repositorio oficial do GitHub..."
            git clone https://github.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7.git "$DESKTOP_DIR"
        else
            mkdir -p "$DESKTOP_DIR"
            echo "  [*] Baixando assistente de inicializacao do GitHub..."
            curl -sSL "https://raw.githubusercontent.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/main/iniciar.py" -o "$DESKTOP_DIR/iniciar.py"
        fi
    fi
    PROJECT_DIR="$DESKTOP_DIR"
elif [ -f "$CURRENT_DIR/Scripts_Automacao/launcher_t7.py" ]; then
    PROJECT_DIR="$CURRENT_DIR"
elif [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/Scripts_Automacao/launcher_t7.py" ]; then
    PROJECT_DIR="$SCRIPT_DIR"
elif [ -d "$HOME/Desktop/Acer-Predator-Connect-T7/Scripts_Automacao" ]; then
    PROJECT_DIR="$HOME/Desktop/Acer-Predator-Connect-T7"
elif [ -d "$HOME/Acer-Predator-Connect-T7/Scripts_Automacao" ]; then
    PROJECT_DIR="$HOME/Acer-Predator-Connect-T7"
else
    # Se nao existe em nenhum local conhecido, clonar para a Mesa (Desktop)
    DESKTOP_DIR="$HOME/Desktop/Acer-Predator-Connect-T7"
    echo "==========================================================================="
    echo "  [+] Configurando suite Acer Predator Connect T7 na Mesa (Desktop)..."
    echo "==========================================================================="
    if [ -d "$DESKTOP_DIR/.git" ]; then
        git -C "$DESKTOP_DIR" pull --ff-only 2>/dev/null || true
    else
        if [ -d "$DESKTOP_DIR" ]; then
            rm -rf "$DESKTOP_DIR"
        fi
        if command -v git >/dev/null 2>&1; then
            git clone https://github.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7.git "$DESKTOP_DIR"
        else
            mkdir -p "$DESKTOP_DIR"
            curl -sSL "https://raw.githubusercontent.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/main/iniciar.py" -o "$DESKTOP_DIR/iniciar.py"
        fi
    fi
    PROJECT_DIR="$DESKTOP_DIR"
fi

cd "$PROJECT_DIR"

# 2. Detectar o melhor interpretador Python 3
PYTHON_CMD=""
if [ -x "/Users/user/.antigravity-tools-env/bin/python3" ]; then
    PYTHON_CMD="/Users/user/.antigravity-tools-env/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    if python -c "import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)" >/dev/null 2>&1; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "==========================================================================="
    echo " [-] ERRO: PYTHON 3 NÃO FOI ENCONTRADO!"
    echo "==========================================================================="
    echo " Instale o Python 3 para executar a suíte Predator Connect T7:"
    echo " -> macOS (Terminal): brew install python3"
    echo " -> Linux (Debian/Ubuntu): sudo apt update && sudo apt install -y python3"
    echo "==========================================================================="
    exit 1
fi

# 3. Definir script de entrada
ENTRY_SCRIPT="$PROJECT_DIR/iniciar.py"
if [ ! -f "$ENTRY_SCRIPT" ]; then
    ENTRY_SCRIPT="$PROJECT_DIR/Scripts_Automacao/launcher_t7.py"
fi

# 4. Selecao de Idioma e Execucao Interativa
LANG_PARAM="pt"

if [ $# -gt 0 ]; then
    exec "$PYTHON_CMD" "$ENTRY_SCRIPT" "$@"
fi

# Se estiver sendo executado via pipe (curl | bash), redirecionar entrada para /dev/tty
if [ -t 0 ]; then
    # Terminal normal
    echo "==========================================================================="
    echo "              ACER PREDATOR CONNECT T7 & X7 MANAGEMENT SUITE"
    echo "==========================================================================="
    echo "  Pasta de Trabalho: $PROJECT_DIR"
    echo ""
    echo "  Selecione o Idioma / Select Language:"
    echo "  [1] English"
    echo "  [2] Português (Brasil) (Padrão - Pressione ENTER)"
    echo ""
    printf "  Escolha / Choice [1/2] (Padrão: 2): "
    read -r LANG_INPUT
    if [ "$LANG_INPUT" = "1" ] || [ "$LANG_INPUT" = "en" ]; then
        LANG_PARAM="en"
    fi
    exec "$PYTHON_CMD" "$ENTRY_SCRIPT" --lang "$LANG_PARAM"
elif [ -c /dev/tty ]; then
    # Executado via curl | bash mas com tty disponivel
    echo "==========================================================================="
    echo "              ACER PREDATOR CONNECT T7 & X7 MANAGEMENT SUITE"
    echo "==========================================================================="
    echo "  Pasta de Trabalho: $PROJECT_DIR"
    echo ""
    echo "  Selecione o Idioma / Select Language:"
    echo "  [1] English"
    echo "  [2] Português (Brasil) (Padrão - Pressione ENTER)"
    echo ""
    printf "  Escolha / Choice [1/2] (Padrão: 2): "
    read -r LANG_INPUT </dev/tty
    if [ "$LANG_INPUT" = "1" ] || [ "$LANG_INPUT" = "en" ]; then
        LANG_PARAM="en"
    fi
    exec "$PYTHON_CMD" "$ENTRY_SCRIPT" --lang "$LANG_PARAM" </dev/tty
else
    # Sem TTY interativo, executa com portugues direto
    exec "$PYTHON_CMD" "$ENTRY_SCRIPT" --lang "pt"
fi
