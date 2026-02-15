import subprocess
import logging
import sys

logger = logging.getLogger(__name__)

try:
    import pyautogui
except Exception as e:
    logger.warning("pyautogui not available: %s", e)
    pyautogui = None


def volume_control(level):
    if sys.platform != "win32":
        return False, "Volume control only supported on Windows"

    level = level.lower().strip()
    try:
        if level == "up":
            for _ in range(5):
                pyautogui.press("volumeup")
            return True, "Volume increased"
        elif level == "down":
            for _ in range(5):
                pyautogui.press("volumedown")
            return True, "Volume decreased"
        elif level == "mute":
            pyautogui.press("volumemute")
            return True, "Volume muted"
        elif level == "unmute":
            pyautogui.press("volumemute")
            return True, "Volume unmuted"
        else:
            return False, f"Unknown volume level: {level}"
    except Exception as e:
        return False, f"Volume control failed: {e}"


def take_screenshot():
    try:
        import datetime
        from pathlib import Path
        screenshots_dir = Path.home() / "Pictures" / "Screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = screenshots_dir / f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(str(filepath))
        logger.info("Screenshot saved: %s", filepath)
        return True, f"Screenshot saved to {filepath}"
    except Exception as e:
        logger.error("Screenshot failed: %s", e)
        return False, f"Screenshot failed: {e}"


def lock_screen():
    if sys.platform == "win32":
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            return True, "Screen locked"
        except Exception as e:
            return False, f"Lock failed: {e}"
    return False, "Lock screen only supported on Windows"


def search(query):
    if sys.platform == "win32":
        try:
            pyautogui.hotkey("win", "s")
            pyautogui.sleep(0.5)
            pyautogui.typewrite(query, interval=0.03)
            return True, f"Searching for: {query}"
        except Exception as e:
            return False, f"Search failed: {e}"
    return False, "Search only supported on Windows"
