from src import utils
import logging
import ttkbootstrap as tk

logger = logging.getLogger()


class XiaoGuiController(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.ocr_util = utils.Ocr()

    def show_position(self, image_base64):
        # 截取对应位置的图片
        # ocr_text_list = self.ocr_util.ocr.run(r"E:\test\mh\3.png")
        ocr_text_list = self.ocr_util.ocr.runBase64(image_base64)
        text_list = []
        if ocr_text_list["code"] == 100:
            for text_obj in ocr_text_list["data"]:
                text_list.append(text_obj["text"])
        ocr_text = "".join(text_list)
        logging.info("ocr_text %s", ocr_text)
        xiao_gui_info = utils.map_util.find_xiao_gui_info(ocr_text)
        logging.info("最终信息 %s", xiao_gui_info)
        return xiao_gui_info

