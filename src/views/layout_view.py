import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from src.views.log_view import LogView
from src.views.xiaogui_view import XiaoGuiView
# from src.views.ask_view import AskView


class Layout(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)

        menu = tk.Menu(master, tearoff=0)

        # menu.add_command(label="答题", command=self.show_ask)
        menu.add_command(label="坐标", command=self.show_position)
        menu.add_command(label="日志", command=self.show_log)

        master.config(menu=menu)

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.log = LogView(master, master)

        self.show_position()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # def show_ask(self):
    #     self.clear_frame()
    #     view = AskView(self.master, self.main_frame)
    #     view.pack(fill=tk.BOTH, expand=True)

    def show_position(self):
        self.clear_frame()
        view = XiaoGuiView(self.master, self.main_frame)
        view.pack(fill=tk.BOTH, expand=True)

    def show_log(self):
        self.log.show_log()
