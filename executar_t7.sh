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

# Funcao para preparar a suite na Mesa com retentativas e fallback
preparar_suite_desktop() {
    DESKTOP_DIR="$HOME/Desktop/Acer-Predator-Connect-T7"
    echo "==========================================================================="
    echo "  [+] Configurando suite Acer Predator Connect T7 na Mesa (Desktop)..."
    echo "==========================================================================="

    mkdir -p "$DESKTOP_DIR"
    echo "  [*] Conectando ao GitHub (Download Modular Inteligente)..."
    if curl -sSL --retry 3 --retry-delay 2 "https://raw.githubusercontent.com/Despensativo/Acer-Predator-Connect-T7-Wi-Fi-7/main/iniciar.py" -o "$DESKTOP_DIR/iniciar.py"; then
        PROJECT_DIR="$DESKTOP_DIR"
        return 0
    else
        echo "==========================================================================="
        echo "  [-] ERRO: FALHA DE CONEXAO COM A INTERNET!"
        echo "==========================================================================="
        echo "  Nao foi possivel conectar ao GitHub para iniciar a suite."
        echo "  Por favor, verifique sua conexao de rede e execute novamente."
        echo "==========================================================================="
        exit 1
    fi
}

# Se for execucao via pipe (curl | bash) ou solicitada simulacao de cliente,
# baixa e executa 100% como usuario real na Mesa (Desktop)
if [ "$IS_PIPE" -eq 1 ] || [ "$SIMULAR_CLIENTE" -eq 1 ]; then
    preparar_suite_desktop
elif [ -f "$CURRENT_DIR/Scripts_Automacao/launcher_t7.py" ]; then
    PROJECT_DIR="$CURRENT_DIR"
elif [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/Scripts_Automacao/launcher_t7.py" ]; then
    PROJECT_DIR="$SCRIPT_DIR"
elif [ -d "$HOME/Desktop/Acer-Predator-Connect-T7/Scripts_Automacao" ]; then
    PROJECT_DIR="$HOME/Desktop/Acer-Predator-Connect-T7"
elif [ -d "$HOME/Acer-Predator-Connect-T7/Scripts_Automacao" ]; then
    PROJECT_DIR="$HOME/Acer-Predator-Connect-T7"
else
    preparar_suite_desktop
fi

# Validar se a pasta do projeto existe antes de continuar
if [ -z "$PROJECT_DIR" ] || [ ! -d "$PROJECT_DIR" ]; then
    echo "[-] Erro critico: Pasta de trabalho nao encontrada. Execucao abortada."
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

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

# 3. Definir script de entrada e verificar existencia
ENTRY_SCRIPT="$PROJECT_DIR/iniciar.py"
if [ ! -f "$ENTRY_SCRIPT" ]; then
    ENTRY_SCRIPT="$PROJECT_DIR/Scripts_Automacao/launcher_t7.py"
fi

if [ ! -f "$ENTRY_SCRIPT" ]; then
    echo "==========================================================================="
    echo " [-] ERRO: ARQUIVOS INCOMPLETOS NA PASTA!"
    echo "==========================================================================="
    echo " O download parece ter sido interrompido antes de concluir."
    echo " Execute o comando novamente para que a suíte seja baixada por completo."
    echo "==========================================================================="
    exit 1
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
