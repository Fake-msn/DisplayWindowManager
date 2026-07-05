# DisplayWindowManager

> 一键操控多显示器窗口 —— 轻量、免费、开源

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows_10_11-blue)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/version-V0.52-brightgreen)](https://github.com/Fake-msn/DisplayWindowManager/releases)
[![GitHub Pages](https://img.shields.io/badge/pages-%E5%9C%A8%E7%BA%BF%E4%BD%93%E9%AA%8C-brightgreen)](https://Fake-msn.github.io/DisplayWindowManager/)

---

## 为什么需要这个工具？

你是否遇到过这些场景：
- 断开外接显示器后，第二屏幕的窗口"卡"在看不见的地方，无法拖回主屏
- 远程桌面分辨率不匹配，窗口飞到屏幕外
- 新开的窗口总是跑到不想用的显示器上，需要反复拖拽

**DisplayWindowManager** 就是为了解决这些问题而生。只需一键（或快捷键 `Ctrl+Shift+M`），即可将所有窗口从副屏移至主屏（或反向移动），彻底告别"找不到窗口"的痛苦。

> **温馨提示**：少数系统级窗口（如系统设置、任务管理器等）受 Windows 底层安全机制保护，无法被第三方软件移动，这是操作系统的安全设计，并非软件缺陷。绝大多数日常应用的窗口均可正常移动，详见下方[已知限制](#已知限制)。

---

## 核心功能

| 功能 | 说明 |
|------|------|
| **一键移动窗口** | 点击按钮或按 `Ctrl+Shift+M`，批量将所有窗口移动到目标显示器 |
| **双向移动** | 支持副屏→主屏 和 主屏→副屏 两种方向，随时切换 |
| **显示器屏蔽** | 阻止新窗口进入指定显示器，自动将其移走（`Ctrl+Shift+S` 开关） |
| **DPI 智能缩放** | 跨不同 DPI 缩放比例的显示器移动时，自动调整窗口大小 |
| **系统托盘** | 最小化到托盘，右键菜单快捷操作 |
| **全局热键** | `Ctrl+Shift+M` 移动窗口，`Ctrl+Shift+S` 切换屏蔽 |
| **零依赖** | 纯 Python + Win32 API，打包为单文件 EXE（约 10MB） |
| **浏览器界面** | 美观的 Web UI，通过浏览器访问和控制 |
| **多语言支持** | 中/英文界面一键切换，语言偏好自动保存 |

---

## 快速开始

### 方式一：下载 EXE（推荐）

从 [Releases](https://github.com/Fake-msn/DisplayWindowManager/releases) 页面下载最新的 `DisplayWindowManager.exe`，双击运行即可。

### 方式二：从源码运行

```bash
git clone https://github.com/Fake-msn/DisplayWindowManager.git
cd DisplayWindowManager
python display_window_manager.py
```

浏览器会自动打开 `http://127.0.0.1:18888`。

### 方式三：自行打包

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "DisplayWindowManager" display_window_manager.py
```

---

## 界面预览

### 主界面

清爽的 Web 界面，四个按钮完成所有操作：

- **移动窗口** — 一键移动所有窗口到目标显示器
- **屏蔽开关** — 开启/关闭显示器屏蔽
- **设置** — 修改移动方向、配置屏蔽规则
- **刷新** — 刷新窗口状态
- **语言切换** — 右上角一键切换中/英文界面，偏好自动保存

### 设置面板

- 移动方向：副屏→主屏 / 主屏→副屏
- 显示器屏蔽：选择屏蔽的显示器和目标显示器
- 启用后，被屏蔽显示器上的新窗口会被自动移走

### 系统托盘

- 托盘图标显示当前状态
- 右键菜单：移动窗口 / 切换屏蔽 / 打开界面 / 退出

---

## 竞品对比

| 维度 | **DisplayWindowManager** | DisplayFusion | PowerToys FancyZones | Actual Window Manager | Dual Monitor Tools |
|------|:--:|:--:|:--:|:--:|:--:|
| **价格** | **免费** | ¥232 起 | 免费 | ¥430 起 | 免费 |
| **开源** | **MIT** | 专有 | **MIT** | 专有 | GPL |
| **安装包大小** | **~10 MB** | ~130 MB | ~253 MB¹ | ~13 MB | ~5 MB |
| **一键窗口移动** | **✅ 热键+按钮** | ✅ 标题栏+热键 | ❌ 仅分区内 | ✅ 标题栏+热键 | ✅ 热键 |
| **显示器屏蔽** | **✅ 自动移走新窗口** | 显示器淡化 | ❌ 无 | 鼠标锁定 | 鼠标锁定 |
| **DPI 智能缩放** | **✅ 自动适配** | ✅ | ✅ | ✅ | ❌ |
| **系统托盘** | **✅** | ✅ | ❌ | ✅ | ❌ |
| **全局热键** | **✅ 两组** | ✅ 完全自定义 | ✅ 有限 | ✅ 完全自定义 | ✅ 有限 |
| **浏览器 UI** | **✅** | ❌ | ❌ | ❌ | ❌ |
| **零安装** | **✅ 单文件 EXE** | ❌ 需安装 | ❌ 需安装 | ❌ 需安装 | ✅ 绿色版 |
| **活跃维护** | **✅ 2026** | ✅ 2026 | ✅ 2026 | ✅ 2026 | ❌ 2023 |
| **多语言界面** | **✅ 中/英** | 部分汉化 | ✅ | ❌ | ❌ |

> ¹ PowerToys 整体安装包大小，FancyZones 为其中一个模块

### 我们的独特优势

1. **真正的一键操作** — 不需要在每个窗口标题栏上找按钮，Ctrl+Shift+M 一步到位
2. **显示器屏蔽** — 独家功能，从源头阻止新窗口进入指定显示器，不是简单的"变暗"
3. **零学习成本** — 只有一个 EXE 文件，双击即用，无需安装配置
4. **多语言界面** — 中/英文一键切换，中文用户和海外用户都能轻松使用
5. **浏览器 UI** — 无需学习复杂界面，在浏览器中直观操作
6. **极致轻量** — 不到 10MB 的单文件，内存占用极低

---

## 技术架构

```
display_window_manager.py
├── WindowManager       — 窗口枚举、显示器信息、窗口移动
├── DisplayShield       — 后台轮询、自动移动新窗口
├── ConfigManager       — JSON 配置读写
├── RequestHandler      — HTTP API 服务器
├── TrayWindow          — 系统托盘 + 全局热键
└── App                 — 主控制器
```

- **纯 Python 3.10+**，无第三方依赖
- **Win32 API (ctypes)** — 直接调用系统 API，无中间层损耗
- **HTTP Server + 浏览器 UI** — 稳定可靠，避免原生 GUI 框架的兼容性问题
- **PyInstaller** — 打包为单文件 EXE

---

## API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主界面 HTML |
| `/api/state` | GET | 获取状态（显示器、窗口、屏蔽状态） |
| `/api/move` | GET | 执行窗口移动 |
| `/api/toggle-shield` | GET | 切换屏蔽开关 |
| `/api/ping` | GET | 心跳检测 |
| `/api/quit` | GET | 退出程序 |
| `/api/save-settings` | POST | 保存设置 |
| `/api/set-language` | GET | 切换界面语言（`?lang=zh\|en`） |

---

## 路线图

- [x] 一键移动窗口
- [x] 双向移动方向切换
- [x] 显示器屏蔽
- [x] 全局热键
- [x] 系统托盘
- [x] DPI 缩放适配
- [x] 浏览器 UI
- [ ] 窗口列表预览（移动前确认）
- [ ] 自动启动（开机自启）
- [x] 多语言支持（中/英文）
- [ ] 窗口位置记忆与恢复

---

## 已知限制

### 系统级窗口无法移动

Windows 出于安全考虑，对部分系统关键窗口实施了**完整性级别隔离（Integrity Level / UIPI）**机制，阻止低权限进程操作高权限窗口。以下类型的窗口**无法**被本软件移动，这属于操作系统的安全设计，所有同类工具均受限：

| 窗口类型 | 说明 |
|----------|------|
| **任务管理器** | 系统进程管理窗口，受最高权限保护 |
| **系统设置** | Windows 设置应用及相关系统对话框 |
| **UAC 弹窗** | 用户账户控制提权确认窗口 |
| **其他高权限进程窗口** | 以管理员身份运行且启用了 UIPI 保护的应用程序 |

> 绝大多数日常应用（浏览器、办公软件、开发工具、聊天软件等）的窗口均可正常移动，不会受到影响。

### 为什么不能绕过？

这不是软件的技术缺陷，而是 Windows 的安全机制在发挥作用。绕过这一限制需要以管理员权限运行并对系统进行深度修改，这与本工具"轻量、安全、零依赖"的设计理念相悖，也可能带来安全隐患。

---

## 贡献

欢迎提 Issue 和 Pull Request！

## 许可

MIT License &copy; 2026 Fake-msn

---

## 链接

- [在线体验 (GitHub Pages)](https://Fake-msn.github.io/DisplayWindowManager/)
- [Release 下载](https://github.com/Fake-msn/DisplayWindowManager/releases)
- [问题反馈](https://github.com/Fake-msn/DisplayWindowManager/issues)