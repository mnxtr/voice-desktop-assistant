import os
import json
import logging
from typing import Dict, List, Optional, Any
from config import config

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai

    _HAS_GEMINI = True
except ImportError:
    genai = None
    _HAS_GEMINI = False

# System prompt for Gemini - supports both single actions and multi-step workflows
GEMINI_SYSTEM_PROMPT = """You are a desktop navigation assistant for users with motor/mobility impairments.
Your job is to interpret voice commands and return JSON actions.

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

For SIMPLE commands (single action), return:
{"action": "<action_name>", ...parameters...}

For COMPLEX commands (multiple steps), return:
{"workflow": true, "steps": [
  {"action": "open_app", "target": "chrome"},
  {"action": "type_text", "text": "example.com"},
  {"action": "press_key", "key": "enter"}
]}

Rules:
- ONLY return valid JSON. No explanation, no markdown, no extra text.
- If the command is ambiguous, return {"action": "clarify", "message": "<what you need to know>"}.
- For "open" commands, map common names: "browser"/"chrome"/"firefox" → actual executable names.
- "click" without coordinates means click at current mouse position.
- For copy/paste/undo, use hotkey action with appropriate keys.
- Always pick the most specific action that matches the command.
- Use "workflow": true for commands that clearly require multiple steps.

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
- "show desktop" → {"action": "hotkey", "keys": ["win", "d"]}

Examples of multi-step workflows:
- "open chrome and search for weather" → workflow with: open chrome, type "weather", press enter
- "take a screenshot and open paint" → workflow with: screenshot, open paint
- "copy this and paste it in notepad" → workflow with: copy, open notepad, paste
"""


class GeminiProcessor:
    """Gemini API client for processing voice commands into actions"""

    def __init__(self):
        self._api_key = None
        self._model = None
        self._conversation = []
        self._available = False
        self._initialize()

    def _initialize(self):
        """Initialize Gemini API with API key from environment"""
        if not _HAS_GEMINI:
            logger.warning(
                "google-generativeai not installed. Gemini processor unavailable."
            )
            return

        # Get API key from environment variable
        api_key_env = config.gemini_api_key_env
        self._api_key = os.getenv(api_key_env)

        if not self._api_key:
            logger.warning(
                f"Gemini API key not found. Set {api_key_env} environment variable. "
                "Gemini processor will be unavailable."
            )
            return

        try:
            # Configure Gemini API
            genai.configure(api_key=self._api_key)

            # Initialize model
            generation_config = {
                "temperature": config.gemini_temperature,
                "max_output_tokens": config.gemini_max_tokens,
            }

            self._model = genai.GenerativeModel(
                model_name=config.gemini_model,
                generation_config=generation_config,
                system_instruction=GEMINI_SYSTEM_PROMPT,
            )

            self._available = True
            logger.info(f"Gemini processor initialized: {config.gemini_model}")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self._available = False

    def is_available(self) -> bool:
        """Check if Gemini processor is available"""
        return self._available

    def process_command(self, command_text: str) -> Dict[str, Any]:
        """
        Process a voice command and return action or workflow

        Args:
            command_text: The voice command text

        Returns:
            Dict with either single action or workflow
        """
        if not self._available:
            return {
                "action": "error",
                "message": "Gemini API not available. Check API key and internet connection.",
            }

        try:
            # Add command to conversation history (keep last 6 exchanges)
            messages = self._conversation[-6:]

            # Generate response
            response = self._model.generate_content(
                command_text, request_options={"timeout": config.gemini_timeout}
            )

            # Extract text from response
            if not response.text:
                return {"action": "error", "message": "Gemini returned empty response"}

            raw_response = response.text.strip()
            logger.info(f"Gemini raw response: {raw_response}")

            # Update conversation history
            self._conversation.append({"role": "user", "content": command_text})
            self._conversation.append({"role": "assistant", "content": raw_response})

            # Keep conversation history manageable
            if len(self._conversation) > 20:
                self._conversation = self._conversation[-12:]

            # Parse JSON response
            return self._parse_response(raw_response)

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"action": "error", "message": f"Gemini API error: {str(e)}"}

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini response into action dict

        Handles:
        - Plain JSON: {"action": "..."}
        - JSON in markdown code blocks: ```json {...} ```
        - Workflow responses: {"workflow": true, "steps": [...]}
        """
        text = response_text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines).strip()

        # Try to parse as JSON directly
        try:
            result = json.loads(text)
            if isinstance(result, dict):
                # Validate it has required fields
                if "workflow" in result and result["workflow"]:
                    # Multi-step workflow
                    if "steps" in result and isinstance(result["steps"], list):
                        return result
                    else:
                        return {
                            "action": "error",
                            "message": "Invalid workflow format: missing 'steps' array",
                        }
                elif "action" in result:
                    # Single action
                    return result
                else:
                    return {
                        "action": "error",
                        "message": "Response missing 'action' or 'workflow' field",
                    }
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from text (find first { to last })
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                result = json.loads(text[start : end + 1])
                if isinstance(result, dict) and (
                    "action" in result or "workflow" in result
                ):
                    return result
            except json.JSONDecodeError:
                pass

        # Failed to parse
        return {
            "action": "error",
            "message": f"Could not parse Gemini response as JSON: {text[:100]}",
        }

    def clear_history(self):
        """Clear conversation history"""
        self._conversation.clear()
        logger.info("Gemini conversation history cleared")

    def test_connection(self) -> tuple[bool, str]:
        """
        Test Gemini API connection

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self._available:
            return False, "Gemini API not initialized"

        try:
            # Simple test request
            response = self._model.generate_content(
                'Return only this JSON: {"action": "test"}',
                request_options={"timeout": 5},
            )

            if response.text:
                return True, f"Connected to Gemini ({config.gemini_model})"
            else:
                return False, "Gemini returned empty response"

        except Exception as e:
            return False, f"Connection test failed: {e}"
