# 🤖 Project Jarvis — Windows AI Desktop Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078d4.svg)]()
[![Hardware: RTX 3050A Ready](https://img.shields.io/badge/Hardware-NVIDIA%20RTX%203050A-76b900.svg)]()

> A localized, privacy-first, ultra-responsive Windows AI Desktop Assistant inspired by Iron Man's JARVIS. Features a futuristic Arc Reactor Glass HUD, offline speech recognition, zero-latency intent execution, Google OAuth2 Gmail integration, and local LLM reasoning powered by Ollama.

---

## ✨ Features

- **🎙️ Real-Time Voice Pipeline:** Noise-immune Voice Activity Detection (VAD) + `faster-whisper` (int8 CPU/GPU) + Windows SAPI5 0ms Voice Engine.
- **⚡ Hybrid Brain Routing:** Zero-latency deterministic fast-paths for media, system controls, and email queries with local Ollama fallback (`qwen2.5` / `qwen3.5`).
- **📧 Integrated Gmail Assistant:** Native Google OAuth2 client, unread email scanner (up to 15-25 emails), inbox search, content sanitizer, and background email daemon.
- **💎 Glassmorphism HUD:** Frameless, translucent HUD window with interactive resizing, 1-click expand/contract mode, arc reactor audio visualizer, and system tray minimization.
- **⚙️ Deep Windows OS Control:** Volume, brightness, window controls, application launcher, PowerShell executor, and system health diagnostics.
- **🔒 Privacy-First Architecture:** Runs 100% locally on your machine with optional cloud LLM fallback.

---

## 🚀 Quick Start

### 1. Clone & Setup Repository
```bash
git clone https://github.com/Krishna-1416/Jarvis.git
cd Jarvis
```

### 2. Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Gmail Integration (Optional)
1. Download OAuth2 Client Credentials from Google Cloud Console as `data/credentials/credentials.json`.
2. Run the authentication script:
   ```bash
   python scripts/setup_gmail.py
   ```
*(Refer to [`GMAIL_SETUP.md`](GMAIL_SETUP.md) for step-by-step instructions).*

### 4. Launch Jarvis
```bash
run_jarvis.bat
```
*(Or run `python main.py`)*

- **Summon / Dismiss Hotkey:** `Ctrl + Shift + J`

---

## 📂 Project Structure

```
Jarvis/
├── audio/               # STT (faster-whisper), TTS (SAPI5), VAD audio recorder
├── config/              # settings.yaml, hardware & assistant profiles
├── core/                # Hybrid router, context manager, background email daemon, engine
├── data/                # Credentials (gitignored), vector storage, episodic memory
├── memory/              # SQLite persistent long-term storage & vector index
├── scripts/             # Setup helpers & shortcut generators
├── tools/               # Gmail ops, system ops, browser ops, media controls, tool registry
├── ui/                  # PyQt6 Arc Reactor HUD, tray daemon, global hotkeys
├── main.py              # Application entry point & single-instance IPC
└── run_jarvis.bat       # Portable one-click Windows launcher
```

---

## 🛡️ License
MIT License. Created by [Krishna Jadhav](https://github.com/Krishna-1416).
