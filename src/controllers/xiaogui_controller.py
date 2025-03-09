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
        # self.ocr_util = utils.Ocr()

    # def show_position(self, image_base64):
    #     # 截取对应位置的图片
    #     # ocr_text_list = self.ocr_util.ocr.run(r"E:\test\mh\3.png")
    #     ocr_text_list = self.ocr_util.ocr.runBase64(image_base64)
    #     text_list = []
    #     if ocr_text_list["code"] == 100:
    #         for text_obj in ocr_text_list["data"]:
    #             text_list.append(text_obj["text"])
    #     ocr_text = "".join(text_list)
    #     logging.debug("ocr_text %s", ocr_text)
    #     xiao_gui_info = utils.map_util.find_xiao_gui_info(ocr_text)
    #     logging.debug("最终信息 %s", xiao_gui_info)
    #     return xiao_gui_info

    def show_position(self, image):
        # 截取对应位置的图片
        # ocr_text_list = self.ocr_util.ocr.run(r"E:\test\mh\3.png")
        # 将 Pillow 图像转换为 NumPy 数组（RGB 格式）
        rgb_image = np.array(image)
        # 将 RGB 转换为 BGR（OpenCV 格式）
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        map_key, x, y = utils.image_util.get_map_location(utils.image_util.get_map_image(bgr_image))
        xiao_gui_info = XiaoGui(map_name=map_key, x=x, y=y)
        logging.debug("最终信息 %s", xiao_gui_info)
        return xiao_gui_info
