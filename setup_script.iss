[Setup]
AppName=School Management Information System
AppVersion=2.3.4
AppPublisher=SMIS Development Team
AppPublisherURL=https://github.com/ZubairHussainK/smis
DefaultDirName={pf}\SMIS
DefaultGroupName=SMIS
OutputDir=installer
OutputBaseFilename=SMIS_Setup_v2.3.4
Compression=lzma2
SolidCompression=yes
SetupIconFile=resources\icons\app_icon.ico
UninstallDisplayIcon={app}\SMIS.exe
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\SMIS.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SMIS"; Filename: "{app}\SMIS.exe"
Name: "{commondesktop}\SMIS"; Filename: "{app}\SMIS.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SMIS.exe"; Description: "{cm:LaunchProgram,SMIS}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKLM; Subkey: "Software\SMIS"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey

[Code]
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption := 'This will install School Management Information System (SMIS) v2.3.4 on your computer.' + #13#13 +
    'SMIS is a comprehensive school management solution that helps manage student records, attendance, and generate reports.' + #13#13 +
    'Click Next to continue, or Cancel to exit Setup.';
end;

function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath: String;
  SMISDataPath: String;
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Get AppData path
    AppDataPath := ExpandConstant('{userappdata}');
    SMISDataPath := AppDataPath + '\SMIS';
    
    // Ask user if they want to remove user data
    if MsgBox('Do you want to remove all user data including database, settings, and license information?' + #13#13 +
              'This will permanently delete all student records, attendance data, and settings.' + #13#13 +
              'Choose "No" if you plan to reinstall SMIS and want to keep your data.',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Remove entire SMIS AppData directory
      if DirExists(SMISDataPath) then
      begin
        if Exec('cmd.exe', '/c rmdir /s /q "' + SMISDataPath + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
        begin
          MsgBox('All user data has been successfully removed.', mbInformation, MB_OK);
        end else
        begin
          MsgBox('Some user data could not be removed automatically. You may need to manually delete the folder:' + #13#13 + SMISDataPath, mbInformation, MB_OK);
        end;
      end;
    end else
    begin
      MsgBox('User data has been preserved. You can find it at:' + #13#13 + SMISDataPath, mbInformation, MB_OK);
    end;
  end;
end;