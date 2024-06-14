from PIL import Image
import logging

logger = logging.getLogger()


class Map:
    def __init__(self, name="", names=None, width=0, height=0, image_path="", area_color=(255, 0, 0, 128)):
        if names is None:
            names = []
        self.name = name
        self.names = names
        self.width = width
        self.height = height
        self.image_path = image_path
        self.area_color = area_color
        try:
            if len(image_path) != 0:
                image = Image.open(image_path)
                width, height = image.size
                self.image_width = width
                self.scale_width = self.width / self.image_width
                self.image_height = height
                self.scale_height = self.height / self.image_height
                logger.debug("读取地图 %s, 图片宽度 %s, 图片高度 %s, 宽度缩放 %s, 高度缩放 %s",
                             self.name, self.image_width, self.image_height, self.scale_width, self.scale_height)
        except Exception as e:
            logger.error("发生了异常: %s", e)

    def __str__(self):
        return f"Map(name={self.name}, names={self.names}, width={self.width}, height={self.height}, " \
               f"image_path={self.image_path}, image_width={self.image_width}, image_height={self.image_height}, " \
               f"scale_width={self.scale_width}, scale_height={self.scale_height}), area_color={self.area_color})"
