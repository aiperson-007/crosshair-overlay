#!/usr/bin/env python3
"""
🎯 桌面准星工具 — Crosshair Overlay
FPS 游戏专用，屏幕中央始终显示可配置准星
支持：系统托盘 + 配置面板 + 快捷键
"""

import tkinter as tk
import json
import os
import sys
import queue
import threading
from pathlib import Path

# pystray
try:
    import pystray
    from pystray import MenuItem as Item
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# ─── 常量 ───
DEFAULT_CONFIG = {
    "size": 20, "thickness": 2, "gap": 4,
    "color": "#00FF00", "opacity": 0.9,
    "style": "cross", "dot_size": 2,
    "outline": True, "outline_color": "#000000",
}
PRESET_COLORS = ["#00FF00", "#FF0000", "#00BFFF", "#FFFF00", "#FF00FF", "#FFFFFF", "#FF8C00"]
STYLES = ["cross", "dot", "circle", "cross_dot"]
STYLE_NAMES = {"cross": "十字", "dot": "中心点", "circle": "圆环", "cross_dot": "十字+点"}
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
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    clean = {k: v for k, v in cfg.items() if isinstance(v, (str, int, float, bool, type(None)))}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)


def make_icon(size=64):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, arm, gap, w = size // 2, size // 2, size // 3, 4, 2
    green = (0, 255, 0, 255)
    d.line([(cx, cy - arm), (cx, cy - gap)], fill=green, width=w)
    d.line([(cx, cy + gap), (cx, cy + arm)], fill=green, width=w)
    d.line([(cx - arm, cy), (cx - gap, cy)], fill=green, width=w)
    d.line([(cx + gap, cy), (cx + arm, cy)], fill=green, width=w)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=green)
    return img


# ════════════════════════════════════════
#  配置面板
# ════════════════════════════════════════

class ConfigPanel:
    def __init__(self, app):
        self.app = app
        self.win = None

    def show(self):
        if self.win and self.win.winfo_exists():
            self.win.lift(); self.win.focus_force(); return
        self.win = tk.Toplevel(self.app.root)
        self.win.title("🎯 准星设置")
        self.win.geometry("320x540+100+100")
        self.win.resizable(False, False)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="#1e1e1e")
        self.win.protocol("WM_DELETE_WINDOW", self._close)
        self._built = False
        self._build()
        self._built = True
        self.win.focus_force()

    def _close(self):
        if self.win: self.win.destroy(); self.win = None

    def _label(self, text):
        tk.Label(self.win, text=text, fg="#ccc", bg="#1e1e1e",
                 font=("Microsoft YaHei", 10, "bold"), anchor="w"
                 ).pack(pady=(8, 0), padx=30, fill="x")

    def _safe(self):
        """UI 构建中跳过回调"""
        return self._built

    def _build(self):
        cfg = self.app.config
        bg, fg, acc = "#1e1e1e", "#ffffff", "#00BFFF"

        tk.Label(self.win, text="🎯 准星设置", font=("Microsoft YaHei", 16, "bold"),
                 fg=acc, bg=bg).pack(pady=(15, 10))

        # 样式
        self._label("样式")
        self.style_var = tk.StringVar(value=cfg["style"])
        f = tk.Frame(self.win, bg=bg); f.pack(pady=2)
        for s in STYLES:
            tk.Radiobutton(f, text=STYLE_NAMES[s], value=s, variable=self.style_var,
                           fg=fg, bg=bg, selectcolor="#333", activebackground=bg,
                           command=self._change).pack(side="left", padx=8)

        # 颜色
        self._label("颜色")
        self.color_var = tk.StringVar(value=cfg["color"])
        f = tk.Frame(self.win, bg=bg); f.pack(pady=2)
        for c in PRESET_COLORS:
            tk.Radiobutton(f, text="", value=c, variable=self.color_var,
                           bg=c, selectcolor=c, activebackground=c,
                           indicatoron=False, width=3, height=1, bd=2,
                           command=self._change).pack(side="left", padx=3)
        self.color_label = tk.Label(self.win, text=COLOR_NAMES.get(cfg["color"], ""), fg="#aaa", bg=bg, font=("", 9))
        self.color_label.pack()

        # 大小
        self._label("大小")
        self.size_var = tk.IntVar(value=cfg["size"])
        f = tk.Frame(self.win, bg=bg); f.pack(fill="x", padx=30)
        tk.Scale(f, from_=2, to=60, orient="horizontal", variable=self.size_var,
                 fg=fg, bg=bg, troughcolor="#333", highlightthickness=0,
                 command=lambda _: self._change()).pack(fill="x")

        # 粗细
        self._label("线条粗细")
        self.thick_var = tk.IntVar(value=cfg["thickness"])
        f = tk.Frame(self.win, bg=bg); f.pack(fill="x", padx=30)
        tk.Scale(f, from_=1, to=6, orient="horizontal", variable=self.thick_var,
                 fg=fg, bg=bg, troughcolor="#333", highlightthickness=0,
                 command=lambda _: self._change()).pack(fill="x")

        # 中心点
        self._label("中心点大小")
        self.dot_var = tk.IntVar(value=cfg["dot_size"])
        f = tk.Frame(self.win, bg=bg); f.pack(fill="x", padx=30)
        tk.Scale(f, from_=0, to=8, orient="horizontal", variable=self.dot_var,
                 fg=fg, bg=bg, troughcolor="#333", highlightthickness=0,
                 command=lambda _: self._change()).pack(fill="x")

        # 透明度
        self._label("透明度")
        self.opacity_var = tk.DoubleVar(value=cfg["opacity"])
        f = tk.Frame(self.win, bg=bg); f.pack(fill="x", padx=30)
        tk.Scale(f, from_=0.2, to=1.0, orient="horizontal", variable=self.opacity_var,
                 resolution=0.05, fg=fg, bg=bg, troughcolor="#333", highlightthickness=0,
                 command=lambda _: self._change()).pack(fill="x")

        # 描边
        self.outline_var = tk.BooleanVar(value=cfg["outline"])
        tk.Checkbutton(self.win, text="黑色描边", variable=self.outline_var,
                       fg=fg, bg=bg, selectcolor="#333", activebackground=bg,
                       command=self._change).pack(pady=8)

        tk.Label(self.win, text="F1隐藏 F2颜色 F3/F4大小 F5设置 ESC退出",
                 fg="#666", bg=bg, font=("", 8)).pack(side="bottom", pady=8)

    def _change(self):
        if not self._safe(): return
        cfg = self.app.config
        cfg["style"] = self.style_var.get()
        cfg["color"] = self.color_var.get()
        cfg["size"] = self.size_var.get()
        cfg["thickness"] = self.thick_var.get()
        cfg["dot_size"] = self.dot_var.get()
        cfg["opacity"] = self.opacity_var.get()
        cfg["outline"] = self.outline_var.get()
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
        self.tray_icon = None
        # 事件队列：托盘线程 → 主线程
        self._events = queue.Queue()

        try:
            self.color_index = PRESET_COLORS.index(self.config["color"].upper())
        except ValueError:
            self.color_index = 0

        # ─── 窗口 ───
        self.root = tk.Tk()
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.config["opacity"])
        if sys.platform == "win32":
            self.root.wm_attributes("-toolwindow", True)
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")
        self.root.configure(bg="black")
        if sys.platform == "win32":
            self.root.wm_attributes("-transparentcolor", "black")

        self.canvas = tk.Canvas(self.root, width=self.sw, height=self.sh, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.cx, self.cy = self.sw // 2, self.sh // 2

        self._bind_keys()
        self.draw_crosshair()

        # ─── 托盘 ───
        if HAS_TRAY:
            self._start_tray()

        # 主线程轮询事件队列（每 100ms）
        self.root.after(100, self._poll_events)

        # 启动时自动打开设置面板
        self.root.after(300, self.show_panel)

        self.root.mainloop()

    # ─── 事件队列轮询 ───

    def _poll_events(self):
        try:
            while True:
                action = self._events.get_nowait()
                if action == "toggle":
                    self._do_toggle()
                elif action == "panel":
                    self.show_panel()
                elif action == "quit":
                    self.quit()
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    # ─── 系统托盘 ───

    def _start_tray(self):
        def build_menu():
            return pystray.Menu(
                Item(lambda _: "🟢 显示中" if self.visible else "🔴 已隐藏",
                     lambda _: self._events.put("toggle"), default=True),
                Item("⚙️ 设置面板", lambda _: self._events.put("panel")),
                pystray.Menu.SEPARATOR,
                Item("❌ 退出", lambda _: self._events.put("quit")),
            )

        icon = make_icon()
        self.tray_icon = pystray.Icon("CrosshairOverlay", icon, "🎯 准星工具", build_menu())

        # 定期刷新菜单文字（不重建菜单对象，只更新 label）
        def refresh():
            import time
            while True:
                time.sleep(1)
                try:
                    # 触发菜单重建以更新显示文字
                    if self.tray_icon:
                        self.tray_icon.menu = build_menu()
                except Exception:
                    pass

        t = threading.Thread(target=self.tray_icon.run, daemon=True)
        t.start()
        # 刷新线程
        t2 = threading.Thread(target=refresh, daemon=True)
        t2.start()

    # ─── 配置面板 ───

    def show_panel(self):
        if not self.panel:
            self.panel = ConfigPanel(self)
        self.panel.show()

    # ─── 准星绘制 ───

    def draw_crosshair(self):
        self.canvas.delete("crosshair")
        c = self.config
        cx, cy = self.cx, self.cy
        col = c["color"]
        sz = c["size"]
        th = c["thickness"]
        gp = c["gap"]
        ds = c["dot_size"]
        sty = c["style"]
        ol = c.get("outline", True)
        olc = c.get("outline_color", "#000000")
        ow = th + 2 if ol else 0

        def line(x1, y1, x2, y2):
            if ol:
                self.canvas.create_line(x1, y1, x2, y2, fill=olc, width=ow, tags="crosshair")
            self.canvas.create_line(x1, y1, x2, y2, fill=col, width=th, tags="crosshair")

        def dot(x, y, r):
            if r <= 0: return
            if ol:
                self.canvas.create_oval(x-r-1, y-r-1, x+r+1, y+r+1,
                                        fill=olc, outline=olc, tags="crosshair")
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=col, outline=col, tags="crosshair")

        def ring(x, y, r):
            if ol:
                self.canvas.create_oval(x-r-1, y-r-1, x+r+1, y+r+1,
                                        outline=olc, width=th+2, tags="crosshair")
            self.canvas.create_oval(x-r, y-r, x+r, y+r, outline=col, width=th, tags="crosshair")

        if sty in ("cross", "cross_dot"):
            line(cx, cy - gp - sz, cx, cy - gp)
            line(cx, cy + gp, cx, cy + gp + sz)
            line(cx - gp - sz, cy, cx - gp, cy)
            line(cx + gp, cy, cx + gp + sz, cy)
        if sty in ("dot", "cross_dot"):
            dot(cx, cy, ds)
        if sty == "circle":
            ring(cx, cy, sz)

    # ─── 快捷键 ───

    def _bind_keys(self):
        self.root.bind("<F1>", lambda e: self._do_toggle())
        self.root.bind("<F2>", lambda e: self._do_cycle_color())
        self.root.bind("<F3>", lambda e: self._do_adjust_size(5))
        self.root.bind("<F4>", lambda e: self._do_adjust_size(-5))
        self.root.bind("<F5>", lambda e: self.show_panel())
        self.root.bind("<Escape>", lambda e: self.quit())

    def _do_toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.root.deiconify()
            self.draw_crosshair()
        else:
            self.root.withdraw()

    def _do_cycle_color(self):
        self.color_index = (self.color_index + 1) % len(PRESET_COLORS)
        self.config["color"] = PRESET_COLORS[self.color_index]
        save_config(self.config)
        self.draw_crosshair()

    def _do_adjust_size(self, d):
        self.config["size"] = max(2, self.config["size"] + d)
        save_config(self.config)
        self.draw_crosshair()

    def quit(self):
        save_config(self.config)
        if self.tray_icon:
            try: self.tray_icon.stop()
            except: pass
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    CrosshairOverlay()
