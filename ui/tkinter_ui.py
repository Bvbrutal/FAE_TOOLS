import tkinter as tk
from core.plugin_manager import PluginManager

class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("多功能工具箱（插件版）")
        self.root.geometry("450x320")

        tk.Label(root, text="选择功能模块：", font=("微软雅黑", 11)).pack(pady=5)
        self.plugin_var = tk.StringVar()
        self.plugin_var.set(PluginManager.list_plugins()[0])

        tk.OptionMenu(root, self.plugin_var, *PluginManager.list_plugins()).pack()

        tk.Label(root, text="输入内容：", font=("微软雅黑", 11)).pack(pady=5)
        self.input_entry = tk.Entry(root, width=45, font=("Consolas", 11))
        self.input_entry.pack()

        tk.Button(root, text="执行", command=self.run_plugin, width=15).pack(pady=10)

        tk.Label(root, text="输出结果：", font=("微软雅黑", 11)).pack(pady=5)
        self.output_text = tk.Text(root, height=6, width=50, font=("Consolas", 10))
        self.output_text.pack()

    def run_plugin(self):
        plugin_name = self.plugin_var.get()
        plugin = PluginManager.get_plugin(plugin_name)
        value = self.input_entry.get()
        result = plugin.run(value)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)
