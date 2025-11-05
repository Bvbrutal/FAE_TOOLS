import tkinter as tk
from tkinter import ttk, messagebox
import time, threading, sys

try:
    import winsound
    HAVE_WINSOUND = True
except Exception:
    HAVE_WINSOUND = False


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("🍅 番茄钟 - 优化版")
        self.root.geometry("2560x1440")
        self.root.resizable(True, True)
        self.root.configure(bg="#fffaf6")
        self.root.iconbitmap("")  # 去掉Tk默认icon

        # --- 计时参数 ---
        self.default_work = 25 * 60
        self.default_short = 5 * 60
        self.default_long = 15 * 60
        self.cycles_before_long = 4

        self.session_type = "Work"
        self.session_total = self.default_work
        self.session_start_monotonic = None
        self.paused_remaining = None
        self.is_running = False
        self.after_id = None
        self.elapsed_offset = 0.0
        self.completed_work_sessions = 0
        self.auto_start_next = tk.BooleanVar(value=False)

        self._build_ui()
        self._apply_session_type("Work")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # 支持跨线程响铃事件
        self.root.bind("<<playbell>>", lambda e: self.root.bell())

    # ---------------- UI ----------------
    def _build_ui(self):
        ttk.Style().configure("TButton", font=("Segoe UI", 10))

        # 标题
        tk.Label(self.root, text="🍅 番茄钟 Pomodoro Timer", bg="#fffaf6",
                 fg="#503030", font=("Segoe UI", 14, "bold")).pack(pady=(12, 4))

        # Canvas 环形进度
        self.canvas = tk.Canvas(self.root, width=320, height=320, bg="#fffaf6", highlightthickness=0)
        self.canvas.pack(pady=(10, 6))
        self.circle_outer = self.canvas.create_oval(10, 10, 310, 310, outline="#ffe9e6", width=22)
        self.circle_arc = self.canvas.create_arc(10, 10, 310, 310, start=90, extent=0,
                                                 style="arc", width=22, outline="#ff6b6b")

        # 中央显示
        self.label_session = tk.Label(self.root, text="", font=("Segoe UI", 13, "bold"),
                                      bg="#fffaf6", fg="#6b2b2b")
        self.label_session.pack()

        # 模拟阴影时间显示
        self.label_time_shadow = tk.Label(self.root, text="", font=("Segoe UI", 40, "bold"),
                                          bg="#fffaf6", fg="#e1c4c4")
        self.label_time_shadow.place(x=105, y=195)
        self.label_time = tk.Label(self.root, text="00:00", font=("Segoe UI", 40, "bold"),
                                   bg="#fffaf6", fg="#3b0b0b")
        self.label_time.place(x=100, y=190)

        # 控制按钮
        buttons_frame = tk.Frame(self.root, bg="#fffaf6")
        buttons_frame.pack(pady=(10, 10))
        self.btn_start = ttk.Button(buttons_frame, text="▶ 开始", command=self.start_pause, width=12)
        self.btn_reset = ttk.Button(buttons_frame, text="⟳ 重置", command=self.reset_session, width=12)
        self.btn_skip = ttk.Button(buttons_frame, text="⤼ 跳过", command=self.skip_session, width=12)
        for i, b in enumerate((self.btn_start, self.btn_reset, self.btn_skip)):
            b.grid(row=0, column=i, padx=6, pady=4)

        # 设置区域
        settings = tk.LabelFrame(self.root, text="设置（分钟）", bg="#fffaf6")
        settings.pack(padx=16, pady=10, fill="x")

        def _add_row(label, entry, col):
            tk.Label(settings, text=label, bg="#fffaf6").grid(row=0, column=col, padx=6, pady=6)
            entry.grid(row=0, column=col + 1, padx=4)

        self.entry_work = ttk.Entry(settings, width=6)
        self.entry_work.insert(0, "25")
        _add_row("工作", self.entry_work, 0)

        self.entry_short = ttk.Entry(settings, width=6)
        self.entry_short.insert(0, "5")
        _add_row("短休", self.entry_short, 2)

        self.entry_long = ttk.Entry(settings, width=6)
        self.entry_long.insert(0, "15")
        _add_row("长休", self.entry_long, 4)

        row2 = tk.Frame(settings, bg="#fffaf6")
        row2.grid(row=1, column=0, columnspan=6, pady=(6, 10), sticky="w")
        ttk.Checkbutton(row2, text="完成后自动开始下一阶段",
                        variable=self.auto_start_next).pack(side="left", padx=(4, 10))
        tk.Label(row2, text="长休每", bg="#fffaf6").pack(side="left")
        self.spin_cycles = ttk.Spinbox(row2, from_=2, to=8, width=4)
        self.spin_cycles.set("4")
        self.spin_cycles.pack(side="left", padx=(6, 6))
        tk.Label(row2, text="次工作", bg="#fffaf6").pack(side="left")

        self.btn_apply = ttk.Button(settings, text="应用设置", command=self.apply_settings)
        self.btn_apply.grid(row=2, column=0, columnspan=6, pady=5)

        # 底部
        bottom = tk.Frame(self.root, bg="#fffaf6")
        bottom.pack(pady=(6, 8), fill="x", padx=12)
        self.label_done = tk.Label(bottom, text="已完成工作周期: 0", bg="#fffaf6", fg="#503030")
        self.label_done.pack(side="left")

    # ---------------- Session 管理 ----------------
    def _apply_session_type(self, session):
        self.session_type = session
        if session == "Work":
            self.session_total = self.default_work
            self.label_session.config(text="工作中")
            self.canvas.itemconfig(self.circle_arc, outline="#ff6b6b")
        elif session == "Short Break":
            self.session_total = self.default_short
            self.label_session.config(text="短休息")
            self.canvas.itemconfig(self.circle_arc, outline="#4eb36d")
        else:
            self.session_total = self.default_long
            self.label_session.config(text="长休息")
            self.canvas.itemconfig(self.circle_arc, outline="#3b82f6")

        if not self.is_running:
            self.paused_remaining = self.session_total
            self._update_display(self.session_total, 0.0)

    def apply_settings(self):
        try:
            self.default_work = max(60, int(float(self.entry_work.get()) * 60))
            self.default_short = max(60, int(float(self.entry_short.get()) * 60))
            self.default_long = max(60, int(float(self.entry_long.get()) * 60))
            self.cycles_before_long = max(2, int(self.spin_cycles.get()))
            self._apply_session_type(self.session_type)
        except Exception:
            messagebox.showerror("输入错误", "请输入有效数字（分钟）")

    # ---------------- 控制逻辑 ----------------
    def start_pause(self):
        if not self.is_running:
            if self.paused_remaining is None:
                self.paused_remaining = self.session_total
            self.is_running = True
            self.session_start_monotonic = time.monotonic()
            self.elapsed_offset = self.session_total - self.paused_remaining
            self.btn_start.config(text="⏸ 暂停")
            self._schedule_update()
        else:
            self.is_running = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            elapsed = time.monotonic() - self.session_start_monotonic + self.elapsed_offset
            self.paused_remaining = max(0.0, self.session_total - elapsed)
            self.btn_start.config(text="▶ 继续")

    def reset_session(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.is_running = False
        self._apply_session_type(self.session_type)
        self.btn_start.config(text="▶ 开始")

    def skip_session(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.is_running = False
        self._on_finish()

    # ---------------- 更新 ----------------
    def _schedule_update(self):
        if self.after_id is None:
            self.after_id = self.root.after(100, self._update)

    def _update(self):
        self.after_id = None
        if not self.is_running:
            return
        elapsed = time.monotonic() - self.session_start_monotonic + self.elapsed_offset
        remain = max(0.0, self.session_total - elapsed)
        progress = elapsed / self.session_total if self.session_total > 0 else 1.0
        self._update_display(int(remain), progress)
        if remain <= 0:
            self.is_running = False
            self.after_id = None
            self._on_finish()
            return
        self._schedule_update()

    def _update_display(self, remain_seconds: int, progress_ratio: float):
        m, s = divmod(remain_seconds, 60)
        t = f"{m:02d}:{s:02d}"
        self.label_time.config(text=t)
        self.label_time_shadow.config(text=t)
        self.canvas.itemconfig(self.circle_arc, extent=-360 * progress_ratio)

    # ---------------- 完成阶段 ----------------
    def _on_finish(self):
        threading.Thread(target=self._play_sound, daemon=True).start()

        if self.session_type == "Work":
            self.completed_work_sessions += 1
            self.label_done.config(text=f"已完成工作周期: {self.completed_work_sessions}")
            cycles = int(self.spin_cycles.get())
            next_session = "Long Break" if self.completed_work_sessions % cycles == 0 else "Short Break"
        else:
            next_session = "Work"

        self._apply_session_type(next_session)
        self.btn_start.config(text="▶ 开始")
        if self.auto_start_next.get():
            self.start_pause()

    def _play_sound(self):
        try:
            if HAVE_WINSOUND:
                freq = 1000 if self.session_type == "Work" else 700
                winsound.Beep(freq, 600)
            else:
                self.root.event_generate("<<playbell>>")
        except Exception:
            pass

    def _on_close(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    PomodoroTimer(root)
    root.mainloop()
