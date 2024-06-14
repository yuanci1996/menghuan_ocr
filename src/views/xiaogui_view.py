from PIL import Image, ImageTk, ImageDraw, ImageGrab
import ttkbootstrap as tk
import logging
from src.controllers.xiaogui_controller import XiaoGuiController
from src.models.xiaogui import XiaoGui
import base64
import io

logger = logging.getLogger()

axis_space = 10
coordinate_scale = 50
border_size = 50


def draw_coordinate_x(draw: ImageDraw, start_x, start_y, coordinate_scale_x):
    draw.line(
        (start_x, start_y, start_x, start_y + axis_space),
        fill="black", width=2)
    draw.text(
        (start_x, start_y + axis_space),
        str(coordinate_scale_x), fill="black")


def draw_coordinate_y(draw: ImageDraw, start_x, start_y, coordinate_scale_y):
    draw.line(
        (start_x, start_y, border_size - axis_space, start_y),
        fill="black", width=2)
    draw.text(
        (start_x - axis_space * 3, start_y - axis_space),
        str(coordinate_scale_y), fill="black")


def draw_coordinate(xiao_gui_info: XiaoGui):
    image = Image.open(xiao_gui_info.map_info.image_path).convert("RGBA")
    background_image = Image.new('RGBA',
                                 (image.width + 2 * border_size,
                                  image.height + 2 * border_size),
                                 (255, 255, 255, 0))
    background_image.paste(image, (border_size, border_size), image)
    draw = ImageDraw.Draw(background_image)
    scale_width = xiao_gui_info.map_info.scale_width
    scale_height = xiao_gui_info.map_info.scale_height
    map_width = xiao_gui_info.map_info.width
    map_height = xiao_gui_info.map_info.height
    # 绘制地图x轴
    for i in range(0, map_width, coordinate_scale):
        start_x = border_size + i / scale_width
        start_y = border_size + image.height
        draw_coordinate_x(draw, start_x, start_y, i)
    # 绘制地图x轴末尾
    if map_width % coordinate_scale != 0:
        start_x = border_size + map_width / scale_width
        start_y = border_size + image.height
        draw_coordinate_x(draw, start_x, start_y, map_width)
    # 绘制地图y轴
    for i in range(0, map_height, coordinate_scale):
        start_x = border_size
        start_y = border_size + image.height - i / scale_height
        draw_coordinate_y(draw, start_x, start_y, i)
    # 绘制地图y轴末尾
    if map_height % coordinate_scale != 0:
        start_x = border_size
        start_y = border_size + image.height - map_height / scale_height
        draw_coordinate_y(draw, start_x, start_y, map_height)

    # 绘制圆
    position_area_image = Image.new('RGBA',
                                    (image.width + 2 * border_size,
                                     image.height + 2 * border_size),
                                    (255, 255, 255, 0))
    position_area_draw = ImageDraw.Draw(position_area_image)
    x = xiao_gui_info.x / xiao_gui_info.map_info.scale_width + border_size
    y = xiao_gui_info.map_info.image_height + border_size - xiao_gui_info.y / xiao_gui_info.map_info.scale_height
    r = 50 / ((xiao_gui_info.map_info.scale_width + xiao_gui_info.map_info.scale_height) / 2)
    position_area_draw.ellipse((x - r, y - r, x + r, y + r), outline="red", width=3)
    # 绘制区域象限
    if xiao_gui_info.position_area:
        for quadrant in xiao_gui_info.position_area:
            if quadrant == 1:
                # 第一象限：右上
                position_area_draw.pieslice((x - r, y - r, x + r, y + r), start=270, end=360,
                                            fill=xiao_gui_info.map_info.area_color)
            elif quadrant == 2:
                # 第二象限：左上
                position_area_draw.pieslice((x - r, y - r, x + r, y + r), start=180, end=270,
                                            fill=xiao_gui_info.map_info.area_color)
            elif quadrant == 3:
                # 第三象限：左下
                position_area_draw.pieslice((x - r, y - r, x + r, y + r), start=90, end=180,
                                            fill=xiao_gui_info.map_info.area_color)
            elif quadrant == 4:
                # 第四象限：右下
                position_area_draw.pieslice((x - r, y - r, x + r, y + r), start=0, end=90,
                                            fill=xiao_gui_info.map_info.area_color)
    return Image.alpha_composite(background_image, position_area_image)


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


class XiaoGuiView(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self._master = master
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        self.controller = XiaoGuiController()
        self.canvas = None
        self._capture_label = None
        self.photo = None
        self.show_button = None
        self.set_capture_region_button = None
        self.capture_region_button = None
        self._capture_window = None
        self._canvas = None
        self.region = (0, 0, 100, 100)

    def create_widgets(self):
        button_frame = tk.Frame(self)
        button_frame.pack()
        self.show_button = tk.Button(button_frame, text="获取坐标", command=self.show_position)
        self.show_button.pack(side="left", padx=5, pady=5)
        self.set_capture_region_button = tk.Button(button_frame, text="设置截图范围", command=self.show_set_capture_region)
        self.set_capture_region_button.pack(side="left", padx=5, pady=5)

    def show_position(self):
        self.capture()
        xiao_gui_info = self.controller.show_position(image_to_base64(self._capture_label_image))
        print(xiao_gui_info)

        if self.canvas is not None:
            self.canvas.destroy()
        if xiao_gui_info is not None:
            # 绘制坐标轴
            image = draw_coordinate(xiao_gui_info)
            self.photo = ImageTk.PhotoImage(image)
            self.canvas = tk.Canvas(self, width=image.width, height=image.height)
            self.canvas.pack()
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def show_set_capture_region(self):
        self._master.iconify()
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
        self._master.deiconify()
        if self._capture_window is not None:
            self._capture_window.destroy()
        self.capture()

    def capture(self):
        self._capture_label_image = ImageGrab.grab(bbox=self.region)
        self._capture_label_photo = ImageTk.PhotoImage(self._capture_label_image)
        if self._capture_label is not None:
            self._capture_label.destroy()
        self._capture_label = tk.Label(self, image=self._capture_label_photo)
        self._capture_label.pack()
