
from PIL import ImageTk
import ttkbootstrap as tk
import logging
from src.controllers.xiaogui_controller import XiaoGuiController
from src.models.xiaogui import XiaoGui
from src import utils
from src.views.common.capture_region import CaptureRegion
from src.views.common.hot_key_config import HotKeyConfig

logger = logging.getLogger()


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
        self.controller = XiaoGuiController()
        self.canvas = None
        self._capture_label = None
        self.photo = None
        self.show_button = None
        self.set_capture_region_button = None
        self.capture_region_button = None
        self._capture_window = None
        self._canvas = None
        self.key_listeners = {}
        self.region = (0, 0, 100, 100)
        self.create_widgets()

    def create_widgets(self):
        # 实例化 CaptureRegion
        self.capture_region = CaptureRegion(self.master, self.on_capture_region_set)

        xg_id_frame = tk.Frame(self)
        xg_id_frame.pack(fill=tk.BOTH, expand=True)

        hot_key_frame = tk.Frame(xg_id_frame)
        hot_key_frame.pack(fill=tk.BOTH, expand=True)

        HotKeyConfig(hot_key_frame, "xg_hot_key", self.show_position)

        self.show_out_var = tk.IntVar(value=int(utils.config_util.read_config("setting", "show_out")))
        self.show_out_switch = tk.Checkbutton(
            hot_key_frame,
            text="隐藏截图结果",
            variable=self.show_out_var,
            onvalue=1,  # 打开时的值
            offvalue=0,  # 关闭时的值
            command=self.toggle_setting_switch,
        )
        self.show_out_switch.pack(side="left", padx=5, pady=5)

        self.hide_input_var = tk.IntVar(value=int(utils.config_util.read_config("setting", "hide_input")))
        self.hide_input_var_switch = tk.Checkbutton(
            hot_key_frame,
            text="隐藏手动输入",
            variable=self.hide_input_var,
            onvalue=1,  # 打开时的值
            offvalue=0,  # 关闭时的值
            command=self.toggle_setting_switch,
        )
        self.hide_input_var_switch.pack(side="left", padx=5, pady=5)

        self.colorblind_mode_var = tk.IntVar(value=int(utils.config_util.read_config("setting", "colorblind_mode")))
        self.colorblind_mode_var_switch = tk.Checkbutton(
            hot_key_frame,
            text="色盲模式(对应游戏中的设置)",
            variable=self.colorblind_mode_var,
            onvalue=1,  # 打开时的值
            offvalue=0,  # 关闭时的值
            command=self.toggle_setting_switch,
        )
        self.colorblind_mode_var_switch.pack(side="left", padx=5, pady=5)

        self.set_capture_region_button = tk.Button(hot_key_frame, text="设置截图范围",
                                                   command=self.capture_region.show_set_capture_region)
        self.set_capture_region_button.pack(side="left", padx=5, pady=5)

        self.position_map_frame = tk.Frame(xg_id_frame)
        self.position_map_frame.pack(fill=tk.BOTH, expand=True)
        self.map_var = tk.StringVar(value="傲来国")
        for map_name, map_info in utils.map_util.map_infos.items():
            radio = tk.Radiobutton(self.position_map_frame, text=map_name, variable=self.map_var, value=map_name)
            radio.pack(side="left", padx=5, pady=5)

        self.position_frame = tk.Frame(xg_id_frame)
        self.position_frame.pack()
        x_label = tk.Label(self.position_frame, text="x轴")
        x_label.pack(side="left", padx=5, pady=5)
        self.x_entry = tk.Entry(self.position_frame)
        self.x_entry.pack(side="left", padx=5, pady=5)
        self.x_entry.insert(0, 0)
        y_label = tk.Label(self.position_frame, text="y轴")
        y_label.pack(side="left", padx=5, pady=5)
        self.y_entry = tk.Entry(self.position_frame)
        self.y_entry.pack(side="left", padx=5, pady=5)
        self.y_entry.insert(0, 0)
        validate_cmd = self.register(validate_input)
        self.x_entry.config(validate="key", validatecommand=(validate_cmd, "%P"))
        self.y_entry.config(validate="key", validatecommand=(validate_cmd, "%P"))
        self.desc_label = tk.Label(self.position_frame, text="")
        self.desc_label.pack(side="left", padx=5, pady=5)

        self.button_frame = tk.Frame(xg_id_frame)
        self.button_frame.pack()
        self.show_button = tk.Button(self.button_frame, text="OCR获取坐标", command=self.show_position)
        self.show_button.pack(side="left", padx=5, pady=5)
        self.show_button = tk.Button(self.button_frame, text="手动生成坐标", command=self.build_position)
        self.show_button.pack(side="left", padx=5, pady=5)

        self.handle_farm_forget()

    def toggle_setting_switch(self):
        utils.config_util.update_config("setting", "show_out", str(self.show_out_var.get()))
        utils.config_util.update_config("setting", "hide_input", str(self.hide_input_var.get()))
        utils.config_util.update_config("setting", "colorblind_mode", str(self.colorblind_mode_var.get()))
        self.handle_farm_forget()

    def handle_farm_forget(self):
        if self.hide_input_var.get() == 1:
            self.button_frame.pack_forget()
            self.position_map_frame.pack_forget()
            self.position_frame.pack_forget()
        else:
            self.button_frame.pack()
            self.position_map_frame.pack()
            self.position_frame.pack()
        if self.show_out_var.get() == 1:
            if self._capture_label is not None:
                self._capture_label.pack_forget()

    def on_capture_region_set(self, region):
        self.region = region
        self.capture()

    def show_position(self):
        self.capture()
        xiao_gui_info = self.controller.show_position(self._capture_label_image, self.colorblind_mode_var.get())
        utils.map_util.set_position_area(xiao_gui_info)
        self.handle_xiao_gui_info(xiao_gui_info)

    def build_position(self):
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
            if xiao_gui_info.map_name is None or xiao_gui_info.map_name == '':
                return
            image = utils.map_util.draw_coordinate(xiao_gui_info)
            self.photo = ImageTk.PhotoImage(image)
            if self.canvas is not None:
                self.canvas.config(width=image.width, height=image.height)
                self.canvas.itemconfig(self.canvas_image_item, image=self.photo)
            else:
                self.canvas = tk.Canvas(self, width=image.width, height=image.height)
                self.canvas.pack()
                self.canvas_image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def capture(self):
        self._capture_label_image = self.capture_region.capture()
        self._capture_label_photo = ImageTk.PhotoImage(self._capture_label_image)
        if self._capture_label is not None:
            self._capture_label.destroy()
        self._capture_label = tk.Label(self, image=self._capture_label_photo)
        if self.show_out_var.get() == 1:
            self._capture_label.pack_forget()
        else:
            self._capture_label.pack()
