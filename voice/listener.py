import json
import queue
import threading
import logging
from config import config

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
    _HAS_AUDIO = True
except OSError as e:
    logger.warning("Audio system not available: %s", e)
    sd = None
    _HAS_AUDIO = False

try:
    from vosk import Model, KaldiRecognizer
    _HAS_VOSK = True
except ImportError:
    logger.warning("Vosk not available")
    Model = None
    KaldiRecognizer = None
    _HAS_VOSK = False


class VoiceListener:
    def __init__(self, on_command_callback):
        self._callback = on_command_callback
        self._audio_queue = queue.Queue()
        self._running = False
        self._listening = False
        self._wake_word = config.wake_word.lower()
        self._model = None
        self._recognizer = None
        self._stream = None
        self._thread = None

    def _load_model(self):
        model_path = config.vosk_model_path
        logger.info("Loading Vosk model from %s", model_path)
        try:
            self._model = Model(model_path)
        except Exception:
            logger.info("Local model not found, downloading small English model...")
            try:
                self._model = Model(lang="en-us")
            except Exception as e:
                logger.error("Failed to load Vosk model: %s", e)
                self._model = None
                return
        self._recognizer = KaldiRecognizer(self._model, config.sample_rate)

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            logger.warning("Audio status: %s", status)
        self._audio_queue.put(bytes(indata))

    def _process_loop(self):
        while self._running:
            try:
                data = self._audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if self._recognizer.AcceptWaveform(data):
                result = json.loads(self._recognizer.Result())
                text = result.get("text", "").strip().lower()
                if text:
                    self._handle_text(text)
            else:
                partial = json.loads(self._recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip().lower()
                if partial_text and self._wake_word in partial_text:
                    self._listening = True

    def _handle_text(self, text):
        if self._listening:
            command = text
            for ww in [self._wake_word]:
                command = command.replace(ww, "").strip()
            if command:
                logger.info("Command received: %s", command)
                self._listening = False
                self._callback(command)
            return

        if self._wake_word in text:
            command = text.split(self._wake_word, 1)[-1].strip()
            if command:
                logger.info("Wake word + command: %s", command)
                self._callback(command)
            else:
                self._listening = True
                logger.info("Wake word detected, listening for command...")

    def start(self):
        if self._running:
            return
        if not _HAS_AUDIO or not _HAS_VOSK:
            logger.error(
                "Voice listener cannot start: audio=%s vosk=%s. "
                "Install PortAudio (libportaudio2) and vosk to enable voice.",
                _HAS_AUDIO, _HAS_VOSK,
            )
            return
        self._load_model()
        if not self._model:
            logger.error("Voice listener cannot start: speech model failed to load")
            return
        self._running = True
        self._stream = sd.RawInputStream(
            samplerate=config.sample_rate,
            blocksize=config.audio_block_size,
            dtype="int16",
            channels=1,
            callback=self._audio_callback,
        )
        self._stream.start()
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        logger.info("Voice listener started (wake word: '%s')", self._wake_word)

    def stop(self):
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
        logger.info("Voice listener stopped")

    @property
    def is_listening(self):
        return self._listening

    @property
    def is_running(self):
        return self._running
