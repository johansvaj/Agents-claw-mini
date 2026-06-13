@echo off
setlocal enabledelayedexpansion

echo =================================================
echo    Nexcorix Claw Universal Launcher v7.0 (Windows)
echo =================================================

:: Deteksi Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Install Python 3.8+.
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo [✓] Python %PY_VER%

:: Virtual environment
if not exist "venv" (
    echo [i] Membuat virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [✓] Virtual environment aktif

:: Upgrade pip
python -m pip install --upgrade pip >nul 2>&1

:: Pilih mode
echo.
echo Pilih mode instalasi berdasarkan perkiraan ukuran unduhan:
echo   1) Minimal ( ^< 2 MB )   - hanya requests, urllib3
echo   2) Medium ( ~50 MB )    - + chromadb, onnxruntime (memori cerdas)
echo   3) Full ( ~300 MB )     - semua fitur (WebUI, Telegram, Discord, dll)
set /p mode="Masukkan pilihan [1/2/3]: "

:: Minimal selalu
echo [i] Menginstall library minimal...
python -m pip install requests urllib3
if %mode%==2 goto medium
if %mode%==3 goto full
goto run

:medium
echo [i] Menginstall library medium (chromadb, onnxruntime)...
python -m pip install chromadb onnxruntime
echo [i] Mengunduh model ONNX MiniLM-L6-v2 (sekitar 30 MB)...
python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()" 2>nul
goto run

:full
echo [i] Menginstall library medium...
python -m pip install chromadb onnxruntime
echo [i] Menginstall library full (fastapi, uvicorn, telegram, discord, schedule, pyyaml)...
python -m pip install fastapi uvicorn python-telegram-bot discord.py schedule pyyaml
set /p ans="Install sentence-transformers ( ~80 MB )? [y/N]: "
if /i "!ans!"=="y" (
    python -m pip install sentence-transformers
)
goto run

:run
if not exist "nexcorix_claw.py" (
    echo [ERROR] nexcorix_claw.py tidak ditemukan.
    exit /b 1
)
echo [✓] Menjalankan Nexcorix Claw...
python nexcorix_claw.py
pause
