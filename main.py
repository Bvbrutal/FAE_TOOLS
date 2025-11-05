import tkinter as tk
from ui.tkinter_ui import MainUI
# 确保所有插件被导入（从而注册到管理器）
import core.time_converter
import core.esr_checker

def main():
    root = tk.Tk()
    app = MainUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
