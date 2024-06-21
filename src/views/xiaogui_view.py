from PIL import Image, ImageTk, ImageDraw, ImageGrab
import ttkbootstrap as tk
import logging
from src.controllers.xiaogui_controller import XiaoGuiController
from src.models.xiaogui import XiaoGui
import base64
import io
from src import utils
from src.views.capture_region import CaptureRegion

logger = logging.getLogger()


def draw_coordinate(xiao_gui_info: XiaoGui):
    # 绘制圆
    position_area_image = Image.new('RGBA',
                                    (xiao_gui_info.map_info.image_width + 2 * xiao_gui_info.map_info.border_size,
                                     xiao_gui_info.map_info.image_height + 2 * xiao_gui_info.map_info.border_size),
                                    (255, 255, 255, 0))
    position_area_draw = ImageDraw.Draw(position_area_image)
    x = xiao_gui_info.x / xiao_gui_info.map_info.scale_width + xiao_gui_info.map_info.border_size
    y = xiao_gui_info.map_info.image_height + xiao_gui_info.map_info.border_size - xiao_gui_info.y / xiao_gui_info.map_info.scale_height
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
    return Image.alpha_composite(xiao_gui_info.map_info.background_image, position_area_image)


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


def validate_input(new_value):
    # 验证函数，确保输入的是数字
    if new_value.isdigit() or new_value == "":
        return True
    else:
        return False


class XiaoGuiView(tk.Frame):
    def __init__(self, master=None, layout=None):
        super().__init__(layout)
        self.master = master
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
        # 实例化 CaptureRegion
        self.capture_region = CaptureRegion(self.master, self.on_capture_region_set)
        button_frame = tk.Frame(self)
        button_frame.pack()
        self.show_button = tk.Button(button_frame, text="OCR获取坐标", command=self.show_position)
        self.show_button.pack(side="left", padx=5, pady=5)
        self.show_button = tk.Button(button_frame, text="手动生成坐标", command=self.build_position)
        self.show_button.pack(side="left", padx=5, pady=5)
        self.set_capture_region_button = tk.Button(button_frame, text="设置截图范围",
                                                   command=self.capture_region.show_set_capture_region)
        self.set_capture_region_button.pack(side="left", padx=5, pady=5)

        position_map_frame = tk.Frame(self)
        position_map_frame.pack()
        self.map_var = tk.StringVar(value="傲来国")
        for map_name, map_info in utils.map_util.map_infos.items():
            radio = tk.Radiobutton(position_map_frame, text=map_name, variable=self.map_var, value=map_name)
            radio.pack(side="left", padx=5, pady=5)

        position_frame = tk.Frame(self)
        position_frame.pack()
        x_label = tk.Label(position_frame, text="x轴")
        x_label.pack(side="left", padx=5, pady=5)
        self.x_entry = tk.Entry(position_frame)
        self.x_entry.pack(side="left", padx=5, pady=5)
        self.x_entry.insert(0, 0)
        y_label = tk.Label(position_frame, text="y轴")
        y_label.pack(side="left", padx=5, pady=5)
        self.y_entry = tk.Entry(position_frame)
        self.y_entry.pack(side="left", padx=5, pady=5)
        self.y_entry.insert(0, 0)
        validate_cmd = self.register(validate_input)
        self.x_entry.config(validate="key", validatecommand=(validate_cmd, "%P"))
        self.y_entry.config(validate="key", validatecommand=(validate_cmd, "%P"))
        self.desc_label = tk.Label(position_frame, text="")
        self.desc_label.pack(side="left", padx=5, pady=5)

    def on_capture_region_set(self, region):
        self.region = region
        self.capture()

    def show_position(self):
        if self.canvas is not None:
            self.canvas.destroy()
        self.capture()
        xiao_gui_info = self.controller.show_position(image_to_base64(self._capture_label_image))
        self.handle_xiao_gui_info(xiao_gui_info)

    def build_position(self):
        if self.canvas is not None:
            self.canvas.destroy()
        map_name = self.map_var.get()
        x = self.x_entry.get()
        y = self.y_entry.get()
        if x is None or y is None or x == '' or y == '' or map_name is None or map_name == '':
            return
        xiao_gui_info = XiaoGui(x=int(x), y=int(y), map_name=map_name)
        utils.map_util.set_position_area(xiao_gui_info)
        if xiao_gui_info.map_info is None or len(xiao_gui_info.map_info.name) == 0:
            return
        self.handle_xiao_gui_info(xiao_gui_info)

    def handle_xiao_gui_info(self, xiao_gui_info: XiaoGui):
        if xiao_gui_info is not None:
            self.map_var.set(xiao_gui_info.map_info.name)
            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, xiao_gui_info.x)
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, xiao_gui_info.y)
            self.desc_label.config(text=xiao_gui_info.desc)

            # 绘制坐标轴
            image = draw_coordinate(xiao_gui_info)
            self.photo = ImageTk.PhotoImage(image)
            self.canvas = tk.Canvas(self, width=image.width, height=image.height)
            self.canvas.pack()
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def capture(self):
        self._capture_label_image = self.capture_region.capture()
        self._capture_label_photo = ImageTk.PhotoImage(self._capture_label_image)
        if self._capture_label is not None:
            self._capture_label.destroy()
        self._capture_label = tk.Label(self, image=self._capture_label_photo)
        self._capture_label.pack()
