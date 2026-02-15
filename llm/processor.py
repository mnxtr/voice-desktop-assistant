import json
import logging
import requests
from config import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a desktop navigation assistant for users with motor/mobility impairments.
Your job is to interpret voice commands and return a JSON action.

Available actions:
1. {"action": "open_app", "target": "<app name or path>"}
2. {"action": "close_app", "target": "<window title substring>"}
3. {"action": "switch_window", "target": "<window title substring>"}
4. {"action": "minimize_window"} or {"action": "maximize_window"} or {"action": "restore_window"}
5. {"action": "mouse_click", "button": "left|right|double", "x": <optional int>, "y": <optional int>}
6. {"action": "mouse_move", "direction": "up|down|left|right", "distance": <pixels>}
7. {"action": "mouse_move_to", "x": <int>, "y": <int>}
8. {"action": "scroll", "direction": "up|down|left|right", "amount": <int, default 3>}
9. {"action": "type_text", "text": "<text to type>"}
10. {"action": "hotkey", "keys": ["ctrl", "c"]}  (list of keys to press simultaneously)
11. {"action": "press_key", "key": "<key name>"}  (single key press: enter, tab, escape, etc.)
12. {"action": "show_grid"}  (show numbered grid overlay on screen)
13. {"action": "grid_click", "cell": <int>}  (click center of grid cell number)
14. {"action": "hide_grid"}
15. {"action": "volume", "level": "up|down|mute|unmute"}
16. {"action": "screenshot"}
17. {"action": "lock_screen"}
18. {"action": "search", "query": "<search text>"}  (opens Start menu search)
19. {"action": "dictate", "text": "<text>"}  (type longer text content)
20. {"action": "start_gaze"}  (enable eye tracking cursor)
21. {"action": "stop_gaze"}  (disable eye tracking cursor)
22. {"action": "calibrate_gaze"}  (start gaze calibration)
23. {"action": "help"}  (list available commands)
24. {"action": "stop"}  (stop the assistant)
25. {"action": "confirm"}  (confirm pending action)
26. {"action": "cancel"}  (cancel pending action)

Rules:
- ONLY return valid JSON. No explanation, no markdown, no extra text.
- If the command is ambiguous, return {"action": "clarify", "message": "<what you need to know>"}.
- For "open" commands, map common names: "browser"/"chrome"/"firefox" → actual executable names.
- "click" without coordinates means click at current mouse position.
- For copy/paste/undo, use hotkey action with appropriate keys.
- Always pick the most specific action that matches the command.

Common mappings:
- "copy" → {"action": "hotkey", "keys": ["ctrl", "c"]}
- "paste" → {"action": "hotkey", "keys": ["ctrl", "v"]}
- "undo" → {"action": "hotkey", "keys": ["ctrl", "z"]}
- "redo" → {"action": "hotkey", "keys": ["ctrl", "y"]}
- "save" → {"action": "hotkey", "keys": ["ctrl", "s"]}
- "select all" → {"action": "hotkey", "keys": ["ctrl", "a"]}
- "close tab" → {"action": "hotkey", "keys": ["ctrl", "w"]}
- "new tab" → {"action": "hotkey", "keys": ["ctrl", "t"]}
- "switch tab" → {"action": "hotkey", "keys": ["ctrl", "tab"]}
- "go back" → {"action": "hotkey", "keys": ["alt", "left"]}
- "go forward" → {"action": "hotkey", "keys": ["alt", "right"]}
- "task manager" → {"action": "hotkey", "keys": ["ctrl", "shift", "escape"]}
- "desktop" → {"action": "hotkey", "keys": ["win", "d"]}
"""


class LLMProcessor:
    def __init__(self):
        self._url = config.ollama_url
        self._model = config.ollama_model
        self._conversation = []

    def _call_ollama(self, messages):
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 256,
            },
        }
        try:
            resp = requests.post(
                f"{self._url}/api/chat",
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]
        except requests.ConnectionError:
            logger.error("Cannot connect to Ollama at %s", self._url)
            return json.dumps({"action": "error", "message": "Cannot connect to Ollama. Is it running?"})
        except Exception as e:
            logger.error("Ollama error: %s", e)
            return json.dumps({"action": "error", "message": str(e)})

    def process_command(self, command_text):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *self._conversation[-6:],
            {"role": "user", "content": command_text},
        ]

        raw_response = self._call_ollama(messages)
        logger.info("LLM raw response: %s", raw_response)

        self._conversation.append({"role": "user", "content": command_text})
        self._conversation.append({"role": "assistant", "content": raw_response})

        if len(self._conversation) > 20:
            self._conversation = self._conversation[-12:]

        return self._parse_response(raw_response)

    def _parse_response(self, response_text):
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines).strip()

        try:
            result = json.loads(text)
            if isinstance(result, dict) and "action" in result:
                return result
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                result = json.loads(text[start : end + 1])
                if isinstance(result, dict) and "action" in result:
                    return result
            except json.JSONDecodeError:
                pass

        return {"action": "error", "message": f"Could not parse LLM response: {text[:100]}"}

    def check_connection(self):
        try:
            resp = requests.get(f"{self._url}/api/tags", timeout=5)
            resp.raise_for_status()
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            has_model = any(self._model in n for n in model_names)
            return True, has_model, model_names
        except Exception as e:
            return False, False, []

    def clear_history(self):
        self._conversation.clear()
