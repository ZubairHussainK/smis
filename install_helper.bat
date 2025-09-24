@echo off
echo ======================================================
echo SMIS Universal Installation Helper
echo ======================================================
echo.
echo This helper will:
echo - Configure Windows security settings
echo - Install Visual C++ Redistributable if needed
echo - Run the SMIS installer
echo - Test all available versions for compatibility
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [1/4] Adding Windows Defender exclusions...
powershell -Command "Add-MpPreference -ExclusionPath '%PROGRAMFILES%\SMIS' -Force" 2>nul
powershell -Command "Add-MpPreference -ExclusionProcess 'SMIS-*.exe' -Force" 2>nul
echo ✓ Windows Defender exclusions added

echo.
echo [2/4] Checking Visual C++ Redistributable...
if exist "%SystemRoot%\System32\vcruntime140.dll" (
    echo ✓ Visual C++ Redistributable is already installed
) else (
    echo Downloading Visual C++ Redistributable...
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://aka.ms/vs/17/release/vc_redist.x64.exe', 'vc_redist.x64.exe')" 2>nul
    if exist "vc_redist.x64.exe" (
        echo Installing Visual C++ Redistributable...
        vc_redist.x64.exe /quiet /norestart
        del vc_redist.x64.exe
        echo ✓ Visual C++ Redistributable installed
    ) else (
        echo ⚠ Could not download VC++ Redistributable automatically
    )
)

echo.
echo [3/4] Starting SMIS installer...
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
goto :end

:installed
echo.
echo [4/4] Testing installation...
if exist "%PROGRAMFILES%\SMIS\SMIS-SmartLauncher.bat" (
    echo ✓ Installation successful!
    echo.
    echo You can now run SMIS using:
    echo - Desktop shortcut: SMIS
    echo - Start Menu: All Programs → SMIS
    echo - Smart Launcher: %PROGRAMFILES%\SMIS\SMIS-SmartLauncher.bat
    echo.
    echo The Smart Launcher automatically chooses the best version for your system.
    echo.
    set /p "launch=Would you like to test SMIS now? (Y/N): "
    if /i "%launch%"=="Y" (
        "%PROGRAMFILES%\SMIS\SMIS-SmartLauncher.bat"
    )
) else (
    echo ⚠ Installation may not have completed successfully
    echo Please check the installation directory manually
)

:end
echo.
echo Installation process completed!
pause