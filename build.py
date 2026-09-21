"""
Build Script - SpicyConverter als single .exe
Packt alles zusammen: App + ffmpeg + alle Dependencies

Nutzung:
  1. Python + muessen beim BUILD da sein
  2. python build.py
  3. Fertige .exe liegt in dist/
"""

import subprocess
import sys
import os
import shutil
import zipfile
import urllib.request
from pathlib import Path

# CONFIG
APP_NAME    = "SpicyConverter"
APP_VERSION = "1.1"
MAIN_SCRIPT = "tiktok_app.pyw"
ICON_FILE   = "chili.ico"

FFMPEG_URL  = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_DIR  = "ffmpeg_bin"

def cleanup():
    """Vor dem Build: alte Temp-Ordner loeschen um 'Failed to remove' Fehler zu vermeiden"""
    print("[CLEAN] Raeume alte Build-Dateien auf...")
    for d in ["build", "dist"]:
        p = Path(d)
        if p.exists():
            try:
                shutil.rmtree(str(p))
                print("  [OK] " + d + "/ geloescht")
            except Exception as e:
                print("  [!!] " + d + "/ konnte nicht geloescht werden: " + str(e))
                print("  -> Schliesse alle laufenden Prozesse und versuche erneut")
                # Versuche es erneut mit-ignore-errors
                try:
                    shutil.rmtree(str(p), ignore_errors=True)
                    print("  [OK] " + d + "/ teilweise geloescht")
                except:
                    pass
    spec = Path(APP_NAME + ".spec")
    if spec.exists():
        try:
            spec.unlink()
        except:
            pass
    print()

def install_build_deps():
    print("\n[1/4] Installiere Build-Dependencies...")
    deps = ["pyinstaller", "tkinterdnd2"]
    for dep in deps:
        print("  -> " + dep + "...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", dep, "--quiet"],
            capture_output=True
        )
    print("  [OK] Fertig\n")

def download_ffmpeg():
    print("[2/4] Lade ffmpeg herunter...")

    ffmpeg_exe = Path(FFMPEG_DIR) / "ffmpeg.exe"
    if ffmpeg_exe.exists():
        print("  [OK] ffmpeg bereits vorhanden\n")
        return

    os.makedirs(FFMPEG_DIR, exist_ok=True)

    print("  -> Download von " + FFMPEG_URL)
    print("  -> Das kann einen Moment dauern...")

    zip_path = Path(FFMPEG_DIR) / "ffmpeg.zip"

    try:
        urllib.request.urlretrieve(FFMPEG_URL, str(zip_path))

        print("  -> Entpacke ffmpeg...")
        with zipfile.ZipFile(str(zip_path), 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith("ffmpeg.exe") or member.endswith("ffprobe.exe"):
                    filename = os.path.basename(member)
                    data = zip_ref.read(member)
                    with open(Path(FFMPEG_DIR) / filename, 'wb') as f:
                        f.write(data)

        zip_path.unlink()

        if (Path(FFMPEG_DIR) / "ffmpeg.exe").exists():
            print("  [OK] ffmpeg heruntergeladen und installiert\n")
        else:
            print("  [!] ffmpeg.exe nicht im ZIP gefunden")
            print("  -> Lade manuell herunter: https://ffmpeg.org/download.html")
            print("  -> Kopiere ffmpeg.exe in den ffmpeg_bin Ordner")
            print("  -> Starte build.py erneut\n")
            sys.exit(1)

    except Exception as e:
        print("  [!] Download fehlgeschlagen: " + str(e))
        print("  -> Lade manuell herunter: " + FFMPEG_URL)
        print("  -> Kopiere ffmpeg.exe in: " + FFMPEG_DIR + "/")
        print("  -> Starte build.py erneut\n")
        sys.exit(1)

def build_exe():
    print("[3/4] Baue .exe mit PyInstaller...")
    print("  [!!] FFmpeg Dateien werden gebuendelt...")

    icon_arg = []
    if ICON_FILE and os.path.exists(ICON_FILE):
        icon_arg = ["--icon", ICON_FILE]

    # UPX ausschliessen fuer ffmpeg (ist bereits komprimiert, UPX kann kaputt machen)
    upx_exclude = [
        "--upx-exclude", "ffmpeg.exe",
        "--upx-exclude", "ffprobe.exe",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--clean",
        "--add-data", FFMPEG_DIR + os.pathsep + "ffmpeg_bin",
        "--add-data", "fonts" + os.pathsep + "fonts",
        "--add-data", "chili.ico" + os.pathsep + ".",
        "--hidden-import", "tkinterdnd2",
    ] + icon_arg + upx_exclude + [MAIN_SCRIPT]

    print("  -> " + " ".join(cmd) + "\n")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("\n  [!] Build fehlgeschlagen!")
        sys.exit(1)

    # Pruefen ob ffmpeg im .exe ist
    exe_path = Path("dist") / (APP_NAME + ".exe")
    exe_size = exe_path.stat().st_size if exe_path.exists() else 0
    ffmpeg_size = sum(f.stat().st_size for f in Path(FFMPEG_DIR).iterdir() if f.suffix == ".exe")

    print("  [INFO] .exe Groesse: " + str(round(exe_size / 1024 / 1024, 1)) + " MB")
    print("  [INFO] FFmpeg Dateien: " + str(round(ffmpeg_size / 1024 / 1024, 1)) + " MB")

    if exe_size < ffmpeg_size:
        print("  [!] WARNUNG: .exe ist kleiner als FFmpeg! FFmpeg ist MOEGLICHERWEISE nicht gebuendelt!")
        print("  -> Versuche Build mit --noconfirm...")
    else:
        print("  [OK] FFmpeg scheint gebuendelt zu sein\n")

def finalize():
    print("[4/4] Aueraeumen...")

    spec_file = Path(APP_NAME + ".spec")
    if spec_file.exists():
        try:
            spec_file.unlink()
        except:
            pass

    build_dir = Path("build")
    if build_dir.exists():
        try:
            shutil.rmtree(str(build_dir))
        except Exception as e:
            print("  [!!] build/ konnte nicht komplett geloescht werden: " + str(e))
            print("  -> Das ist harmlos, die .exe ist trotzdem fertig!")
            try:
                shutil.rmtree(str(build_dir), ignore_errors=True)
            except:
                pass

    exe_path = Path("dist") / (APP_NAME + ".exe")

    print()
    print("=" * 50)
    print("  [OK] BUILD FERTIG!")
    print("  -> " + str(exe_path))
    size_mb = os.path.getsize(str(exe_path)) / (1024 * 1024)
    print("  -> " + str(round(size_mb, 1)) + " MB")
    print("=" * 50)
    print()
    print("  Die .exe kann jetzt ueberall hin kopiert werden.")
    print("  Kein Python, kein ffmpeg noetig auf dem Ziel-PC.")
    print()

if __name__ == "__main__":
    print()
    print("=" * 50)
    print("  " + APP_NAME + " - Build Script")
    print("  by Djani")
    print("=" * 50)

    cleanup()
    install_build_deps()
    download_ffmpeg()
    build_exe()
    finalize()
