import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.scrolledtext import ScrolledText
from core.plugin_manager import PluginManager


class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎧 FAE 多功能工具箱 Pro")
        self.root.geometry("900x560")
        self.root.resizable(False, False)

        # 启用暗色主题
        style = ttk.Style(theme="superhero")
        title_font = ("微软雅黑", 12, "bold")
        text_font = ("Consolas", 10)

        # 主容器分为左右两区
        self.main_pane = ttk.Panedwindow(root, orient=HORIZONTAL)
        self.main_pane.pack(fill="both", expand=True)

        # ================== 左侧导航栏 ==================
        nav_frame = ttk.Frame(self.main_pane, width=180, bootstyle="dark")
        nav_frame.pack_propagate(False)
        ttk.Label(nav_frame, text="FAE 工具箱", font=("微软雅黑", 14, "bold"), bootstyle="inverse-dark").pack(pady=20)

        nav_buttons = [
            ("工具模块", "wrench", self.show_main_panel),
            ("设置", "gear", self.show_settings),
            ("关于", "info-circle", self.show_about),
        ]
        for name, icon, cmd in nav_buttons:
            btn = ttk.Button(
                nav_frame,
                text=f"  {name}",
                image="",
                compound="left",
                bootstyle="secondary-outline",
                command=cmd,
                width=15
            )
            btn.pack(pady=8, ipadx=4, ipady=4)

        self.main_pane.add(nav_frame)

        # ================== 右侧主工作区 ==================
        self.content_frame = ttk.Frame(self.main_pane, padding=20)
        self.main_pane.add(self.content_frame, weight=3)

        self.create_main_panel(title_font, text_font)
        self.status_var = ttk.StringVar(value="准备就绪 ✅")

        # 状态栏
        status_bar = ttk.Label(
            root, textvariable=self.status_var, anchor="w", bootstyle="inverse-secondary"
        )
        status_bar.pack(side="bottom", fill="x")

    # ========== 主面板（插件执行区） ==========
    def create_main_panel(self, title_font, text_font):
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

    def show_main_panel(self):
        self.create_main_panel(("微软雅黑", 12, "bold"), ("Consolas", 10))

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
