import os
import re
import ttkbootstrap as tk
import webbrowser
from PIL import Image, ImageTk
import logging
logger = logging.getLogger()

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, os.pardir))
project_root = os.path.abspath(os.path.join(project_root, os.pardir))


class ReadmeView(tk.Frame):
    def __init__(self, master=None, layout=None):
        super().__init__(layout)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        self.image_refs = []
        self.create_widgets()

    def create_widgets(self):
        # 1. 超链接
        self.link_label = tk.Label(self, text="点击这里访问项目主页", foreground="blue", cursor="hand2")
        self.link_label.pack(pady=5)
        self.link_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/yuanci1996/menghuan_ocr"))

        # 创建滚动条
        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建文本框
        self.text_widget = tk.Text(self, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Courier", 12))
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # 绑定滚动条
        scrollbar.config(command=self.text_widget.yview)

        # 加载 README 内容
        self.load_readme()

    def load_readme(self):
        """读取 README.md 并解析 Markdown（文本+图片）"""
        readme_path = os.path.join(project_root, "README.md")

        if not os.path.exists(readme_path):
            logger.info("README.md 文件未找到:", readme_path)
            self.insert_text("README.md 文件未找到: " + readme_path)
            return

        logger.info("加载 README.md 文件", readme_path)

        with open(readme_path, "r", encoding="utf-8") as file:
            content = file.read()

        self.text_widget.config(state=tk.NORMAL)  # 允许编辑
        self.text_widget.delete(1.0, tk.END)  # 清空旧内容

        # 解析 Markdown，插入文本 & 图片
        self.insert_markdown(content)

        self.text_widget.config(state=tk.DISABLED)  # 禁止编辑

    def insert_markdown(self, markdown_text):
        """解析 Markdown，插入文本和图片"""
        pattern = r"!\[.*?\]\((.*?)\)"  # 解析 ![alt](path) 格式
        pos = 0

        for match in re.finditer(pattern, markdown_text):
            start, end = match.span()
            text_before = markdown_text[pos:start]
            self.insert_text(text_before)  # 插入普通文本

            image_path = match.group(1)
            self.insert_image(image_path)  # 插入图片
            pos = end

        # 插入剩余的文本
        self.insert_text(markdown_text[pos:])

    def insert_text(self, text):
        """插入普通文本"""
        self.text_widget.insert(tk.END, text)

    def insert_image(self, image_path):
        """插入本地图片"""
        full_path = os.path.join(project_root, image_path)

        if not os.path.exists(full_path):
            self.insert_text(f"[图片未找到: {image_path}]\n")
            return

        # 加载图片
        image = Image.open(full_path)
        image.thumbnail((300, 300))  # 调整大小
        photo = ImageTk.PhotoImage(image)

        # 插入图片并保存引用
        self.text_widget.image_create(tk.END, image=photo)
        self.image_refs.append(photo)

        # 插入换行
        self.text_widget.insert(tk.END, "\n")
