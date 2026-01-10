; SNE Radar - Inno Setup Installer Script
; Para usar: Instale Inno Setup (https://jrsoftware.org/isinfo.php) e compile este script

#define MyAppName "SNE Radar"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SNE Labs"
#define MyAppURL "https://radar.snelabs.space"
#define MyAppExeName "SNE_Radar.exe"

[Setup]
; Identificador único do app (gere um novo GUID em https://www.guidgenerator.com/)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Arquivo de saída do instalador
OutputDir=installer_output
OutputBaseFilename=SNE_Radar_Setup_{#MyAppVersion}
; Ícone do instalador
SetupIconFile=frontend\build\icon.ico
; Compressão
Compression=lzma2/ultra64
SolidCompression=yes
; Estilo moderno
WizardStyle=modern
; Privilégios (user = não precisa de admin para instalar)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Arquitetura
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Executável principal e toda a pasta _internal
Source: "dist\SNE_Radar\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SNE_Radar\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTA: Não use "Flags: ignoreversion" em arquivos DLL do sistema

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Limpar dados do app ao desinstalar (opcional)
Type: filesandordirs; Name: "{userappdata}\SNE_RADAR"
