import tkinter as tk
from tkinter import ttk


class NotificationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notification App")

        self.notify_button = ttk.Button(self, text="显示通知", command=self.show_notification)
        self.notify_button.pack(pady=20)

        self.notification_label = ttk.Label(self, text="", font=("Helvetica", 12), foreground="red")
        self.notification_label.pack(pady=10)

    def show_notification(self):
        self.notification_label.config(text="这是一个通知")
        self.after(3000, self.clear_notification)  # 3秒后自动清除通知

    def clear_notification(self):
        self.notification_label.config(text="")


if __name__ == "__main__":
    app = NotificationApp()
    app.mainloop()
