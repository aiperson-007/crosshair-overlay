#!/usr/bin/env python3
"""
🎯 桌面准星工具 — Crosshair Overlay
FPS 游戏专用，屏幕中央始终显示可配置准星
支持：大小、颜色、样式、透明度、快捷键
"""

import tkinter as tk
import json
import os
import sys
from pathlib import Path

# ─── 默认配置 ───
DEFAULT_CONFIG = {
    "size": 20,            # 准星臂长（像素）
    "thickness": 2,        # 线条粗细
    "gap": 4,              # 中心间隙
    "color": "#00FF00",    # 颜色（支持 #RRGGBB 或颜色名）
    "opacity": 0.9,        # 透明度 0.1~1.0
    "style": "cross",      # cross / dot / circle / cross_dot
    "dot_size": 2,         # 中心点大小（dot 和 cross_dot 样式）
    "outline": True,       # 是否描边（黑色轮廓，提高可见性）
    "outline_color": "#000000",
    "hotkeys": {
        "toggle": "F1",    # 显示/隐藏
        "color": "F2",     # 切换颜色
        "size_up": "F3",   # 增大
        "size_down": "F4",  # 减小
    }
}

PRESET_COLORS = [
    "#00FF00",  # 绿色
    "#FF0000",  # 红色
    "#00BFFF",  # 天蓝
    "#FFFF00",  # 黄色
    "#FF00FF",  # 品红
    "#FFFFFF",  # 白色
    "#FF8C00",  # 橙色
]

CONFIG_DIR = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "CrosshairOverlay"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """加载配置，不存在则用默认值并创建"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            cfg = {**DEFAULT_CONFIG, **saved}
            # 合并 hotkeys
            if "hotkeys" in saved:
                cfg["hotkeys"] = {**DEFAULT_CONFIG["hotkeys"], **saved["hotkeys"]}
            return cfg
        except Exception:
            pass
    return {**DEFAULT_CONFIG}


def save_config(cfg: dict):
    """保存配置到磁盘"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


class CrosshairOverlay:
    """准星覆盖层"""

    def __init__(self):
        self.config = load_config()
        self.visible = True
        self.color_index = 0

        # 找到当前颜色在预设中的位置
        try:
            self.color_index = PRESET_COLORS.index(self.config["color"].upper())
        except ValueError:
            pass

        # ─── 主窗口 ───
        self.root = tk.Tk()
        self.root.title("Crosshair Overlay")

        # 获取屏幕尺寸
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # 无边框 + 置顶 + 透明
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.config["opacity"])

        # Windows 特有：设置为工具窗口（不在任务栏显示）
        if sys.platform == "win32":
            self.root.wm_attributes("-toolwindow", True)

        # 窗口覆盖整个屏幕但完全透明，只在中心画准星
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        self.root.configure(bg="black")
        # Windows 下黑色变为透明
        if sys.platform == "win32":
            self.root.wm_attributes("-transparentcolor", "black")

        # 画布
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_w,
            height=self.screen_h,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)
        # 让画布黑色也透明
        if sys.platform == "win32":
            pass  # 已经通过 root 设置

        self.cx = self.screen_w // 2
        self.cy = self.screen_h // 2

        # ─── 状态栏（底部提示，5秒后自动隐藏）───
        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Consolas", 11),
            fg="#00FF00",
            bg="#111111",
            anchor="w",
            padx=8,
            pady=2,
        )
        self.status_hide_job = None

        # ─── 绑定快捷键 ───
        self._bind_hotkeys()

        # ─── 绘制准星 ───
        self.draw_crosshair()

        # ─── 显示初始提示 ───
        self.show_status(
            f"🎯 准星已启动 | {self.config['style']} | "
            f"大小:{self.config['size']} | "
            f"F1隐藏 F2颜色 F3/F4大小"
        )

        # 点击画布也可以穿透（不拦截鼠标事件的提示）
        # ESC 退出
        self.root.bind("<Escape>", lambda e: self.quit())

        self.root.mainloop()

    def _bind_hotkeys(self):
        hk = self.config["hotkeys"]
        self.root.bind(f"<{hk['toggle']}>", lambda e: self.toggle_visibility())
        self.root.bind(f"<{hk['color']}>", lambda e: self.cycle_color())
        self.root.bind(f"<{hk['size_up']}>", lambda e: self.adjust_size(5))
        self.root.bind(f"<{hk['size_down']}>", lambda e: self.adjust_size(-5))

    def draw_crosshair(self):
        """在屏幕中央绘制准星"""
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

        # 描边宽度
        ow = thickness + 2 if outline else 0

        def line(x1, y1, x2, y2):
            if outline:
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=outline_color, width=ow,
                    tags="crosshair",
                )
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color, width=thickness,
                tags="crosshair",
            )

        def dot(x, y, r):
            if outline:
                self.canvas.create_oval(
                    x - r - 1, y - r - 1, x + r + 1, y + r + 1,
                    fill=outline_color, outline=outline_color,
                    tags="crosshair",
                )
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline=color,
                tags="crosshair",
            )

        def circle_ring(x, y, r):
            if outline:
                self.canvas.create_oval(
                    x - r - 1, y - r - 1, x + r + 1, y + r + 1,
                    outline=outline_color, width=thickness + 2,
                    tags="crosshair",
                )
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                outline=color, width=thickness,
                tags="crosshair",
            )

        if style == "cross" or style == "cross_dot":
            # 上
            line(cx, cy - gap - size, cx, cy - gap)
            # 下
            line(cx, cy + gap, cx, cy + gap + size)
            # 左
            line(cx - gap - size, cy, cx - gap, cy)
            # 右
            line(cx + gap, cy, cx + gap + size, cy)

        if style == "dot" or style == "cross_dot":
            dot(cx, cy, dot_size)

        if style == "circle":
            circle_ring(cx, cy, size)

    def toggle_visibility(self):
        """显示/隐藏准星"""
        self.visible = not self.visible
        if self.visible:
            self.root.deiconify()
            self.draw_crosshair()
            self.show_status("✅ 准星已显示")
        else:
            self.root.withdraw()
            # 再次调用 deiconify 以便快捷键还能生效
            self.root.after(100, lambda: self.root.withdraw())

    def cycle_color(self):
        """切换预设颜色"""
        self.color_index = (self.color_index + 1) % len(PRESET_COLORS)
        self.config["color"] = PRESET_COLORS[self.color_index]
        save_config(self.config)
        self.draw_crosshair()
        self.show_status(f"🎨 颜色: {self.config['color']}")

    def adjust_size(self, delta: int):
        """调整准星大小"""
        self.config["size"] = max(2, self.config["size"] + delta)
        save_config(self.config)
        self.draw_crosshair()
        self.show_status(f"📏 大小: {self.config['size']}")

    def show_status(self, text: str):
        """底部显示状态信息，自动消失"""
        self.status_label.config(text=text)
        self.status_label.place(relx=0.5, rely=1.0, anchor="s", y=-20)

        if self.status_hide_job:
            self.root.after_cancel(self.status_hide_job)
        self.status_hide_job = self.root.after(3000, self.status_label.place_forget)

    def quit(self):
        save_config(self.config)
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    CrosshairOverlay()
