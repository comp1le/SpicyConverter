; ═══════════════════════════════════════════════════════
;  TikTok 60fps — Inno Setup Installer
;  by Weat
; ═══════════════════════════════════════════════════════

#define MyAppName "SpicyConverter"
#define MyAppVersion "1.0"
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

[Run]
; App nach Installation starten
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} starten"; Flags: nowait postinstall skipifsilent

[Code]
// ═══════════════════════════════════════════════════════
//  Custom Wizard Pages — Dunkles Design
// ═══════════════════════════════════════════════════════

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Nach Installation: App optional starten
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
    '120fps Ultra Smooth fuer TikTok — maximale Qualitaet.' + #13#10#13#10 +
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
      'So benutzt du es:' + #13#10 +
      '  1. App ueber Desktop-Verknuepfung oder Startmenu oeffnen' + #13#10 +
      '  2. Video per Drag & Drop oder Klick auswaehlen' + #13#10 +
      '  3. "START PROCESSING" klicken' + #13#10 +
      '  4. Ergebnis auf tiktok.com hochladen' + #13#10#13#10 +
      'WICHTIG: Immer ueber tiktok.com uploaden, NICHT die Mobile-App!';
  end;
end;
