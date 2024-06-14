from src.models.map import Map


class XiaoGui:
    def __init__(self, ocr_text="", map_name="", x=0, y=0, monster_name="", map_info=None, position_area=None):
        if map_info is None:
            map_info = Map()
        if position_area is None:
            position_area = []
        self.ocr_text = ocr_text
        self.map_name = map_name
        self.x = x
        self.y = y
        self.monster_name = monster_name
        self.map_info = map_info
        self.position_area = position_area

    def __str__(self):
        return (f"XiaoGui(ocr_text={self.ocr_text}, map_name={self.map_name}, "
                f"x={self.x}, y={self.y}, monster_name={self.monster_name}), "
                f"map_info={self.map_info}), position_area={self.position_area})")
