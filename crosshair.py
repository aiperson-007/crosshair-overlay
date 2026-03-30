#!/usr/bin/env python3
"""
🎯 桌面准星工具 — Crosshair Overlay
FPS 游戏专用，屏幕中央始终显示可配置准星
支持：配置面板窗口、快捷键、自动记忆
纯 tkinter 实现，无外部依赖
"""

import tkinter as tk
from tkinter import ttk
import json
import os
import sys
from pathlib import Path

# ─── 默认配置 ───
DEFAULT_CONFIG = {
    "size": 20,
    "thickness": 2,
    "gap": 4,
    "color": "#00FF00",
    "opacity": 0.9,
    "style": "cross",
    "dot_size": 2,
    "outline": True,
    "outline_color": "#000000",
}

PRESET_COLORS = [
    "#00FF00", "#FF0000", "#00BFFF", "#FFFF00",
    "#FF00FF", "#FFFFFF", "#FF8C00",
]

STYLES = ["cross", "dot", "circle", "cross_dot"]
STYLE_NAMES = {
    "cross": "十字",
    "dot": "中心点",
    "circle": "圆环",
    "cross_dot": "十字+点",
}
COLOR_NAMES = {
    "#00FF00": "绿色", "#FF0000": "红色", "#00BFFF": "天蓝",
    "#FFFF00": "黄色", "#FF00FF": "品红", "#FFFFFF": "白色", "#FF8C00": "橙色",
}

CONFIG_DIR = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "CrosshairOverlay"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            return {**DEFAULT_CONFIG, **saved}
        except Exception:
            pass
    return {**DEFAULT_CONFIG}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    clean = {}
    for k, v in cfg.items():
        if isinstance(v, (str, int, float, bool, type(None))):
            clean[k] = v
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)


# ════════════════════════════════════════
#  配置面板
# ════════════════════════════════════════

class ConfigPanel:
    """独立的配置面板窗口"""

    def __init__(self, app: "CrosshairOverlay"):
        self.app = app
        self.win = None

    def show(self):
        if self.win and self.win.winfo_exists():
            self.win.lift()
            self.win.focus_force()
            return

        self.win = tk.Toplevel(self.app.root)
        self.win.title("🎯 准星设置")
        self.win.geometry("320x520+100+100")
        self.win.resizable(False, False)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#1e1e1e")

        # 关闭时清理
        self.win.protocol("on_close", self._on_close)

        self._build_ui()
        self.win.focus_force()

    def _on_close(self):
        self.win.destroy()
        self.win = None

    def _build_ui(self):
        cfg = self.app.config
        bg = "#1e1e1e"
        fg = "#ffffff"
        accent = "#00BFFF"

        # 标题
        tk.Label(self.win, text="🎯 准星设置", font=("Microsoft YaHei", 16, "bold"),
                 fg=accent, bg=bg).pack(pady=(15, 10))

        # ── 样式 ──
        self._section_label("样式")
        self.style_var = tk.StringVar(value=cfg["style"])
        frame = tk.Frame(self.win, bg=bg)
        frame.pack(pady=2)
        for s in STYLES:
            tk.Radiobutton(
                frame, text=STYLE_NAMES[s], value=s, variable=self.style_var,
                fg=fg, bg=bg, selectcolor="#333", activebackground=bg,
                command=self._on_change
            ).pack(side="left", padx=8)

        # ── 颜色 ──
        self._section_label("颜色")
        self.color_var = tk.StringVar(value=cfg["color"])
        frame = tk.Frame(self.win, bg=bg)
        frame.pack(pady=2)
        for c in PRESET_COLORS:
            tk.Radiobutton(
                frame, text="", value=c, variable=self.color_var,
                bg=c, selectcolor=c, activebackground=c,
                indicatoron=False, width=3, height=1, bd=2,
                command=self._on_change,
            ).pack(side="left", padx=3)

        # 颜色名称提示
        self.color_label = tk.Label(
            self.win, text=COLOR_NAMES.get(cfg["color"], cfg["color"]),
            fg="#aaa", bg=bg, font=("Microsoft YaHei", 9)
        )
        self.color_label.pack()

        # ── 大小 ──
        self._section_label("大小")
        self.size_var = tk.IntVar(value=cfg["size"])
        frame = tk.Frame(self.win, bg=bg)
        frame.pack(pady=2, fill="x", padx=30)
        tk.Scale(
            frame, from_=2, to=60, orient="horizontal", variable=self.size_var,
            fg=fg, bg=bg, troughcolor="#333", highlightthickness=0,
            command=lambda _: self._on_change()
        ).pack(fill="x")

        # ── 粗细 ──
        self._section_label("线条粗细")
        self.thick_var = tk.IntVar(value=cfg["thickness"])
        frame = tk.Frame(self.win, bg=bg)
        frame.pack(pady=2, fill="x", padx=30)
        tk.Scale(
            frame, from_=1, to=6, orient="horizontal", variable=self.thick_var,
            fg=fg, bg=bg, troughcolor="#333", highlightthickness=0,
            command=lambda _: self._on_change()
        ).pack(fill="x")

        # ── 中心点 ──
        self._section_label("中心点大小")
        self.dot_var = tk.IntVar(value=cfg["dot_size"])
        frame = tk.Frame(self.win, bg=bg)
        frame.pack(pady=2, fill="x", padx=30)
        tk.Scale(
            frame, from_=0, to=8, orient="horizontal", variable=self.dot_var,
            fg=fg, bg=bg, troughcolor="#333", highlightthickness=0,
            command=lambda _: self._on_change()
        ).pack(fill="x")

        # ── 透明度 ──
        self._section_label("透明度")
        self.opacity_var = tk.DoubleVar(value=cfg["opacity"])
        frame = tk.Frame(self.win, bg=bg)
        frame.pack(pady=2, fill="x", padx=30)
        tk.Scale(
            frame, from_=0.2, to=1.0, orient="horizontal",
            variable=self.opacity_var, resolution=0.05,
            fg=fg, bg=bg, troughcolor="#333", highlightthickness=0,
            command=lambda _: self._on_change()
        ).pack(fill="x")

        # ── 描边 ──
        self.outline_var = tk.BooleanVar(value=cfg["outline"])
        tk.Checkbutton(
            self.win, text="黑色描边（提高可见性）",
            variable=self.outline_var,
            fg=fg, bg=bg, selectcolor="#333", activebackground=bg,
            command=self._on_change
        ).pack(pady=8)

        # ── 底部快捷键提示 ──
        tk.Label(
            self.win,
            text="F1 隐藏 | F2 颜色 | F3/F4 大小 | ESC 退出",
            fg="#666", bg=bg, font=("Microsoft YaHei", 8)
        ).pack(side="bottom", pady=8)

    def _section_label(self, text):
        tk.Label(
            self.win, text=text,
            fg="#ccc", bg="#1e1e1e", font=("Microsoft YaHei", 10, "bold"),
            anchor="w"
        ).pack(pady=(8, 0), padx=30, fill="x")

    def _on_change(self):
        """配置变了，实时更新准星"""
        # UI 构建期间可能被回调，检查所有变量是否已就绪
        for attr in ("style_var", "color_var", "size_var", "thick_var",
                      "dot_var", "opacity_var", "outline_var"):
            if not hasattr(self, attr):
                return

        cfg = self.app.config
        cfg["style"] = self.style_var.get()
        cfg["color"] = self.color_var.get()
        cfg["size"] = self.size_var.get()
        cfg["thickness"] = self.thick_var.get()
        cfg["dot_size"] = self.dot_var.get()
        cfg["opacity"] = self.opacity_var.get()
        cfg["outline"] = self.outline_var.get()

        # 更新颜色名称
        if hasattr(self, "color_label"):
            self.color_label.config(text=COLOR_NAMES.get(cfg["color"], cfg["color"]))

        self.app.root.attributes("-alpha", cfg["opacity"])
        self.app.draw_crosshair()
        save_config(cfg)


# ════════════════════════════════════════
#  主程序
# ════════════════════════════════════════

class CrosshairOverlay:
    def __init__(self):
        self.config = load_config()
        self.visible = True
        self.panel = None

        try:
            self.color_index = PRESET_COLORS.index(self.config["color"].upper())
        except ValueError:
            self.color_index = 0

        # ─── 主窗口 ───
        self.root = tk.Tk()
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.config["opacity"])

        if sys.platform == "win32":
            self.root.wm_attributes("-toolwindow", True)

        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        self.root.configure(bg="black")
        if sys.platform == "win32":
            self.root.wm_attributes("-transparentcolor", "black")

        self.canvas = tk.Canvas(
            self.root, width=self.screen_w, height=self.screen_h,
            bg="black", highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.cx = self.screen_w // 2
        self.cy = self.screen_h // 2

        # 快捷键
        self._bind_hotkeys()

        # 绘制准星
        self.draw_crosshair()

        # 自动弹出配置面板
        self.root.after(300, self.show_config_panel)

        self.root.mainloop()

    def show_config_panel(self):
        if not self.panel:
            self.panel = ConfigPanel(self)
        self.panel.show()

    # ════════════════════════════════════════
    #  准星绘制
    # ════════════════════════════════════════

    def draw_crosshair(self):
        self.canvas.delete("crosshair")
        cfg = self.config
        cx, cy = self.cx, self.cy
        color = cfg["color"]
        size = cfg["size"]
        thickness = cfg["thickness"]
        gap = cfg["gap"]
        dot_size = cfg["dot_size"]
        style = cfg["style"]
        outline = cfg.get("outline", True)
        outline_color = cfg.get("outline_color", "#000000")
        ow = thickness + 2 if outline else 0

        def line(x1, y1, x2, y2):
            if outline:
                self.canvas.create_line(
                    x1, y1, x2, y2, fill=outline_color, width=ow, tags="crosshair"
                )
            self.canvas.create_line(
                x1, y1, x2, y2, fill=color, width=thickness, tags="crosshair"
            )

        def dot(x, y, r):
            if r <= 0:
                return
            if outline:
                self.canvas.create_oval(
                    x - r - 1, y - r - 1, x + r + 1, y + r + 1,
                    fill=outline_color, outline=outline_color, tags="crosshair"
                )
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline=color, tags="crosshair"
            )

        def circle_ring(x, y, r):
            if outline:
                self.canvas.create_oval(
                    x - r - 1, y - r - 1, x + r + 1, y + r + 1,
                    outline=outline_color, width=thickness + 2, tags="crosshair"
                )
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                outline=color, width=thickness, tags="crosshair"
            )

        if style in ("cross", "cross_dot"):
            line(cx, cy - gap - size, cx, cy - gap)
            line(cx, cy + gap, cx, cy + gap + size)
            line(cx - gap - size, cy, cx - gap, cy)
            line(cx + gap, cy, cx + gap + size, cy)

        if style in ("dot", "cross_dot"):
            dot(cx, cy, dot_size)

        if style == "circle":
            circle_ring(cx, cy, size)

    # ════════════════════════════════════════
    #  快捷键
    # ════════════════════════════════════════

    def _bind_hotkeys(self):
        self.root.bind("<F1>", lambda e: self.toggle_visibility())
        self.root.bind("<F2>", lambda e: self.cycle_color())
        self.root.bind("<F3>", lambda e: self.adjust_size(5))
        self.root.bind("<F4>", lambda e: self.adjust_size(-5))
        self.root.bind("<F5>", lambda e: self.show_config_panel())
        self.root.bind("<Escape>", lambda e: self.quit())

    def toggle_visibility(self):
        self.visible = not self.visible
        if self.visible:
            self.root.deiconify()
            self.draw_crosshair()
        else:
            self.root.withdraw()

    def cycle_color(self):
        self.color_index = (self.color_index + 1) % len(PRESET_COLORS)
        self.config["color"] = PRESET_COLORS[self.color_index]
        save_config(self.config)
        self.draw_crosshair()

    def adjust_size(self, delta: int):
        self.config["size"] = max(2, self.config["size"] + delta)
        save_config(self.config)
        self.draw_crosshair()

    def quit(self):
        save_config(self.config)
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    CrosshairOverlay()
