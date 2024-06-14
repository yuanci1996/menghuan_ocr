# main.py
from src.views.log_view import LogView
from src.views.xiaogui_view import XiaoGuiView
import ttkbootstrap as ttk


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
    # root.geometry("1200x720")
    LogView(main_window)
    XiaoGuiView(main_window)
    main_window.mainloop()


if __name__ == "__main__":
    main()
