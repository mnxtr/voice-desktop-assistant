import tkinter as tk
import time
import logging
import numpy as np

logger = logging.getLogger(__name__)


class GazeCalibrator:
    def __init__(self, tracker):
        self._tracker = tracker
        self._points = []
        self._gaze_samples = []
        self._current_samples = []
        self._sample_duration = 2.0
        self._result = None

    def _generate_calibration_points(self, screen_w, screen_h):
        margin_x = int(screen_w * 0.1)
        margin_y = int(screen_h * 0.1)
        return [
            (screen_w // 2, screen_h // 2),
            (margin_x, margin_y),
            (screen_w - margin_x, margin_y),
            (margin_x, screen_h - margin_y),
            (screen_w - margin_x, screen_h - margin_y),
            (screen_w // 2, margin_y),
            (screen_w // 2, screen_h - margin_y),
            (margin_x, screen_h // 2),
            (screen_w - margin_x, screen_h // 2),
        ]

    def run_calibration(self):
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.attributes("-topmost", True)
        root.configure(bg="black")

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        self._points = self._generate_calibration_points(screen_w, screen_h)
        self._gaze_samples = []

        canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        label = canvas.create_text(
            screen_w // 2, 30,
            text="Look at each dot and hold your gaze steady. Press ESC to cancel.",
            fill="white",
            font=("Arial", 16),
        )

        current_point_idx = [0]
        dot = [None]
        ring = [None]
        collecting = [False]
        samples = [[]]

        def _on_gaze(x, y):
            if collecting[0]:
                samples[0].append((x, y))

        original_callback = self._tracker._on_gaze_callback
        self._tracker.set_callback(_on_gaze)

        def show_next_point():
            idx = current_point_idx[0]
            if idx >= len(self._points):
                self._compute_calibration(screen_w, screen_h)
                self._tracker.set_callback(original_callback)
                root.destroy()
                return

            px, py = self._points[idx]

            if dot[0]:
                canvas.delete(dot[0])
            if ring[0]:
                canvas.delete(ring[0])

            ring[0] = canvas.create_oval(
                px - 25, py - 25, px + 25, py + 25,
                outline="white", width=2,
            )
            dot[0] = canvas.create_oval(
                px - 8, py - 8, px + 8, py + 8,
                fill="red", outline="red",
            )

            canvas.itemconfig(label, text=f"Point {idx + 1}/{len(self._points)} - Look at the red dot")

            samples[0] = []
            collecting[0] = True
            root.after(int(self._sample_duration * 1000), lambda: finish_point())

        def finish_point():
            collecting[0] = False
            self._gaze_samples.append(list(samples[0]))
            current_point_idx[0] += 1
            root.after(500, show_next_point)

        def on_escape(event):
            self._tracker.set_callback(original_callback)
            self._result = None
            root.destroy()

        root.bind("<Escape>", on_escape)
        root.after(1000, show_next_point)
        root.mainloop()

        return self._result

    def _compute_calibration(self, screen_w, screen_h):
        if len(self._gaze_samples) < 5:
            logger.warning("Not enough calibration points")
            self._result = None
            return

        target_xs = []
        target_ys = []
        gaze_xs = []
        gaze_ys = []

        for i, (tx, ty) in enumerate(self._points[:len(self._gaze_samples)]):
            samples = self._gaze_samples[i]
            if len(samples) < 5:
                continue
            trimmed = samples[len(samples) // 4:]
            avg_gx = np.mean([s[0] for s in trimmed])
            avg_gy = np.mean([s[1] for s in trimmed])
            target_xs.append(tx)
            target_ys.append(ty)
            gaze_xs.append(avg_gx)
            gaze_ys.append(avg_gy)

        if len(target_xs) < 3:
            self._result = None
            return

        target_xs = np.array(target_xs)
        target_ys = np.array(target_ys)
        gaze_xs = np.array(gaze_xs)
        gaze_ys = np.array(gaze_ys)

        gaze_range_x = gaze_xs.max() - gaze_xs.min()
        gaze_range_y = gaze_ys.max() - gaze_ys.min()
        target_range_x = target_xs.max() - target_xs.min()
        target_range_y = target_ys.max() - target_ys.min()

        if gaze_range_x > 0:
            scale_x = target_range_x / gaze_range_x
        else:
            scale_x = 1.0

        if gaze_range_y > 0:
            scale_y = target_range_y / gaze_range_y
        else:
            scale_y = 1.0

        offset_x = np.mean(target_xs) - np.mean(gaze_xs) * scale_x
        offset_y = np.mean(target_ys) - np.mean(gaze_ys) * scale_y

        self._result = {
            "offset_x": float(offset_x),
            "offset_y": float(offset_y),
            "scale_x": float(scale_x * screen_w),
            "scale_y": float(scale_y * screen_h),
        }

        logger.info("Calibration complete: %s", self._result)
