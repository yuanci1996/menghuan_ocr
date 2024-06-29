# hot_key_config.py

import ttkbootstrap as tk
from src import utils
import keyboard
import logging
import os

logger = logging.getLogger()


class HotKeyConfig(tk.Frame):
    def __init__(self, parent_frame, hot_key="ask_hot_key", hot_key_event=None):
        super().__init__(parent_frame)
        self.parent_frame = parent_frame
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(current_directory, "..\\..\\static\\config\\config.ini")
        print(self.config_file)
        self.key_listeners = {}
        self.hot_key_setting_util = utils.HotKeyPressListener()
        self.hot_key_event = hot_key_event
        self.hot_keyboard = utils.config_util.read_config(self.config_file, "hot_key", hot_key)
        self.create_widgets()

    def destroy(self):
        # 自定义操作
        for key in list(self.key_listeners.keys()):
            self.remove_key_listener(key)
        # 调用父类的 destroy 方法
        super().destroy()

    def create_widgets(self):
        hot_key_frame = tk.Frame(self.parent_frame)
        hot_key_frame.pack(fill=tk.BOTH, expand=True)

        hot_key_desc = tk.Label(hot_key_frame, text="快捷键：")
        hot_key_desc.pack(side="left", padx=5, pady=5)

        self.hot_key_label = tk.Label(hot_key_frame, text=self.hot_keyboard)
        self.hot_key_label.pack(side="left", padx=5, pady=5)

        self.hot_key_setting_button = tk.Button(hot_key_frame, text="设置快捷键", command=self.handle_hot_key_setting)
        self.hot_key_setting_button.pack(side="left", padx=5, pady=5)

        self.hot_key_confirm_button = tk.Button(hot_key_frame, text="确认快捷键", command=self.handle_hot_key_confirm)
        self.hot_key_confirm_button.pack_forget()

        self.hot_key_cancel_button = tk.Button(hot_key_frame, text="取消", command=self.handle_hot_key_cancel)
        self.hot_key_cancel_button.pack_forget()

        self.add_key_listener(self.hot_keyboard, self.hot_key_event)

    def add_key_listener(self, key, callback):
        if key not in self.key_listeners:
            # 注册键监听器
            keyboard.add_hotkey(key, callback)
            self.key_listeners[key] = callback
            logger.debug(f"Started listening to {key}")

    def remove_key_listener(self, key):
        if key in self.key_listeners:
            # 取消键监听器
            keyboard.remove_hotkey(key)
            del self.key_listeners[key]
            logger.debug(f"Stopped listening to {key}")

    def handle_hot_key_setting(self):
        self.remove_key_listener(self.hot_keyboard)
        self.hot_key_setting_util.start_listening(self.handle_hot_key_callback)
        self.hot_key_setting_button.pack_forget()
        self.hot_key_confirm_button.pack(side="left", padx=5, pady=5)
        self.hot_key_cancel_button.pack(side="left", padx=5, pady=5)

    def handle_hot_key_callback(self, keys):
        keys_text = "+".join(keys)
        self.hot_key_label.config(text=keys_text)

    def handle_hot_key_confirm(self):
        self.hot_keyboard = self.hot_key_label.cget('text')
        utils.config_util.update_config(self.config_file, 'hot_key', 'ask_hot_key', self.hot_keyboard)
        self.add_key_listener(self.hot_keyboard, self.hot_key_event)
        self.hot_key_setting_button.pack(side="left", padx=5, pady=5)
        self.hot_key_confirm_button.pack_forget()
        self.hot_key_cancel_button.pack_forget()
        self.hot_key_setting_util.stop_listening()

    def handle_hot_key_cancel(self):
        self.hot_key_label.config(text=self.hot_keyboard)
        self.add_key_listener(self.hot_keyboard, self.hot_key_event)
        self.hot_key_setting_button.pack(side="left", padx=5, pady=5)
        self.hot_key_confirm_button.pack_forget()
        self.hot_key_cancel_button.pack_forget()
        self.hot_key_setting_util.stop_listening()
