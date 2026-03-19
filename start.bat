@echo off
echo ============================================
echo  SmartCompress AI v3 - Pure Python Edition
echo  No FFmpeg system install required!
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo Download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
echo [OK] Python found

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
echo [OK] Virtual environment ready

echo Installing dependencies (first run takes 1-2 minutes)...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

if not exist "temp"   mkdir temp
if not exist "assets" mkdir assets

echo.
echo [OK] All done! Launching app...
echo.
streamlit run app.py
pause
