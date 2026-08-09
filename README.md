# MC 数据包翻译工具 (Minecraft DataPack Translation Tool)

一个用于**手动编辑** Minecraft Java 版数据包（Datapack）文本的桌面工具。直接打开 `.zip` 数据包，自动抽取 JSON 与 MCFunction 中所有可翻译文本，在表格中逐条编辑后，一键导出翻译后的数据包。

## 功能特性

### 核心功能
- **一键打开数据包** - 支持拖拽或文件对话框打开 `.zip` 数据包
- **深度文本抽取** - 自动扫描数据包内全部 `.json` 与 `.mcfunction` 文件
- **表格化编辑** - 文件 / 路径(行号) / 原文 / 译文 四列布局，双击即可编辑
- **安全回写** - 保留原始压缩结构，输出为 `xxx_translated.zip`

### 支持的文本类型
- **JSON 字段**：`title`、`description`、`displayName`、`text`、`subtitle`、`name`
- **MCFunction 命令**：`tellraw`、`title`、`bossbar`、`team`、`scoreboard`、`item`（含 `execute ... run` 形式）

### 界面特色
- **深色 / 浅色主题** - 一键切换，记忆用户偏好
- **中英双语界面** - 内置 `zh_CN` / `en_US` 语言包，设置中即时切换
- **拖拽打开** - 将数据包拖入窗口即可开始
- **最近文件** - 快速回访最近打开的 5 个数据包
- **可配置抽取规则** - 勾选需要翻译的 JSON 字段与命令类型
- **原版命名空间过滤** - 可隐藏 `minecraft:` 命名空间的文本

### 技术特性
- **多线程解析** - 大数据包解析不卡界面
- **全版本兼容** - 支持所有 Java 版数据包格式

## 安装使用

### 方法一：直接运行源码
```bash
git clone https://github.com/BiliBiliACEGE/Minecraft-DataPack-Translation-Tool.git
cd Minecraft-DataPack-Translation-Tool

# 安装依赖（推荐使用 uv）
uv pip install PyQt6 PyQt6-Fluent-Widgets pyinstaller
# 或使用 pip
pip install PyQt6 PyQt6-Fluent-Widgets pyinstaller

# 运行
python main.py
```

### 方法二：使用打包好的 exe
从 [Releases](https://github.com/BiliBiliACEGE/Minecraft-DataPack-Translation-Tool/releases) 下载 `MC DataPack Translation Tool.exe`，双击即可运行。

## 使用指南

1. **打开数据包** - 拖拽 `.zip` 文件到窗口，或点击「加载数据包」/菜单「文件 → 打开数据包」（`Ctrl+O`）
2. **编辑翻译** - 在表格「译文」列双击单元格输入翻译
3. **（可选）调整设置** - 菜单「编辑 → 设置」（`Ctrl+,`）中勾选字段、命令类型、界面语言
4. **保存翻译** - 点击「保存翻译」，将生成 `xxx_translated.zip`

## 项目结构

```
Minecraft-DataPack-Translation-Tool/
├── main.py          # 主程序（窗口、解析、回写、多语言、设置）
├── Style.py         # 主题样式表（深色/浅色 QSS）
├── langs/           # 语言包
│   ├── zh_CN.json   # 简体中文
│   └── en_US.json   # English
├── icon.ico         # 应用图标
├── main.spec        # PyInstaller 打包配置
├── 打包.bat         # 一键打包脚本
├── LICENSE          # MIT 开源协议
└── README.md        # 项目文档
```

## 技术栈

- **Python 3.11+**
- **PyQt6** - GUI 框架
- **PyQt6-Fluent-Widgets** - Fluent Design 组件库
- **PyInstaller** - 打包工具

## 自行打包

```bash
# 使用打包脚本
打包.bat

# 或手动执行
pyinstaller main.py --noconsole --icon=icon.ico --add-data "langs;langs"
```

打包产物位于 `dist/` 目录。

## 许可证

本项目采用 [MIT 许可证](LICENSE) 开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 联系

- 作者：Ace
- 提交 [GitHub Issue](https://github.com/BiliBiliACEGE/Minecraft-DataPack-Translation-Tool/issues)
