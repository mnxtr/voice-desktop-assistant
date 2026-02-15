import logging

logger = logging.getLogger(__name__)

try:
    import pyautogui
    pyautogui.FAILSAFE = True
except Exception as e:
    logger.warning("pyautogui not available: %s", e)
    pyautogui = None

SAFE_HOTKEYS = {
    frozenset(["ctrl", "c"]),
    frozenset(["ctrl", "v"]),
    frozenset(["ctrl", "x"]),
    frozenset(["ctrl", "z"]),
    frozenset(["ctrl", "y"]),
    frozenset(["ctrl", "s"]),
    frozenset(["ctrl", "a"]),
    frozenset(["ctrl", "f"]),
    frozenset(["ctrl", "w"]),
    frozenset(["ctrl", "t"]),
    frozenset(["ctrl", "n"]),
    frozenset(["ctrl", "p"]),
    frozenset(["ctrl", "tab"]),
    frozenset(["ctrl", "shift", "tab"]),
    frozenset(["ctrl", "shift", "escape"]),
    frozenset(["alt", "tab"]),
    frozenset(["alt", "f4"]),
    frozenset(["alt", "left"]),
    frozenset(["alt", "right"]),
    frozenset(["win", "d"]),
    frozenset(["win", "e"]),
    frozenset(["win", "l"]),
    frozenset(["win", "r"]),
    frozenset(["win", "s"]),
    frozenset(["win", "tab"]),
    frozenset(["win", "shift", "s"]),
}

BLOCKED_HOTKEYS = {
    frozenset(["ctrl", "alt", "delete"]),
    frozenset(["alt", "f4", "ctrl"]),
}


def type_text(text, interval=0.03):
    try:
        pyautogui.typewrite(text, interval=interval) if text.isascii() else pyautogui.write(text)
        logger.info("Typed text: %s...", text[:30])
        return True, f"Typed: {text[:50]}{'...' if len(text) > 50 else ''}"
    except Exception as e:
        logger.error("Type failed: %s", e)
        return False, f"Type failed: {e}"


def press_key(key):
    try:
        key = key.lower().strip()
        pyautogui.press(key)
        logger.info("Pressed key: %s", key)
        return True, f"Pressed {key}"
    except Exception as e:
        logger.error("Key press failed: %s", e)
        return False, f"Key press failed: {e}"


def hotkey(keys):
    key_set = frozenset(k.lower().strip() for k in keys)

    if key_set in BLOCKED_HOTKEYS:
        msg = f"Hotkey {'+'.join(keys)} is blocked for safety"
        logger.warning(msg)
        return False, msg

    if key_set not in SAFE_HOTKEYS:
        logger.warning("Hotkey %s not in safe list, executing anyway", keys)

    try:
        normalized = [k.lower().strip() for k in keys]
        pyautogui.hotkey(*normalized)
        combo = "+".join(normalized)
        logger.info("Pressed hotkey: %s", combo)
        return True, f"Pressed {combo}"
    except Exception as e:
        logger.error("Hotkey failed: %s", e)
        return False, f"Hotkey failed: {e}"
