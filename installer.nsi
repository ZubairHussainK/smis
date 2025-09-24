; ----------------------------
; SMIS Installer Script (NSIS)
; ----------------------------

; === Define App Info ===
!define APPNAME "SMIS"
!ifndef VERSION
  !define VERSION "2.1.0"
!endif
!define COMPANY "SMIS Development Team"

; === Basic Config ===
Name "${APPNAME} v${VERSION}"
OutFile "${APPNAME}-Setup-${VERSION}.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
InstallDirRegKey HKCU "Software\${COMPANY}\${APPNAME}" "Install_Dir"

; === Icons ===
Icon "resources\icons\app_icon.ico"
UninstallIcon "resources\icons\app_icon.ico"

; === UI (Modern Interface) ===
!include "MUI2.nsh"

!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

; ----------------------------
; Installer Section
; ----------------------------
Section "Install"

  SetOutPath "$INSTDIR"
  ; Copy main executable with version in name
  File "dist\SMIS-${VERSION}.exe"
  
  ; Copy icon if exists
  IfFileExists "resources\icons\app_icon.ico" 0 +2
  File "resources\icons\app_icon.ico"

  ; Save installation path
  WriteRegStr HKCU "Software\${COMPANY}\${APPNAME}" "Install_Dir" "$INSTDIR"

  ; Add Uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Desktop Shortcut
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico" 0

  ; Start Menu Shortcuts (single shortcut, no folder)
  CreateShortcut "$SMPROGRAMS\${APPNAME}.lnk" "$INSTDIR\SMIS-${VERSION}.exe" "" "$INSTDIR\app_icon.ico" 0

SectionEnd

; ----------------------------
; Uninstaller Section
; ----------------------------
Section "Uninstall"

  ; Delete files
  Delete "$INSTDIR\SMIS-${VERSION}.exe"
  Delete "$INSTDIR\app_icon.ico"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"

  ; Delete registry key
  DeleteRegKey HKCU "Software\${COMPANY}\${APPNAME}"

  ; Delete shortcuts
  Delete "$DESKTOP\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}.lnk"

SectionEnd
