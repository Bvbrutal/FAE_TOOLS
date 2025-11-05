import tkinter as tk
from tkinter import messagebox
import pyperclip
from core.time_converter import TimeConverter


class TimestampToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("时间戳转换工具")
        self.root.geometry("400x280")
        self.root.resizable(False, False)

        tk.Label(root, text="请输入时间戳或时间：", font=("微软雅黑", 11)).pack(pady=10)
        self.input_entry = tk.Entry(root, width=40, font=("Consolas", 11))
        self.input_entry.pack()

        frame = tk.Frame(root)
        frame.pack(pady=10)
        tk.Button(frame, text="时间戳 → 时间", command=self.convert_ts_to_time, width=15).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="时间 → 时间戳", command=self.convert_time_to_ts, width=15).grid(row=0, column=1, padx=5)

        tk.Label(root, text="转换结果：", font=("微软雅黑", 11)).pack(pady=10)
        self.output_label = tk.Label(root, text="", font=("Consolas", 12), fg="blue")
        self.output_label.pack()

        tk.Button(root, text="复制结果", command=self.copy_result, width=15).pack(pady=10)

    def convert_ts_to_time(self):
        val = self.input_entry.get()
        try:
            result = TimeConverter.timestamp_to_time(val)
            self.output_label.config(text=result)
        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def convert_time_to_ts(self):
        val = self.input_entry.get()
        try:
            result = TimeConverter.time_to_timestamp(val)
            self.output_label.config(text=result)
        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def copy_result(self):
        text = self.output_label.cget("text")
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("提示", "结果已复制")
        else:
            messagebox.showwarning("提示", "没有结果可复制")
