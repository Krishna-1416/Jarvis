# 🛠️ Implementation Plan: Custom Local Jarvis AI Assistant

Build an always-on, voice-and-text personal AI assistant on Windows with sub-second response times, deep OS automation, persistent memory, and hybrid local/cloud intelligence—engineered to stay well within the **4GB VRAM constraint of the RTX 3050A**.

---

## User Review Required

> [!IMPORTANT]
> **VRAM Optimization Strategy (Qwen 3.5 4B Pre-Installed):**
> To guarantee stability on a 4GB GPU while other apps and Windows DWM are running:
> 1. **Local LLM:** We will use `qwen3.5:4b` hosted in Ollama (~2.4 GB VRAM, higher intelligence & reasoning).
> 2. **TTS:** Synthesized via `kokoro-onnx` or `piper-tts` on **CPU** (0 MB VRAM, <150ms latency, high audio quality).
> 3. **STT:** `faster-whisper` (base.en) using `int8` with GPU CUDA or CPU fallback (~200 MB VRAM).
> 4. **Embeddings:** `all-MiniLM-L6-v2` executed on CPU RAM (0 MB VRAM).
> This guarantees total GPU VRAM stays under **3.5 GB**, perfectly utilizing your RTX 3050A without extra downloads!

> [!NOTE]
> **Prerequisites:**
> - Python 3.11+
> - Ollama for Windows (Already has `qwen3.5:4b` installed ✅)
> - Visual C++ Redistributable (standard for Windows Python audio libs)
> - Optional Cloud API keys: Anthropic / OpenAI / Gemini / Groq for fallback

---

## Key Decisions & Configuration

> [!NOTE]
> 1. **Default Summon Hotkey:** **`Ctrl + Shift + J`** (configurable in `config/settings.yaml`).
> 2. **TTS Voice Flavor:** Authentic British AI assistant accent via Kokoro-82M ONNX (`bm_george` / `bm_lewis`).

---

## Architecture & Directory Structure

```
jarvis/
├── config/
│   ├── settings.yaml            # Hotkeys, model names, voice speed, threshold configs
│   └── tools_config.yaml        # Allowed shell commands, blacklists, safety policies
├── core/
│   ├── __init__.py
│   ├── engine.py                # Main async orchestrator event loop
│   ├── router.py                # Hybrid brain: Local (3B) vs Cloud fallback classifier
│   └── context_manager.py       # Short-term sliding context & conversation buffer
├── audio/
│   ├── __init__.py
│   ├── recorder.py              # PyAudio / sounddevice stream with Silero VAD
│   ├── stt.py                   # faster-whisper transcription engine (CUDA/CPU int8)
│   ├── tts.py                   # Piper / Kokoro neural TTS streaming player
│   └── sound_effects.py         # Futuristic chimes (wake, ready, success, error)
├── memory/
│   ├── __init__.py
│   ├── db.py                    # SQLite database for episodic logs and metadata
│   ├── vector_store.py          # CPU-based embeddings (sqlite-vec / Chroma)
│   └── memory_manager.py        # Long-term recall & associative retrieval
├── tools/
│   ├── __init__.py
│   ├── registry.py              # Tool decorator & auto-schema generator for LLM
│   ├── system_ops.py            # Windows app launcher, window focus, volume, brightness
│   ├── powershell_runner.py     # Sandboxed PowerShell/CMD script executor with guardrails
│   ├── web_search.py            # DuckDuckGo/Tavily search & web scraper
│   ├── file_ops.py              # Windows search (Everything SDK/glob), read/write/organize
│   └── media_control.py         # Media keys, Spotify play/pause/track control
├── ui/
│   ├── __init__.py
│   ├── tray.py                  # Windows system tray app with context menu & status icon
│   ├── hud_window.py            # Frameless, translucent floating HUD (PyQt6 / QML)
│   ├── audio_visualizer.py      # Real-time waveform / pulsing ring widget
│   └── hotkey_listener.py       # Global Windows keyboard hook (pynput / keyboard)
├── main.py                      # Application entry point
├── requirements.txt             # Dependency definitions
└── README.md                    # Setup & installation guide
```

---

## Step-by-Step Implementation Phases

### Phase 1: Core Scaffolding & Audio Engine (STT + TTS + VAD)
- [NEW] `requirements.txt`: Add `sounddevice`, `pyaudio`, `faster-whisper`, `piper-tts` / `kokoro-onnx`, `torch` (for Silero VAD), `pyyaml`, `ollama`, `requests`.
- [NEW] `audio/recorder.py`: Implement non-blocking audio capture with `Silero VAD` to detect voice pauses.
- [NEW] `audio/stt.py`: Initialize `faster-whisper` (`base.en`, compute_type="int8", device="cuda" with CPU fallback).
- [NEW] `audio/tts.py`: Implement streaming neural TTS output via `piper-tts` or `kokoro-onnx` on CPU with instant cancellation/interruption.
- [NEW] `audio/sound_effects.py`: Generate/play subtle synthetic audio cues for activation and processing.

### Phase 2: Hybrid LLM Router & Function Calling Registry
- [NEW] `core/router.py`: Connect to local Ollama (`qwen2.5:3b` or `llama3.2:3b`). Add heuristics for when to escalate to Cloud APIs (OpenAI / Claude / Gemini).
- [NEW] `tools/registry.py`: Build a clean `@tool` decorator that registers Python functions, auto-extracts JSON schemas, and handles LLM tool execution loops.
- [NEW] `tools/system_ops.py`: Implement Windows automation (`pywin32`, `pycaw` for volume, `subprocess` for app launching).
- [NEW] `tools/powershell_runner.py`: Add PowerShell execution tool with a strict confirmation gate for dangerous commands.
- [NEW] `tools/web_search.py`: Add fast web search (`duckduckgo-search` or Tavily) and web page text extractor.
- [NEW] `tools/file_ops.py`: Implement smart file search, document reading, and directory organization.

### Phase 3: Persistent Episodic Memory System
- [NEW] `memory/db.py`: SQLite schema for conversation logs, user preferences, and fact key-values.
- [NEW] `memory/vector_store.py`: Lightweight embedding index using `sentence-transformers` (`all-MiniLM-L6-v2`) on CPU.
- [NEW] `memory/memory_manager.py`: Retrieve top-k relevant memories and inject them into system prompt dynamically.

### Phase 4: Modern Desktop UI & System Tray
- [NEW] `ui/tray.py`: PyQt6 system tray icon with states: `Idle`, `Listening`, `Thinking`, `Speaking`.
- [NEW] `ui/hud_window.py`: Futuristic, dark-mode glassmorphic floating overlay that appears upon hotkey trigger or voice wake.
- [NEW] `ui/audio_visualizer.py`: Dynamic glowing audio visualizer bar/ring reflecting live microphone input.
- [NEW] `ui/hotkey_listener.py`: Global background hotkey handler (`pynput` / Win32 API `RegisterHotKey`).
- [NEW] `main.py`: Assemble the entire system into a single async orchestrator.

---

## Verification Plan

### Automated & Unit Tests
- **Audio Loopback Test:** Verify microphone recording -> VAD trigger -> Whisper transcription accuracy.
- **TTS Latency Benchmark:** Benchmark time-to-first-sound for Piper/Kokoro on CPU (<150ms).
- **VRAM Profiler Script:** Run `nvidia-smi` monitor script during simultaneous LLM generation + Whisper STT to verify VRAM never exceeds 2.8 GB.
- **Tool Registry Test:** Unit test all tool executions (app launching, volume change, web search, file search).
- **Memory Retrieval Test:** Store test facts ("My favourite project is Jarvis") and test retrieval on query ("What is my favourite project?").

### Manual & End-to-End Verification
1. **Summon Test:** Press `Ctrl + Shift + J` -> verify HUD appears in <100ms.
2. **Voice Interaction Test:** Speak "Jarvis, what's the weather and open Spotify" -> verify transcription, tool execution, and voice reply.
3. **Interruption Test:** Speak while Jarvis is speaking -> verify immediate TTS stop and new query listening.
4. **Cloud Escalation Test:** Ask a deep complex coding / research question -> verify router smoothly escalates to Cloud API fallback.
