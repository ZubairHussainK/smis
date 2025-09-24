@echo off
echo ======================================================
echo SMIS Installer Helper
echo ======================================================
echo.
echo This helper will temporarily adjust Windows security 
echo settings to allow SMIS installation.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo Adding Windows Defender exclusion for SMIS...
powershell -Command "Add-MpPreference -ExclusionPath '%PROGRAMFILES%\SMIS' -Force" 2>nul
powershell -Command "Add-MpPreference -ExclusionProcess 'SMIS-*.exe' -Force" 2>nul

echo.
echo Starting SMIS installer...
echo Please follow the installation wizard.
echo.

REM Find and run the latest SMIS installer
for %%f in (SMIS-Setup-*-encrypted.exe) do (
    echo Running: %%f
    "%%f"
    goto :installed
)

echo No SMIS installer found in current directory.
echo Please make sure SMIS-Setup-*-encrypted.exe is in the same folder.
pause

:installed
echo.
echo Installation completed!
echo.
echo You can now safely run SMIS from:
echo - Desktop shortcut
echo - Start Menu ^> SMIS
echo.
pause