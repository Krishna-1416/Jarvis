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
- **🔒 Privacy-First Architecture:** Runs 100% locally on your machine with zero external cloud dependencies.

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
*(See [`docs/setup/INSTALL.md`](docs/setup/INSTALL.md) for detailed installation instructions).*

### 3. Setup Gmail Integration (Optional)
1. Download OAuth2 Client Credentials from Google Cloud Console as `data/credentials/credentials.json`.
2. Run the authentication script:
   ```bash
   python scripts/setup_gmail.py
   ```
*(Refer to [`docs/setup/GMAIL_SETUP.md`](docs/setup/GMAIL_SETUP.md) for step-by-step instructions).*

### 4. Launch Jarvis
```bash
run_jarvis.bat
```
*(Or run `python main.py`)*

- **Summon / Dismiss Hotkey:** `Ctrl + Shift + J`

---

## 📂 Project Architecture

```
Jarvis/
├── docs/                                # 📚 Centralized Technical Documentation
│   ├── architecture/                    # System design, async pipelines & event loops
│   │   └── architecture.md              # Core engine architecture & pipeline specifications
│   └── setup/                           # Step-by-step setup and integration guides
│       ├── INSTALL.md                   # Environment setup & dependency installation
│       └── GMAIL_SETUP.md               # Google OAuth2 Cloud Console walkthrough
│
├── config/                              # ⚙️ Application Configuration
│   ├── settings.yaml                    # Main assistant, LLM, voice, and system parameters
│   └── tools_config.yaml                # Tool registry permissions and quotas
│
├── audio/                               # 🎙️ Audio Processing Layer
│   ├── recorder.py                      # VAD-based mic stream & energy thresholding
│   ├── sound_effects.py                 # Cyberpunk futuristic audio chimes
│   ├── stt.py                           # Faster-Whisper offline transcription
│   └── tts.py                           # Windows Native SAPI5 engine (0ms latency)
│
├── core/                                # 🧠 Core Brain, Routing & Engine Logic
│   ├── config.py                        # YAML runtime configuration loader
│   ├── context_manager.py               # Dynamic system prompt & sliding memory window
│   ├── email_daemon.py                  # Background Gmail polling worker & briefings
│   ├── engine.py                        # Central Jarvis lifecycle orchestrator
│   └── router.py                        # Deterministic 0ms fast-path & Ollama LLM router
│
├── tools/                               # 🛠️ Modular Extensible Tools
│   ├── registry.py                      # Decorator-driven tool registry (@tool)
│   ├── browser_ops.py                   # Media playback, YouTube, Spotify, website actions
│   ├── file_ops.py                      # Local filesystem search, read, write
│   ├── gmail_ops.py                     # Authenticated Google OAuth2 email actions
│   ├── media_control.py                 # Windows media keys (play/pause/skip)
│   ├── powershell_runner.py             # Safe sandboxed command executor
│   ├── rag_researcher.py                # Deep web scraping & summarization
│   ├── system_ops.py                    # Volume, brightness, window state, app discovery
│   ├── web_search.py                    # Web scraping & search
│   └── window_ops.py                    # Window minimize/close/switch
│
├── memory/                              # 💾 Storage & Long-Term Memory
│   ├── db.py                            # SQLite persistent conversation memory
│   ├── memory_manager.py                # Fact extraction & retrieval manager
│   └── vector_store.py                  # Semantic embeddings & local vector index
│
├── ui/                                  # 💎 User Interface (PyQt6)
│   ├── app.py                           # PyQt6 Application & Single-Instance IPC Server
│   ├── audio_visualizer.py              # Arc Reactor QPainter visualizer
│   ├── hotkey_listener.py               # Global keyboard hooks (Ctrl+Shift+J)
│   ├── hud_window.py                    # Translucent glassmorphism HUD with resize grips
│   └── tray.py                          # Windows System Tray daemon & menu
│
├── data/                                # 📁 Runtime Data (Safe & Ignored)
│   ├── credentials/                     # OAuth client_secret & tokens (Gitignored)
│   │   └── credentials.json.example     # Safe sample template
│   ├── memory/                          # SQLite DB files
│   └── vectors/                         # Vector cache
│
├── models/                              # 📦 Local Weights & ONNX Models
│   ├── vad/                             # Silero VAD weights
│   └── tts/                             # SAPI5 & Kokoro fallback weights
│
├── scripts/                             # 🔧 Developer & Setup Automation Scripts
│   ├── create_shortcut.py               # Windows desktop .lnk shortcut creator
│   ├── download_models.py               # Automated model asset downloader
│   └── setup_gmail.py                   # Interactive OAuth2 login setup
│
├── tests/                               # 🧪 Automated Test Suite
│   ├── test_app_discovery.py
│   ├── test_audio_input.py
│   ├── test_gmail_ops.py
│   ├── test_router_intelligence.py
│   └── test_universal_apps.py
│
├── .env.example                         # Environment variables template
├── .gitignore                           # Strict gitignore for secrets and bytecode
├── LICENSE                              # MIT Open Source License
├── pyproject.toml                       # PEP 518/621 Modern Python Project Metadata
├── README.md                            # Comprehensive repository landing page
├── requirements.txt                     # Production pip dependencies
├── main.py                              # Clean top-level entrypoint
└── run_jarvis.bat                       # Portable one-click Windows launcher
```

---

## 🛡️ License
MIT License. Copyright (c) 2026 [Krishna Jadhav](https://github.com/Krishna-1416).
