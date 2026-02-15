import threading
import logging
import time
import numpy as np

logger = logging.getLogger(__name__)

try:
    import cv2
    import mediapipe as mp
    _HAS_GAZE_DEPS = True
except ImportError as e:
    logger.warning("Gaze dependencies not available: %s", e)
    cv2 = None
    mp = None
    _HAS_GAZE_DEPS = False

LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
LEFT_EYE_INNER = 362
LEFT_EYE_OUTER = 263
RIGHT_EYE_INNER = 133
RIGHT_EYE_OUTER = 33


class GazeTracker:
    def __init__(self, screen_width, screen_height, smoothing=5):
        self._screen_w = screen_width
        self._screen_h = screen_height
        self._smoothing = smoothing
        self._running = False
        self._thread = None
        self._cap = None
        self._gaze_x = screen_width // 2
        self._gaze_y = screen_height // 2
        self._history_x = []
        self._history_y = []
        self._calibration_data = None
        self._on_gaze_callback = None
        self._face_mesh = None

    def set_callback(self, callback):
        self._on_gaze_callback = callback

    def set_calibration(self, calibration_data):
        self._calibration_data = calibration_data

    def _init_mediapipe(self):
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def _get_iris_center(self, landmarks, iris_indices, img_w, img_h):
        points = []
        for idx in iris_indices:
            lm = landmarks[idx]
            points.append((lm.x * img_w, lm.y * img_h))
        points = np.array(points)
        return np.mean(points, axis=0)

    def _get_eye_width(self, landmarks, inner_idx, outer_idx, img_w, img_h):
        inner = landmarks[inner_idx]
        outer = landmarks[outer_idx]
        return abs((inner.x - outer.x) * img_w)

    def _estimate_gaze(self, landmarks, img_w, img_h):
        left_iris = self._get_iris_center(landmarks, LEFT_IRIS, img_w, img_h)
        right_iris = self._get_iris_center(landmarks, RIGHT_IRIS, img_w, img_h)

        left_eye_w = self._get_eye_width(landmarks, LEFT_EYE_INNER, LEFT_EYE_OUTER, img_w, img_h)
        right_eye_w = self._get_eye_width(landmarks, RIGHT_EYE_INNER, RIGHT_EYE_OUTER, img_w, img_h)

        left_inner = landmarks[LEFT_EYE_INNER]
        left_outer = landmarks[LEFT_EYE_OUTER]
        left_center_x = (left_inner.x + left_outer.x) / 2 * img_w
        left_center_y = (left_inner.y + left_outer.y) / 2 * img_h

        right_inner = landmarks[RIGHT_EYE_INNER]
        right_outer = landmarks[RIGHT_EYE_OUTER]
        right_center_x = (right_inner.x + right_outer.x) / 2 * img_w
        right_center_y = (right_inner.y + right_outer.y) / 2 * img_h

        if left_eye_w > 0:
            left_ratio_x = (left_iris[0] - left_center_x) / left_eye_w
        else:
            left_ratio_x = 0

        if right_eye_w > 0:
            right_ratio_x = (right_iris[0] - right_center_x) / right_eye_w
        else:
            right_ratio_x = 0

        avg_ratio_x = (left_ratio_x + right_ratio_x) / 2

        left_eye_h = left_eye_w * 0.4
        right_eye_h = right_eye_w * 0.4

        if left_eye_h > 0:
            left_ratio_y = (left_iris[1] - left_center_y) / left_eye_h
        else:
            left_ratio_y = 0

        if right_eye_h > 0:
            right_ratio_y = (right_iris[1] - right_center_y) / right_eye_h
        else:
            right_ratio_y = 0

        avg_ratio_y = (left_ratio_y + right_ratio_y) / 2

        if self._calibration_data:
            cal = self._calibration_data
            gaze_x = cal["offset_x"] + avg_ratio_x * cal["scale_x"]
            gaze_y = cal["offset_y"] + avg_ratio_y * cal["scale_y"]
        else:
            gaze_x = self._screen_w / 2 - avg_ratio_x * self._screen_w * 1.5
            gaze_y = self._screen_h / 2 + avg_ratio_y * self._screen_h * 1.5

        gaze_x = max(0, min(self._screen_w, gaze_x))
        gaze_y = max(0, min(self._screen_h, gaze_y))

        return gaze_x, gaze_y

    def _smooth(self, x, y):
        self._history_x.append(x)
        self._history_y.append(y)
        if len(self._history_x) > self._smoothing:
            self._history_x.pop(0)
            self._history_y.pop(0)

        weights = np.arange(1, len(self._history_x) + 1, dtype=float)
        weights /= weights.sum()

        smooth_x = np.average(self._history_x, weights=weights)
        smooth_y = np.average(self._history_y, weights=weights)
        return int(smooth_x), int(smooth_y)

    def _tracking_loop(self):
        self._init_mediapipe()
        self._cap = cv2.VideoCapture(0)
        if not self._cap.isOpened():
            logger.error("Cannot open webcam")
            self._running = False
            return

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self._cap.set(cv2.CAP_PROP_FPS, 30)

        logger.info("Gaze tracker started")

        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self._face_mesh.process(rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                h, w = frame.shape[:2]
                raw_x, raw_y = self._estimate_gaze(landmarks, w, h)
                self._gaze_x, self._gaze_y = self._smooth(raw_x, raw_y)

                if self._on_gaze_callback:
                    self._on_gaze_callback(self._gaze_x, self._gaze_y)

            time.sleep(0.016)

        self._cap.release()
        self._face_mesh.close()
        logger.info("Gaze tracker stopped")

    def start(self):
        if self._running:
            return
        if not _HAS_GAZE_DEPS:
            logger.error("Cannot start gaze tracker: mediapipe/opencv not available")
            return
        self._running = True
        self._thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None

    @property
    def gaze_position(self):
        return self._gaze_x, self._gaze_y

    @property
    def is_running(self):
        return self._running
