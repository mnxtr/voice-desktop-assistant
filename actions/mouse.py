import logging
from config import config

logger = logging.getLogger(__name__)

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except Exception as e:
    logger.warning("pyautogui not available: %s", e)
    pyautogui = None


def click(button="left", x=None, y=None):
    try:
        if x is not None and y is not None:
            pyautogui.click(x=int(x), y=int(y), button=button)
            return True, f"Clicked {button} at ({x}, {y})"
        elif button == "double":
            pyautogui.doubleClick()
            return True, "Double clicked"
        elif button == "right":
            pyautogui.rightClick()
            return True, "Right clicked"
        else:
            pyautogui.click()
            return True, "Clicked"
    except Exception as e:
        logger.error("Click failed: %s", e)
        return False, f"Click failed: {e}"


def move(direction, distance=100):
    distance = int(distance)
    dx, dy = 0, 0
    direction = direction.lower()

    if direction == "up":
        dy = -distance
    elif direction == "down":
        dy = distance
    elif direction == "left":
        dx = -distance
    elif direction == "right":
        dx = distance
    else:
        return False, f"Unknown direction: {direction}"

    try:
        pyautogui.moveRel(dx, dy, duration=config.mouse_move_speed)
        return True, f"Moved mouse {direction} by {distance}px"
    except Exception as e:
        logger.error("Move failed: %s", e)
        return False, f"Move failed: {e}"


def move_to(x, y):
    try:
        pyautogui.moveTo(int(x), int(y), duration=config.mouse_move_speed)
        return True, f"Moved mouse to ({x}, {y})"
    except Exception as e:
        logger.error("Move to failed: %s", e)
        return False, f"Move to failed: {e}"


def scroll(direction="down", amount=3):
    amount = int(amount)
    try:
        if direction in ("up",):
            pyautogui.scroll(amount)
        elif direction in ("down",):
            pyautogui.scroll(-amount)
        elif direction in ("left",):
            pyautogui.hscroll(-amount)
        elif direction in ("right",):
            pyautogui.hscroll(amount)
        else:
            return False, f"Unknown scroll direction: {direction}"
        return True, f"Scrolled {direction} by {amount}"
    except Exception as e:
        logger.error("Scroll failed: %s", e)
        return False, f"Scroll failed: {e}"


def get_position():
    pos = pyautogui.position()
    return pos.x, pos.y


def get_screen_size():
    size = pyautogui.size()
    return size.width, size.height
