import sys
import os
import signal
import logging
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.makedirs(os.path.expanduser("~/.desktop_llm_assistant"), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.expanduser("~"), ".desktop_llm_assistant", "assistant.log")),
    ],
)
logger = logging.getLogger("main")

from config import config
from voice.listener import VoiceListener
from voice.speaker import Speaker
from llm.processor import LLMProcessor
from gaze.tracker import GazeTracker
from gaze.calibration import GazeCalibrator
from gaze.dwell import DwellClicker

mouse = None
desktop = None
keyboard = None
system = None

try:
    from actions import desktop as _desktop
    desktop = _desktop
except Exception as e:
    logger.warning("Desktop actions not available: %s", e)

try:
    from actions import mouse as _mouse
    mouse = _mouse
except Exception as e:
    logger.warning("Mouse actions not available: %s", e)

try:
    from actions import keyboard as _keyboard
    keyboard = _keyboard
except Exception as e:
    logger.warning("Keyboard actions not available: %s", e)

try:
    from actions import system as _system
    system = _system
except Exception as e:
    logger.warning("System actions not available: %s", e)

try:
    from ui.overlay import StatusOverlay
    _HAS_OVERLAY = True
except Exception as e:
    logger.warning("Overlay UI not available: %s", e)
    _HAS_OVERLAY = False
    StatusOverlay = None

try:
    from ui.tray import SystemTray
    _HAS_TRAY = True
except Exception as e:
    logger.warning("System tray not available: %s", e)
    _HAS_TRAY = False
    SystemTray = None


class DummyOverlay:
    def start(self): pass
    def stop(self): pass
    def set_state(self, s): logger.info("State: %s", s)
    def set_command(self, c): logger.info("Command: %s", c)
    def set_result(self, r): logger.info("Result: %s", r)
    def show_grid(self): pass
    def hide_grid(self): pass
    def get_grid_cell_center(self, n): return None, None


class DesktopAssistant:
    def __init__(self):
        self._running = False
        self._speaker = Speaker()
        self._llm = LLMProcessor()
        self._overlay = StatusOverlay() if _HAS_OVERLAY else DummyOverlay()
        self._listener = None
        self._gaze_tracker = None
        self._dwell_clicker = None
        self._tray = None

    def _on_voice_command(self, command):
        logger.info("Voice command: %s", command)
        self._overlay.set_state("processing")
        self._overlay.set_command(command)

        threading.Thread(
            target=self._process_command,
            args=(command,),
            daemon=True,
        ).start()

    def _process_command(self, command):
        try:
            action = self._llm.process_command(command)
            logger.info("Action: %s", action)
            self._overlay.set_state("executing")
            success, message = self._execute_action(action)

            if success:
                self._overlay.set_result(message)
                self._speaker.say(message)
            else:
                self._overlay.set_state("error")
                self._overlay.set_result(message)
                self._speaker.say(message)

        except Exception as e:
            logger.error("Command processing error: %s", e)
            self._overlay.set_state("error")
            self._overlay.set_result(str(e))
            self._speaker.say(f"Error: {e}")

        time.sleep(1)
        self._overlay.set_state("idle")

    def _execute_action(self, action):
        act = action.get("action", "")

        if act in ("open_app", "close_app", "switch_window", "minimize_window",
                    "maximize_window", "restore_window") and not desktop:
            return False, "Desktop actions not available on this system"

        if act in ("mouse_click", "mouse_move", "mouse_move_to", "scroll",
                    "grid_click") and not mouse:
            return False, "Mouse actions not available on this system"

        if act in ("type_text", "dictate", "hotkey", "press_key") and not keyboard:
            return False, "Keyboard actions not available on this system"

        if act in ("volume", "screenshot", "lock_screen", "search") and not system:
            return False, "System actions not available on this system"

        if act == "open_app":
            return desktop.open_app(action.get("target", ""))

        elif act == "close_app":
            return desktop.close_app(action.get("target", ""))

        elif act == "switch_window":
            return desktop.switch_window(action.get("target", ""))

        elif act == "minimize_window":
            return desktop.minimize_window()

        elif act == "maximize_window":
            return desktop.maximize_window()

        elif act == "restore_window":
            return desktop.restore_window()

        elif act == "mouse_click":
            btn = action.get("button", "left")
            x = action.get("x")
            y = action.get("y")
            return mouse.click(button=btn, x=x, y=y)

        elif act == "mouse_move":
            direction = action.get("direction", "down")
            distance = action.get("distance", 100)
            return mouse.move(direction, distance)

        elif act == "mouse_move_to":
            return mouse.move_to(action.get("x", 0), action.get("y", 0))

        elif act == "scroll":
            direction = action.get("direction", "down")
            amount = action.get("amount", 3)
            return mouse.scroll(direction, amount)

        elif act == "type_text":
            return keyboard.type_text(action.get("text", ""))

        elif act == "dictate":
            return keyboard.type_text(action.get("text", ""))

        elif act == "hotkey":
            keys = action.get("keys", [])
            return keyboard.hotkey(keys)

        elif act == "press_key":
            return keyboard.press_key(action.get("key", ""))

        elif act == "show_grid":
            self._overlay.show_grid()
            return True, "Grid overlay shown. Say a number to click that cell."

        elif act == "grid_click":
            cell = action.get("cell", 1)
            cx, cy = self._overlay.get_grid_cell_center(cell)
            if cx is not None:
                self._overlay.hide_grid()
                return mouse.click(x=cx, y=cy)
            return False, f"Invalid grid cell: {cell}"

        elif act == "hide_grid":
            self._overlay.hide_grid()
            return True, "Grid hidden"

        elif act == "volume":
            return system.volume_control(action.get("level", "up"))

        elif act == "screenshot":
            return system.take_screenshot()

        elif act == "lock_screen":
            return system.lock_screen()

        elif act == "search":
            return system.search(action.get("query", ""))

        elif act == "start_gaze":
            return self._start_gaze_tracking()

        elif act == "stop_gaze":
            return self._stop_gaze_tracking()

        elif act == "calibrate_gaze":
            return self._calibrate_gaze()

        elif act == "help":
            return self._show_help()

        elif act == "stop":
            self._speaker.say("Goodbye")
            time.sleep(1)
            self.shutdown()
            return True, "Assistant stopping"

        elif act == "clarify":
            msg = action.get("message", "Could you please repeat that?")
            return True, msg

        elif act == "error":
            return False, action.get("message", "Unknown error")

        else:
            return False, f"Unknown action: {act}"

    def _start_gaze_tracking(self):
        if self._gaze_tracker and self._gaze_tracker.is_running:
            return True, "Eye tracking is already active"

        try:
            import pyautogui
            screen_w, screen_h = pyautogui.size()

            self._gaze_tracker = GazeTracker(screen_w, screen_h, smoothing=config.gaze_smoothing)
            self._dwell_clicker = DwellClicker(
                lambda x, y: mouse.click(x=x, y=y)
            )
            self._gaze_tracker.set_callback(self._on_gaze_update)
            self._gaze_tracker.start()
            self._overlay.set_state("gaze")
            return True, "Eye tracking started. Look at a spot to move cursor, dwell to click."
        except Exception as e:
            logger.error("Gaze tracking failed: %s", e)
            return False, f"Could not start eye tracking: {e}"

    def _stop_gaze_tracking(self):
        if self._gaze_tracker:
            self._gaze_tracker.stop()
            self._gaze_tracker = None
            self._dwell_clicker = None
        return True, "Eye tracking stopped"

    def _on_gaze_update(self, x, y):
        try:
            import pyautogui
            pyautogui.moveTo(x, y, _pause=False)
            if self._dwell_clicker:
                self._dwell_clicker.update_gaze(x, y)
        except Exception:
            pass

    def _calibrate_gaze(self):
        if not self._gaze_tracker or not self._gaze_tracker.is_running:
            success, msg = self._start_gaze_tracking()
            if not success:
                return False, msg
            time.sleep(1)

        try:
            self._speaker.say("Starting calibration. Look at each red dot.")
            calibrator = GazeCalibrator(self._gaze_tracker)
            result = calibrator.run_calibration()
            if result:
                self._gaze_tracker.set_calibration(result)
                return True, "Calibration complete"
            return False, "Calibration cancelled or failed"
        except Exception as e:
            return False, f"Calibration error: {e}"

    def _show_help(self):
        help_text = (
            "Available commands: open app, close app, switch window, "
            "click, scroll, type, copy, paste, undo, save, show grid, "
            "screenshot, volume up or down, lock screen, search, "
            "start or stop eye tracking, calibrate gaze, stop assistant"
        )
        return True, help_text

    def _on_toggle_listening(self, icon=None, item=None):
        if self._listener and self._listener.is_running:
            self._listener.stop()
            self._overlay.set_state("idle")
            self._overlay.set_result("Listening paused")
        else:
            self._listener = VoiceListener(self._on_voice_command)
            self._listener.start()
            self._overlay.set_state("idle")
            self._overlay.set_result("Listening resumed")

    def _on_toggle_gaze(self, icon=None, item=None):
        if self._gaze_tracker and self._gaze_tracker.is_running:
            self._stop_gaze_tracking()
        else:
            self._start_gaze_tracking()

    def _on_show_help(self, icon=None, item=None):
        _, msg = self._show_help()
        self._speaker.say(msg)

    def _on_quit(self, icon=None, item=None):
        self.shutdown()

    def _check_ollama(self):
        connected, has_model, models = self._llm.check_connection()
        if not connected:
            logger.warning("Ollama not running at %s", config.ollama_url)
            self._speaker.say("Warning: Cannot connect to Ollama. Please make sure it is running.")
            return False
        if not has_model:
            logger.warning("Model '%s' not found. Available: %s", config.ollama_model, models)
            self._speaker.say(
                f"Warning: Model {config.ollama_model} not found. "
                f"Please run ollama pull {config.ollama_model}"
            )
            return False
        logger.info("Ollama connected. Model: %s", config.ollama_model)
        return True

    def start(self):
        logger.info("Starting Desktop LLM Assistant...")
        self._running = True

        os.makedirs(os.path.expanduser("~/.desktop_llm_assistant"), exist_ok=True)

        self._speaker.start()
        self._overlay.start()
        time.sleep(0.5)

        if _HAS_TRAY and SystemTray:
            self._tray = SystemTray(
                on_quit=self._on_quit,
                on_toggle_listening=self._on_toggle_listening,
                on_toggle_gaze=self._on_toggle_gaze,
                on_show_help=self._on_show_help,
            )
            self._tray.start()
        else:
            logger.info("System tray not available, running without tray icon")

        self._check_ollama()

        self._listener = VoiceListener(self._on_voice_command)
        self._listener.start()

        self._speaker.say("Desktop assistant ready. Say hey assistant followed by your command.")
        self._overlay.set_state("idle")

        logger.info("Desktop Assistant is running")

        try:
            while self._running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            logger.info("Interrupted")
        finally:
            self.shutdown()

    def shutdown(self):
        if not self._running:
            return
        logger.info("Shutting down...")
        self._running = False

        if self._listener:
            self._listener.stop()
        if self._gaze_tracker:
            self._gaze_tracker.stop()

        self._speaker.stop()
        self._overlay.stop()

        if self._tray:
            self._tray.stop()

        logger.info("Shutdown complete")


def main():
    signal.signal(signal.SIGINT, lambda s, f: None)
    assistant = DesktopAssistant()
    assistant.start()


if __name__ == "__main__":
    main()
