import tkinter as tk
from tkinter import ttk
data = [
    {'q': '<b>第120届武神坛乙组亚军是</b>？', 'a': '少林寺'},
    {'q': '<b>第121届武神坛乙组亚军是</b>？', 'a': '白驼山'},
    {'q': '<b>第122届武神坛乙组亚军是</b>？', 'a': '华山派'},
    {'q': '<b>第123届武神坛乙组亚军是</b>？', 'a': '峨眉派'}
]

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("问题和答案展示")
        self.create_widgets()

    def create_widgets(self):
        for index, item in enumerate(data):
            print(index)
            print(item)
            bg_color = '#f0f0f0'
            if index % 2 != 0:
                bg_color = self.cget("bg")
            frame = ttk.Frame(self)
            frame.pack(fill=tk.X, padx=10, pady=5)

            # 使用 Text 小部件显示问题
            question = item['q']
            question_text = tk.Text(frame, height=1, wrap=tk.WORD, borderwidth=0, highlightthickness=0, bg=self.cget("bg"))
            question_text.pack(side="left", padx=5, pady=5)

            # 解析并设置问题文本
            self.set_question_text(question_text, question)
            question_text.configure(state='disabled')

            # 显示答案
            answer = item['a']
            answer_label = tk.Label(frame, text=answer, fg='blue', anchor='e', bg=self.cget("bg"))
            answer_label.pack(side="left", padx=5, pady=5)

    def set_question_text(self, text_widget, text):
        parts = text.split('<b>')
        for part in parts:
            if '</b>' in part:
                sub_parts = part.split('</b>')
                text_widget.insert(tk.END, sub_parts[0], 'red')
                text_widget.insert(tk.END, sub_parts[1])
            else:
                text_widget.insert(tk.END, part)

        text_widget.tag_configure('red', foreground='red')

if __name__ == "__main__":
    app = Application()
    app.mainloop()
