@echo off
title SMIS Smart Launcher
color 0A

echo ========================================
echo SMIS - Smart Launcher
echo ========================================
echo.
echo Detecting best compatible version...
echo.

REM Get version from directory
for /f "delims=" %%i in ('dir /b SMIS-*-GUI.exe 2^>nul') do set GUI_VERSION=%%i
for /f "delims=" %%i in ('dir /b SMIS-*-Console.exe 2^>nul') do set CONSOLE_VERSION=%%i
for /f "delims=" %%i in ('dir /b SMIS-*-Minimal.exe 2^>nul') do set MINIMAL_VERSION=%%i

REM Try GUI version first (recommended)
if exist "%GUI_VERSION%" (
    echo [1/3] Trying GUI version: %GUI_VERSION%
    echo Please wait...
    start "" "%GUI_VERSION%"
    timeout /t 3 /nobreak >nul
    
    REM Check if process started successfully
    tasklist /fi "imagename eq %GUI_VERSION%" 2>nul | find /i "%GUI_VERSION%" >nul
    if %errorlevel% equ 0 (
        echo ✓ GUI version started successfully!
        echo.
        echo SMIS is now running. You can close this window.
        pause
        exit /b 0
    ) else (
        echo ✗ GUI version failed to start
        echo.
    )
)

REM Try Console version if GUI failed
if exist "%CONSOLE_VERSION%" (
    echo [2/3] Trying Console version: %CONSOLE_VERSION%
    echo.
    echo Starting in console mode for better compatibility...
    echo Note: This version shows debug information.
    echo.
    pause
    "%CONSOLE_VERSION%"
    if %errorlevel% equ 0 (
        echo ✓ Console version completed successfully!
        pause
        exit /b 0
    ) else (
        echo ✗ Console version encountered errors
        echo.
    )
)

REM Try Minimal version as last resort
if exist "%MINIMAL_VERSION%" (
    echo [3/3] Trying Minimal version: %MINIMAL_VERSION%
    echo.
    echo This is the most basic version with minimal dependencies.
    echo.
    pause
    "%MINIMAL_VERSION%"
    if %errorlevel% equ 0 (
        echo ✓ Minimal version completed successfully!
        pause
        exit /b 0
    ) else (
        echo ✗ Minimal version also failed
        echo.
    )
)

REM If all versions failed
echo ========================================
echo ERROR: All SMIS versions failed to start
echo ========================================
echo.
echo Troubleshooting steps:
echo 1. Check if you have administrator privileges
echo 2. Install Visual C++ Redistributable x64
echo 3. Add Windows Defender exclusion
echo 4. Check COMPATIBILITY.txt file for details
echo 5. Run Windows Update
echo.
echo System Information:
ver
echo.
pause