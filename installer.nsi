!include "MUI2.nsh"!include "MUI2.nsh"; ================================================; ================================================; ================================================



Name "SMIS"

OutFile "SMIS-Setup-${VERSION}.exe"

InstallDir "$PROGRAMFILES\SMIS"Name "SMIS School Management System"; SMIS Simple Installer Script (NSIS)

RequestExecutionLevel admin

OutFile "SMIS-Setup-${VERSION}.exe"

SetCompressor /SOLID lzma

SetCompressorDictSize 32InstallDir "$PROGRAMFILES\SMIS"; Single executable, clean installation; SMIS Simple Installer Script (NSIS); SMIS Installer Script (NSIS)

BrandingText "SMIS Team"

RequestExecutionLevel admin

!ifndef VERSION

  !define VERSION "0.0.0"; ================================================

!endif

SetCompressor /SOLID lzma

VIProductVersion "${VERSION}.0"

VIAddVersionKey /LANG=1033 "ProductName" "SMIS"SetCompressorDictSize 32; Single executable, clean installation; Generated and maintained via build workflow

VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"

SetDatablockOptimize on

!define ICON_PATH "resources\icons\app_icon.ico"

!if /FileExists "${ICON_PATH}"CRCCheck on!include "MUI2.nsh"

  Icon "${ICON_PATH}"

!endifXPStyle on



!insertmacro MUI_PAGE_WELCOMEBrandingText "SMIS Development Team"; ================================================; ================================================

!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILESShowInstDetails show

!insertmacro MUI_PAGE_FINISH

ShowUnInstDetails show; --------------------------------

!insertmacro MUI_UNPAGE_CONFIRM

!insertmacro MUI_UNPAGE_INSTFILES



!insertmacro MUI_LANGUAGE "English"!ifndef VERSION; Metadata



Section "Install"  !define VERSION "0.0.0"

  SetOutPath "$INSTDIR"

  File "dist\SMIS-${VERSION}.exe"!endif; --------------------------------

  

  !if /FileExists "${ICON_PATH}"; Metadata

    File "${ICON_PATH}"

  !endifVIProductVersion "${VERSION}.0"; --------------------------------



  CreateShortcut "$DESKTOP\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe"VIAddVersionKey /LANG=1033 "ProductName" "SMIS School Management System"Name "SMIS School Management System"

  CreateShortcut "$SMPROGRAMS\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe"

VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"OutFile "SMIS-Setup-${VERSION}.exe"

  WriteUninstaller "$INSTDIR\Uninstall.exe"

VIAddVersionKey /LANG=1033 "CompanyName" "SMIS Development Team"InstallDir "$PROGRAMFILES\SMIS"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayName" "SMIS"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "UninstallString" "$INSTDIR\Uninstall.exe"VIAddVersionKey /LANG=1033 "LegalCopyright" "© 2025 SMIS Development Team"RequestExecutionLevel admin

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayVersion" "${VERSION}"

SectionEndVIAddVersionKey /LANG=1033 "FileDescription" "School Management Information System Installer"



Section "Uninstall"RequestExecutionLevel admin

  Delete "$INSTDIR\SMIS-${VERSION}.exe"

  Delete "$INSTDIR\app_icon.ico"!define ICON_PATH "resources\icons\app_icon.ico"

  Delete "$INSTDIR\Uninstall.exe"

  Delete "$DESKTOP\SMIS.lnk"!if /FileExists "${ICON_PATH}"; --------------------------------; download and silently install NSIS automatically (see build-and-release.yml).

  Delete "$SMPROGRAMS\SMIS.lnk"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS"  Icon "${ICON_PATH}"

  RMDir "$INSTDIR"

SectionEnd  UninstallIcon "${ICON_PATH}"; Installation attributes

!endif

SetCompressor /SOLID lzma; Metadata; Ensure PyInstaller produced dist/SMIS-<version>.exe before invoking makensis.

!define MUI_WELCOMEPAGE_TITLE "Welcome to SMIS Setup"

!define MUI_WELCOMEPAGE_TEXT "This will install SMIS School Management System on your computer."SetCompressorDictSize 32

!insertmacro MUI_PAGE_WELCOME

!insertmacro MUI_PAGE_LICENSE "LICENSE"SetDatablockOptimize on; --------------------------------; Icon and LICENSE inclusion are conditional.

!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILESCRCCheck on

!define MUI_FINISHPAGE_RUN "$INSTDIR\SMIS-${VERSION}.exe"

!insertmacro MUI_PAGE_FINISHXPStyle onName "SMIS - School Management Information System"



!insertmacro MUI_UNPAGE_CONFIRMBrandingText "SMIS Development Team"

!insertmacro MUI_UNPAGE_INSTFILES

ShowInstDetails showOutFile "SMIS-Setup-${VERSION}.exe"!include "MUI2.nsh"

!insertmacro MUI_LANGUAGE "English"

ShowUnInstDetails show

Section "Install"

  SetOutPath "$INSTDIR"InstallDir "$PROGRAMFILES\SMIS"



  File "dist\SMIS-${VERSION}.exe"; VERSION will be injected by GitHub Actions

  

  !if /FileExists "${ICON_PATH}"!ifndef VERSIONRequestExecutionLevel admin; --------------------------------

    File "${ICON_PATH}"

  !endif  !define VERSION "0.0.0"



  !if /FileExists "${ICON_PATH}"!endif; Metadata

    CreateShortcut "$DESKTOP\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico"

  !else

    CreateShortcut "$DESKTOP\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe"

  !endifVIProductVersion "${VERSION}.0"; Installation attributes; --------------------------------

  

  !if /FileExists "${ICON_PATH}"VIAddVersionKey /LANG=1033 "ProductName" "SMIS - School Management Information System"

    CreateShortcut "$SMPROGRAMS\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico"

  !elseVIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"SetCompressor /SOLID lzmaName "SMIS - School Management Information System"

    CreateShortcut "$SMPROGRAMS\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe"

  !endifVIAddVersionKey /LANG=1033 "CompanyName" "SMIS Development Team"



  WriteUninstaller "$INSTDIR\Uninstall.exe"VIAddVersionKey /LANG=1033 "LegalCopyright" "© 2025 SMIS Development Team"SetCompressorDictSize 32OutFile "SMIS-Setup-${VERSION}.exe"



  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayName" "SMIS School Management System"VIAddVersionKey /LANG=1033 "FileDescription" "School Management Information System Installer"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "UninstallString" "$INSTDIR\Uninstall.exe"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayVersion" "${VERSION}"SetDatablockOptimize onInstallDir "$PROGRAMFILES\SMIS"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "Publisher" "SMIS Development Team"

  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "NoModify" 1; --------------------------------

  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "NoRepair" 1

; Icons (conditional)CRCCheck onRequestExecutionLevel admin

SectionEnd

; --------------------------------

Section "Uninstall"

  Delete "$INSTDIR\SMIS-${VERSION}.exe"!define ICON_PATH "resources\icons\app_icon.ico"XPStyle on

  Delete "$INSTDIR\app_icon.ico"

  Delete "$INSTDIR\Uninstall.exe"!if /FileExists "${ICON_PATH}"

  

  Delete "$DESKTOP\SMIS.lnk"  Icon "${ICON_PATH}"BrandingText "SMIS Development Team"; Installation attributes to help with Windows security

  Delete "$SMPROGRAMS\SMIS.lnk"

    UninstallIcon "${ICON_PATH}"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS"

  !endifShowInstDetails showSetCompressor /SOLID lzma

  RMDir "$INSTDIR"

SectionEnd

; --------------------------------ShowUnInstDetails showSetCompressorDictSize 32

; Pages

; --------------------------------SetDatablockOptimize on

!define MUI_WELCOMEPAGE_TITLE "Welcome to SMIS Setup"

!define MUI_WELCOMEPAGE_TEXT "This will install SMIS - School Management Information System on your computer."; VERSION will be injected by GitHub ActionsCRCCheck on

!insertmacro MUI_PAGE_WELCOME

!insertmacro MUI_PAGE_LICENSE "LICENSE"!ifndef VERSIONXPStyle on

!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES  !define VERSION "0.0.0"BrandingText "SMIS Development Team"

!define MUI_FINISHPAGE_RUN "$INSTDIR\SMIS-${VERSION}.exe"

!insertmacro MUI_PAGE_FINISH!endifShowInstDetails show



!insertmacro MUI_UNPAGE_CONFIRMShowUnInstDetails show

!insertmacro MUI_UNPAGE_INSTFILES

VIProductVersion "${VERSION}.0"

; --------------------------------

; LanguagesVIAddVersionKey /LANG=1033 "ProductName" "SMIS - School Management Information System"; VERSION will be injected by GitHub Actions (makensis /DVERSION=1.2.3)

; --------------------------------

!insertmacro MUI_LANGUAGE "English"VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"!ifndef VERSION



; --------------------------------VIAddVersionKey /LANG=1033 "CompanyName" "SMIS Development Team"  !define VERSION "0.0.0"

; Installation Section

; --------------------------------VIAddVersionKey /LANG=1033 "LegalCopyright" "© 2025 SMIS Development Team"!endif

Section "Install"

  SetOutPath "$INSTDIR"VIAddVersionKey /LANG=1033 "FileDescription" "School Management Information System Installer"



  ; Install the main SMIS executableVIProductVersion "${VERSION}.0"

  File "dist\SMIS-${VERSION}.exe"

  ; --------------------------------VIAddVersionKey /LANG=1033 "ProductName" "SMIS - School Management Information System"

  ; Include icon if present

  !if /FileExists "${ICON_PATH}"; Icons (conditional)VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"

    File "${ICON_PATH}"

  !endif; --------------------------------VIAddVersionKey /LANG=1033 "CompanyName" "SMIS Development Team"



  ; Create single desktop shortcut!define ICON_PATH "resources\icons\app_icon.ico"VIAddVersionKey /LANG=1033 "LegalCopyright" "© 2025 SMIS Development Team"

  !if /FileExists "${ICON_PATH}"

    CreateShortcut "$DESKTOP\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico"!if /FileExists "${ICON_PATH}"VIAddVersionKey /LANG=1033 "FileDescription" "School Management Information System Installer"

  !else

    CreateShortcut "$DESKTOP\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe"  Icon "${ICON_PATH}"VIAddVersionKey /LANG=1033 "InternalName" "SMIS-Setup"

  !endif

    UninstallIcon "${ICON_PATH}"VIAddVersionKey /LANG=1033 "OriginalFilename" "SMIS-Setup-${VERSION}.exe"

  ; Create single Start Menu entry (no folder)

  !if /FileExists "${ICON_PATH}"!endifVIAddVersionKey /LANG=1033 "ProductVersion" "${VERSION}"

    CreateShortcut "$SMPROGRAMS\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico"

  !else; --------------------------------

    CreateShortcut "$SMPROGRAMS\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe"

  !endif; --------------------------------; Icons (conditional)



  ; Write uninstaller; Pages; --------------------------------

  WriteUninstaller "$INSTDIR\Uninstall.exe"

; --------------------------------!define ICON_PATH "resources\icons\app_icon.ico"

  ; Add/Remove Programs entry

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayName" "SMIS - School Management Information System"!define MUI_WELCOMEPAGE_TITLE "Welcome to SMIS Setup"!if /FileExists "${ICON_PATH}"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "UninstallString" "$INSTDIR\Uninstall.exe"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "DisplayVersion" "${VERSION}"!define MUI_WELCOMEPAGE_TEXT "This will install SMIS - School Management Information System on your computer."  Icon "${ICON_PATH}"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "Publisher" "SMIS Development Team"

  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "NoModify" 1!insertmacro MUI_PAGE_WELCOME  UninstallIcon "${ICON_PATH}"

  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS" "NoRepair" 1

!insertmacro MUI_PAGE_LICENSE "LICENSE"!else

SectionEnd

!insertmacro MUI_PAGE_DIRECTORY  !warning "Icon not found at ${ICON_PATH}. Using default NSIS icon."

; --------------------------------

; Uninstall Section!insertmacro MUI_PAGE_INSTFILES!endif

; --------------------------------

Section "Uninstall"!define MUI_FINISHPAGE_RUN "$INSTDIR\SMIS-${VERSION}.exe"

  ; Remove executable

  Delete "$INSTDIR\SMIS-${VERSION}.exe"!insertmacro MUI_PAGE_FINISH; --------------------------------

  Delete "$INSTDIR\app_icon.ico"

  Delete "$INSTDIR\Uninstall.exe"; UI Pages

  

  ; Remove shortcuts!insertmacro MUI_UNPAGE_CONFIRM; --------------------------------

  Delete "$DESKTOP\SMIS.lnk"

  Delete "$SMPROGRAMS\SMIS.lnk"!insertmacro MUI_UNPAGE_INSTFILES!insertmacro MUI_PAGE_WELCOME

  

  ; Remove registry entries!if /FileExists "LICENSE"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS"

  ; --------------------------------  !insertmacro MUI_PAGE_LICENSE "LICENSE"

  ; Remove directory

  RMDir "$INSTDIR"; Languages!endif

SectionEnd
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
