# ========================
# ✅ 标准库导入（放最前）
# ========================
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# ========================
# ✅ 第三方库导入
# ========================
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Icon
from PIL import Image as PILImage, ImageDraw
import pystray

# ========================
# ✅ 项目内模块导入
# ========================
from core.plugin_manager import PluginManager
import win32gui, win32con, win32api, win32gui_struct
import ctypes

class MainUI:
    version = "1.0"

    def __init__(self, root):
        # ================= 1. 保存根窗口 =================
        # 注意不要覆盖 root，否则 ttkbootstrap.Window 会丢失
        self.root = root
        self.root.geometry("900x600")  # 设置窗口初始大小
        self.root.overrideredirect(False)  # 隐藏系统标题栏
        self.root.resizable(True, True)  # 允许用户调整窗口大小
        root.title("FAE 工具箱")

        # ================= 设置窗口图标 =================
        icon = tk.PhotoImage(file="resource/png/pumpkin.png")  # png 或 ico
        self.root.iconphoto(True, icon)

        # ================= 2. 样式 =================
        self.style = ttk.Style(theme="superhero")  # 启用暗色主题

        # ================= 3. 保存图标引用 =================
        # 用于标题栏按钮，防止 PhotoImage 被垃圾回收
        self._titlebar_images = []

        # ================= 4. 自定义标题栏 =================
        # self.create_titlebar()  # 左标题 + 右按钮 + 拖动逻辑

        # ================= 5. 字体设置 =================
        self.title_font = ("微软雅黑", 12, "bold")  # 标题字体
        self.text_font = ("Consolas", 10)  # 正文字体

        # ================= 6. 主体布局 =================
        # 主容器分左右两部分
        self.main_pane = ttk.Panedwindow(self.root, orient=HORIZONTAL)
        self.main_pane.pack(fill="both", expand=True)

        # 左侧导航栏
        self.create_nav_frame()

        # 右侧主内容区
        self.create_content_frame()

        # ================= 7. 状态栏 =================
        self.status_var = ttk.StringVar(value="准备就绪 ✅")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            bootstyle="inverse-secondary"
        )
        status_bar.pack(side="bottom", fill="x")

        # ================= 8. 居中显示 =================
        self.center_window(900, 600)  # 窗口初始化时居中

        # ================= 9. 创建托盘 ================
        threading.Thread(target=self._create_tray, daemon=True).start()



    # ------------------ 居中 ------------------
    def center_window(self, width=900, height=560):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # ------------------ 自定义标题栏 ------------------

    def create_titlebar(self):
        # 标题栏
        titlebar = ttk.Frame(self.root, bootstyle="dark")
        titlebar.pack(fill="x")

        # 左侧标题文字
        title_label = ttk.Label(
            titlebar,
            text="🎧 FAE 工具箱",
            anchor="w",        # 左对齐
            padding=(10, 5),
            font=("微软雅黑", 12, "bold")
        )
        title_label.pack(side="left", fill="x",padx=4, pady=4)


        # 右侧按钮容器
        btn_frame = ttk.Frame(titlebar)
        btn_frame.pack(side="right", padx=4, pady=4)

        # 按钮图标
        minimize_img = tk.PhotoImage(file="resource/fontawesome-free-7.1.0-desktop/svgs-full/solid_png/minus.png").subsample(2, 2)
        close_img = tk.PhotoImage(file="resource/fontawesome-free-7.1.0-desktop/svgs-full/solid_png/xmark.png").subsample(2, 2)

        # 保存引用防止回收
        self._titlebar_images.extend([minimize_img, close_img])

        # 按钮配置
        buttons = [
            {"image": minimize_img, "command": self.minimize, "bootstyle": "secondary-outline"},
            {"image": close_img, "command": self.root.destroy, "bootstyle": "danger-outline"}
        ]

        # 调整按钮大小 (width, height) 并水平居中
        for btn_info in reversed(buttons):
            btn = ttk.Button(
                btn_frame,
                image=btn_info["image"],
                command=btn_info["command"],
                bootstyle=btn_info["bootstyle"],
                width=10,  # 调整宽度
                padding=2  # 减小内边距
            )
            btn.pack(side="right", padx=2, pady=2)

        # 拖动窗口
        titlebar.bind("<Button-1>", self.click_window)
        titlebar.bind("<B1-Motion>", self.drag_window)
        title_label.bind("<Button-1>", self.click_window)
        title_label.bind("<B1-Motion>", self.drag_window)


    def click_window(self, event):
        self._x = event.x
        self._y = event.y

    def drag_window(self, event):
        x = event.x_root - self._x
        y = event.y_root - self._y
        self.root.geometry(f"+{x}+{y}")

    def minimize(self):
        try:
            self.root.withdraw()  # 模拟最小化
        except Exception as e:
            print("Minimize failed:", e)



    # ------------------ Windows 托盘 ------------------
    def _create_tray(self):
        message_map = {
            win32con.WM_DESTROY: self._destroy_window,
            win32con.WM_USER + 20: self._tray_notify
        }
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = message_map
        wc.lpszClassName = "FAE_Toolbox"
        classAtom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(classAtom, "FAE", 0, 0, 0, 0, 0, 0, 0, 0, None)
        hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, hicon, "FAE 多功能工具箱")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

        # 消息循环
        win32gui.PumpMessages()

    def _tray_notify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONUP:
            # 左键单击 → 显示窗口
            self.show_window()
        elif lparam == win32con.WM_RBUTTONUP:
            # 右键弹出菜单
            self._show_tray_menu()
        return True

    def _show_tray_menu(self):
        menu = win32gui.CreatePopupMenu()
        # 添加“显示窗口”菜单
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1, "显示窗口")
        # 添加“退出程序”菜单
        win32gui.AppendMenu(menu, win32con.MF_STRING, 2, "退出程序")

        # 获取鼠标位置
        pos = win32gui.GetCursorPos()
        # 弹出菜单
        win32gui.SetForegroundWindow(self.hwnd)
        cmd = win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_LEFTALIGN | win32con.TPM_BOTTOMALIGN | win32con.TPM_RETURNCMD,
            pos[0],
            pos[1],
            0,
            self.hwnd,
            None
        )

        # 响应菜单选择
        if cmd == 1:
            self.show_window()
        elif cmd == 2:
            self.exit_app()

    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        self.root.lift()
        self.center_window()

    def exit_app(self, icon=None, item=None):
        self._destroy_window()
        self.root.destroy()

    def _destroy_window(self, hwnd=None, msg=None, wparam=None, lparam=None):
        # 删除托盘图标
        nid = (hwnd, 0)
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        except Exception:
            pass
            pass


    # ------------------ 左侧导航栏 ------------------
    def create_nav_frame(self):
        nav_frame = ttk.Frame(self.main_pane, width=180, bootstyle="dark")
        nav_frame.pack_propagate(False)

        ttk.Label(
            nav_frame, text="FAE 工具箱",
            font=("微软雅黑", 14, "bold"),
            bootstyle="inverse-dark"
        ).pack(pady=20)

        nav_groups = {
            "常用工具": [
                ("时间戳转换", "clock", self.show_timestamp),
                ("版本获取", "layers", self.show_version),
                ("解栈", "file-binary", self.show_stack),
            ],
            "辅助工具": [
                ("reset info转换", "shuffle", self.show_reset),
                ("问题模板", "file-text", self.show_template),
            ],
            "系统": [
                ("设置", "gear", self.show_settings),
                ("关于", "info-circle", self.show_about),
            ]
        }

        for group, buttons in nav_groups.items():
            ttk.Label(
                nav_frame, text=group,
                font=("微软雅黑", 10, "bold"),
                bootstyle="inverse-dark"
            ).pack(pady=(10, 2))
            for name, icon, cmd in buttons:
                ttk.Button(
                    nav_frame,
                    text=f"  {name}",
                    compound="left",
                    bootstyle="secondary-outline",
                    command=cmd,
                    width=15
                ).pack(pady=8, ipadx=4, ipady=4)

        self.main_pane.add(nav_frame)

    # ------------------ 主内容区 ------------------
    def create_content_frame(self):
        self.content_frame = ttk.Frame(self.main_pane, padding=20)
        self.main_pane.add(self.content_frame, weight=3)
        self.show_timestamp(self.title_font ,self.text_font)


    # ========== 主面板（插件执行区） ==========
    def show_timestamp(self, title_font=None, text_font=None):
        if title_font is None:
            title_font = self.title_font
        if text_font is None:
            text_font = self.text_font

        # 清空内容区域
        frame = self.content_frame
        for widget in frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(frame, text="🕒 时间戳转换工具", font=title_font).pack(anchor="w", pady=(0, 10))

        # 父容器：一行左右两列
        input_frame = ttk.Frame(frame)
        input_frame.pack(anchor="w", pady=5, fill="x")

        # 左侧输入框列
        left_frame = ttk.Frame(input_frame)
        left_frame.pack(side="left", anchor="n")  # 左列靠左，顶部对齐
        ttk.Label(left_frame, text="请输入时间 (格式: YYYY-MM-DD HH:MM:SS 或时间戳):", font=text_font).pack(anchor="w")
        self.input_entry = ttk.Entry(left_frame, width=40, font=text_font)
        self.input_entry.pack(anchor="w", pady=5)

        # 右侧时区列
        right_frame = ttk.Frame(input_frame)
        right_frame.pack(side="left", padx=20, anchor="n")  # 左列右边间距20
        ttk.Label(right_frame, text="选择时区:", font=text_font).pack(anchor="w")
        tz_list = ["Asia/Shanghai", "UTC", "Asia/Tokyo", "America/New_York", "Europe/London"]
        self.tz_var = ttk.StringVar(value="Asia/Shanghai")
        self.tz_menu = ttk.Combobox(
            right_frame,
            textvariable=self.tz_var,
            values=tz_list,
            width=25,
            bootstyle="info",
            state="readonly"
        )
        self.tz_menu.pack(anchor="w", pady=5)

        # 输出框
        ttk.Label(frame, text="结果:", font=text_font).pack(anchor="w", pady=(15, 5))
        self.output_text = ScrolledText(frame, font=text_font, height=6, wrap="word", relief="flat", bd=5)
        self.output_text.pack(fill="both", expand=True, pady=5)

        # 按钮函数
        def calc_timestamp():
            input_value = self.input_entry.get().strip()
            tz_name = self.tz_var.get()
            from core.time_converter import TimeConverter  # 假设插件文件名
            converter = TimeConverter()
            try:
                result = converter.run(input_value, tz=tz_name)
            except Exception as e:
                result = f"计算出错: {e}"
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", result)
            self.output_text.config(state="disabled")
            self.status_var.set("计算完成 ✅")
            frame.after(3000, lambda: self.status_var.set("准备就绪 ✅"))

        # 按钮行
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="计算时间戳", bootstyle="primary", width=20, command=calc_timestamp).pack(
            side="left", padx=10)

        def copy_to_clipboard():
            result = self.output_text.get("1.0", "end").strip()
            if result:
                frame.clipboard_clear()
                frame.clipboard_append(result)
                frame.update()
                self.status_var.set("结果已复制到剪贴板 ✅")
            else:
                self.status_var.set("输出为空，无法复制 ⚠️")

        # 按钮行增加复制按钮
        ttk.Button(btn_frame, text="复制结果", bootstyle="success-outline", width=15,
                   command=copy_to_clipboard).pack(side="left", padx=10)
        self.output_text.config(state="disabled")


    # ========== 其他页面 ==========
    def show_settings(self):
        frame = self.content_frame
        for widget in frame.winfo_children():
            widget.destroy()
        ttk.Label(frame, text="⚙️ 系统设置", font=("微软雅黑", 14, "bold")).pack(pady=30)
        ttk.Label(frame, text="（未来可以添加主题切换、插件管理等功能）", bootstyle="secondary").pack()

    def show_about(self):
        frame = self.content_frame
        for widget in frame.winfo_children():
            widget.destroy()
        ttk.Label(frame, text="📘 关于本程序", font=("微软雅黑", 14, "bold")).pack(pady=30)
        ttk.Label(
            frame,
            text="FAE 多功能工具箱 v1.0\n\nDesigned by 松焕彭\n支持插件扩展 / 栈解码 / 时间戳 / 日志分析",
            bootstyle="secondary",
            justify="center",
        ).pack(pady=20)

    def show_version(self):
        frame = self.content_frame
        for widget in frame.winfo_children():
            widget.destroy()
        ttk.Label(frame, text="📘 关于本程序", font=("微软雅黑", 14, "bold")).pack(pady=30)
        ttk.Label(
            frame,
            text="FAE 多功能工具箱 v1.0\n\nDesigned by 松焕彭\n支持插件扩展 / 栈解码 / 时间戳 / 日志分析",
            bootstyle="secondary",
            justify="center",
        ).pack(pady=20)

    def show_stack(self):
        frame = self.content_frame
        for widget in frame.winfo_children():
            widget.destroy()
        ttk.Label(frame, text="📘 关于本程序", font=("微软雅黑", 14, "bold")).pack(pady=30)
        ttk.Label(
            frame,
            text="FAE 多功能工具箱 v1.0\n\nDesigned by 松焕彭\n支持插件扩展 / 栈解码 / 时间戳 / 日志分析",
            bootstyle="secondary",
            justify="center",
        ).pack(pady=20)

    def show_reset(self, title_font=None, text_font=None):
        if title_font is None:
            title_font = self.title_font
        if text_font is None:
            text_font = self.text_font

        # 清空内容区域
        frame = self.content_frame
        for widget in frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(frame, text="🔧 ResetCode 转换工具", font=title_font).pack(anchor="w", pady=(0, 10))

        # 输入框
        ttk.Label(frame, text="请输入 reset-info:", font=text_font).pack(anchor="w")
        self.input_entry = ttk.Entry(frame, width=80, font=text_font)  # 宽度约80字符
        self.input_entry.pack(anchor="w", pady=5, fill="x")

        # 输出框
        ttk.Label(frame, text="结果:", font=text_font).pack(anchor="w", pady=(15, 5))
        self.output_text = ScrolledText(frame, font=text_font, height=8, wrap="word", state="disabled")
        self.output_text.pack(fill="both", expand=True, pady=5)

        # 按钮函数
        def calc_result():
            ts_text = self.input_entry.get().strip()
            if not ts_text:
                self.status_var.set("输入为空 ⚠️")
                self.output_text.after(3000, lambda: self.status_var.set("准备就绪 ✅"))
                return
            from core.covert_rebootcode_to_rebootinfo import ResetCodeConverter
            resetcodeconverter = ResetCodeConverter()
            ret = resetcodeconverter.run(ts_text, pri=False)
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", "end")
            for t_str, msg in ret:
                self.output_text.insert("end", f"{t_str}  {msg}\n")
            self.output_text.config(state="disabled")
            self.status_var.set("转换完成 ✅")
            self.output_text.after(3000, lambda: self.status_var.set("准备就绪 ✅"))

        def copy_to_clipboard():
            result = self.output_text.get("1.0", "end").strip()
            if result:
                frame.clipboard_clear()
                frame.clipboard_append(result)
                frame.update()
                self.status_var.set("结果已复制到剪贴板 ✅")
            else:
                self.status_var.set("输出为空，无法复制 ⚠️")
            self.output_text.after(3000, lambda: self.status_var.set("准备就绪 ✅"))

        def clear_output():
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.config(state="disabled")
            self.status_var.set("已清空输出 ⚠️")
            self.output_text.after(3000, lambda: self.status_var.set("准备就绪 ✅"))

        # 按钮行
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="转换", bootstyle="primary", width=20, command=calc_result).pack(side="left",
                                                                                                    padx=10)
        ttk.Button(btn_frame, text="清空输出", bootstyle="secondary-outline", width=15, command=clear_output).pack(
            side="left", padx=10)
        ttk.Button(btn_frame, text="复制结果", bootstyle="success-outline", width=15, command=copy_to_clipboard).pack(
            side="left", padx=10)

    def show_template(self, title_font=None, text_font=None):
        if title_font is None:
            title_font = self.title_font
        if text_font is None:
            text_font = self.text_font

        # 清空内容区域
        frame = self.content_frame
        for widget in frame.winfo_children():
            widget.destroy()

        # 标题
        ttk.Label(frame, text="🔧 问题模板", font=title_font).pack(anchor="w", pady=(0, 10))

        # 输出框
        ttk.Label(frame, text="结果:", font=text_font).pack(anchor="w", pady=(15, 5))
        self.output_text = ScrolledText(frame, font=text_font, height=12, wrap="word", state="disabled")
        self.output_text.pack(fill="both", expand=True, pady=5)

        # 读取 txt 文件内容
        txt_path = r"resource/issue_template.txt"  # 替换为你的路径
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"读取文件出错: {e}"

        # 显示到输出框
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", content)
        self.output_text.config(state="disabled")



if __name__ == "__main__":
    MainUI.create_tray_icon(MainUI)
