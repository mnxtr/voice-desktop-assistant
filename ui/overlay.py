import tkinter as tk
import threading
import logging
import time
from config import config

logger = logging.getLogger(__name__)


class StatusOverlay:
    STATES = {
        "idle": {"color": "#4CAF50", "text": "Ready"},
        "listening": {"color": "#2196F3", "text": "Listening..."},
        "processing": {"color": "#FF9800", "text": "Processing..."},
        "executing": {"color": "#9C27B0", "text": "Executing..."},
        "error": {"color": "#F44336", "text": "Error"},
        "gaze": {"color": "#00BCD4", "text": "Gaze Active"},
    }

    def __init__(self):
        self._root = None
        self._thread = None
        self._running = False
        self._state = "idle"
        self._last_command = ""
        self._last_result = ""
        self._canvas = None
        self._status_dot = None
        self._status_text = None
        self._command_text = None
        self._result_text = None
        self._grid_window = None
        self._grid_visible = False
        self._gaze_cursor_window = None

    def _create_window(self):
        self._root = tk.Tk()
        self._root.title("Desktop Assistant")
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", config.overlay_opacity)

        width = 320
        height = 100
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()

        pos = config.overlay_position
        if pos == "top-right":
            x = screen_w - width - 20
            y = 20
        elif pos == "top-left":
            x = 20
            y = 20
        elif pos == "bottom-right":
            x = screen_w - width - 20
            y = screen_h - height - 60
        elif pos == "bottom-left":
            x = 20
            y = screen_h - height - 60
        else:
            x = screen_w - width - 20
            y = 20

        self._root.geometry(f"{width}x{height}+{x}+{y}")

        self._canvas = tk.Canvas(
            self._root,
            width=width,
            height=height,
            bg="#1E1E1E",
            highlightthickness=1,
            highlightbackground="#333333",
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._status_dot = self._canvas.create_oval(10, 10, 26, 26, fill="#4CAF50")
        self._status_text = self._canvas.create_text(
            34, 18, text="Ready", fill="white", anchor="w", font=("Segoe UI", 11, "bold"),
        )
        self._command_text = self._canvas.create_text(
            10, 45, text="Say 'Hey Assistant' to start", fill="#AAAAAA", anchor="w",
            font=("Segoe UI", 9),
        )
        self._result_text = self._canvas.create_text(
            10, 70, text="", fill="#888888", anchor="w", font=("Segoe UI", 9),
        )

        self._root.bind("<Button-1>", self._start_drag)
        self._root.bind("<B1-Motion>", self._on_drag)

        self._drag_x = 0
        self._drag_y = 0

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        x = self._root.winfo_x() + event.x - self._drag_x
        y = self._root.winfo_y() + event.y - self._drag_y
        self._root.geometry(f"+{x}+{y}")

    def _update_display(self):
        if not self._running or not self._root:
            return

        state_info = self.STATES.get(self._state, self.STATES["idle"])
        self._canvas.itemconfig(self._status_dot, fill=state_info["color"])
        self._canvas.itemconfig(self._status_text, text=state_info["text"])

        cmd_display = self._last_command[:45] + "..." if len(self._last_command) > 45 else self._last_command
        self._canvas.itemconfig(self._command_text, text=cmd_display or "Say 'Hey Assistant' to start")

        res_display = self._last_result[:45] + "..." if len(self._last_result) > 45 else self._last_result
        self._canvas.itemconfig(self._result_text, text=res_display)

        self._root.after(100, self._update_display)

    def _run(self):
        self._create_window()
        self._update_display()
        self._root.mainloop()

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Status overlay started")

    def stop(self):
        self._running = False
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass
        if self._grid_window:
            self.hide_grid()

    def set_state(self, state):
        self._state = state

    def set_command(self, command):
        self._last_command = command

    def set_result(self, result):
        self._last_result = result

    def show_grid(self):
        if self._grid_visible:
            return

        def _create_grid():
            self._grid_window = tk.Toplevel()
            self._grid_window.attributes("-fullscreen", True)
            self._grid_window.attributes("-topmost", True)
            self._grid_window.attributes("-alpha", 0.3)
            self._grid_window.configure(bg="black")

            screen_w = self._grid_window.winfo_screenwidth()
            screen_h = self._grid_window.winfo_screenheight()

            canvas = tk.Canvas(
                self._grid_window, width=screen_w, height=screen_h,
                bg="black", highlightthickness=0,
            )
            canvas.pack()

            rows = config.grid_rows
            cols = config.grid_cols
            cell_w = screen_w / cols
            cell_h = screen_h / rows

            cell_num = 1
            for r in range(rows):
                for c in range(cols):
                    x1 = c * cell_w
                    y1 = r * cell_h
                    x2 = x1 + cell_w
                    y2 = y1 + cell_h

                    canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=2)

                    cx = x1 + cell_w / 2
                    cy = y1 + cell_h / 2
                    canvas.create_text(
                        cx, cy, text=str(cell_num), fill="yellow",
                        font=("Arial", 48, "bold"),
                    )
                    cell_num += 1

            self._grid_window.bind("<Escape>", lambda e: self.hide_grid())
            self._grid_visible = True
            logger.info("Grid overlay shown")

        if self._root:
            self._root.after(0, _create_grid)

    def hide_grid(self):
        if self._grid_window:
            try:
                self._grid_window.destroy()
            except Exception:
                pass
            self._grid_window = None
        self._grid_visible = False
        logger.info("Grid overlay hidden")

    def get_grid_cell_center(self, cell_number):
        if not self._root:
            return None, None

        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        rows = config.grid_rows
        cols = config.grid_cols

        cell_number = int(cell_number)
        if cell_number < 1 or cell_number > rows * cols:
            return None, None

        idx = cell_number - 1
        row = idx // cols
        col = idx % cols

        cell_w = screen_w / cols
        cell_h = screen_h / rows

        cx = int(col * cell_w + cell_w / 2)
        cy = int(row * cell_h + cell_h / 2)
        return cx, cy

    def show_gaze_cursor(self, x, y):
        pass

    def update_gaze_cursor(self, x, y):
        pass

    def hide_gaze_cursor(self):
        pass
