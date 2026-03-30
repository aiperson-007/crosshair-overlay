# 🎯 Crosshair Overlay

FPS 游戏桌面准星工具，屏幕中央始终显示可配置准星。

## 功能

- **4 种准星样式**：十字 / 中心点 / 圆环 / 十字+点
- **7 色一键切换**：绿、红、蓝、黄、紫、白、橙
- **黑色描边**：任何背景都能看清
- **系统托盘配置**：右键托盘图标，随时调整所有参数
- **快捷键操作**：F1~F4 快速切换
- **配置自动记忆**：下次启动保持上次设置

## 系统托盘菜单

右键任务栏右下角的 🎯 图标，可以配置：

| 菜单 | 选项 |
|------|------|
| 样式 | 十字 / 中心点 / 圆环 / 十字+点 |
| 颜色 | 绿 / 红 / 蓝 / 黄 / 紫 / 白 / 橙 |
| 大小 | 小(10) / 中(20) / 大(30) / 特大(40) / 自定义 |
| 粗细 | 1~5 px |
| 透明度 | 50%~100% |
| 中心点 | 0~5 px |
| 描边 | 开/关 |

## 快捷键

| 键 | 功能 |
|---|---|
| F1 | 显示/隐藏准星 |
| F2 | 切换颜色 |
| F3 | 增大准星 |
| F4 | 减小准星 |
| ESC | 退出程序 |

## 安装 & 使用

### 方式一：直接运行
```bash
pip install pystray pillow
python crosshair.py
```

### 方式二：打包 exe
```bash
pip install pyinstaller pystray pillow
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

手动编辑配置文件后重启程序即可生效。
