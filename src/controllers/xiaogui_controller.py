import cv2
import numpy as np

from src import utils
import logging
import ttkbootstrap as tk

from src.models.xiaogui import XiaoGui

logger = logging.getLogger()


class XiaoGuiController(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.run_ing = False

    def show_position(self, image, colorblind_mode=1):
        if self.run_ing:
            logger.debug("识别正在运行")
            print("识别正在运行")
            return XiaoGui()
        self.run_ing = True
        try:
            # 将 Pillow 图像转换为 NumPy 数组（RGB 格式）
            rgb_image = np.array(image)
            # 将 RGB 转换为 BGR（OpenCV 格式）
            bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
            map_key, x, y = utils.map_util.get_map_location(utils.map_util.get_map_image(bgr_image, colorblind_mode))
            xiao_gui_info = XiaoGui(map_name=map_key, x=x, y=y)
            logging.debug("最终信息 %s", xiao_gui_info)
            return xiao_gui_info
        except Exception as e:
            print("识别失败 %s", e)
            logger.error("识别失败 %s", e)
        finally:
            self.run_ing = False
