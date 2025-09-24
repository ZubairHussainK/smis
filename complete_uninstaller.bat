@echo off
echo ===============================================
echo SMIS Complete Uninstaller
echo ===============================================
echo This will completely remove SMIS from your system
echo.
pause

echo.
echo [1/6] Stopping any running SMIS processes...
taskkill /F /IM "SMIS*.exe" 2>nul
timeout /t 2 >nul

echo [2/6] Removing SMIS installation directory...
if exist "C:\Program Files\SMIS" (
    echo Removing: C:\Program Files\SMIS
    rmdir /S /Q "C:\Program Files\SMIS"
)
if exist "C:\Program Files (x86)\SMIS" (
    echo Removing: C:\Program Files (x86)\SMIS
    rmdir /S /Q "C:\Program Files (x86)\SMIS"
)

echo [3/6] Removing Desktop shortcuts...
if exist "%USERPROFILE%\Desktop\SMIS.lnk" (
    echo Removing: Desktop shortcut
    del "%USERPROFILE%\Desktop\SMIS.lnk"
)

echo [4/6] Removing Start Menu shortcuts...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\SMIS.lnk" (
    echo Removing: Start Menu shortcut
    del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\SMIS.lnk"
)

echo [5/6] Cleaning registry entries...
echo Removing HKLM registry entries...
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" /f 2>nul
reg delete "HKLM\Software\ZubairHussainK\SMIS" /f 2>nul

echo Removing HKCU registry entries...
reg delete "HKCU\Software\ZubairHussainK\SMIS" /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "SMIS" /f 2>nul

echo [6/6] Cleaning temporary files...
if exist "%TEMP%\SMIS*" (
    echo Removing temp files...
    del /Q "%TEMP%\SMIS*" 2>nul
)

echo.
echo ===============================================
echo SMIS has been completely uninstalled!
echo ===============================================
echo.
echo You can now safely install the latest version.
echo Download v2.1.3 from: https://github.com/ZubairHussainK/smis/releases/latest
echo.
pause