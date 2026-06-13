@echo off
setlocal enabledelayedexpansion

echo =================================================
echo    Nexcorix Claw Universal Launcher v6.0 (Windows)
echo =================================================

:: Deteksi Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Install Python 3.8+.
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo [✓] Python %PY_VER%

:: Setup virtual environment
if not exist "venv" (
    echo [i] Membuat virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [✓] Virtual environment aktif

:: Upgrade pip
python -m pip install --upgrade pip >nul 2>&1
echo [✓] pip upgrade selesai

:: Install minimal
echo [i] Menginstall library minimal...
python -m pip install requests urllib3 >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] requests dan urllib3 terinstall
) else (
    echo [❌] Gagal install library minimal
)

:: Tanya advanced
echo.
set /p answer="Install library advanced untuk fitur penuh? (chromadb, fastapi, dll) [y/N]: "
if /i "%answer%"=="y" (
    echo [i] Menginstall library advanced...
    set FAILED=0
    for %%l in (chromadb sentence-transformers fastapi uvicorn python-telegram-bot discord.py schedule pyyaml sqlite-utils) do (
        echo [⏳] Menginstall %%l...
        python -m pip install %%l >nul 2>&1
        if !errorlevel! equ 0 (
            echo [✅] %%l berhasil
        ) else (
            echo [❌] %%l gagal
            set FAILED=1
        )
    )
    if !FAILED! equ 0 (
        echo [✓] Semua library advanced terinstall.
    ) else (
        echo [!] Beberapa library advanced gagal, program mungkin berjalan terbatas.
    )
) else (
    echo [i] Lewati install library advanced.
)

:: Jalankan program
if not exist "nexcorix_claw.py" (
    echo [ERROR] File nexcorix_claw.py tidak ditemukan.
    exit /b 1
)
echo [✓] Menjalankan Nexcorix Claw...
python nexcorix_claw.py

pause
