import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pyperclip

class TimestampTool:
    def __init__(self, root):
        self.root = root
        self.root.title("时间戳转换工具")
        self.root.geometry("400x280")
        self.root.resizable(False, False)

        # 输入标签与输入框
        tk.Label(root, text="请输入时间戳或时间：", font=("微软雅黑", 11)).pack(pady=10)
        self.input_entry = tk.Entry(root, width=40, font=("Consolas", 11))
        self.input_entry.pack()

        # 按钮区
        frame = tk.Frame(root)
        frame.pack(pady=10)
        tk.Button(frame, text="时间戳 → 时间", command=self.timestamp_to_time, width=15).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="时间 → 时间戳", command=self.time_to_timestamp, width=15).grid(row=0, column=1, padx=5)

        # 输出标签
        tk.Label(root, text="转换结果：", font=("微软雅黑", 11)).pack(pady=10)
        self.output_label = tk.Label(root, text="", font=("Consolas", 12), fg="blue")
        self.output_label.pack()

        # 复制按钮
        tk.Button(root, text="复制结果", command=self.copy_result, width=15).pack(pady=10)

    def timestamp_to_time(self):
        val = self.input_entry.get().strip()
        try:
            ts = float(val)
            # 自动识别秒 / 毫秒
            if ts > 1e12:
                ts /= 1000
            time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
            self.output_label.config(text=time_str)
        except Exception:
            messagebox.showerror("错误", "请输入正确的时间戳（支持秒或毫秒）")

    def time_to_timestamp(self):
        val = self.input_entry.get().strip()
        try:
            dt = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            ts = int(dt.timestamp())
            self.output_label.config(text=str(ts))
        except Exception:
            messagebox.showerror("错误", "请输入正确的时间格式：YYYY-MM-DD HH:MM:SS")

    def copy_result(self):
        text = self.output_label.cget("text")
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("提示", "结果已复制到剪贴板")
        else:
            messagebox.showwarning("提示", "没有结果可复制")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimestampTool(root)
    root.mainloop()
