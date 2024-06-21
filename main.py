# main.py
from src.views.log_view import LogView
from src.views.xiaogui_view import XiaoGuiView
from src.views.layout_view import Layout
import ttkbootstrap as ttk
import tkinter as tk


def main():
    # response = requests.get('https://175dt.com/api/search', params={"id": 53, "c": 33333, "kw": "120"}, proxies={
    #     "http": None,
    #     "https": None,
    # })
    # if response.status_code == 200:
    #     # 打印响应内容
    #     print(response.text)
    # else:
    #     print('请求失败，状态码:', response.status_code)
    main_window = ttk.Window()
    main_window.title("坐标预测")
    # root.geometry("1200x720")
    # LogView(main_window)
    Layout(main_window)
    main_window.mainloop()


if __name__ == "__main__":
    main()
