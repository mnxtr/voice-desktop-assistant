import threading
import queue
import logging
from config import config

logger = logging.getLogger(__name__)

try:
    import pyttsx3
    _HAS_TTS = True
except Exception:
    pyttsx3 = None
    _HAS_TTS = False


class Speaker:
    def __init__(self):
        self._queue = queue.Queue()
        self._running = False
        self._thread = None
        self._engine = None
        self._available = _HAS_TTS

    def _init_engine(self):
        if not _HAS_TTS:
            logger.warning("TTS not available, speaker will only log output")
            return
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", config.voice_rate)
            self._engine.setProperty("volume", config.voice_volume)
            voices = self._engine.getProperty("voices")
            if voices:
                self._engine.setProperty("voice", voices[0].id)
        except Exception as e:
            logger.error("Failed to init TTS engine: %s", e)
            self._engine = None

    def _speak_loop(self):
        self._init_engine()
        while self._running:
            try:
                text = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if text is None:
                break
            try:
                logger.info("Speaking: %s", text)
                if self._engine:
                    self._engine.say(text)
                    self._engine.runAndWait()
            except Exception as e:
                logger.error("TTS error: %s", e)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._speak_loop, daemon=True)
        self._thread.start()
        logger.info("Speaker started")

    def stop(self):
        self._running = False
        self._queue.put(None)
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None
        logger.info("Speaker stopped")

    def say(self, text):
        self._queue.put(text)

    def say_immediate(self, text):
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        self._queue.put(text)
