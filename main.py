# main.py
from src.views.layout_view import Layout
import ttkbootstrap as ttk


# pyinstaller --windowed --add-data "src/static;src/static" --add-data "src/libs;src/libs"
# --add-data "readme;readme" --add-data "README.md;." --uac-admin --name mh_ocr main.py
def main():
    main_window = ttk.Window()
    main_window.title("坐标预测 by爱花")
    # main_window.geometry("800x600")
    Layout(main_window)
    main_window.mainloop()


if __name__ == "__main__":
    main()
