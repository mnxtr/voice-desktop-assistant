# Desktop LLM Assistant

A voice-controlled desktop navigation assistant for users with motor/mobility impairments. Uses a local LLM (Ollama) to interpret natural language commands and automate desktop actions on Windows.

## Features

- **Voice Control**: Hands-free desktop navigation using natural speech
- **Local LLM**: All processing via Ollama (offline, private, no cloud)
- **Eye-Gaze Tracking**: Webcam-based eye tracking with dwell-click (experimental)
- **Screen Grid**: Numbered grid overlay for quick location-based clicking
- **Desktop Automation**: Open/close apps, mouse control, keyboard input, system controls
- **Audio Feedback**: Spoken confirmation of every action
- **Always-On Overlay**: Status indicator showing current state

## Prerequisites

1. **Python 3.10+**
2. **Ollama** - Install from https://ollama.ai
3. **A microphone**
4. **Webcam** (optional, for eye tracking)

## Setup

### 1. Install Ollama and pull a model

```bash
# After installing Ollama, pull the Mistral model:
ollama pull mistral
```

### 2. Install Python dependencies

```bash
cd desktop_llm_assistant
pip install -r requirements.txt
```

### 3. Download Vosk speech model (automatic on first run)

The assistant will auto-download a small English speech model on first run. For better accuracy, manually download a larger model:

```bash
# Download from https://alphacephei.com/vosk/models
# Extract to ~/.desktop_llm_assistant/vosk-model/
```

### 4. Run the assistant

```bash
python main.py
```

## Usage

### Voice Commands

Say **"Hey Assistant"** followed by your command:

| Command | What it does |
|---------|-------------|
| "Open Chrome" | Launches Google Chrome |
| "Close Notepad" | Closes Notepad window |
| "Switch to Firefox" | Brings Firefox to focus |
| "Click" | Clicks at current cursor position |
| "Right click" | Right-clicks at current position |
| "Scroll down" | Scrolls down |
| "Type hello world" | Types "hello world" |
| "Copy" | Presses Ctrl+C |
| "Paste" | Presses Ctrl+V |
| "Save" | Presses Ctrl+S |
| "Undo" | Presses Ctrl+Z |
| "Show grid" | Shows numbered grid overlay |
| "Click 5" | Clicks center of grid cell 5 |
| "Volume up" | Increases system volume |
| "Screenshot" | Takes and saves a screenshot |
| "Search calculator" | Opens Windows search |
| "Start eye tracking" | Enables gaze cursor |
| "Calibrate gaze" | Runs gaze calibration |
| "Stop" | Shuts down the assistant |
| "Help" | Lists available commands |

### Eye-Gaze Tracking

1. Say "Start eye tracking" to enable
2. Say "Calibrate gaze" for better accuracy
3. Look at a spot for 1.5 seconds to dwell-click
4. Say "Stop eye tracking" to disable

### Screen Grid

1. Say "Show grid" to display numbered overlay
2. Say "Click [number]" to click that grid cell
3. Grid auto-hides after clicking

### System Tray

Right-click the tray icon for:
- Toggle Listening on/off
- Toggle Eye Tracking
- Help
- Quit

## Configuration

Settings are stored in `~/.desktop_llm_assistant/config.json`. Key settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `wake_word` | "hey assistant" | Phrase to activate listening |
| `ollama_model` | "mistral" | Ollama model to use |
| `dwell_time` | 1.5 | Seconds of gaze dwell before click |
| `gaze_smoothing` | 5 | Gaze position smoothing frames |
| `grid_rows` / `grid_cols` | 3 / 3 | Grid overlay dimensions |
| `overlay_position` | "top-right" | Status overlay position |
| `voice_rate` | 175 | TTS speech rate |

## Architecture

```
desktop_llm_assistant/
├── main.py              # Entry point, orchestrates all components
├── config.py            # Configuration management
├── voice/
│   ├── listener.py      # Vosk offline speech-to-text
│   └── speaker.py       # pyttsx3 text-to-speech feedback
├── llm/
│   └── processor.py     # Ollama LLM intent parsing
├── actions/
│   ├── desktop.py       # App management (open, close, switch)
│   ├── mouse.py         # Mouse control (click, move, scroll)
│   ├── keyboard.py      # Keyboard input (type, hotkeys)
│   └── system.py        # System controls (volume, screenshot, lock)
├── gaze/
│   ├── tracker.py       # MediaPipe eye tracking via webcam
│   ├── calibration.py   # 9-point gaze calibration
│   └── dwell.py         # Dwell-click detection
├── ui/
│   ├── overlay.py       # Transparent status overlay + grid
│   └── tray.py          # System tray icon + menu
└── requirements.txt
```

## Troubleshooting

- **"Cannot connect to Ollama"**: Make sure Ollama is running (`ollama serve`)
- **"Model not found"**: Run `ollama pull mistral`
- **No audio input**: Check microphone permissions in Windows Settings
- **Eye tracking not working**: Ensure webcam is available and well-lit
- **Voice not recognized**: Try speaking slower/clearer, or download a larger Vosk model
