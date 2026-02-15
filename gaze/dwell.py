import time
import math
import threading
import logging
from config import config

logger = logging.getLogger(__name__)


class DwellClicker:
    def __init__(self, click_callback):
        self._click_callback = click_callback
        self._dwell_time = config.dwell_time
        self._dwell_radius = 40
        self._last_x = 0
        self._last_y = 0
        self._dwell_start = None
        self._running = False
        self._thread = None
        self._enabled = True
        self._on_progress_callback = None

    def set_progress_callback(self, callback):
        self._on_progress_callback = callback

    def update_gaze(self, x, y):
        if not self._enabled:
            return

        dist = math.hypot(x - self._last_x, y - self._last_y)

        if dist > self._dwell_radius:
            self._last_x = x
            self._last_y = y
            self._dwell_start = time.time()
            if self._on_progress_callback:
                self._on_progress_callback(0, x, y)
            return

        if self._dwell_start is None:
            self._dwell_start = time.time()

        elapsed = time.time() - self._dwell_start
        progress = min(1.0, elapsed / self._dwell_time)

        if self._on_progress_callback:
            self._on_progress_callback(progress, x, y)

        if elapsed >= self._dwell_time:
            logger.info("Dwell click at (%d, %d)", x, y)
            self._click_callback(x, y)
            self._dwell_start = None
            if self._on_progress_callback:
                self._on_progress_callback(0, x, y)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if not value:
            self._dwell_start = None

    @property
    def dwell_time(self):
        return self._dwell_time

    @dwell_time.setter
    def dwell_time(self, value):
        self._dwell_time = max(0.3, value)
