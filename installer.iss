; ═══════════════════════════════════════════════════════
;  SpicyConverter — Inno Setup Installer
;  by Djani
; ═══════════════════════════════════════════════════════

#define MyAppName "SpicyConverter"
#define MyAppVersion "1.1"
#define MyAppPublisher "SpicyConverter"
#define MyAppExeName "SpicyConverter.exe"

[Setup]
; Grundlegende App-Info
AppId={{B8F7E3A1-4D2C-4E5F-9A6B-1C8D3E7F2A4B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Installer Aussehen
OutputDir=installer_output
OutputBaseFilename=SpicyConverter_Setup
SetupIconFile=chili.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=110

; Farben (dunkles Theme)
WizardImageFile=wizard_background.bmp
WizardSmallImageFile=wizard_logo.bmp
; BackColor=0d0d0d
; BackColor2=1a1a2e

; Sprache
LanguageDetectionMethod=uiLanguage
ShowLanguageDialog=yes

; Rechte
PrivilegesRequired=lowest

; Sonstiges
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
CloseApplications=force
RestartApplications=no

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Icons:"; Flags: checkedonce
Name: "startmenu"; Description: "Startmenü-Eintrag erstellen"; GroupDescription: "Zusätzliche Icons:"; Flags: checkedonce
Name: "cleaninstall"; Description: "Alte Installation bereinigen (empfohlen bei Update)"; GroupDescription: "Installation:"; Flags: unchecked

[Files]
; Die gebaute .exe aus dem dist Ordner
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Falls ffmpeg nicht in der .exe gebündelt ist — separat mitliefern
; Source: "ffmpeg_bin\*"; DestDir: "{app}\ffmpeg_bin"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Startmenü
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} deinstallieren"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[UninstallDelete]
; Dateien im Installationsordner loeschen
Type: files; Name: "{app}\*.*"

[Run]
; App nach Installation starten
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} starten"; Flags: nowait postinstall skipifsilent

[Manifest]
ExecutionLevel=admin
Compatibility=nogui
UACRestart=standard

[Code]
// ═══════════════════════════════════════════════════════
//  Custom Wizard Pages — Dunkles Design
// ═══════════════════════════════════════════════════════

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DelTree(ExpandConstant('{app}'), True, True, True);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Falls "cleaninstall" ausgewaehlt, alte Dateien loeschen
    if WizardIsTaskSelected('cleaninstall') then
    begin
      // Alte Config-Dateien loeschen (falls vorhanden)
      DeleteFile(ExpandConstant('{app}\config.ini'));
      DeleteFile(ExpandConstant('{app}\settings.ini'));
      // Alte Log-Dateien loeschen
      DelTree(ExpandConstant('{app}\*.log'), False, True, False);
    end;
  end;
end;

// ═══════════════════════════════════════════════════════
//  Willkommensseite anpassen
// ═══════════════════════════════════════════════════════

procedure InitializeWizard;
begin
  // Installer Titel
  WizardForm.Caption := 'SpicyConverter Installation';
  
  // Willkommens-Text
  WizardForm.WelcomeLabel1.Caption := 'SpicyConverter Installation';
  WizardForm.WelcomeLabel2.Caption := 
    'Dieser Installer richtet SpicyConverter auf deinem Computer ein.' + #13#10#13#10 +
    '120fps Ultra Smooth fuer TikTok & YouTube — maximale Qualitaet.' + #13#10#13#10 +
    'Klicke auf Weiter um fortzufahren.';
end;

// ═══════════════════════════════════════════════════════
//  Abschlussseite anpassen
// ═══════════════════════════════════════════════════════

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    WizardForm.FinishedLabel.Caption := 
      'Installation abgeschlossen!' + #13#10#13#10 +
      'SpicyConverter wurde erfolgreich installiert.' + #13#10#13#10 +
      'Klicke auf "Fertig stellen" um den Installer zu schliessen.';
  end;
end;
