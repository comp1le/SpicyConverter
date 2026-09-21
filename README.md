# SpicyConverter 🌶️

**120fps video converter for TikTok & YouTube gaming montages.**

Clean interpolation, maximum quality, professional motion blur. Free & open-source.

![Version](https://img.shields.io/badge/version-1.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12+-yellow)

---

## Features

- **120fps Interpolation** — smooth frame blending for ultra-fluid playback
- **Dual Mode** — TikTok (clean) & YouTube (enhanced with motion blur + sharpening)
- **Queue System** — process multiple videos sequentially
- **Cancel Anytime** — stop processing mid-queue
- **No Ghosting** — blend interpolation avoids motion estimation artifacts
- **Single .exe** — no Python or ffmpeg needed on target machine
- **Modern UI** — dark theme, real-time progress, queue management

---

## Download

Download `SpicyConverter_Setup.exe` from [Releases](../../releases).

Or use the portable `SpicyConverter.exe` directly — no installation required.

---

## Usage

### Quick Start

1. **Launch** SpicyConverter
2. **Select Mode** — TikTok (clean) or YouTube (motion blur)
3. **Browse** — select one or more video files
4. **Start Processing** — click the green button
5. **Upload** — output files appear in the same folder as input

### TikTok Mode
Clean 120fps interpolation — no effects, pure smoothness.

### YouTube Mode
Enhanced pipeline for gaming montages:
- 120fps interpolation
- Subtle motion blur (18% opacity)
- Adaptive sharpening (CAS 0.8)
- CRF 8 encoding for maximum quality

---

## Queue System

- **Add multiple videos** — click "Browse" or "+ Add Video"
- **Status indicators:**
  - ⏳ Pending — waiting to process
  - ⚡ Processing — currently converting
  - ✅ Done — successfully completed
  - ❌ Failed — error occurred
- **Remove videos** — click ✕ on pending items
- **Clear all** — reset the queue

---

## Encoding Settings

| Setting | TikTok | YouTube |
|---------|--------|---------|
| FPS | 120 | 120 |
| Interpolation | Blend | Blend |
| Motion Blur | — | tblend 18% |
| Sharpening | — | CAS 0.8 |
| Encoder | libx264 | libx264 |
| Preset | veryslow | veryslow |
| CRF | 10 | 8 |
| Bitrate | 100 Mbps | 120 Mbps |
| Max Rate | 120 Mbps | 150 Mbps |
| Pixel Format | yuv420p | yuv420p |
| Color Space | BT.709 | BT.709 |
| Audio | AAC 320k | AAC 384k |

---

## Upload Tips

### TikTok
1. Use **tiktok.com** in your browser (NOT the mobile app)
2. Enable **"Allow high-quality uploads"** in settings
3. Upload the `*_120fps.mp4` file

### YouTube
1. Use **youtube.com** or YouTube Studio
2. Enable **4K upload** in channel settings
3. Select the highest quality option when uploading

---

## Building from Source

### Prerequisites
- Python 3.12+
- Inno Setup 6 (for installer)

### Build Steps

```bash
# Install dependencies
pip install pyinstaller customtkinter

# Build .exe (downloads ffmpeg automatically)
python build.py

# Build installer
& "C:\path\to\ISCC.exe" installer.iss
```

### Project Structure

```
SpicyConverter/
├── tiktok_app.pyw      # Main application
├── build.py            # PyInstaller build script
├── installer.iss       # Inno Setup installer script
├── chili.ico           # App icon
├── wizard_background.bmp  # Installer background
├── wizard_logo.bmp     # Installer logo
├── LICENSE             # MIT License
├── README.md           # This file
└── ffmpeg_bin/         # ffmpeg binaries (downloaded during build)
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| UI Framework | customtkinter |
| Video Processing | ffmpeg |
| Packaging | PyInstaller |
| Installer | Inno Setup 6 |

---

## Supported Formats

**Input:** MP4, MOV, AVI, MKV, WEBM

**Output:** MP4 (H.264 + AAC)

---

## How It Works

### Interpolation
SpicyConverter uses ffmpeg's `minterpolate` filter with blend mode to generate smooth intermediate frames without motion estimation artifacts (no ghosting).

### YouTube Enhancement
The YouTube pipeline adds professional post-processing:
1. **Motion Blur** — `tblend` filter blends consecutive frames for cinematic smoothness
2. **Sharpening** — `cas` (Contrast Adaptive Sharpening) restores detail lost during interpolation

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Credits

**Djani** — Developer

Built for gaming montage creators who demand the smoothest possible footage.

---

<p align="center">
  <i>Made with 🌶️ for the gaming community</i>
</p>
