from src.utils.PPOCR_api import GetOcrApi
import os
import time
import logging

logger = logging.getLogger()


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Ocr:
    def __init__(self):
        time1 = time.time()
        current_directory = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_directory, os.pardir))
        exe_path = os.path.join(project_root, "libs\\PaddleOCR-json_v.1.3.1\\PaddleOCR-json.exe")
        logger.debug("ocr插件所在目录 %s", exe_path)
        self.ocr = GetOcrApi(rf"{exe_path}")
        time2 = time.time()
        logger.debug("ocr插件初始化花费时间秒数 %s", time2 - time1)
