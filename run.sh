#!/usr/bin/env bash
# Nexcorix Claw - Universal Launcher with Size Options

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Nexcorix Claw Universal Launcher v7.0   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"

# ---------- 1. Deteksi Python ----------
detect_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}[ERROR] Python tidak ditemukan. Install Python 3.8+.${NC}"
        exit 1
    fi
    PY_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
    PY_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
    if [ "$PY_MAJOR" -lt 3 ] || ( [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ] ); then
        echo -e "${RED}[ERROR] Python $PY_MAJOR.$PY_MINOR < 3.8. Upgrade Python.${NC}"
        exit 1
    fi
    echo -e "${GREEN}[✓] Python $PY_MAJOR.$PY_MINOR ($PYTHON_CMD)${NC}"
}

# ---------- 2. Virtual Environment ----------
setup_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}[i] Membuat virtual environment...${NC}"
        $PYTHON_CMD -m venv venv
    fi
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo -e "${GREEN}[✓] Virtual environment aktif (venv)${NC}"
    PYTHON_CMD="python"
}

# ---------- 3. Pilih Mode Instalasi ----------
choose_mode() {
    echo ""
    echo -e "${YELLOW}Pilih mode instalasi berdasarkan perkiraan ukuran unduhan:${NC}"
    echo "  1) Minimal ( < 2 MB )   - hanya library dasar (requests, urllib3)"
    echo "  2) Medium ( ~50 MB )    - + chromadb + onnxruntime (memori cerdas tanpa sentence-transformers)"
    echo "  3) Full ( ~300 MB )     - semua fitur (WebUI, Telegram, Discord, cron, sentence-transformers)"
    echo -n "Masukkan pilihan [1/2/3]: "
    read -r mode
    case $mode in
        1) INSTALL_MODE="minimal" ;;
        2) INSTALL_MODE="medium" ;;
        3) INSTALL_MODE="full" ;;
        *) echo -e "${RED}Pilihan tidak valid, menggunakan mode minimal.${NC}"; INSTALL_MODE="minimal" ;;
    esac
}

# ---------- 4. Install Library Berdasarkan Mode ----------
install_libs() {
    echo -e "${YELLOW}[i] Upgrade pip...${NC}"
    $PYTHON_CMD -m pip install --upgrade pip > /dev/null 2>&1
    echo -e "${GREEN}[✓] pip upgrade selesai.${NC}"

    # Library minimal (selalu)
    echo -e "${YELLOW}[i] Menginstall library minimal...${NC}"
    $PYTHON_CMD -m pip install requests urllib3
    echo -e "${GREEN}[✓] Library minimal terinstall.${NC}"

    if [ "$INSTALL_MODE" = "medium" ] || [ "$INSTALL_MODE" = "full" ]; then
        echo -e "${YELLOW}[i] Menginstall library medium (chromadb, onnxruntime)...${NC}"
        $PYTHON_CMD -m pip install chromadb onnxruntime
        echo -e "${GREEN}[✓] ChromaDB dan onnxruntime terinstall.${NC}"
        echo -e "${YELLOW}[i] Mengunduh model ONNX MiniLM-L6-v2 (sekitar 30 MB)...${NC}"
        # Pre-download model agar tidak mengganggu saat pertama run
        $PYTHON_CMD -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()" 2>/dev/null || true
        echo -e "${GREEN}[✓] Model embedding ONNX siap.${NC}"
    fi

    if [ "$INSTALL_MODE" = "full" ]; then
        echo -e "${YELLOW}[i] Menginstall library full (fastapi, uvicorn, telegram, discord, schedule, pyyaml, sentence-transformers)...${NC}"
        $PYTHON_CMD -m pip install fastapi uvicorn python-telegram-bot discord.py schedule pyyaml
        # sentence-transformers opsional (berat, 80 MB) -> tanya lagi?
        echo -e "${YELLOW}Install sentence-transformers untuk semantic search terbaik? ( ~80 MB ) [y/N]:${NC}"
        read -r ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            $PYTHON_CMD -m pip install sentence-transformers
            echo -e "${GREEN}[✓] sentence-transformers terinstall.${NC}"
        else
            echo -e "${GREEN}[i] Lewati sentence-transformers (fallback ke ONNX).${NC}"
        fi
        echo -e "${GREEN}[✓] Library full selesai.${NC}"
    fi

    echo -e "${GREEN}[✓] Instalasi selesai.${NC}"
}

# ---------- 5. Jalankan Program ----------
run_claw() {
    if [ ! -f "nexcorix_claw.py" ]; then
        echo -e "${RED}[ERROR] File nexcorix_claw.py tidak ditemukan.${NC}"
        exit 1
    fi
    echo -e "${GREEN}[✓] Menjalankan Nexcorix Claw...${NC}"
    $PYTHON_CMD nexcorix_claw.py
}

# ---------- Main ----------
detect_python
setup_venv
choose_mode
install_libs
run_claw
