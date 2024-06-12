import logging
import re
import os
import string

from models.map import Map
from models.xiaogui import XiaoGui

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, os.pardir))

logger = logging.getLogger()
map_infos = {'傲来国': Map(name="傲来国", names=["傲来国", "傲来", "来国"], width=224, height=150,
                        image_path=os.path.join(project_root, "static\\images\\map\\alg.png")),
             '宝象国': Map(name="宝象国", names=["宝象国", "大唐", "境外"], width=160, height=120,
                        image_path=os.path.join(project_root, "static\\images\\map\\bxg.png")),
             '长寿村': Map(name="长寿村", names=["长寿村", "大唐", "境外"], width=160, height=210,
                        image_path=os.path.join(project_root, "static\\images\\map\\csc.png")),
             '大唐境外': Map(name="大唐境外", names=["大唐境外", "大唐", "境外"], width=640, height=120,
                         image_path=os.path.join(project_root, "static\\images\\map\\dtjw.png"),
                         area_color=(255, 0, 0, 128)),
             '建邺城': Map(name="建邺城", names=["建邺城", "大唐", "境外"], width=288, height=144,
                        image_path=os.path.join(project_root, "static\\images\\map\\jyc.png")),
             '江南野外': Map(name="江南野外", names=["江南野外", "大唐", "境外"], width=160, height=120,
                         image_path=os.path.join(project_root, "static\\images\\map\\jnyw.png")),
             '女儿村': Map(name="女儿村", names=["女儿村", "大唐", "境外"], width=130, height=144,
                        image_path=os.path.join(project_root, "static\\images\\map\\nec.png")),
             '普陀山': Map(name="普陀山", names=["普陀山", "大唐", "境外"], width=95, height=72,
                        image_path=os.path.join(project_root, "static\\images\\map\\pts.png")),
             '五庄观': Map(name="五庄观", names=["五庄观", "大唐", "境外"], width=100, height=75,
                        image_path=os.path.join(project_root, "static\\images\\map\\wzg.png")),
             '西凉女国': Map(name="西凉女国", names=["西凉女国", "大唐", "境外"], width=163, height=124,
                         image_path=os.path.join(project_root, "static\\images\\map\\xlng.png")),
             '朱紫国': Map(name="朱紫国", names=["朱紫国", "大唐", "境外"], width=191, height=120,
                        image_path=os.path.join(project_root, "static\\images\\map\\zzg.png"))
             }


def find_xiao_gui_info(ocr_text: string):
    pattern = r"去(.*?)，(.*?)附近抓(.*?)鬼"
    match = re.search(pattern, ocr_text)
    info = XiaoGui(ocr_text=ocr_text)
    if match is not None and len(match.groups()) > 0:
        logging.debug("ocr_text match %s", match.group(0))
        if len(match.groups()) != 3:
            logging.error("未找到怪物坐标匹配信息 %s", ocr_text)
            return None
        info.y = int(match.group(2))
        info.monster_name = match.group(3) + "鬼"
        map_width_pattern = r'([\u4e00-\u9fff]+)(\d+)'
        map_width_match = re.findall(map_width_pattern, match.group(1))
        if map_width_match:
            for match in map_width_match:
                letters, numbers = match
                info.map_name = letters
                info.x = int(numbers)
        else:
            logging.error("未找到地图信息与x坐标 %s", match.group(1))
            return None
    else:
        logging.error("未找到怪物坐标匹配信息 %s", ocr_text)
        return None
    set_position_area(info)
    return info


def set_position_area(xiao_gui_info: XiaoGui):
    map_info = map_infos[xiao_gui_info.map_name]
    if map_info is None:
        logging.error("未找到地图信息 %s", xiao_gui_info)
        return
    else:
        xiao_gui_info.map_info = map_info
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
