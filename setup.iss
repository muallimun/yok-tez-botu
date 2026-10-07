; YÖK Tez Botu Premium v3.6 - Inno Setup Script
; Yayıncı: muallimun.net

#define MyAppName "YÖK Tez Botu Premium"
#define MyAppVersion "3.6"
#define MyAppPublisher "muallimun.net"
#define MyAppExeName "YOK_Tez_Premium.exe"

[Setup]
; Bu AppId benzersizdir. Gelecekte programa güncelleme yaparsanız (v4.0 gibi), 
; aynı id'yi kullandığınız için eski sürümün üzerine sorunsuz kurulur.
AppId={{D8A1C3B2-7901-4F4E-9B2F-9C8A1B2C3D4E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
LicenseFile=E:\python_denemeleri\yok_tez_bot\Lisans_Sozlesmesi.txt

; Programın Kullanıcıda Kurulacağı Klasör: C:\Program Files (x86)\muallimun.net\YÖK Tez Botu Premium
DefaultDirName={autopf}\{#MyAppPublisher}\{#MyAppName}
DefaultGroupName={#MyAppPublisher}
AllowNoIcons=yes

; Oluşacak Setup.exe dosyasının SİZİN bilgisayarınızda kaydedileceği yer ve adı
OutputDir=E:\python_denemeleri\yok_tez_bot
OutputBaseFilename=YOK_Tez_Bot_Premium_Setup_v3.6

; Setup'ın kendi ikonu
SetupIconFile=E:\python_denemeleri\yok_tez_bot\icon.ico

; Premium LZMA2 Ultra64 Sıkıştırma (Dosya boyutunu ciddi oranda küçültür)
Compression=lzma2/ultra64
SolidCompression=yes

; Modern Kurulum Arayüzü
WizardStyle=modern
UninstallDisplayIcon={app}\icon.ico


[Languages]
; Kurulum Sihirbazı Dili (Tamamen Türkçe)
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
; Masaüstü Kısayolu (Varsayılan olarak işaretli gelir)
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; EXE dosyamız
Source: "E:\python_denemeleri\yok_tez_bot\YOK_Tez_Premium\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Program İkonumuz
Source: "E:\python_denemeleri\yok_tez_bot\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; _internal klasörü ve içindeki tüm kütüphaneler (Alt klasörleri de kapsar)
Source: "E:\python_denemeleri\yok_tez_bot\YOK_Tez_Premium\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Not: Üstteki satır hedef klasördeki tüm gizli/açık dosyaları otomatik olarak paketler.
; Program Logomuz
Source: "E:\python_denemeleri\yok_tez_bot\logo.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Başlat Menüsü Kısayolu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
; Başlat Menüsü Kaldır (Uninstall) Kısayolu
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Masaüstü Kısayolu
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
; Kurulum Bittiğinde Programı Çalıştırma Seçeneği
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent