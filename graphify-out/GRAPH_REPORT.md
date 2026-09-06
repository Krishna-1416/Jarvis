# Graph Report - Jarvis  (2026-08-26)

## Corpus Check
- 37 files · ~15,479 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 346 nodes · 431 edges · 20 communities detected
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 39 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]

## God Nodes (most connected - your core abstractions)
1. `JarvisEngine` - 18 edges
2. `JarvisHUDWindow` - 17 edges
3. `TextToSpeech` - 14 edges
4. `JarvisApp` - 14 edges
5. `AudioRecorder` - 13 edges
6. `ContextManager` - 13 edges
7. `BrainRouter` - 11 edges
8. `Database` - 11 edges
9. `AudioVisualizerWidget` - 10 edges
10. `SoundEffects` - 9 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `run_app()`  [INFERRED]
  main.py → ui\app.py
- `JarvisEngine` --uses--> `AudioRecorder`  [INFERRED]
  core\engine.py → audio\recorder.py
- `main()` --calls--> `AudioRecorder`  [INFERRED]
  tests\test_audio_input.py → audio\recorder.py
- `main()` --calls--> `AudioRecorder`  [INFERRED]
  tests\test_audio_loop.py → audio\recorder.py
- `JarvisEngine` --uses--> `SpeechToText`  [INFERRED]
  core\engine.py → audio\stt.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (23): Jarvis Memory Subsystem Contains SQLite episodic storage, CPU vector embeddings,, forget_user_fact(), list_all_user_memories(), MemoryManager, Memory Manager & Recall Engine for Project Jarvis. Provides unified semantic and, Delete a saved fact.     topic: The topic name or key to delete from memory, List all stored memories., Store a fact or preference in long-term memory. (+15 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (12): QObject, QWidget, AudioVisualizerWidget, Dynamic Futuristic Audio Visualizer Widget (Arc Reactor / Waveform) for Project, Update live audio input amplitude level (0.0 to 1.0)., Global Hotkey Listener for Project Jarvis. Monitors system-wide keyboard shortcu, JarvisHUDWindow, Futuristic Glassmorphic Floating HUD Window for Project Jarvis. Frameless, trans (+4 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (15): ContextManager, Conversation Context & Sliding History Manager for Project Jarvis. Maintains sho, Assemble dynamic system prompt with real-time timestamp and optional memory fact, Return full messages list starting with system prompt., Keep history within configured max turns to maintain sub-second latency., BrainRouter, Hybrid Brain Router for Project Jarvis. Orchestrates reasoning via local Ollama, Execute cloud API chat fallback via OpenAI SDK. (+7 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (12): QSystemTrayIcon, main(), Diagnostic test for Jarvis PyQt6 UI, HUD Window, and Visualizer., JarvisApp, Desktop Application Coordinator for Project Jarvis. Unites PyQt6 Application, Gl, Launch the entire Jarvis assistant system., run_app(), HotkeyListener (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.1
Nodes (11): Jarvis Audio Subsystem Contains VAD, Speech-to-Text (STT), Text-to-Speech (TTS),, Voice Activity Detection (VAD) & Audio Capture Stream for Project Jarvis. Uses S, Speech-to-Text (STT) Engine using faster-whisper. Runs on CPU int8 delivering <1, Load the faster-whisper model with fallback., Transcribe a 16kHz float32 numpy audio array.         Returns: (transcribed_text, SpeechToText, Multi-Engine Ultra-Fast Text-to-Speech Subsystem for Project Jarvis. Supports: 1, main() (+3 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (11): Strip markdown syntax, URLs, and code blocks for clean pronunciation., Instant zero-latency speech using Windows SAPI5., High quality neural streaming via Microsoft Ryan British voice., Synthesize and play audio synchronously with zero delay., Asynchronously speak in background thread., Initialize Windows SAPI5 voice engine., Initialize Kokoro ONNX model., Instant interruption / barge-in. Halts playback immediately. (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (9): JarvisEngine, Core Orchestration Engine for Project Jarvis. Asynchronously coordinates audio i, Process a text command (from voice transcription or HUD text input)., Start listening loop., Stop listening loop and cleanup., Called when user starts speaking. Handles barge-in interruption., Called when user stops speaking (silence detected by VAD)., main() (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (8): AudioRecorder, Background worker evaluating VAD chunks and dispatching completed utterances., Start recording and listening for voice input., Initialize Silero VAD ONNX model., Calculate neural speech probability for a 512-sample 16kHz chunk., Raw audio stream callback from sounddevice., main(), Diagnostic test for Jarvis Microphone input and VAD detection.

### Community 8 - "Community 8"
Cohesion: 0.12
Nodes (9): Jarvis Windows Tools & Capabilities Suite. Exports the tool registry and registe, Tool Registry & Schema Generator for Project Jarvis. Allows Python functions to, Return list of JSON schemas for all registered tools., Find tool by name, execute it, and format result as a clean string., Convert function signature and type hints into JSON Schema., Execute the tool function with filtered keyword arguments matching signature., Decorator or direct method to register a tool., Tool (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.19
Nodes (8): Procedural Futuristic Sound Effects for Project Jarvis. Generates and plays clea, Play synthesized audio non-blocking in a background thread., Crisp rising two-tone chime when Jarvis wakes up / summoned., Soft harmonic acknowledgement chime., Subtle blip when computation/tool execution starts., Warm triad chime upon successful tool execution., Soft low descending tone on error., SoundEffects

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (8): Database, SQLite Database Storage Layer for Project Jarvis. Manages persistent episodic co, Delete a memory by topic., Fetch all stored memories., Create tables and indices if they do not exist., Save a single conversation turn., Retrieve recent conversation turns., Insert or update a memory by topic.

### Community 11 - "Community 11"
Cohesion: 0.13
Nodes (2): Config, Configuration Loader for Project Jarvis. Loads and validates settings.yaml and t

### Community 12 - "Community 12"
Cohesion: 0.15
Nodes (15): _get_audio_endpoint(), get_system_stats(), get_system_volume(), launch_application(), lock_workstation(), Windows System Operations & OS Automation for Project Jarvis. Handles app launch, Mute or unmute master volume.     mute: True to mute, False to unmute, Lock the Windows desktop workstation. (+7 more)

### Community 13 - "Community 13"
Cohesion: 0.25
Nodes (10): media_next_track(), media_play_pause(), media_previous_track(), media_stop(), Media Playback & Windows Multimedia Keys Tool for Project Jarvis. Sends virtual, Send keydown and keyup for a virtual key code., Toggle media play/pause., Skip to next media track. (+2 more)

### Community 14 - "Community 14"
Cohesion: 0.2
Nodes (9): list_directory(), File Management & Document Tools for Project Jarvis. Search, read, write, and in, Search for files matching a pattern.     pattern: Filename or wildcard pattern (, Read content of a file.     file_path: Absolute or relative path to the file, Write text to a file.     file_path: Path to the destination file     content: T, List directory contents.     dir_path: Path to directory (defaults to current wo, read_file_text(), search_files() (+1 more)

### Community 15 - "Community 15"
Cohesion: 0.25
Nodes (7): open_website(), open_youtube(), Browser & Website Navigation Tools for Project Jarvis. Allows Jarvis to open web, Open YouTube or search for a specific video/song.     query: Optional song, vide, Open a website in the default browser.     target: The website name, domain, or, Open browser and search with a specific engine.     query: The search term or to, search_in_browser()

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (5): fetch_webpage_content(), Web Search and Webpage Reader Tool for Project Jarvis. Provides internet search, Search the web for information.     query: The search query string     max_resul, Fetch webpage readable text.     url: The web URL to fetch and read, search_web()

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (3): download_with_headers(), main(), Robust Model Downloader for Project Jarvis. Downloads Kokoro ONNX model and voic

### Community 18 - "Community 18"
Cohesion: 0.5
Nodes (3): PowerShell & CMD Execution Tool with Safety Interlocks. Executes non-destructive, Execute a PowerShell command.     command: The PowerShell command string to run, run_powershell_command()

### Community 19 - "Community 19"
Cohesion: 0.67
Nodes (1): Diagnostic test for Jarvis Windows Tool Registry & Built-in Tools.

## Knowledge Gaps
- **122 isolated node(s):** `Project Jarvis - Personal AI Desktop Assistant for Windows. Main Entry Point sup`, `Voice Activity Detection (VAD) & Audio Capture Stream for Project Jarvis. Uses S`, `Initialize Silero VAD ONNX model.`, `Calculate neural speech probability for a 512-sample 16kHz chunk.`, `Raw audio stream callback from sounddevice.` (+117 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 11`** (16 nodes): `assistant_name()`, `Config`, `.__init__()`, `._load_yaml()`, `local_model()`, `ollama_url()`, `push_to_talk_hotkey()`, `config.py`, `Configuration Loader for Project Jarvis. Loads and validates settings.yaml and t`, `silence_duration_ms()`, `stt_device()`, `stt_model_size()`, `summon_hotkey()`, `tts_speed()`, `tts_voice()`, `vad_threshold()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (3 nodes): `main()`, `test_tools.py`, `Diagnostic test for Jarvis Windows Tool Registry & Built-in Tools.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JarvisEngine` connect `Community 6` to `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.199) - this node is a cross-community bridge._
- **Why does `JarvisApp` connect `Community 3` to `Community 1`, `Community 6`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `TextToSpeech` connect `Community 5` to `Community 4`, `Community 6`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `JarvisEngine` (e.g. with `BrainRouter` and `ContextManager`) actually correct?**
  _`JarvisEngine` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `JarvisHUDWindow` (e.g. with `JarvisApp` and `AudioVisualizerWidget`) actually correct?**
  _`JarvisHUDWindow` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `TextToSpeech` (e.g. with `JarvisEngine` and `.__init__()`) actually correct?**
  _`TextToSpeech` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `JarvisApp` (e.g. with `JarvisEngine` and `JarvisHUDWindow`) actually correct?**
  _`JarvisApp` has 4 INFERRED edges - model-reasoned connections that need verification._