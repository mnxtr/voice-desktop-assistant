<div align="center">

# Voice Desktop Assistant

### Hands-free desktop control powered by local AI

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

<br />

A voice-controlled desktop navigation assistant designed for users with **motor and mobility impairments**. Speak naturally to control your entire desktop — open apps, click, scroll, type, and more — all processed locally with zero cloud dependency.

<br />

[Getting Started](#-getting-started) · [Voice Commands](#-voice-commands) · [Eye Tracking](#-eye-gaze-tracking) · [Configuration](#%EF%B8%8F-configuration) · [Architecture](#-architecture)

---

</div>

<br />

## Highlights

<table>
<tr>
<td width="50%">

**Voice-First Navigation**
> Say *"Hey Assistant, open Chrome"* and it just works. Natural language commands are interpreted by a local LLM and translated into desktop actions instantly.

</td>
<td width="50%">

**100% Offline & Private**
> Everything runs on your machine. Speech recognition (Vosk), LLM processing (Ollama), and text-to-speech (pyttsx3) — no internet, no telemetry, no cloud.

</td>
</tr>
<tr>
<td width="50%">

**Eye-Gaze Control**
> Use your webcam as an eye tracker. Look at a target, dwell for 1.5s to click. Combine gaze with voice for precise, hands-free control.

</td>
<td width="50%">

**Screen Grid System**
> Say *"Show grid"* to overlay numbered cells on your screen. Then say *"Click 5"* to instantly click that region. Fast, accurate, no mouse needed.

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

## Eye-Gaze Tracking

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
| `ollama_model` | `mistral` | LLM model for intent parsing |
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
│   └── processor.py         Ollama LLM — natural language → structured JSON actions
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
