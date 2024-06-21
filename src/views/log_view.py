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
    def __init__(self, master=None, layout=None):
        super().__init__(layout)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.pack(fill=tk.BOTH, expand=True)

    def show_log(self):

        self.log_top = tk.Toplevel(self)
        self.log_top.title("日志窗口")
        self.log_top.geometry("600x400")

        self.log_text = ScrolledText(self.log_top, state='disabled', width=80, height=20, font='TkFixedFont')
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # 配置日志
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        self.text_handler = TextHandler(self.log_text)
        self.text_handler.setLevel(logging.DEBUG)

        formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.text_handler.setFormatter(formatter)
        logger.addHandler(self.text_handler)
        self.log_top.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.log_top.destroy()
        logging.getLogger().removeHandler(self.text_handler)

    def clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state='disabled')
