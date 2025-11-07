import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.scrolledtext import ScrolledText
from core.plugin_manager import PluginManager
from PIL import Image, ImageDraw
import threading
import pystray
from ttkbootstrap.icons import Icon


from ttkbootstrap.constants import *
from tkinter import *

class MainUI:
    def __init__(self, root):
        # ✅ 初始化窗口（注意：不要覆盖 root）
        self.root = root
        self.root.geometry("900x560")
        self.root.overrideredirect(True)  # 隐藏系统标题栏
        self.root.resizable(True, True)
        self.style = ttk.Style(theme="superhero")

        # ================== 自定义标题栏 ==================
        self.create_titlebar()
        # 启用暗色主题
        self.title_font = ("微软雅黑", 12, "bold")
        self.text_font = ("Consolas", 10)


        # ================== 主体布局 ==================
        self.main_pane = ttk.Panedwindow(self.root, orient=HORIZONTAL)
        self.main_pane.pack(fill="both", expand=True)

        self.create_nav_frame()
        self.create_content_frame()

        # ================== 状态栏 ==================
        self.status_var = ttk.StringVar(value="准备就绪 ✅")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var,
            anchor="w", bootstyle="inverse-secondary"
        )
        status_bar.pack(side="bottom", fill="x")

    # ------------------ 自定义标题栏 ------------------
    def create_titlebar(self):
        titlebar = ttk.Frame(self.root, bootstyle="dark")
        titlebar.pack(fill="x")

        ttk.Label(
            titlebar, text="🎧 FAE 工具箱",
            anchor="w", padding=10,
            font=("微软雅黑", 12, "bold")
        ).pack(side="left")

        ttk.Button(
            titlebar, text="—",
            command=self.minimize,
            bootstyle="secondary-outline"
        ).pack(side="right", padx=5, pady=3)

        ttk.Button(
            titlebar, text="✖",
            command=self.root.destroy,
            bootstyle="danger-outline"
        ).pack(side="right", padx=5, pady=3)

        # 支持拖动窗口
        titlebar.bind("<Button-1>", self.click_window)
        titlebar.bind("<B1-Motion>", self.drag_window)

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
            threading.Thread(target=self.create_tray_icon, daemon=True).start()
        except Exception as e:
            print("Minimize failed:", e)



    # ========== 创建系统托盘 ==========
    def create_tray_icon(self):
        # 创建一个简单的托盘图标
        image = Image.new("RGB", (64, 64), color=(40, 40, 40))
        draw = ImageDraw.Draw(image)
        draw.rectangle((10, 10, 54, 54), fill=(255, 0, 80))

        menu = pystray.Menu(
            pystray.MenuItem("显示窗口", self.show_window),
            pystray.MenuItem("退出程序", self.exit_app)
        )

        self.icon = pystray.Icon("fae_toolbox", image, "FAE 工具箱", menu)
        self.icon.run()


    # ========== 从托盘恢复 ==========
    def show_window(self, icon=None, item=None):
        if self.icon:
            self.icon.stop()
        self.root.deiconify()
        self.root.lift()

    # ========== 退出程序 ==========
    def exit_app(self, icon=None, item=None):
        if self.icon:
            self.icon.stop()
        self.root.destroy()


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
    def show_timestamp(self, title_font, text_font):
        frame = self.content_frame
        for widget in frame.winfo_children():
            widget.destroy()

        ttk.Label(frame, text="🎯 功能选择", font=title_font).pack(anchor="w", pady=(0, 5))
        plugins = PluginManager.list_plugins()
        self.plugin_var = ttk.StringVar(value=plugins[0] if plugins else "")
        self.plugin_menu = ttk.Combobox(
            frame,
            textvariable=self.plugin_var,
            values=plugins,
            width=45,
            bootstyle="info",
        )
        self.plugin_menu.pack(anchor="w", pady=5)

        ttk.Label(frame, text="📝 输入内容", font=title_font).pack(anchor="w", pady=(20, 5))
        self.input_entry = ttk.Entry(frame, width=80, font=text_font)
        self.input_entry.pack(pady=5)

        # 按钮行
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="执行", bootstyle="danger", width=15, command=self.run_plugin).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="清空输出", bootstyle="secondary-outline", width=15, command=self.clear_output).pack(side="left", padx=10)

        ttk.Label(frame, text="📤 输出结果", font=title_font).pack(anchor="w", pady=(20, 5))
        self.output_text = ScrolledText(frame, font=text_font, height=12, wrap="word", relief="flat", bd=5)
        self.output_text.pack(fill="both", expand=True, pady=5)

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


    def show_reset(self):
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

    def show_template(self):
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

    # ========== 插件执行逻辑 ==========
    def run_plugin(self):
        plugin_name = self.plugin_var.get()
        plugin = PluginManager.get_plugin(plugin_name)
        value = self.input_entry.get()
        try:
            self.status_var.set(f"正在执行：{plugin_name} ...")
            self.root.update_idletasks()
            result = plugin.run(value)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", result)
            self.status_var.set("执行完成 ✅")
        except Exception as e:
            self.status_var.set(f"执行失败 ❌ {e}")

    def clear_output(self):
        self.output_text.delete("1.0", "end")
        self.status_var.set("输出已清空 ✅")


if __name__ == "__main__":
    app = ttk.Window(themename="superhero")
    MainUI(app)
    app.mainloop()
