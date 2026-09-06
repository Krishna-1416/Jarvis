# 🧭 Project Jarvis: System Workflow & Lifecycle Diagrams

This document illustrates the end-to-end data pipelines, event loops, VRAM allocation flows, and decision-making logic powering **Project Jarvis**.

---

## 1. 🎙️ End-to-End Voice & Text Interaction Loop

This diagram maps the complete journey from user input (voice or hotkey text) to tool execution and neural voice playback.

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User
    participant HUD as 🖥️ Floating HUD / Tray
    participant VAD as 🎙️ Silero VAD (Audio In)
    participant STT as 📝 faster-whisper (STT)
    participant Core as ⚙️ Async Engine Loop
    participant Mem as 🧠 Memory & Vector DB
    participant Brain as 🤖 Local LLM (Qwen 2.5 1.5B)
    participant Tools as 🛠️ Windows Tool Engine
    participant TTS as 🔊 Kokoro TTS (CPU)

    alt Voice Input Mode
        User->>VAD: Speaks "Jarvis, open Spotify and set volume to 50%"
        VAD->>STT: Stream audio chunks (silence detected)
        STT->>Core: Transcribed text string
    else Text Input Mode
        User->>HUD: Presses Ctrl+Shift+J & types command
        HUD->>Core: Dispatches user text query
    end

    Core->>HUD: Update status ("Thinking...")
    Core->>Mem: Query relevant past memories & user context
    Mem-->>Core: Injected context facts

    Core->>Brain: Augmented prompt + JSON Tool Schemas
    Brain-->>Core: Tool Call Request: launch_app("Spotify") + set_volume(50)

    Core->>Tools: Execute OS commands via pywin32 & pycaw
    Tools-->>Core: Execution status: Success

    Core->>Brain: Tool output feedback
    Brain-->>Core: Final verbal reply: "Spotify is open and volume is at 50%, sir."

    par Audio & Visual Output
        Core->>TTS: Synthesize reply audio (CPU ONNX)
        TTS-->>User: Stream voice reply to speakers
    and HUD Display
        Core->>HUD: Render markdown chat response & status ("Idle")
    end

    Core->>Mem: Save conversation turn to SQLite episodic memory
```

---

## 2. 🔀 Hybrid Brain & Tool Routing Workflow

How Jarvis dynamically chooses between the local Qwen 3.5 4B brain and cloud API escalation.

```mermaid
flowchart TD
    Start([User Request Ingested]) --> Classify{Intent & Complexity Check}
    
    Classify -->|OS Controls / Quick Chat / Media / Apps| LocalRoute[Local Brain: Qwen 3.5 4B]
    Classify -->|Deep Coding / Research / Explicit 'Cloud' Command| CloudRoute[Cloud Brain: Claude 3.5 / GPT-4o]
    
    subgraph Local_Execution [Local Engine - ~2.4 GB VRAM]
        LocalRoute --> GenToolCall[Generate JSON Tool Call]
        GenToolCall --> ValidateSchema{Valid Schema?}
        ValidateSchema -->|Yes| SafetyGate
        ValidateSchema -->|Retry / Fallback| CloudRoute
    end
    
    subgraph Safety_System [Windows Safety Interlock]
        SafetyGate{Is Destructive Action?<br/>e.g. rm, format, registry}
        SafetyGate -->|Yes| PromptUser[Prompt User for Vocal/Click Confirmation]
        SafetyGate -->|No / Safe| ExecTool[Execute Python Tool Handler]
        PromptUser -->|Confirmed| ExecTool
        PromptUser -->|Denied| CancelTool[Abort & Return Cancellation Notice]
    end
    
    subgraph Tool_Handlers [Windows OS Execution Suite]
        ExecTool --> T1[App Launcher & Window Focus]
        ExecTool --> T2[Volume & Media Keys Control]
        ExecTool --> T3[PowerShell Script Sandbox]
        ExecTool --> T4[DuckDuckGo Search & Web Scraper]
        ExecTool --> T5[File Search & Everything SDK]
    end
    
    Tool_Handlers --> ResultSynthesis[Synthesize Final Human-Friendly Reply]
    CloudRoute --> ResultSynthesis
    CancelTool --> ResultSynthesis
    
    ResultSynthesis --> TTSStream[Send to Kokoro CPU TTS Stream]
```

---

## 3. ⚡ Voice Interruption (Barge-In) Handling

How Jarvis instantly stops speaking and listens when you interrupt him mid-sentence.

```mermaid
stateDiagram-v2
    [*] --> Idle: Waiting for trigger
    
    Idle --> Listening: Hotkey pressed / Wake-word / Speech detected
    Listening --> Processing: Silence detected by Silero VAD (600ms)
    Processing --> Speaking: Generating & streaming Kokoro TTS audio
    
    Speaking --> Idle: Speech finishes naturally
    
    Speaking --> Interrupted: User speaks while TTS is active
    note right of Interrupted
      1. Immediate PyAudio stream abort
      2. Clear remaining TTS buffer
      3. Capture new audio stream
    end note
    
    Interrupted --> Listening: Process new speech immediately
```

---

## 4. 💾 Dual-Layer Memory & Context Pipeline

```mermaid
flowchart LR
    subgraph User_Turn [Incoming Conversation]
        InputQuery[User Query]
    end

    subgraph Memory_Engine [Episodic & Semantic Memory]
        EmbeddingModel["MiniLM-L6-v2<br/>(CPU Vectorizer)"]
        VectorDB[("Vector Store<br/>(Semantic Match)")]
        SQLiteDB[("SQLite DB<br/>(Recent History & Facts)")]
    end

    subgraph Prompt_Builder [System Prompt Assembly]
        BasePrompt[Base Jarvis Persona & Rules]
        RelevantFacts[Retrieved Facts & Preferences]
        SlidingHistory[Last 5 Conversation Turns]
        ToolDefinitions[Active Tool Schemas]
    end

    InputQuery --> EmbeddingModel
    EmbeddingModel -->|Vector Search| VectorDB
    VectorDB -->|Top-K Context| RelevantFacts
    SQLiteDB -->|Rolling Buffer| SlidingHistory

    BasePrompt --> FinalContext[Compiled LLM Context]
    RelevantFacts --> FinalContext
    SlidingHistory --> FinalContext
    ToolDefinitions --> FinalContext
    InputQuery --> FinalContext

    FinalContext --> OllamaRunner[Ollama Qwen 3.5 4B Inference]
```

---

## 5. 🖥️ Physical Hardware & VRAM Resource Layout

Exact mapping of how models and processes share hardware on your **RTX 3050A (4GB VRAM)** laptop with pre-installed `qwen3.5:4b`.

```
+-----------------------------------------------------------------------------------------+
|                                    NVIDIA RTX 3050A (4GB VRAM)                          |
+-----------------------------------------------------------------------------------------+
| [▓▓▓▓▓▓▓▓▓▓] Windows 11 DWM & Desktop Display Buffer       : ~850 MB                    |
| [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓] Qwen 3.5 4B in Ollama       : ~2,500 MB                  |
| [▓▓▓] faster-whisper base.en (int8 on CUDA)                : ~200 MB                    |
| [░░░░░░░░] Free GPU Safety Headroom                        : ~546 MB (STABLE & SAFE)    |
+-----------------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------------+
|                                      SYSTEM CPU & RAM                                   |
+-----------------------------------------------------------------------------------------+
| [⚙️ CPU Core] Silero VAD (Voice Activity Detection)         : < 1% CPU                   |
| [⚙️ CPU Core + ONNX] Kokoro-82M Neural TTS Engine          : ~120 MB RAM / <100ms chunk |
| [⚙️ CPU Core] all-MiniLM-L6-v2 Embeddings & SQLite DB       : ~110 MB RAM                |
| [⚙️ CPU Core] PyQt6 Floating Glass HUD & Global Hotkeys    : ~70 MB RAM                 |
+-----------------------------------------------------------------------------------------+
```
