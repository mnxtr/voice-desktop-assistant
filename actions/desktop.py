import subprocess
import logging
import sys

logger = logging.getLogger(__name__)

APP_ALIASES = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "browser": "chrome.exe",
    "firefox": "firefox.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "files": "explorer.exe",
    "terminal": "wt.exe",
    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "task manager": "taskmgr.exe",
    "settings": "ms-settings:",
    "paint": "mspaint.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "outlook": "outlook.exe",
    "teams": "teams.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "slack": "slack.exe",
    "vscode": "code.exe",
    "visual studio code": "code.exe",
    "code": "code.exe",
    "snipping tool": "snippingtool.exe",
}


def open_app(target):
    target_lower = target.lower().strip()
    executable = APP_ALIASES.get(target_lower, target)

    try:
        if executable.startswith("ms-"):
            subprocess.Popen(["start", executable], shell=True)
        else:
            subprocess.Popen(executable, shell=True)
        logger.info("Opened app: %s (%s)", target, executable)
        return True, f"Opening {target}"
    except Exception as e:
        logger.error("Failed to open %s: %s", target, e)
        return False, f"Could not open {target}: {e}"


def close_app(target):
    if sys.platform == "win32":
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            windows = desktop.windows()
            target_lower = target.lower()
            for win in windows:
                try:
                    title = win.window_text().lower()
                    if target_lower in title:
                        win.close()
                        logger.info("Closed window: %s", win.window_text())
                        return True, f"Closed {win.window_text()}"
                except Exception:
                    continue
            return False, f"No window found matching '{target}'"
        except ImportError:
            subprocess.run(["taskkill", "/fi", f"WINDOWTITLE eq *{target}*"], shell=True)
            return True, f"Attempted to close {target}"
    return False, "Close not supported on this platform"


def switch_window(target):
    if sys.platform == "win32":
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            windows = desktop.windows()
            target_lower = target.lower()
            for win in windows:
                try:
                    title = win.window_text().lower()
                    if target_lower in title:
                        win.set_focus()
                        logger.info("Switched to: %s", win.window_text())
                        return True, f"Switched to {win.window_text()}"
                except Exception:
                    continue
            return False, f"No window found matching '{target}'"
        except ImportError:
            return False, "pywinauto not available"
    return False, "Window switching not supported on this platform"


def minimize_window():
    if sys.platform == "win32":
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            fg = desktop.top_window()
            fg.minimize()
            return True, "Window minimized"
        except Exception as e:
            return False, f"Could not minimize: {e}"
    return False, "Not supported on this platform"


def maximize_window():
    if sys.platform == "win32":
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            fg = desktop.top_window()
            fg.maximize()
            return True, "Window maximized"
        except Exception as e:
            return False, f"Could not maximize: {e}"
    return False, "Not supported on this platform"


def restore_window():
    if sys.platform == "win32":
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            fg = desktop.top_window()
            fg.restore()
            return True, "Window restored"
        except Exception as e:
            return False, f"Could not restore: {e}"
    return False, "Not supported on this platform"


def list_windows():
    if sys.platform == "win32":
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            windows = desktop.windows()
            titles = []
            for win in windows:
                try:
                    title = win.window_text()
                    if title.strip():
                        titles.append(title)
                except Exception:
                    continue
            return titles
        except ImportError:
            return []
    return []
