import keyboard


class HotKeyPressListener:
    def __init__(self):
        self.pressed_keys = []
        self.is_listening = False
        self.callback = None
        self.key_press_handler = None

    def start_listening(self, callback=None):
        if not self.is_listening:
            self.is_listening = True
            self.pressed_keys.clear()

            self.key_press_handler = keyboard.on_press(self.on_key_press)
            self.callback = callback

    def stop_listening(self):
        if self.is_listening:
            self.is_listening = False
            if self.key_press_handler is not None:
                keyboard.unhook(self.key_press_handler)

    def on_key_press(self, event):
        key_name = event.name
        if key_name not in self.pressed_keys:
            self.pressed_keys.append(key_name)
        if self.callback is not None:
            self.callback(self.pressed_keys)


if __name__ == "__main__":
    listener = HotKeyPressListener()

    listener.start_listening()

    listener.stop_listening()
