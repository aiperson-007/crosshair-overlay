# 🎯 Crosshair Overlay

FPS 游戏桌面准星工具，屏幕中央始终显示可配置准星。

## 功能

- 4 种准星样式：十字 / 中心点 / 圆环 / 十字+点
- 7 色一键切换
- 黑色描边，任何背景都能看清
- 透明度可调
- 配置自动保存

## 快捷键

| 键 | 功能 |
|---|---|
| F1 | 显示/隐藏 |
| F2 | 切换颜色 |
| F3 | 增大 |
| F4 | 减小 |
| ESC | 退出 |

## 使用

### 直接运行
```bash
pip install pyinstaller  # 仅打包需要
python crosshair.py
```

### 打包 exe
```bash
pyinstaller --onefile --noconsole crosshair.py
```
生成 `dist/CrosshairOverlay.exe`，双击即用。

## 配置文件

首次运行自动创建 `%APPDATA%\CrosshairOverlay\config.json`：

```json
{
  "size": 20,
  "thickness": 2,
  "gap": 4,
  "color": "#00FF00",
  "opacity": 0.9,
  "style": "cross",
  "dot_size": 2,
  "outline": true
}
```
