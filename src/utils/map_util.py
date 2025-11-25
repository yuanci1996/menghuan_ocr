import logging
from PIL import Image, ImageDraw

from matplotlib import pyplot as plt
from src.models.map import Map
from src.models.xiaogui import XiaoGui
import os
import cv2
import numpy as np
from . import config_util

# pip install opencv-python --index-url https://mirrors.aliyun.com/pypi/simple/
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, os.pardir))
scales_config = [float(x) for x in config_util.read_config("map_pars", "scales").split(", ")]
# scales_str = ", ".join(map(str, scales))
scales_runtime = []
scale_runtime = config_util.read_config("map_pars", "run_time_scale")
if scale_runtime is not None and len(scale_runtime) > 0:
    scales_config = [float(x) for x in scale_runtime.split(", ")]
print(f"初始化缩放比例：{scales_config}")

logger = logging.getLogger()
map_infos = {'傲来国': Map(name="傲来国", names=["傲来国", "傲来", "来国", "傲", "来"], width=224, height=150,
                        image_path=os.path.join(project_root, "static\\images\\map\\alg.png")),
             '宝象国': Map(name="宝象国", names=["宝象国", "宝象", "象国", "宝", "象"], width=160, height=120,
                        image_path=os.path.join(project_root, "static\\images\\map\\bxg.png")),
             '长寿村': Map(name="长寿村", names=["长寿村", "长寿", "寿村", "长", "寿"], width=160, height=210,
                        image_path=os.path.join(project_root, "static\\images\\map\\csc.png")),
             '大唐境外': Map(name="大唐境外", names=["大唐境外", "大唐", "唐境外", "境外", "大", "唐", "境"], width=640, height=120,
                         image_path=os.path.join(project_root, "static\\images\\map\\dtjw.png"),
                         area_color=(255, 0, 0, 128)),
             '建邺城': Map(name="建邺城", names=["建邺城", "建邺", "邺城", "建", "邺"], width=288, height=144,
                        image_path=os.path.join(project_root, "static\\images\\map\\jyc.png")),
             '江南野外': Map(name="江南野外", names=["江南野外", "江南", "南野外", "野外", "江", "南", "野"], width=160, height=120,
                         image_path=os.path.join(project_root, "static\\images\\map\\jnyw.png")),
             '女儿村': Map(name="女儿村", names=["女儿村", "女儿", "儿村", "儿"], width=130, height=144,
                        image_path=os.path.join(project_root, "static\\images\\map\\nec.png")),
             '普陀山': Map(name="普陀山", names=["普陀山", "普陀", "陀山", "普", "陀"], width=95, height=72,
                        image_path=os.path.join(project_root, "static\\images\\map\\pts.png")),
             '五庄观': Map(name="五庄观", names=["五庄观", "五庄", "庄观", "五", "庄"], width=100, height=75,
                        image_path=os.path.join(project_root, "static\\images\\map\\wzg.png")),
             '西凉女国': Map(name="西凉女国", names=["西凉女国", "西凉", "凉女国", "西", "凉", "女国"], width=163, height=124,
                         image_path=os.path.join(project_root, "static\\images\\map\\xlng.png")),
             '朱紫国': Map(name="朱紫国", names=["朱紫国", "朱紫", "紫国", "朱", "紫"], width=191, height=120,
                        image_path=os.path.join(project_root, "static\\images\\map\\zzg.png"))
             }


def set_position_area(xiao_gui_info: XiaoGui):
    if xiao_gui_info is None:
        return False
    if xiao_gui_info.map_name is not None:
        for key, map_obj in map_infos.items():
            names = map_obj.names
            for name in names:
                if name in xiao_gui_info.map_name:
                    xiao_gui_info.map_info = map_obj
                    xiao_gui_info.map_name = map_obj.name
                    break
    if xiao_gui_info.map_info is None or len(xiao_gui_info.map_info.name) == 0:
        logging.debug("未找到地图信息 %s", xiao_gui_info.map_name)
        return False
    else:
        xiao_gui_info.desc = "可信度：100%"
        logging.debug("找到地图信息 %s", xiao_gui_info.map_info)
    #                 x<y    |   x > 150 and y > 150
    #                   2    |   1
    #               ------- x,y ---------
    #  五庄观 or 普陀山   3    |   4
    #  x < 50 and y < 50     |   x > y or (x > 150 and y < 50)
    if xiao_gui_info.map_info.name == "普陀山" or xiao_gui_info.map_info.name == "五庄观":
        xiao_gui_info.position_area.append(3)
    else:
        position_area = [2, 1, 3, 4]
        if xiao_gui_info.x > 150:
            remove_list_value(position_area, [2, 3])
        if xiao_gui_info.x < 50:
            remove_list_value(position_area, [1, 4])
        if xiao_gui_info.y > 150:
            remove_list_value(position_area, [3, 4])
        if xiao_gui_info.y < 50:
            remove_list_value(position_area, [2, 1])
        # if len(position_area) == 4:
        #     if xiao_gui_info.x < xiao_gui_info.y:
        #         xiao_gui_info.desc = "可信度：25%"
        #         remove_list_value(position_area, [1, 3, 4])
        #     if xiao_gui_info.x > xiao_gui_info.y:
        #         xiao_gui_info.desc = "可信度：25%"
        #         remove_list_value(position_area, [1, 3, 2])
        xiao_gui_info.position_area = position_area
        return True


def remove_list_value(value_list, values):
    for value in values:
        if value in value_list:
            value_list.remove(value)


def draw_coordinate(xiao_gui_info: XiaoGui):
    if xiao_gui_info.map_info.name is None:
        return None
    # 绘制正方形
    position_area_image = Image.new('RGBA',
                                    (xiao_gui_info.map_info.image_width + 2 * xiao_gui_info.map_info.border_size,
                                     xiao_gui_info.map_info.image_height + 2 * xiao_gui_info.map_info.border_size),
                                    (255, 255, 255, 0))
    position_area_draw = ImageDraw.Draw(position_area_image)
    x = xiao_gui_info.x / xiao_gui_info.map_info.scale_width + xiao_gui_info.map_info.border_size
    y = xiao_gui_info.map_info.image_height + xiao_gui_info.map_info.border_size - xiao_gui_info.y / xiao_gui_info.map_info.scale_height
    side = 50 / ((xiao_gui_info.map_info.scale_width + xiao_gui_info.map_info.scale_height) / 2)

    position_area_draw.rectangle((x - side, y - side, x + side, y + side), outline="red", width=3)

    # 绘制区域象限
    if xiao_gui_info.position_area:
        for quadrant in xiao_gui_info.position_area:
            if quadrant == 1:
                # 第一象限：右上
                position_area_draw.rectangle((x, y - side, x + side, y), fill=xiao_gui_info.map_info.area_color)
            elif quadrant == 2:
                # 第二象限：左上
                position_area_draw.rectangle((x - side, y - side, x, y), fill=xiao_gui_info.map_info.area_color)
            elif quadrant == 3:
                # 第三象限：左下
                position_area_draw.rectangle((x - side, y, x, y + side), fill=xiao_gui_info.map_info.area_color)
            elif quadrant == 4:
                # 第四象限：右下
                position_area_draw.rectangle((x, y, x + side, y + side), fill=xiao_gui_info.map_info.area_color)

    image = Image.alpha_composite(xiao_gui_info.map_info.background_image, position_area_image)
    scale = config_util.read_config("map_pars", "composite_image_scale")
    if (scale is not None):
        image_bgr = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        image_rgb = cv2.cvtColor(cv2.resize(image_bgr, None, fx=float(scale), fy=float(scale), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)
        return Image.fromarray(image_rgb)
    else:
        return image


def show_image(title, img):
    cv2.imshow(title, img)
    cv2.waitKey(0)


def show_image_plt(title, img):
    plt.title(title)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.ion()
    plt.axis('on')
    plt.show()


def pyramid_template_matching(image,
                              template,
                              scales=None,
                              threshold=0.8,
                              proximity_threshold=5):
    """
    在不同尺度上对原图进行缩放，并进行模板匹配，返回所有匹配的结果
    :param image:待匹配的原图（灰度图）
    :param template:模板图像（灰度图）
    :param scales:原图缩放因子列表，例如 np.linspace(1.0, 2.0, num=10)
    :param threshold:设定的匹配阈值（0~1），超过该值的匹配才会被记录
    :param proximity_threshold: 去重时的距离阈值，单位：像素
    :return: (matched_objects) 包含多个匹配位置、匹配尺度、匹配得分的信息
    """
    if scales is None:
        global scales_config
        print(scale_runtime)
        scales = scales_config
    print(f"scales:{scales}")
    matched_objects = []
    matched_locations = np.empty((0, 2), dtype=int)  # Stores matched locations as a numpy array

    for scale in scales:
        # 按当前尺度缩放原图
        resized_image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        if resized_image.shape[0] < template.shape[0] or resized_image.shape[1] < template.shape[1]:
            break  # 停止继续缩小

        # print(f"当前尺度：{scale}，缩放后原图尺寸：{resized_image.shape}")

        # 进行模板匹配
        result = cv2.matchTemplate(resized_image, template, cv2.TM_CCOEFF_NORMED)

        # 找出所有匹配度大于阈值的点
        locations = np.where(result >= threshold)

        for loc in zip(*locations[::-1]):  # 解析匹配的坐标
            # 映射回原始尺度
            original_loc = (int(loc[0] / scale), int(loc[1] / scale))

            # Check if the current location is too close to any of the previous matched locations
            if len(matched_locations) > 0:
                # Calculate the absolute difference in x and y coordinates
                diff = np.abs(matched_locations - original_loc)

                # Check if the difference in both x and y is below the proximity threshold (5 pixels)
                if np.all(diff <= proximity_threshold, axis=1).any():
                    continue  # Skip this duplicate match

            # If not duplicate, add to the list
            matched_objects.append((original_loc,
                                    (int(template.shape[1] / scale), int(template.shape[0] / scale)),
                                    scale,
                                    result[loc[1], loc[0]]))
            matched_locations = np.vstack([matched_locations, original_loc])  # Add new location

        # 可选择性地添加停止条件，避免不必要的多次迭代
        if len(matched_objects) > 0:
            global scales_runtime
            scales_runtime.append(scale)
            break

    return matched_objects


def get_map_image(image, colorblind_mode=1):
    if colorblind_mode == 1:
        return cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV),
                           np.array([25, 35, 150]),
                           np.array([35, 255, 255]))
    else:
        return cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV),
                           np.array([170, 100, 100]),
                           np.array([180, 255, 255]))


map_keys = [
    ('傲来国', 'alg'),
    ('宝象国', 'bxg'),
    ('长寿村', 'csc'),
    ('大唐境外', 'dtjw'),
    ('建邺城', 'jyc'),
    ('江南野外', 'jnyw'),
    ('女儿村', 'nec'),
    ('普陀山', 'pts'),
    ('五庄观', 'wzg'),
    ('西凉女国', 'xlng'),
    ('朱紫国', 'zzg'),
]


def is_overlap(obj1, obj2):
    """
    判断两个矩形区域是否存在重叠
    :param obj1: (x, y, w, h) -> 第一个矩形 (map_location)
    :param obj2: (x, y, w, h) -> 第二个矩形 (matched_object)
    :return: True/False 是否重叠
    """
    x1, y1, w1, h1 = obj1
    x2, y2, w2, h2 = obj2

    # 计算矩形的边界
    left1, right1, top1, bottom1 = x1, x1 + w1, y1, y1 + h1
    left2, right2, top2, bottom2 = x2, x2 + w2, y2, y2 + h2

    # 判断是否有重叠
    if right1 > left2 and right2 > left1 and bottom1 > top2 and bottom2 > top1:
        return True  # 存在重叠
    return False  # 无重叠


def get_map_location(image):
    # x, y, w, h, map_name
    map_location = None

    # show_image("待检测图片：", image)
    for map_name, map_key in map_keys:
        path = os.path.normpath(os.path.join(project_root, "static", "images", "key", f"{map_key}.png"))
        template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        # print("开始匹配" + map_key)
        matched_objects = pyramid_template_matching(image,
                                                    template)
        if len(matched_objects) > 0:
            print("匹配地图位置：", matched_objects)
            (x, y), (w, h), _, _ = matched_objects[0]
            map_location = [x, y, w, h, map_name]
            logger.debug(f"匹配地图位置：{map_location}")
            break

    if map_location is None:
        print("未匹配到地图位置")
        logger.debug("未匹配到地图位置")
        return '', 0, 0
    image[map_location[1]:map_location[1] + map_location[3] * 2, map_location[0]:map_location[0] + map_location[2]] = 0
    image = image[map_location[1]:map_location[1] + map_location[3] * 2, :]
    map_location[1] = 0
    # show_image("image：", image)
    num_locations = []

    for i in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'dh']:
        path = os.path.normpath(os.path.join(project_root, "static", "images", "key", f"{i}.png"))
        template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        matched_objects = pyramid_template_matching(image,
                                                    template)
        if len(matched_objects) > 0:
            print(f"匹配{i}：", matched_objects)
            for matched_object in matched_objects:
                (x, y), (w, h), _, _ = matched_object
                if y > map_location[1] - 5 and y + h < map_location[1] + map_location[3] + 5:
                    num_locations.append((x, i))
                else:
                    print(f"{i}不在地图范围内")
                    logger.debug(f"{i}不在地图范围内")

    print(num_locations)
    # 按 x 从小到大排序
    sorted_data = sorted(num_locations, key=lambda item: item[0])

    # 找到 'dh' 的索引
    split_index = next((i for i, (x, key) in enumerate(sorted_data) if key == 'dh'), None)

    # 分割列表
    if split_index is not None:
        part1 = sorted_data[:split_index]  # 'dh' 之前的部分
        part2 = sorted_data[split_index + 1:]  # 'dh' 之后的部分
    else:
        part1 = sorted_data
        part2 = []

    # 提取 key 并组合成数字
    location_x = ''.join([key for (x, key) in part1])
    location_y = ''.join([key for (x, key) in part2])

    # 打印结果
    print(f"map_name: {map_location[4]}, x: {location_x}, y: {location_y}")
    logger.debug(f"map_name: {map_location[4]}, x: {location_x}, y: {location_y}")
    global scales_runtime
    print("scales_runtime", scales_runtime)
    if len(scales_runtime) > 20:
        global scales_config
        scales_config = list(dict.fromkeys(scales_runtime))
        scales_runtime.clear()
        config_util.update_config("map_pars", "run_time_scale", ", ".join(map(str, scales_config)))
    return map_location[4], safe_int(location_x), safe_int(location_y)


def safe_int(value, default=None):
    if value is None or value == "":
        return default
    return int(value)
