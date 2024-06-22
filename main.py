# main.py
from src.views.layout_view import Layout
import ttkbootstrap as ttk


def main():
    main_window = ttk.Window()
    main_window.title("坐标预测")
    # main_window.geometry("800x600")
    Layout(main_window)
    main_window.mainloop()


if __name__ == "__main__":
    main()
