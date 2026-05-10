@echo off
title JARVIS AI — Launcher
color 0B
cls
echo.
echo  =============================================
echo    J.A.R.V.I.S  v2.0  —  COMPLETE EDITION
echo    Powered by Google Gemini AI
echo  =============================================
echo.

:: ── Python check ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo  Download Python 3.10+ from: https://python.org
    pause & exit /b 1
)

:: ── Install dependencies ──────────────────────────────────────────────────
echo  Checking/installing dependencies...
pip install pyautogui pillow requests pygetwindow ^
            pyttsx3 psutil ^
            -q --disable-pip-version-check 2>nul
echo  [OK] Dependencies ready.
echo.

:: ── Create plugins folder if missing ─────────────────────────────────────
if not exist "plugins\" mkdir plugins

:: ── Launch ────────────────────────────────────────────────────────────────
echo  Launching JARVIS...
echo  (Avatar appears bottom-right. Double-click it to open the HUD.)
echo.
python jarvis.py

if errorlevel 1 (
    echo.
    echo  [ERROR] JARVIS exited with an error.
    echo  Check the error above and re-run.
    pause
)
