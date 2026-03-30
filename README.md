# 🎯 Crosshair Overlay

FPS 游戏桌面准星工具，屏幕中央始终显示可配置准星。

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![平台](https://img.shields.io/badge/平台-Windows-green) ![依赖](https://img.shields.io/badge/依赖-pystray%20%7C%20Pillow-orange)

## 功能特性

- **4 种准星样式**：十字 / 中心点 / 圆环 / 十字+点
- **7 色一键切换**：绿、红、蓝、黄、紫、白、橙
- **黑色描边**：任何游戏背景都能看清准星
- **配置面板**：滑块实时调参，所见即所得
- **系统托盘**：右键托盘图标，显示/隐藏/设置/退出
- **快捷键操作**：游戏内快速切换
- **配置自动记忆**：下次启动保持上次设置
- **置顶显示**：始终在最上层，全屏游戏也能看到

## 快捷键

| 键 | 功能 |
|---|---|
| F1 | 显示 / 隐藏准星 |
| F2 | 切换颜色 |
| F3 | 增大准星 |
| F4 | 减小准星 |
| F5 | 打开设置面板 |
| ESC | 退出程序 |

## 系统托盘

启动后任务栏右下角会出现 🎯 图标，右键可操作：

| 菜单项 | 功能 |
|--------|------|
| 点击托盘 | 显示 / 隐藏准星 |
| ⚙️ 设置面板 | 打开配置面板 |
| ❌ 退出 | 退出程序 |

## 配置面板

启动自动弹出设置面板（按 F5 也可打开），支持实时调整：

| 参数 | 范围 | 说明 |
|------|------|------|
| 样式 | 十字/点/圆环/十字+点 | 准星形态 |
| 颜色 | 7 色色块 | 点击切换 |
| 大小 | 2 ~ 60 px | 滑块调节 |
| 粗细 | 1 ~ 6 px | 线条粗细 |
| 中心点 | 0 ~ 8 px | 中心圆点大小 |
| 透明度 | 20% ~ 100% | 窗口透明度 |
| 描边 | 开/关 | 黑色轮廓提高可见性 |

## 安装 & 使用

### 方式一：直接运行（需要 Python）

```bash
# 安装依赖
pip install pystray pillow

# 运行
python crosshair.py
```

### 方式二：打包成 exe（推荐）

```bash
# 安装打包工具和依赖
pip install pyinstaller pystray pillow

# 打包
pyinstaller --onefile --noconsole crosshair.py
```

生成的 exe 在 `dist/CrosshairOverlay.exe`，双击即用，无需安装 Python。

> 💡 调试时去掉 `--noconsole` 参数，可以看到报错信息。

## 配置文件

首次运行自动创建配置文件：

- **Windows**: `%APPDATA%\CrosshairOverlay\config.json`

配置格式：

```json
{
  "size": 20,
  "thickness": 2,
  "gap": 4,
  "color": "#00FF00",
  "opacity": 0.9,
  "style": "cross",
  "dot_size": 2,
  "outline": true,
  "outline_color": "#000000"
}
```

也可以直接编辑配置文件，重启生效。

## 项目结构

```
crosshair-overlay/
├── crosshair.py      # 主程序
├── crosshair.spec    # PyInstaller 打包配置
└── README.md         # 本文件
```

## 技术栈

- **Python 3.8+**
- **tkinter** — 准星绘制 + 配置面板（Python 内置）
- **pystray** — 系统托盘图标
- **Pillow** — 托盘图标生成
- **PyInstaller** — 打包 exe

## License

MIT
