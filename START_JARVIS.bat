@echo off
title JARVIS AI Launcher
color 0B
echo.
echo  ========================================
echo     J.A.R.V.I.S  -  AI Desktop Assistant
echo  ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Please install Python 3.8+
    echo  Download from: https://python.org
    pause
    exit /b 1
)

:: Install requirements silently
echo  Installing/checking requirements...
pip install pyautogui pillow requests pygetwindow -q --disable-pip-version-check

echo.
echo  ========================================
echo   OPTIONAL: Set Anthropic API Key for
echo   full AI natural language features.
echo.
echo   Get your key at: console.anthropic.com
echo.
echo   Type your key below or press Enter
echo   to run in keyword mode (still works!):
echo  ========================================
echo.
set /p apikey="  API Key (or Enter to skip): "

if not "%apikey%"=="" (
    set ANTHROPIC_API_KEY=%apikey%
    echo  [OK] AI features ENABLED
) else (
    echo  [OK] Running in keyword mode
)

echo.
echo  Launching JARVIS...
echo.

python jarvis.py

if errorlevel 1 (
    echo.
    echo  [ERROR] JARVIS crashed. Check errors above.
    pause
)
