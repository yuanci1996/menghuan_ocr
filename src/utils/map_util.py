import logging
import re
import os
import string

from src.models.map import Map
from src.models.xiaogui import XiaoGui

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, os.pardir))

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
             '女儿村': Map(name="女儿村", names=["女儿村", "女儿", "儿村", "女", "儿"], width=130, height=144,
                        image_path=os.path.join(project_root, "static\\images\\map\\nec.png")),
             '普陀山': Map(name="普陀山", names=["普陀山", "普陀", "陀山", "普", "陀"], width=95, height=72,
                        image_path=os.path.join(project_root, "static\\images\\map\\pts.png")),
             '五庄观': Map(name="五庄观", names=["五庄观", "五庄", "庄观", "五", "庄"], width=100, height=75,
                        image_path=os.path.join(project_root, "static\\images\\map\\wzg.png")),
             '西凉女国': Map(name="西凉女国", names=["西凉女国", "西凉", "凉女国", "西", "凉", "女国", "女"], width=163, height=124,
                         image_path=os.path.join(project_root, "static\\images\\map\\xlng.png")),
             '朱紫国': Map(name="朱紫国", names=["朱紫国", "朱紫", "紫国", "朱", "紫"], width=191, height=120,
                        image_path=os.path.join(project_root, "static\\images\\map\\zzg.png"))
             }

print("project_root = ", project_root)


def remove_after_substring(main_string, sub_string):
    # 找到子字符串的位置
    position = main_string.find(sub_string)

    if position != -1:
        # 返回子字符串之前的部分
        return main_string[:position]
    else:
        # 如果未找到子字符串，则根据具体情况处理，这里简单返回原字符串
        return main_string


def find_xiao_gui_info(ocr_text: string):
    # pattern = r"去(.*?)，(.*?)附近抓(.*?)鬼"
    # match = re.search(pattern, ocr_text)
    numbers = re.findall(r'\d+', ocr_text)
    logging.debug("字符串匹配信息 %s 坐标查找 %s", ocr_text, numbers)
    info = XiaoGui(ocr_text=ocr_text)
    if numbers is not None and 1 < len(numbers) < 4:
        if len(numbers) == 2:
            info.x = int(numbers[0])
            info.y = int(numbers[1])
        if len(numbers) == 3:
            info.x = int(numbers[1])
            info.y = int(numbers[2])
        info.map_name = remove_after_substring(ocr_text, numbers[0])
        logging.debug("地图子字符串 %s", info.map_name)
    else:
        logging.debug("未找到怪物坐标匹配信息 %s 坐标查找 %s", ocr_text, numbers)
        return None
    set_position_area(info)
    if info.map_info is None or len(info.map_info.name) == 0:
        return None
    return info


def set_position_area(xiao_gui_info: XiaoGui):
    for key, map_obj in map_infos.items():
        names = map_obj.names
        for name in names:
            if name in xiao_gui_info.map_name:
                xiao_gui_info.map_info = map_obj
                xiao_gui_info.map_name = map_obj.name
                break
    # map_info = map_infos[xiao_gui_info.map_name]
    if xiao_gui_info.map_info is None or len(xiao_gui_info.map_info.name) == 0:
        logging.debug("未找到地图信息 %s", xiao_gui_info.map_name)
        return
    else:
        logging.debug("找到地图信息 %s", xiao_gui_info.map_info)
    #                 x<y    |   x > 150 and y > 150
    #                   2    |   1
    #               ------- x,y ---------
    #  五庄观 or 普陀山   3    |   4
    #  x < 50 and y < 50     |   x > y or x > 150 and y < 50
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
        if len(position_area) == 4:
            if xiao_gui_info.x < xiao_gui_info.y:
                remove_list_value(position_area, [1, 3, 4])
            if xiao_gui_info.x > xiao_gui_info.y:
                remove_list_value(position_area, [1, 3, 2])
        xiao_gui_info.position_area = position_area


def remove_list_value(value_list, values):
    for value in values:
        if value in value_list:
            value_list.remove(value)
