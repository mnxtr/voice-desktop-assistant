<div align="center">

# Voice Desktop Assistant

### Hands-free desktop control powered by local AI

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gemini](https://img.shields.io/badge/Gemini-API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

<br />

A voice-controlled desktop navigation assistant designed for users with **motor and mobility impairments**. Speak naturally to control your entire desktop — open apps, click, scroll, type, and more. 

**NEW**: Now with **Gemini API support** for agentic multi-step workflows! Use Gemini for cloud-powered intelligence or run 100% offline with Ollama.

<br />

[Getting Started](#-getting-started) · [Voice Commands](#-voice-commands) · [Multi-Step Workflows](#-multi-step-workflows-new) · [Eye Tracking](#-eye-gaze-tracking) · [Gemini Setup](docs/GEMINI_SETUP.md) · [Configuration](#%EF%B8%8F-configuration)

---

</div>

<br />

## Highlights

<table>
<tr>
<td width="50%">

**Voice-First Navigation**
> Say *"Hey Assistant, open Chrome and search for weather"* and watch it execute multiple steps automatically. Natural language commands powered by Gemini AI or local Ollama LLM.

</td>
<td width="50%">

**Hybrid LLM Processing**
> Choose your mode: **Gemini API** for agentic workflows (cloud), **Ollama** for offline privacy, or **Hybrid** (best of both worlds with automatic fallback).

</td>
</tr>
<tr>
<td width="50%">

**Eye-Gaze Control**
> Use your webcam as an eye tracker. Look at a target, dwell for 1.5s to click. Combine gaze with voice for precise, hands-free control.

</td>
<td width="50%">

**Multi-Step Workflows (NEW)**
> Complex commands become automatic workflows. "Take a screenshot and open Paint" → 2-step workflow executes seamlessly.

</td>
</tr>
</table>

<br />

## Prerequisites

| Requirement | Details |
|:-----------:|---------|
| **Python** | 3.10 or higher |
| **Ollama** | [Install from ollama.ai](https://ollama.ai) |
| **Microphone** | Any USB or built-in mic |
| **Webcam** | Optional — for eye-gaze tracking |

<br />

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/mnxtr/voice-desktop-assistant.git
cd voice-desktop-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull the LLM model

```bash
ollama pull mistral
```

### 4. Launch

```bash
python main.py
```

> The Vosk speech model (~40MB) downloads automatically on first run.
> For better accuracy, download a larger model from [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) and extract it to `~/.desktop_llm_assistant/vosk-model/`.

<br />

## Voice Commands

Say **"Hey Assistant"** followed by any command:

<details>
<summary><b>App Control</b></summary>

| Command | Action |
|---------|--------|
| `Open Chrome` | Launches Google Chrome |
| `Close Notepad` | Closes the Notepad window |
| `Switch to Firefox` | Brings Firefox to the foreground |
| `Minimize window` | Minimizes the active window |
| `Maximize window` | Maximizes the active window |

</details>

<details>
<summary><b>Mouse & Navigation</b></summary>

| Command | Action |
|---------|--------|
| `Click` | Left click at current position |
| `Right click` | Right click at current position |
| `Double click` | Double click at current position |
| `Scroll down` | Scrolls the page down |
| `Scroll up` | Scrolls the page up |
| `Show grid` | Displays numbered grid overlay |
| `Click 5` | Clicks the center of grid cell 5 |

</details>

<details>
<summary><b>Keyboard & Text</b></summary>

| Command | Action |
|---------|--------|
| `Type hello world` | Types "hello world" |
| `Copy` | <kbd>Ctrl</kbd>+<kbd>C</kbd> |
| `Paste` | <kbd>Ctrl</kbd>+<kbd>V</kbd> |
| `Undo` | <kbd>Ctrl</kbd>+<kbd>Z</kbd> |
| `Save` | <kbd>Ctrl</kbd>+<kbd>S</kbd> |
| `Select all` | <kbd>Ctrl</kbd>+<kbd>A</kbd> |
| `New tab` | <kbd>Ctrl</kbd>+<kbd>T</kbd> |
| `Close tab` | <kbd>Ctrl</kbd>+<kbd>W</kbd> |

</details>

<details>
<summary><b>System</b></summary>

| Command | Action |
|---------|--------|
| `Volume up` | Increases system volume |
| `Volume down` | Decreases system volume |
| `Mute` | Toggles mute |
| `Screenshot` | Saves screenshot to ~/Pictures |
| `Lock screen` | Locks the workstation |
| `Search calculator` | Opens Windows Start search |

</details>

<details>
<summary><b>Eye Tracking</b></summary>

| Command | Action |
|---------|--------|
| `Start eye tracking` | Enables gaze-controlled cursor |
| `Stop eye tracking` | Disables gaze control |
| `Calibrate gaze` | Runs 9-point calibration |

</details>

<br />

## 🔗 Multi-Step Workflows (NEW)

With **Gemini API** integration, the assistant can now execute **complex multi-step commands** automatically:

### Example Workflows

| Voice Command | Workflow Steps |
|---------------|----------------|
| `Open Chrome and search for weather` | 1. Open Chrome<br>2. Type "weather"<br>3. Press Enter |
| `Take a screenshot and open Paint` | 1. Take screenshot<br>2. Open Paint application |
| `Copy this and paste it in Notepad` | 1. Copy (Ctrl+C)<br>2. Open Notepad<br>3. Paste (Ctrl+V) |
| `Minimize this window and show desktop` | 1. Minimize current window<br>2. Press Win+D (show desktop) |

### How It Works

1. **Gemini AI** analyzes your command and creates a step-by-step execution plan
2. **Workflow Engine** executes each step sequentially with status updates
3. **Visual Feedback** shows progress in the status overlay
4. **Automatic Error Handling** — if a step fails, the workflow aborts gracefully

### Configuration

Edit `~/.desktop_llm_assistant/config.json`:

```json
{
  "llm_mode": "hybrid",
  "gemini_model": "gemini-1.5-flash",
  "gemini_fallback_enabled": true
}
```

**LLM Modes**:
- `"hybrid"` (Recommended) — Gemini with Ollama fallback
- `"gemini"` — Gemini API only (requires API key)
- `"ollama"` — Offline-only mode

### Setup Gemini API

See [Gemini Setup Guide](docs/GEMINI_SETUP.md) for detailed instructions.

**Quick Start**:
```bash
# 1. Get API key from https://ai.google.dev/
# 2. Set environment variable
export GEMINI_API_KEY="your-api-key-here"

# 3. Restart the assistant
python main.py
```

**Cost**: ~$0.26/month for heavy usage (stays within free tier for most users)

<br />

## 👁️ Eye-Gaze Tracking

The experimental gaze module uses **MediaPipe Face Mesh** through your webcam — no special hardware required.

```
1. Say "Start eye tracking"      → Cursor follows your gaze
2. Say "Calibrate gaze"          → 9-point calibration for accuracy
3. Look at a target for 1.5s     → Dwell-click triggers automatically
4. Say "Stop eye tracking"       → Returns to voice-only mode
```

> **Tip:** Combine gaze and voice for the best experience — gaze moves the cursor, voice confirms the click.

<br />

## Screen Grid

A numbered overlay that divides your screen into clickable regions:

```
┌─────┬─────┬─────┐
│  1  │  2  │  3  │
├─────┼─────┼─────┤
│  4  │  5  │  6  │
├─────┼─────┼─────┤
│  7  │  8  │  9  │
└─────┴─────┴─────┘
```

- Say **"Show grid"** to display
- Say **"Click 5"** to click the center of that cell
- Grid auto-hides after a click

<br />

## Configuration

All settings are stored in `~/.desktop_llm_assistant/config.json` and can be edited at any time.

| Setting | Default | Description |
|---------|:-------:|-------------|
| `wake_word` | `hey assistant` | Phrase to activate listening |
| `llm_mode` | `hybrid` | LLM processing mode (gemini/ollama/hybrid) |
| `gemini_model` | `gemini-1.5-flash` | Gemini API model name |
| `ollama_model` | `mistral` | Ollama LLM model for intent parsing |
| `dwell_time` | `1.5` | Seconds of gaze dwell before click |
| `gaze_smoothing` | `5` | Number of frames for gaze smoothing |
| `grid_rows` | `3` | Grid overlay row count |
| `grid_cols` | `3` | Grid overlay column count |
| `overlay_position` | `top-right` | Status overlay screen position |
| `voice_rate` | `175` | Text-to-speech speaking rate |
| `mouse_move_speed` | `0.3` | Mouse movement animation duration |

<br />

## Architecture

```
voice-desktop-assistant/
│
├── main.py                  Entry point & orchestrator
├── config.py                JSON-based configuration management
│
├── voice/
│   ├── listener.py          Vosk offline speech-to-text + wake word detection
│   └── speaker.py           pyttsx3 text-to-speech audio feedback
│
├── llm/
│   ├── gemini_processor.py  Gemini API client for agentic workflows
│   ├── processor.py         Ollama LLM — natural language → structured JSON actions
│   ├── hybrid_processor.py  Smart LLM selector (Gemini ↔ Ollama fallback)
│   └── workflow_engine.py   Multi-step workflow executor with status callbacks
│
├── actions/
│   ├── desktop.py           App lifecycle — open, close, switch, minimize, maximize
│   ├── mouse.py             Cursor control — click, move, scroll
│   ├── keyboard.py          Text input — type, hotkeys, with safety blocklist
│   └── system.py            OS controls — volume, screenshot, lock, search
│
├── gaze/
│   ├── tracker.py           MediaPipe Face Mesh iris tracking via webcam
│   ├── calibration.py       9-point fullscreen gaze calibration
│   └── dwell.py             Dwell-click — sustained gaze triggers a click
│
├── ui/
│   ├── overlay.py           Transparent draggable status overlay + grid system
│   └── tray.py              System tray icon with quick-access menu
│
└── requirements.txt
```

<br />

## How It Works

```
  Microphone ──► Vosk STT ──► "open chrome" ──► Ollama LLM ──► {"action": "open_app", "target": "chrome"}
                                                                          │
  Speaker ◄── "Opening Chrome" ◄── TTS ◄── Execute Action ◄──────────────┘
```

1. **Listen** — Vosk continuously processes audio, waiting for the wake word
2. **Transcribe** — Speech is converted to text entirely offline
3. **Understand** — The local LLM parses natural language into a structured JSON action
4. **Execute** — The action module performs the desktop operation
5. **Confirm** — TTS speaks the result back to the user

<br />

## Troubleshooting

<details>
<summary><b>"Cannot connect to Ollama"</b></summary>

Make sure Ollama is running:
```bash
ollama serve
```
</details>

<details>
<summary><b>"Model not found"</b></summary>

Pull the required model:
```bash
ollama pull mistral
```
</details>

<details>
<summary><b>No audio input detected</b></summary>

- Check microphone permissions in **Windows Settings > Privacy > Microphone**
- Ensure `libportaudio2` is installed (Linux: `sudo apt install libportaudio2`)
</details>

<details>
<summary><b>Eye tracking not working</b></summary>

- Ensure your webcam is connected and not in use by another app
- Good lighting improves tracking accuracy significantly
- Run calibration for best results
</details>

<details>
<summary><b>Voice not recognized accurately</b></summary>

- Speak clearly at a moderate pace
- Reduce background noise
- Download a [larger Vosk model](https://alphacephei.com/vosk/models) for better accuracy
</details>

<br />

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Speech-to-Text | [Vosk](https://alphacephei.com/vosk/) | Offline voice recognition |
| LLM | [Ollama](https://ollama.ai) + Mistral | Natural language understanding |
| Text-to-Speech | [pyttsx3](https://github.com/nateshmbhat/pyttsx3) | Audio feedback |
| Desktop Automation | [PyAutoGUI](https://pyautogui.readthedocs.io/) + [pywinauto](https://pywinauto.readthedocs.io/) | Mouse, keyboard, window control |
| Eye Tracking | [MediaPipe](https://mediapipe.dev/) + OpenCV | Webcam-based gaze detection |
| UI | Tkinter + [pystray](https://github.com/moses-palmer/pystray) | Overlay & system tray |

<br />

## Contributing

Contributions are welcome. Please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

<br />

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

<br />

<div align="center">

---

Built with the goal of making desktop computing accessible to everyone.

</div>
