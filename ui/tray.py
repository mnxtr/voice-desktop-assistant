import threading
import logging
import sys

logger = logging.getLogger(__name__)


def _create_icon_image():
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill=(76, 175, 80, 255))
    draw.ellipse([18, 18, 46, 46], fill=(255, 255, 255, 255))
    draw.ellipse([24, 24, 40, 40], fill=(33, 150, 243, 255))
    return img


class SystemTray:
    def __init__(self, on_quit, on_toggle_listening, on_toggle_gaze, on_show_help):
        self._on_quit = on_quit
        self._on_toggle_listening = on_toggle_listening
        self._on_toggle_gaze = on_toggle_gaze
        self._on_show_help = on_show_help
        self._icon = None
        self._thread = None

    def _build_menu(self):
        import pystray
        return pystray.Menu(
            pystray.MenuItem("Toggle Listening", self._on_toggle_listening),
            pystray.MenuItem("Toggle Eye Tracking", self._on_toggle_gaze),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Help", self._on_show_help),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

    def _run(self):
        try:
            import pystray
            image = _create_icon_image()
            self._icon = pystray.Icon(
                "desktop_assistant",
                image,
                "Desktop LLM Assistant",
                menu=self._build_menu(),
            )
            self._icon.run()
        except Exception as e:
            logger.warning("System tray failed to start: %s", e)
            logger.info("Assistant is running without a tray icon. Use Ctrl+C to quit.")

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("System tray started")

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
        logger.info("System tray stopped")

    def notify(self, title, message):
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass
