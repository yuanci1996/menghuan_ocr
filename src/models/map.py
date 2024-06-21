from PIL import Image, ImageDraw
import logging

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


class Map:
    def __init__(self, name="", names=None, width=0, height=0, image_path="", area_color=(255, 0, 0, 128)):
        self.axis_space = axis_space
        self.coordinate_scale = coordinate_scale
        self.border_size = border_size
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
                image = Image.open(image_path).convert("RGBA")
                width, height = image.size
                self.image_width = width
                self.scale_width = self.width / self.image_width
                self.image_height = height
                self.scale_height = self.height / self.image_height
                logger.debug("读取地图 %s, 图片宽度 %s, 图片高度 %s, 宽度缩放 %s, 高度缩放 %s",
                             self.name, self.image_width, self.image_height, self.scale_width, self.scale_height)
                self.background_image = Image.new('RGBA',
                                                  (image.width + 2 * border_size,
                                                   image.height + 2 * border_size),
                                                  (255, 255, 255, 0))
                self.background_image.paste(image, (border_size, border_size), image)
                draw = ImageDraw.Draw(self.background_image)
                scale_width = self.scale_width
                scale_height = self.scale_height
                map_width = self.width
                map_height = self.height
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
        except Exception as e:
            logger.error("发生了异常: %s", e)

    def __str__(self):
        return f"Map(name={self.name}, names={self.names}, width={self.width}, height={self.height}, " \
               f"image_path={self.image_path}, image_width={self.image_width}, image_height={self.image_height}, " \
               f"scale_width={self.scale_width}, scale_height={self.scale_height}), area_color={self.area_color})"
