; ================================================
; SMIS Installer Script (NSIS)
; Generated and maintained via build workflow
; ================================================

; NOTE:
; If building in GitHub Actions and NSIS is missing, the workflow step will
; download and silently install NSIS automatically (see build-and-release.yml).
; Ensure PyInstaller produced dist/SMIS-<version>.exe before invoking makensis.
; Icon and LICENSE inclusion are conditional.

!include "MUI2.nsh"

; --------------------------------
; Metadata
; --------------------------------
Name "SMIS - School Management Information System"
OutFile "SMIS-Setup-${VERSION}.exe"
InstallDir "$PROGRAMFILES\SMIS"
RequestExecutionLevel admin

; Installation attributes to help with Windows security
SetCompressor /SOLID lzma
SetCompressorDictSize 32
SetDatablockOptimize on
CRCCheck on
XPStyle on
BrandingText "SMIS Development Team"
ShowInstDetails show
ShowUnInstDetails show

; VERSION will be injected by GitHub Actions (makensis /DVERSION=1.2.3)
!ifndef VERSION
  !define VERSION "0.0.0"
!endif

VIProductVersion "${VERSION}.0"
VIAddVersionKey /LANG=1033 "ProductName" "SMIS - School Management Information System"
VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"
VIAddVersionKey /LANG=1033 "CompanyName" "SMIS Development Team"
VIAddVersionKey /LANG=1033 "LegalCopyright" "© 2025 SMIS Development Team"
VIAddVersionKey /LANG=1033 "FileDescription" "School Management Information System Installer"
VIAddVersionKey /LANG=1033 "InternalName" "SMIS-Setup"
VIAddVersionKey /LANG=1033 "OriginalFilename" "SMIS-Setup-${VERSION}.exe"
VIAddVersionKey /LANG=1033 "ProductVersion" "${VERSION}"
; --------------------------------
; Icons (conditional)
; --------------------------------
!define ICON_PATH "resources\icons\app_icon.ico"
!if /FileExists "${ICON_PATH}"
  Icon "${ICON_PATH}"
  UninstallIcon "${ICON_PATH}"
!else
  !warning "Icon not found at ${ICON_PATH}. Using default NSIS icon."
!endif

; --------------------------------
; UI Pages
; --------------------------------
!insertmacro MUI_PAGE_WELCOME
!if /FileExists "LICENSE"
  !insertmacro MUI_PAGE_LICENSE "LICENSE"
!endif
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

; --------------------------------
; Definitions
; --------------------------------
Var StartMenuFolder

; --------------------------------
; Install Section
; --------------------------------
Section "Install"
  SetOutPath "$INSTDIR"

  ; Main application executable built by PyInstaller
  File "dist\\SMIS-${VERSION}.exe"
  
  ; Include portable version as alternative
  !if /FileExists "dist\\SMIS-${VERSION}-Portable.exe"
    File "dist\\SMIS-${VERSION}-Portable.exe"
  !endif
  
  ; Include compatibility info
  !if /FileExists "dist\\SMIS-${VERSION}-info.txt"
    File "dist\\SMIS-${VERSION}-info.txt"
  !endif

  ; Include icon in install directory if present
  !if /FileExists "${ICON_PATH}"
    File "${ICON_PATH}"
  !endif

  ; Create Start Menu folder
  CreateDirectory "$SMPROGRAMS\SMIS"

  ; Shortcuts - Main version
  CreateShortcut "$DESKTOP\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico"
  CreateShortcut "$SMPROGRAMS\SMIS\SMIS.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico"
  
  ; Additional shortcut for portable version if exists
  !if /FileExists "dist\\SMIS-${VERSION}-Portable.exe"
    CreateShortcut "$SMPROGRAMS\SMIS\SMIS (Portable).lnk" "$INSTDIR\SMIS-${VERSION}-Portable.exe" "" "$INSTDIR\app_icon.ico"
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
  Delete "$INSTDIR\SMIS-${VERSION}.exe"
  Delete "$INSTDIR\SMIS-${VERSION}-Portable.exe"
  Delete "$INSTDIR\SMIS-${VERSION}-info.txt"
  Delete "$INSTDIR\app_icon.ico"
  Delete "$DESKTOP\SMIS.lnk"
  Delete "$SMPROGRAMS\SMIS\SMIS.lnk"
  Delete "$SMPROGRAMS\SMIS\SMIS (Portable).lnk"
  RMDir  "$SMPROGRAMS\SMIS"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SMIS"
  RMDir /r "$INSTDIR"
SectionEnd
