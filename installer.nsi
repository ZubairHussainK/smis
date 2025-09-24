; ================================================; ================================================

; SMIS Simple Installer Script (NSIS); SMIS Installer Script (NSIS)

; Single executable, clean installation; Generated and maintained via build workflow

; ================================================; ================================================



!include "MUI2.nsh"; NOTE:

; If building in GitHub Actions and NSIS is missing, the workflow step will

; --------------------------------; download and silently install NSIS automatically (see build-and-release.yml).

; Metadata; Ensure PyInstaller produced dist/SMIS-<version>.exe before invoking makensis.

; --------------------------------; Icon and LICENSE inclusion are conditional.

Name "SMIS - School Management Information System"

OutFile "SMIS-Setup-${VERSION}.exe"!include "MUI2.nsh"

InstallDir "$PROGRAMFILES\SMIS"

RequestExecutionLevel admin; --------------------------------

; Metadata

; Installation attributes; --------------------------------

SetCompressor /SOLID lzmaName "SMIS - School Management Information System"

SetCompressorDictSize 32OutFile "SMIS-Setup-${VERSION}.exe"

SetDatablockOptimize onInstallDir "$PROGRAMFILES\SMIS"

CRCCheck onRequestExecutionLevel admin

XPStyle on

BrandingText "SMIS Development Team"; Installation attributes to help with Windows security

ShowInstDetails showSetCompressor /SOLID lzma

ShowUnInstDetails showSetCompressorDictSize 32

SetDatablockOptimize on

; VERSION will be injected by GitHub ActionsCRCCheck on

!ifndef VERSIONXPStyle on

  !define VERSION "0.0.0"BrandingText "SMIS Development Team"

!endifShowInstDetails show

ShowUnInstDetails show

VIProductVersion "${VERSION}.0"

VIAddVersionKey /LANG=1033 "ProductName" "SMIS - School Management Information System"; VERSION will be injected by GitHub Actions (makensis /DVERSION=1.2.3)

VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"!ifndef VERSION

VIAddVersionKey /LANG=1033 "CompanyName" "SMIS Development Team"  !define VERSION "0.0.0"

VIAddVersionKey /LANG=1033 "LegalCopyright" "© 2025 SMIS Development Team"!endif

VIAddVersionKey /LANG=1033 "FileDescription" "School Management Information System Installer"

VIProductVersion "${VERSION}.0"

; --------------------------------VIAddVersionKey /LANG=1033 "ProductName" "SMIS - School Management Information System"

; Icons (conditional)VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"

; --------------------------------VIAddVersionKey /LANG=1033 "CompanyName" "SMIS Development Team"

!define ICON_PATH "resources\icons\app_icon.ico"VIAddVersionKey /LANG=1033 "LegalCopyright" "© 2025 SMIS Development Team"

!if /FileExists "${ICON_PATH}"VIAddVersionKey /LANG=1033 "FileDescription" "School Management Information System Installer"

  Icon "${ICON_PATH}"VIAddVersionKey /LANG=1033 "InternalName" "SMIS-Setup"

  UninstallIcon "${ICON_PATH}"VIAddVersionKey /LANG=1033 "OriginalFilename" "SMIS-Setup-${VERSION}.exe"

!endifVIAddVersionKey /LANG=1033 "ProductVersion" "${VERSION}"

; --------------------------------

; --------------------------------; Icons (conditional)

; Pages; --------------------------------

; --------------------------------!define ICON_PATH "resources\icons\app_icon.ico"

!define MUI_WELCOMEPAGE_TITLE "Welcome to SMIS Setup"!if /FileExists "${ICON_PATH}"

!define MUI_WELCOMEPAGE_TEXT "This will install SMIS - School Management Information System on your computer."  Icon "${ICON_PATH}"

!insertmacro MUI_PAGE_WELCOME  UninstallIcon "${ICON_PATH}"

!insertmacro MUI_PAGE_LICENSE "LICENSE"!else

!insertmacro MUI_PAGE_DIRECTORY  !warning "Icon not found at ${ICON_PATH}. Using default NSIS icon."

!insertmacro MUI_PAGE_INSTFILES!endif

!define MUI_FINISHPAGE_RUN "$INSTDIR\SMIS-${VERSION}.exe"

!insertmacro MUI_PAGE_FINISH; --------------------------------

; UI Pages

!insertmacro MUI_UNPAGE_CONFIRM; --------------------------------

!insertmacro MUI_UNPAGE_INSTFILES!insertmacro MUI_PAGE_WELCOME

!if /FileExists "LICENSE"

; --------------------------------  !insertmacro MUI_PAGE_LICENSE "LICENSE"

; Languages!endif

; --------------------------------!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_LANGUAGE "English"!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_PAGE_FINISH

; --------------------------------!insertmacro MUI_UNPAGE_CONFIRM

; Installation Section!insertmacro MUI_UNPAGE_INSTFILES

; --------------------------------!insertmacro MUI_LANGUAGE "English"

Section "Install"

  SetOutPath "$INSTDIR"; --------------------------------

; Definitions

  ; Install the main SMIS executable; --------------------------------

  File "dist\SMIS-${VERSION}.exe"Var StartMenuFolder

  

  ; Include icon if present; --------------------------------

  !if /FileExists "${ICON_PATH}"; Install Section

    File "${ICON_PATH}"; --------------------------------

  !endifSection "Install"

  SetOutPath "$INSTDIR"

  ; Create single desktop shortcut

  !if /FileExists "${ICON_PATH}"  ; Multiple application executables for maximum compatibility

    CreateShortcut "$DESKTOP\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico"  !if /FileExists "dist\\SMIS-${VERSION}-GUI.exe"

  !else    File "dist\\SMIS-${VERSION}-GUI.exe"

    CreateShortcut "$DESKTOP\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe"  !endif

  !endif  !if /FileExists "dist\\SMIS-${VERSION}-Console.exe"

      File "dist\\SMIS-${VERSION}-Console.exe"

  ; Create single Start Menu entry (no folder)  !endif  

  !if /FileExists "${ICON_PATH}"  !if /FileExists "dist\\SMIS-${VERSION}-Minimal.exe"

    CreateShortcut "$SMPROGRAMS\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico"    File "dist\\SMIS-${VERSION}-Minimal.exe"

  !else  !endif

    CreateShortcut "$SMPROGRAMS\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe"  

  !endif  ; Include compatibility information

  !if /FileExists "dist\\SMIS-${VERSION}-COMPATIBILITY.txt"

  ; Write uninstaller    File "dist\\SMIS-${VERSION}-COMPATIBILITY.txt"

  WriteUninstaller "$INSTDIR\Uninstall.exe"  !endif

  

  ; Add/Remove Programs entry  ; Include smart launcher

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayName" "SMIS - School Management Information System"  !if /FileExists "dist\\SMIS-SmartLauncher.bat"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "UninstallString" "$INSTDIR\Uninstall.exe"    File "dist\\SMIS-SmartLauncher.bat"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayVersion" "${VERSION}"  !endif

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "Publisher" "SMIS Development Team"

  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "NoModify" 1  ; Include icon in install directory if present

  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "NoRepair" 1  !if /FileExists "${ICON_PATH}"

    File "${ICON_PATH}"

SectionEnd  !endif



; --------------------------------  ; Create Start Menu folder

; Uninstall Section  CreateDirectory "$SMPROGRAMS\SMIS"

; --------------------------------

Section "Uninstall"  ; Primary shortcut - Smart Launcher (automatically chooses best version)

  ; Remove executable  !if /FileExists "dist\\SMIS-SmartLauncher.bat"

  Delete "$INSTDIR\SMIS-${VERSION}.exe"    CreateShortcut "$DESKTOP\SMIS.lnk" "$INSTDIR\SMIS-SmartLauncher.bat" "" "$INSTDIR\app_icon.ico"

  Delete "$INSTDIR\app_icon.ico"    CreateShortcut "$SMPROGRAMS\SMIS\SMIS (Smart Launcher).lnk" "$INSTDIR\SMIS-SmartLauncher.bat" "" "$INSTDIR\app_icon.ico"

  Delete "$INSTDIR\Uninstall.exe"  !endif

    

  ; Remove shortcuts  ; Direct shortcuts for manual selection

  Delete "$DESKTOP\SMIS.lnk"  !if /FileExists "dist\\SMIS-${VERSION}-GUI.exe"

  Delete "$SMPROGRAMS\SMIS.lnk"    CreateShortcut "$SMPROGRAMS\SMIS\SMIS (GUI Mode).lnk" "$INSTDIR\SMIS-${VERSION}-GUI.exe" "" "$INSTDIR\app_icon.ico"

    !endif

  ; Remove registry entries  

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS"  !if /FileExists "dist\\SMIS-${VERSION}-Console.exe"

      CreateShortcut "$SMPROGRAMS\SMIS\SMIS (Console Mode).lnk" "$INSTDIR\SMIS-${VERSION}-Console.exe" "" "$INSTDIR\app_icon.ico"

  ; Remove directory  !endif

  RMDir "$INSTDIR"  

SectionEnd  !if /FileExists "dist\\SMIS-${VERSION}-Minimal.exe"
    CreateShortcut "$SMPROGRAMS\SMIS\SMIS (Minimal).lnk" "$INSTDIR\SMIS-${VERSION}-Minimal.exe" "" "$INSTDIR\app_icon.ico"
  !endif

  ; Uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Registry (Uninstall info)
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayName" "SMIS"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "Publisher" "ZubairHussainKharal"
SectionEnd

; --------------------------------
; Uninstall Section
; --------------------------------
Section "Uninstall"
  ; Remove all executable variants
  Delete "$INSTDIR\SMIS-${VERSION}-GUI.exe"
  Delete "$INSTDIR\SMIS-${VERSION}-Console.exe"
  Delete "$INSTDIR\SMIS-${VERSION}-Minimal.exe"
  Delete "$INSTDIR\SMIS-${VERSION}-COMPATIBILITY.txt"
  Delete "$INSTDIR\SMIS-SmartLauncher.bat"
  Delete "$INSTDIR\app_icon.ico"
  
  ; Remove all shortcuts
  Delete "$DESKTOP\SMIS.lnk"
  Delete "$SMPROGRAMS\SMIS\SMIS (Smart Launcher).lnk"
  Delete "$SMPROGRAMS\SMIS\SMIS (GUI Mode).lnk"
  Delete "$SMPROGRAMS\SMIS\SMIS (Console Mode).lnk"
  Delete "$SMPROGRAMS\SMIS\SMIS (Minimal).lnk"
  RMDir  "$SMPROGRAMS\SMIS"
  
  ; Remove registry entries
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS"
  RMDir /r "$INSTDIR"
SectionEnd
