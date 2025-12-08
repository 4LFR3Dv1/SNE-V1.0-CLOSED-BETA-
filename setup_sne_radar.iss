; Script de Instalação Inno Setup para SNE RADAR
; Gera um instalador profissional .exe
; Requer: Inno Setup (gratuito) - https://jrsoftware.org/isinfo.php

#define MyAppName "SNE RADAR"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SNE Trading Systems"
#define MyAppURL "https://github.com/seu-repo"
#define MyAppExeName "SNE_RADAR.exe"
#define MyAppId "{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"

[Setup]
; Informações básicas
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=installer
OutputBaseFilename=SNE_RADAR_Setup
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Aparência
WizardImageFile=
WizardSmallImageFile=
WizardImageStretch=no

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Executável principal
Source: "dist\SNE_RADAR.exe"; DestDir: "{app}"; Flags: ignoreversion
; Frontend buildado (se necessário incluir separadamente)
Source: "dist\frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: DirExistsCheck('{src}\dist\frontend')
; Arquivos de configuração (se houver)
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: DirExistsCheck('{src}\config')
; Documentação (opcional - só inclui se existir)
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme; Check: FileExistsCheck('{src}\README.md')
Source: "COMO_BUILDAR_WINDOWS.md"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExistsCheck('{src}\COMO_BUILDAR_WINDOWS.md')

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Verificar se já existe instalação
  if RegKeyExists(HKEY_LOCAL_MACHINE, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1') then
  begin
    if MsgBox('SNE RADAR já está instalado. Deseja desinstalar a versão anterior?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Executar desinstalador
      Exec(ExpandConstant('{uninstallexe}'), '', '', SW_SHOWNORMAL, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;

function DirExistsCheck(DirName: String): Boolean;
begin
  Result := DirExists(ExpandConstant(DirName));
end;

function FileExistsCheck(FileName: String): Boolean;
var
  FullPath: String;
begin
  FullPath := ExpandConstant(FileName);
  Result := FileExists(FullPath);
end;

