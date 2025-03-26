import tkinter as tk
import mss
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
        self.screens = []
        self.active_monitor = None
        self._capture_windows = {}  # 记录各显示器的Toplevel窗口

    def show_set_capture_region(self):
        """显示截图区域选择窗口"""
        self.master.iconify()
        with mss.mss() as sct:
            self.screens = sct.monitors[1:]  # 第一个是全部屏幕, 所以跳过

        for monitor in self.screens:
            top = monitor["top"]
            left = monitor["left"]
            width = monitor["width"]
            height = monitor["height"]

            window = tk.Toplevel()
            window.geometry(f"{width}x{height}+{left}+{top}")
            window.attributes('-alpha', 0.3)
            window.attributes('-topmost', True)
            window.configure(bg='black')
            window.overrideredirect(True)
            canvas = tk.Canvas(window, cursor="cross", bg="black", highlightthickness=0)
            canvas.bind("<Enter>", lambda e, win=window: self._set_active_monitor(win))  # 鼠标进入该屏幕时激活
            canvas.bind("<ButtonPress-1>", self._on_button_press)
            canvas.bind("<B1-Motion>", self._on_mouse_drag)
            canvas.bind("<ButtonRelease-1>", self._on_button_release)
            canvas.pack(fill=tk.BOTH, expand=True)

            self._capture_windows[window] = canvas  # 记录窗口

    def _set_active_monitor(self, active_window):
        """激活鼠标所在的显示器窗口"""
        self.active_monitor = active_window

    def _on_button_press(self, event):
        """记录用户的截图起始点"""
        if not self.active_monitor:
            return
        self._canvas = self._capture_windows[self.active_monitor]
        self._start_x = self._canvas.canvasx(event.x)
        self._start_y = self._canvas.canvasy(event.y)
        self._rect = self._canvas.create_rectangle(self._start_x, self._start_y, self._start_x, self._start_y,
                                                   outline="red", width=3)

    def _on_mouse_drag(self, event):
        """绘制截图选框"""
        if not self._canvas or not self._rect:
            return
        cur_x = self._canvas.canvasx(event.x)
        cur_y = self._canvas.canvasy(event.y)
        self._canvas.coords(self._rect, self._start_x, self._start_y, cur_x, cur_y)

    def _on_button_release(self, event):
        """用户释放鼠标，确定截图区域"""
        if not self._canvas or not self.active_monitor:
            return
        end_x = self._canvas.canvasx(event.x)
        end_y = self._canvas.canvasy(event.y)

        monitor_index = list(self._capture_windows.keys()).index(self.active_monitor)
        monitor = self.screens[monitor_index]

        # 计算相对整个屏幕的坐标
        self.region = (
            int(min(self._start_x, end_x) + monitor["left"]),
            int(min(self._start_y, end_y) + monitor["top"]),
            int(max(self._start_x, end_x) + monitor["left"]),
            int(max(self._start_y, end_y) + monitor["top"])
        )

        # 清理窗口
        for win in self._capture_windows.keys():
            win.destroy()
        self._capture_windows.clear()
        self.master.deiconify()
        self.callback(self.region)

    def capture(self):
        return ImageGrab.grab(bbox=self.region, all_screens=True)
