# 🚀 Project Jarvis: Installation & Setup Guide (Windows)

This guide walks you through setting up **Project Jarvis** on Windows with an **NVIDIA RTX 3050A (4GB VRAM)**, ensuring zero VRAM overflow and sub-second voice/text response latency.

---

## 📋 System Prerequisites

| Component | Recommended Version | Purpose |
|---|---|---|
| **OS** | Windows 10 / 11 (64-bit) | Operating Environment |
| **Python** | Python 3.10 or 3.11 (64-bit) | Core runtime (ensure "Add Python to PATH" is checked) |
| **GPU Driver** | NVIDIA Game Ready / Studio Driver (CUDA 12+) | Hardware acceleration |
| **Ollama** | Latest Windows installer | Local LLM host for 3B models |
| **MSVC Runtime** | Visual C++ Redistributable 2015–2022 | Required by `pyaudio`, `sounddevice`, `onnxruntime` |

> [!TIP]
> Download the **Visual C++ Redistributable**: [Microsoft Official Link](https://aka.ms/vs/17/release/vc_redist.x64.exe)

---

## 🛠️ Step-by-Step Installation

### Step 1: Open PowerShell as Administrator & Clone/Navigate
Open PowerShell and navigate to your Jarvis project root:
```powershell
cd c:\Users\Krishna\Jarvis
```

---

### Step 2: Create and Activate Python Virtual Environment
Creating an isolated virtual environment prevents library conflicts:
```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1
```
*(If you see an execution policy error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

---

### Step 3: Install PyTorch with CUDA Support
Install PyTorch compiled for CUDA 12.1 to enable GPU acceleration for Whisper and VAD:
```powershell
pip install --upgrade pip setuptools wheel
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

To verify CUDA is recognized:
```powershell
python -c "import torch; print('CUDA Available:', torch.cuda.is_available(), '| Device:', torch.cuda.get_device_name(0))"
```

---

### Step 4: Install Dependencies

Create or verify your `requirements.txt` with the following optimized dependencies:

```text
# Speech & Audio
faster-whisper>=1.0.0
sounddevice>=0.4.6
pyaudio>=0.2.14
soundfile>=0.12.1
numpy<2.0.0
scipy>=1.11.0

# Neural TTS (CPU-accelerated)
kokoro-onnx>=0.3.0
onnxruntime>=1.17.0

# Local & Cloud LLM Integrations
ollama>=0.3.0
openai>=1.30.0
anthropic>=0.28.0
google-genai>=0.1.0

# Memory & Embeddings (CPU-based)
sentence-transformers>=2.7.0

# Windows Automation & UI
PyQt6>=6.6.0
pywin32>=306
pycaw>=20240210
pynput>=1.7.6
duckduckgo-search>=6.0.0
pyyaml>=6.0.1
rich>=13.7.0
```

Install them with:
```powershell
pip install -r requirements.txt
```

> [!NOTE]
> **If `pyaudio` fails to build on Windows:**
> Install the pre-compiled wheel using `pipwin`:
> ```powershell
> pip install pipwin
> pipwin install pyaudio
> ```

---

### Step 5: Configure Local Brain (Qwen 2.5 1.5B)

Test that Ollama is serving locally:
```powershell
ollama run qwen2.5:1.5b "Hello Jarvis, are you ready?"
```

---

### Step 6: Download Neural Voice Models (Kokoro / Piper TTS)

Kokoro-82M is ultra-lightweight, runs on CPU in <100ms, and produces studio-quality voices.

Create a `models/` directory and download the voice weights:
```powershell
mkdir -p models/tts
mkdir -p models/vad
```

Download Kokoro ONNX model files:
- `models/tts/kokoro-v0_19.onnx`
- `models/tts/voices.json`

*(A helper script `scripts/download_models.py` will automate this step).*

---

### Step 7: Configure Settings & API Keys

Create `config/settings.yaml`:
```yaml
assistant:
  name: "Jarvis"
  summon_hotkey: "<ctrl>+<shift>+j"   # Hotkey to open floating HUD (or "<ctrl>+j")
  push_to_talk_hotkey: "<ctrl>+space"

llm:
  provider: "ollama"
  local_model: "qwen3.5:4b"
  ollama_base_url: "http://localhost:11434"
  cloud_fallback:
    enabled: true
    provider: "openai"              # "openai" | "anthropic" | "gemini"
    api_key_env: "OPENAI_API_KEY"

voice:
  stt:
    model_size: "base.en"           # "base.en" or "small.en"
    device: "cuda"                  # "cuda" with automatic CPU fallback
    compute_type: "int8"
  tts:
    engine: "kokoro"
    voice_name: "bm_george"         # British Jarvis tone ("bm_george" / "bm_lewis" / "af_bella")
    speed: 1.05
  vad:
    threshold: 0.5
    silence_duration_ms: 600

memory:
  db_path: "data/jarvis_memory.db"
  embedding_model: "all-MiniLM-L6-v2"
  device: "cpu"
```

---

## 🧪 Verification & Smoke Test

Run individual module diagnostics to ensure all subsystems are green:

```powershell
# 1. Test Audio Input (Microphone & VAD)
python -m tests.test_audio_input

# 2. Test TTS Speech Output (Speakers)
python -m tests.test_tts

# 3. Test Local Ollama Connection & Function Calling
python -m tests.test_llm

# 4. Check GPU VRAM Footprint
nvidia-smi
```

---

## 🎯 Running Jarvis

Once configured, launch the main desktop agent:
```powershell
python main.py
```

- Jarvis will sit quietly in your **Windows System Tray**.
- Press **`Ctrl + Shift + J`** (or your configured hotkey) to summon the floating HUD or speak directly if wake-word/VAD is enabled.
- Press **`Ctrl + C`** in terminal or right-click the tray icon to Exit.

---

## 🔧 Troubleshooting

### 1. `CUDA error: out of memory`
- Ensure no other heavy VRAM applications (like Stable Diffusion or games) are running.
- In `config/settings.yaml`, switch STT compute from `cuda` to `cpu`.

### 2. `Microphone not accessible`
- Check Windows Settings: **Privacy & Security > Microphone > Let desktop apps access your microphone** (ensure turned ON).

### 3. `Ollama Connection Refused`
- Make sure the Ollama application is running in your Windows taskbar. Start it with `ollama serve`.
