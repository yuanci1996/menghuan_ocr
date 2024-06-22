import ttkbootstrap as tk
import logging
from src.views.capture_region import CaptureRegion
from PIL import ImageTk
from src.controllers.ask_controller import AskController
import base64
import io

logger = logging.getLogger()


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


class AskView(tk.Frame):
    def __init__(self, master=None, layout=None):
        super().__init__(layout)
        self.master = master
        self.controller = AskController()
        self._capture_label = None
        self.ask_frame = None
        self.create_widgets()

    def create_widgets(self):
        self.pack(fill=tk.BOTH, expand=True)
        # 实例化 CaptureRegion
        self.capture_region = CaptureRegion(self.master, self.on_capture_region_set)

        self.ask_id_var = tk.StringVar(value=53)

        ask_id_frame = tk.Frame(self)
        ask_id_frame.pack(fill=tk.BOTH, expand=True)

        ask_desc_frame = tk.Frame(ask_id_frame)
        ask_desc_frame.pack(fill=tk.BOTH, expand=True)
        ask_fb_desc_label = tk.Label(ask_desc_frame, text="题库：175dt.com")
        ask_fb_desc_label.pack(side="left", padx=5, pady=5)

        ask_fb_frame = tk.Frame(ask_id_frame)
        ask_fb_frame.pack(fill=tk.BOTH, expand=True)
        ask_fb_desc_label = tk.Label(ask_fb_frame, text="副本：")
        ask_fb_desc_label.pack(side="left", padx=5, pady=5)

        ask_kz_frame = tk.Frame(ask_id_frame)
        ask_kz_frame.pack(fill=tk.BOTH, expand=True)
        ask_fb_desc_label = tk.Label(ask_kz_frame, text="科举：")
        ask_fb_desc_label.pack(side="left", padx=5, pady=5)

        ask_rc_frame = tk.Frame(ask_id_frame)
        ask_rc_frame.pack(fill=tk.BOTH, expand=True)
        ask_fb_desc_label = tk.Label(ask_rc_frame, text="日常：")
        ask_fb_desc_label.pack(side="left", padx=5, pady=5)

        ask_jr_frame = tk.Frame(ask_id_frame)
        ask_jr_frame.pack(fill=tk.BOTH, expand=True)
        ask_fb_desc_label = tk.Label(ask_jr_frame, text="节日：")
        ask_fb_desc_label.pack(side="left", padx=5, pady=5)

        ask_qt_frame = tk.Frame(ask_id_frame)
        ask_qt_frame.pack(fill=tk.BOTH, expand=True)
        ask_fb_desc_label = tk.Label(ask_qt_frame, text="其他：")
        ask_fb_desc_label.pack(side="left", padx=5, pady=5)

        ask_list = [{"text": "四季", "value": 14, "frame": ask_fb_frame},
                    {"text": "通天河", "value": 10, "frame": ask_fb_frame},
                    {"text": "黑风山", "value": 12, "frame": ask_fb_frame},
                    {"text": "车迟斗法", "value": 9, "frame": ask_fb_frame},
                    {"text": "四门绝阵", "value": 30, "frame": ask_fb_frame},
                    {"text": "剑陵魔影", "value": 45, "frame": ask_fb_frame},
                    {"text": "大闹天宫", "value": 46, "frame": ask_fb_frame},
                    {"text": "衣冠古丘", "value": 54, "frame": ask_fb_frame},
                    {"text": "胡姬琵琶行", "value": 13, "frame": ask_fb_frame},
                    {"text": "金兜洞兕大王", "value": 44, "frame": ask_fb_frame},
                    {"text": "敦煌夜谭上部", "value": 58, "frame": ask_fb_frame},
                    {"text": "乡试", "value": 15, "frame": ask_kz_frame},
                    {"text": "会试", "value": 16, "frame": ask_kz_frame},
                    {"text": "附加题", "value": 35, "frame": ask_kz_frame},
                    {"text": "文韵墨香", "value": 41, "frame": ask_kz_frame},
                    {"text": "全民知识赛", "value": 42, "frame": ask_kz_frame},
                    {"text": "寻梦追忆", "value": 50, "frame": ask_rc_frame},
                    {"text": "降妖伏魔", "value": 57, "frame": ask_rc_frame},
                    {"text": "元宵节", "value": 17, "frame": ask_jr_frame},
                    {"text": "文星赛诗会", "value": 34, "frame": ask_jr_frame},
                    {"text": "签到答题", "value": 53, "frame": ask_qt_frame},
                    {"text": "三界书院", "value": 3, "frame": ask_qt_frame},
                    {"text": "翰墨抄写", "value": 11, "frame": ask_qt_frame},
                    {"text": "师徒任务", "value": 52, "frame": ask_qt_frame},
                    {"text": "赛诗大会", "value": 1, "frame": ask_qt_frame},
                    {"text": "梦幻课堂", "value": 7, "frame": ask_qt_frame},
                    {"text": "本事和尚", "value": 18, "frame": ask_qt_frame},
                    {"text": "异域欢歌", "value": 47, "frame": ask_qt_frame},
                    {"text": "六艺修行", "value": 29, "frame": ask_qt_frame},
                    {"text": "幻境节日", "value": 43, "frame": ask_qt_frame},
                    {"text": "房都尉", "value": 25, "frame": ask_qt_frame},
                    {"text": "密保节", "value": 2, "frame": ask_qt_frame},
                    {"text": "战神山", "value": 26, "frame": ask_qt_frame}]
        for ask_info in ask_list:
            radio = tk.Radiobutton(ask_info["frame"], text=ask_info["text"], variable=self.ask_id_var,
                                   value=ask_info["value"])
            radio.pack(side="left", padx=5, pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack()
        self.ask_button = tk.Button(button_frame, text="OCR获取答案", command=self.ask)
        self.ask_button.pack(side="left", padx=5, pady=5)
        self.set_capture_region_button = tk.Button(button_frame, text="设置截图范围",
                                                   command=self.capture_region.show_set_capture_region)
        self.set_capture_region_button.pack(side="left", padx=5, pady=5)

    def on_capture_region_set(self, region):
        self.capture()

    def ask(self):
        self.capture()

        if self.ask_frame is not None:
            self.ask_frame.destroy()

        self.ask_frame = tk.Frame(self)
        self.ask_frame.pack(fill=tk.BOTH, expand=True)

        response_text = self.controller.ask(image_to_base64(self._capture_label_image), self.ask_id_var.get())
        if response_text["status"] == 200:
            hits = response_text["hits"]
            for index, item in enumerate(hits):
                frame = tk.Labelframe(self.ask_frame, bootstyle="info")
                frame.pack(fill=tk.X, padx=10, pady=5)

                # 使用 Text 小部件显示问题
                question = item['q']
                self.set_question_text(frame, question)

                # 显示答案
                answer = item['a']
                answer_label = tk.Label(frame, text=answer, bootstyle="primary")
                answer_label.pack(side="left", padx=5, pady=5, anchor='center')
        else:
            frame = tk.Labelframe(self.ask_frame, bootstyle="info")
            frame.pack(fill=tk.X, padx=10, pady=5)
            answer_label = tk.Label(frame, text="未找到答案", bootstyle="primary")
            answer_label.pack(side="left", padx=5, pady=5, anchor='center')

    def set_question_text(self, frame, text):
        parts = text.split('<b>')
        for part in parts:
            if '</b>' in part:
                sub_parts = part.split('</b>')
                question_label = tk.Label(frame, text=sub_parts[0], bootstyle="danger")
                question_label.pack(side="left", anchor='center')
                question_label1 = tk.Label(frame, text=sub_parts[1], bootstyle="default")
                question_label1.pack(side="left", anchor='center')
            else:
                question_label = tk.Label(frame, text=part, bootstyle="default")
                question_label.pack(side="left", padx=5, pady=5, anchor='center')

    def capture(self):
        self._capture_label_image = self.capture_region.capture()
        self._capture_label_photo = ImageTk.PhotoImage(self._capture_label_image)
        if self._capture_label is not None:
            self._capture_label.destroy()
        self._capture_label = tk.Label(self, image=self._capture_label_photo)
        self._capture_label.pack()
