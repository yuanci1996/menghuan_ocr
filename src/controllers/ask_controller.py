from src import utils
import logging
import requests
import ttkbootstrap as tk
import random
import json

logger = logging.getLogger()


class AskController(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.ocr_util = utils.Ocr()
        self.hot_key_setting = utils.HotKeyPressListener()

    def ask(self, image_base64, kw_id=53):
        # 截取对应位置的图片
        # ocr_text_list = self.ocr_util.ocr.run(r"E:\test\mh\3.png")
        ocr_text_list = self.ocr_util.ocr.runBase64(image_base64)
        text_list = []
        if ocr_text_list["code"] == 100:
            for text_obj in ocr_text_list["data"]:
                text_list.append(text_obj["text"])
        ocr_text = "".join(text_list)
        logging.debug("ocr_text %s", ocr_text)
        response = requests.get('https://175dt.com/api/search',
                                params={"id": kw_id, "c": random.randint(10000, 30000), "kw": ocr_text},
                                proxies={
                                    "http": None,
                                    "https": None,
                                })
        if response.status_code != 200:
            # 打印响应内容
            logging.debug('请求失败，状态码: %s', response.status_code)
        logging.debug("最终信息 %s", response.text)
        return json.loads(response.text)
