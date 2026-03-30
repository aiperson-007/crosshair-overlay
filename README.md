# 🎯 Crosshair Overlay

FPS 游戏桌面准星工具，屏幕中央始终显示可配置准星。

## 功能

- 4 种准星样式：十字 / 中心点 / 圆环 / 十字+点
- 7 色一键切换
- 黑色描边，任何背景都能看清
- **配置面板**：启动自动弹出，滑块实时调参
- 快捷键操作
- 配置自动记忆
- **零外部依赖**：纯 tkinter，不需要装任何库

## 快捷键

| 键 | 功能 |
|---|---|
| F1 | 显示/隐藏准星 |
| F2 | 切换颜色 |
| F3 | 增大准星 |
| F4 | 减小准星 |
| F5 | 打开设置面板 |
| ESC | 退出程序 |

## 使用

### 直接运行
```bash
python crosshair.py
```

### 打包 exe（无需安装 Python 也能用）
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole crosshair.py
```
生成 `dist/CrosshairOverlay.exe`，双击即用。

## 配置面板

启动后自动弹出设置面板，可以调整：
- 样式（十字/点/圆环/十字+点）
- 颜色（7 色色块点击切换）
- 大小（滑块 2~60）
- 粗细（滑块 1~6）
- 中心点（滑块 0~8）
- 透明度（滑块 20%~100%）
- 黑色描边（开关）

所有调整**实时生效**，自动保存。

## 配置文件

首次运行自动创建 `%APPDATA%\CrosshairOverlay\config.json`。
