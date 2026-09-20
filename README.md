# SpicyConverter

120fps video converter for TikTok. Clean interpolation, maximum quality, no filters.

## Features

- **120fps Frame Interpolation** — motion-compensated (AOBMC + vsbmc) for smooth playback
- **Maximum Quality** — CRF 10, 100Mbps, libx264 veryslow
- **Clean Pipeline** — no denoise, no sharpen. Pure interpolation + encoding
- **Single .exe** — no Python or ffmpeg needed on the target machine
- **Modern UI** — dark theme, Bahnschrift font, real-time progress

## Download

Download `SpicyConverter_Setup.exe` from [Releases](../../releases).

## License

SpicyConverter requires a license key to activate. Your Hardware ID is displayed automatically when you start the app — contact me to get your license key.

## Usage

1. Run `SpicyConverter.exe` or install via `SpicyConverter_Setup.exe`
2. Click **Browse Video** and select your file (MP4, MOV, AVI, MKV, WEBM)
3. Click **START PROCESSING**
4. Wait for the 120fps conversion to complete
5. Upload the output file to TikTok via **tiktok.com** (not the mobile app!)

## TikTok Upload Tips

1. Use **tiktok.com** in your browser, NOT the mobile app
2. Enable **"Allow high-quality uploads"** in settings
3. The output file (`*_120fps.mp4`) will be in the same folder as your input

## Building from Source

```bash
# Install dependencies
pip install pyinstaller customtkinter

# Build .exe (downloads ffmpeg automatically)
python build.py

# Build installer (requires Inno Setup 6)
# Open installer.iss in Inno Setup and compile
```

## Tech Stack

- **Python 3.12** — application logic
- **customtkinter** — modern dark UI
- **ffmpeg** — frame interpolation and encoding
- **PyInstaller** — single .exe packaging
- **Inno Setup** — installer creation

## Encoding Settings

| Setting | Value |
|---------|-------|
| FPS | 120 |
| Encoder | libx264 |
| Preset | veryslow |
| CRF | 10 |
| Bitrate | 100Mbps VBR |
| Max | 120Mbps |
| Pixel Format | yuv420p |
| Color | BT.709 |
| Audio | AAC 320kbps 48kHz |

## License

MIT
