@echo off
chcp 65001 >nul
title Anime Buddy - Setup
echo.
echo  === Anime Buddy for Windows ===
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found!
    echo  Please install Python from https://python.org
    echo  IMPORTANT: Tick "Add Python to PATH" during install!
    pause
    exit /b 1
)

echo  Python found! Installing packages...
echo.

pip install pyautogui pillow --quiet --upgrade

if errorlevel 1 (
    echo  Warning: Some packages may not have installed correctly.
    echo  Try running: pip install pyautogui pillow
    pause
)

echo.
echo  Starting Anime Buddy...
echo  - A transparent character window will appear on screen
echo  - A chat panel will open - type commands there
echo  - Right-click the character for quick actions
echo  - Drag the character to move her anywhere
echo.

python "%~dp0anime_buddy.py"

pause
