import tkinter as tk
from PIL import ImageGrab

class CaptureRegion:
    def __init__(self, master, callback):
        self.master = master
        self.callback = callback
        self.region = (0, 0, 100, 100)
        self._capture_window = None
        self._canvas = None
        self._start_x = 0
        self._start_y = 0
        self._rect = None

    def show_set_capture_region(self):
        self.master.iconify()
        self._capture_window = tk.Toplevel()
        self._capture_window.attributes('-fullscreen', True)
        self._capture_window.attributes('-alpha', 0.3)
        self._capture_window.attributes('-topmost', True)
        self._capture_window.configure(bg='black')
        self._canvas = tk.Canvas(self._capture_window, cursor="cross", bg="black", highlightthickness=0)

        self._canvas.bind("<ButtonPress-1>", self._on_button_press)
        self._canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_button_release)
        self._canvas.pack(fill=tk.BOTH, expand=True)

    def _on_button_press(self, event):
        self._start_x = self._canvas.canvasx(event.x)
        self._start_y = self._canvas.canvasy(event.y)
        self._rect = self._canvas.create_rectangle(self._start_x, self._start_y, self._start_x, self._start_y,
                                                   outline="red",
                                                   width=3)

    def _on_mouse_drag(self, event):
        cur_x = self._canvas.canvasx(event.x)
        cur_y = self._canvas.canvasy(event.y)
        self._canvas.coords(self._rect, self._start_x, self._start_y, cur_x, cur_y)

    def _on_button_release(self, event):
        end_x = self._canvas.canvasx(event.x)
        end_y = self._canvas.canvasy(event.y)
        self.region = (int(min(self._start_x, end_x)),
                       int(min(self._start_y, end_y)),
                       int(max(self._start_x, end_x)),
                       int(max(self._start_y, end_y)))
        self._capture_window.withdraw()
        self._capture_window.update()
        if self._canvas is not None:
            self._canvas.destroy()
        self.master.deiconify()
        if self._capture_window is not None:
            self._capture_window.destroy()
        self.callback(self.region)

    def capture(self):
        return ImageGrab.grab(bbox=self.region)
