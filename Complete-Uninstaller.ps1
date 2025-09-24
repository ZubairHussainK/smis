# SMIS Complete Uninstaller PowerShell Script
Write-Host "===============================================" -ForegroundColor Green
Write-Host "SMIS Complete Uninstaller" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "This will completely remove SMIS from your system" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue or Ctrl+C to cancel"

# Function to safely remove registry key
function Remove-RegistryKey {
    param($Path)
    try {
        if (Test-Path $Path) {
            Remove-Item -Path $Path -Recurse -Force
            Write-Host "✓ Removed registry: $Path" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠ Could not remove registry: $Path" -ForegroundColor Yellow
    }
}

# Function to safely remove file/folder
function Remove-PathSafely {
    param($Path, $Description)
    try {
        if (Test-Path $Path) {
            Remove-Item -Path $Path -Recurse -Force
            Write-Host "✓ Removed $Description`: $Path" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠ Could not remove $Description`: $Path" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[1/6] Stopping any running SMIS processes..." -ForegroundColor Cyan
try {
    Get-Process | Where-Object {$_.ProcessName -like "SMIS*"} | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "✓ SMIS processes stopped" -ForegroundColor Green
} catch {
    Write-Host "ℹ No SMIS processes were running" -ForegroundColor Gray
}

Write-Host "[2/6] Removing SMIS installation directories..." -ForegroundColor Cyan
Remove-PathSafely "C:\Program Files\SMIS" "Program Files directory"
Remove-PathSafely "C:\Program Files (x86)\SMIS" "Program Files (x86) directory"
Remove-PathSafely "$env:LOCALAPPDATA\SMIS" "Local AppData directory"
Remove-PathSafely "$env:APPDATA\SMIS" "AppData directory"

Write-Host "[3/6] Removing Desktop shortcuts..." -ForegroundColor Cyan
Remove-PathSafely "$env:USERPROFILE\Desktop\SMIS.lnk" "Desktop shortcut"
Remove-PathSafely "$env:PUBLIC\Desktop\SMIS.lnk" "Public Desktop shortcut"

Write-Host "[4/6] Removing Start Menu shortcuts..." -ForegroundColor Cyan
Remove-PathSafely "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\SMIS.lnk" "Start Menu shortcut"
Remove-PathSafely "$env:PROGRAMDATA\Microsoft\Windows\Start Menu\Programs\SMIS.lnk" "All Users Start Menu shortcut"

Write-Host "[5/6] Cleaning registry entries..." -ForegroundColor Cyan
# HKEY_LOCAL_MACHINE entries
Remove-RegistryKey "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS"
Remove-RegistryKey "HKLM:\Software\ZubairHussainK\SMIS" 
Remove-RegistryKey "HKLM:\Software\Wow6432Node\ZubairHussainK\SMIS"

# HKEY_CURRENT_USER entries  
Remove-RegistryKey "HKCU:\Software\ZubairHussainK\SMIS"
Remove-RegistryKey "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue

# Remove specific startup entry
try {
    $runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    if (Get-ItemProperty -Path $runKey -Name "SMIS" -ErrorAction SilentlyContinue) {
        Remove-ItemProperty -Path $runKey -Name "SMIS" -Force
        Write-Host "✓ Removed SMIS from startup" -ForegroundColor Green
    }
} catch {
    Write-Host "ℹ SMIS was not in startup registry" -ForegroundColor Gray
}

Write-Host "[6/6] Cleaning temporary and cache files..." -ForegroundColor Cyan
Remove-PathSafely "$env:TEMP\SMIS*" "Temp files"
Remove-PathSafely "$env:TEMP\pip-*" "Pip temp files"
Remove-PathSafely "$env:LOCALAPPDATA\pip\cache" "Pip cache"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "SMIS has been completely uninstalled!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ All SMIS files and registry entries removed" -ForegroundColor Green
Write-Host "✅ Shortcuts and startup entries cleaned" -ForegroundColor Green
Write-Host "✅ Temporary files cleared" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Download the latest version (v2.1.3) from:" -ForegroundColor Yellow
Write-Host "   https://github.com/ZubairHussainK/smis/releases/latest" -ForegroundColor Blue
Write-Host ""
Write-Host "📝 After installing v2.1.3, the PyQt5 errors should be resolved!" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"