import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import logging


# 自定义日志处理器
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self.append_text, msg + '\n')

    def append_text(self, msg):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg)
        self.text_widget.configure(state='disabled')
        self.text_widget.yview(tk.END)

class CustomFormatter(logging.Formatter):
    def format(self, record):
        # 自定义格式化逻辑
        if isinstance(record.msg, dict):
            record.msg = str(record.msg)
        return super().format(record)

class LogView(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.log_text = ScrolledText(self, state='disabled', width=80, height=20)
        self.create_widgets()

    def create_widgets(self):
        self.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(font='TkFixedFont')
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        text_handler = TextHandler(self.log_text)
        text_handler.setLevel(logging.DEBUG)

        formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        text_handler.setFormatter(formatter)

        logger.addHandler(text_handler)
