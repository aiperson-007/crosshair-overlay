#!/usr/bin/env python3
"""
🎯 桌面准星工具 — Crosshair Overlay
FPS 游戏专用，屏幕中央始终显示可配置准星
支持：系统托盘右键菜单配置、快捷键、自动记忆
"""

import tkinter as tk
import json
import os
import sys
from pathlib import Path

# pystray 导入（系统托盘）
try:
    import pystray
    from pystray import MenuItem as Item
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False
    pystray = None
    Item = None
    Image = None
    ImageDraw = None

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
    "hotkeys": {
        "toggle": "F1",
        "color": "F2",
        "size_up": "F3",
        "size_down": "F4",
    }
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
            cfg = {**DEFAULT_CONFIG, **saved}
            if "hotkeys" in saved:
                cfg["hotkeys"] = {**DEFAULT_CONFIG["hotkeys"], **saved["hotkeys"]}
            return cfg
        except Exception:
            pass
    return {**DEFAULT_CONFIG}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def create_tray_icon(size=64) -> Image.Image:
    """生成一个简单的十字准星图标"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    arm = size // 3
    gap = 4
    w = 2
    # 十字
    draw.line([(cx, cy - arm), (cx, cy - gap)], fill=(0, 255, 0, 255), width=w)
    draw.line([(cx, cy + gap), (cx, cy + arm)], fill=(0, 255, 0, 255), width=w)
    draw.line([(cx - arm, cy), (cx - gap, cy)], fill=(0, 255, 0, 255), width=w)
    draw.line([(cx + gap, cy), (cx + arm, cy)], fill=(0, 255, 0, 255), width=w)
    # 中心点
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(0, 255, 0, 255))
    return img


class CrosshairOverlay:
    def __init__(self):
        self.config = load_config()
        self.visible = True
        self.tray_icon = None

        try:
            self.color_index = PRESET_COLORS.index(self.config["color"].upper())
        except ValueError:
            self.color_index = 0

        # ─── 主窗口 ───
        self.root = tk.Tk()
        self.root.withdraw()  # 先隐藏，等画好再显示

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
        self.root.bind("<Escape>", lambda e: self.quit())

        # 绘制准星
        self.draw_crosshair()
        self.root.deiconify()

        # ─── 系统托盘 ───
        if HAS_TRAY:
            self._setup_tray()
        else:
            print("⚠️ 未安装 pystray/pillow，系统托盘不可用")
            print("   运行: pip install pystray pillow")

        self.root.mainloop()

    # ════════════════════════════════════════
    #  系统托盘
    # ════════════════════════════════════════

    def _setup_tray(self):
        icon_img = create_tray_icon()
        menu = self._build_tray_menu()
        self.tray_icon = pystray.Icon(
            "CrosshairOverlay", icon_img, "🎯 准星工具", menu
        )
        import threading
        t = threading.Thread(target=self.tray_icon.run, daemon=True)
        t.start()

    def _build_tray_menu(self):
        cfg = self.config

        # ── 样式子菜单（用 checked callable 动态判断）──
        style_items = []
        for s in STYLES:
            style_items.append(Item(
                STYLE_NAMES[s],
                lambda _, s=s: self._set_style(s),
                checked=lambda _, s=s: self.config["style"] == s,
                radio=True,
            ))

        # ── 颜色子菜单 ──
        color_items = []
        for c in PRESET_COLORS:
            color_items.append(Item(
                COLOR_NAMES.get(c, c),
                lambda _, c=c: self._set_color(c),
                checked=lambda _, c=c: self.config["color"].upper() == c.upper(),
                radio=True,
            ))

        # ── 大小子菜单 ──
        size_items = [
            Item("小 (10)", lambda: self._set_size(10),
                 checked=lambda _: self.config["size"] == 10, radio=True),
            Item("中 (20)", lambda: self._set_size(20),
                 checked=lambda _: self.config["size"] == 20, radio=True),
            Item("大 (30)", lambda: self._set_size(30),
                 checked=lambda _: self.config["size"] == 30, radio=True),
            Item("特大 (40)", lambda: self._set_size(40),
                 checked=lambda _: self.config["size"] == 40, radio=True),
            pystray.Menu.SEPARATOR,
            Item("➕ 增大 (+5)", lambda: self._adjust_size(5)),
            Item("➖ 减小 (-5)", lambda: self._adjust_size(-5)),
        ]

        # ── 粗细子菜单 ──
        thick_items = []
        for t in [1, 2, 3, 4, 5]:
            thick_items.append(Item(
                f"{t}px",
                lambda _, t=t: self._set_thickness(t),
                checked=lambda _, t=t: self.config["thickness"] == t,
                radio=True,
            ))

        # ── 透明度子菜单 ──
        opacity_items = []
        for o in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            opacity_items.append(Item(
                f"{int(o * 100)}%",
                lambda _, o=o: self._set_opacity(o),
                checked=lambda _, o=o: abs(self.config["opacity"] - o) < 0.01,
                radio=True,
            ))

        # ── 中心点大小 ──
        dot_items = []
        for d in [0, 1, 2, 3, 4, 5]:
            dot_items.append(Item(
                f"{d}px",
                lambda _, d=d: self._set_dot_size(d),
                checked=lambda _, d=d: self.config["dot_size"] == d,
                radio=True,
            ))

        menu = pystray.Menu(
            Item(
                lambda _: "🟢 显示中" if self.visible else "🔴 已隐藏",
                lambda: self.toggle_visibility(),
                default=True,
            ),
            pystray.Menu.SEPARATOR,
            Item("🎯 样式", pystray.Menu(*style_items)),
            Item("🎨 颜色", pystray.Menu(*color_items)),
            Item("📏 大小", pystray.Menu(*size_items)),
            Item("📐 粗细", pystray.Menu(*thick_items)),
            Item("🔍 透明度", pystray.Menu(*opacity_items)),
            Item("⏺ 中心点", pystray.Menu(*dot_items)),
            Item(lambda _: "✅ 黑色描边" if self.config["outline"] else "⬜ 黑色描边",
                 lambda: self._toggle_outline(),
                 checked=lambda _: self.config["outline"]),
            pystray.Menu.SEPARATOR,
            Item("❌ 退出", lambda: self.quit()),
        )
        return menu

    def _refresh_tray(self):
        """更新托盘菜单勾选状态"""
        if self.tray_icon:
            try:
                self.tray_icon.update_menu()
            except Exception:
                pass

    # ════════════════════════════════════════
    #  配置操作
    # ════════════════════════════════════════

    def _set_style(self, style):
        self.config["style"] = style
        save_config(self.config)
        self.draw_crosshair()
        self._refresh_tray()

    def _set_color(self, color):
        self.config["color"] = color
        save_config(self.config)
        self.draw_crosshair()
        try:
            self.color_index = PRESET_COLORS.index(color.upper())
        except ValueError:
            pass
        self._refresh_tray()

    def _set_size(self, size):
        self.config["size"] = size
        save_config(self.config)
        self.draw_crosshair()
        self._refresh_tray()

    def _set_thickness(self, t):
        self.config["thickness"] = t
        save_config(self.config)
        self.draw_crosshair()
        self._refresh_tray()

    def _set_opacity(self, o):
        self.config["opacity"] = o
        save_config(self.config)
        self.root.attributes("-alpha", o)
        self._refresh_tray()

    def _set_dot_size(self, d):
        self.config["dot_size"] = d
        save_config(self.config)
        self.draw_crosshair()
        self._refresh_tray()

    def _toggle_outline(self):
        self.config["outline"] = not self.config["outline"]
        save_config(self.config)
        self.draw_crosshair()
        self._refresh_tray()

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
    #  快捷键 & 可见性
    # ════════════════════════════════════════

    def _bind_hotkeys(self):
        hk = self.config.get("hotkeys", {})
        self.root.bind(f"<{hk.get('toggle', 'F1')}>", lambda e: self.toggle_visibility())
        self.root.bind(f"<{hk.get('color', 'F2')}>", lambda e: self.cycle_color())
        self.root.bind(f"<{hk.get('size_up', 'F3')}>", lambda e: self.adjust_size(5))
        self.root.bind(f"<{hk.get('size_down', 'F4')}>", lambda e: self.adjust_size(-5))

    def toggle_visibility(self):
        self.visible = not self.visible
        if self.visible:
            self.root.deiconify()
            self.draw_crosshair()
        else:
            self.root.withdraw()
        self._refresh_tray()

    def cycle_color(self):
        self.color_index = (self.color_index + 1) % len(PRESET_COLORS)
        self.config["color"] = PRESET_COLORS[self.color_index]
        save_config(self.config)
        self.draw_crosshair()
        self._refresh_tray()

    def adjust_size(self, delta: int):
        self.config["size"] = max(2, self.config["size"] + delta)
        save_config(self.config)
        self.draw_crosshair()
        self._refresh_tray()

    def quit(self):
        save_config(self.config)
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    CrosshairOverlay()
