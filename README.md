# 🗣️ Interactive Feedback MCP - 增强版

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io)

一个功能强大的 **MCP Server**，专为AI辅助开发工具（如 **Cursor**、**Claude Desktop** 和 **Windsurf**）设计，支持**人工智能在环工作流**，实现智能交互反馈系统。

## ✨ 功能特性

### 🎯 核心功能

* **💬 智能交互反馈** - 实时与AI助手交互，避免猜测性开发
* **🎥 视频内容分析** - AI驱动的视频内容理解和分析  
* **🖼️ 图片识别处理** - OCR文字识别和图像内容提取
* **📁 文件引用系统** - `@filename` 语法快速引用项目文件
* **🎨 现代化UI界面** - 支持图片粘贴和拖拽上传
* **📊 实时项目数据** - 动态显示Git状态、项目信息、文件统计

### 🎥 视频分析功能

* **支持格式**: MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V
* **分析类型**: 演示视频、代码教学、UI设计、通用内容
* **智能提取**: 关键帧提取和并行处理
* **详细元数据**: 时长、分辨率、编码、音频信息

### 🖼️ 图像处理功能

* **OCR文字识别** - 提取图片中的文字内容
* **内容分析** - AI理解图片内容和结构
* **多格式支持** - PNG, JPG, GIF, WebP
* **实时处理** - 拖拽即分析

### 🎨 增强版UI特性

* **三栏式布局** - 消息内容 + 智能推荐 + 项目信息
* **毛玻璃效果** - 现代化界面设计
* **中文字体优化** - 完美支持中文显示
* **动态窗口标题** - 显示当前项目名称
* **实时数据更新** - Git状态、文件统计自动刷新

## 💡 为什么使用？

在 **Cursor** 等环境中，每次提示都被视为独立请求，消耗您的月度限额。这在需要迭代优化或澄清误解时效率很低。

**Interactive Feedback MCP** 通过**工具调用暂停机制**解决这个问题：

* 🔄 模型可以暂停并请求澄清，而不是完成请求
* 🎯 在单个请求内进行多轮反馈循环
* 💰 工具调用不计入高级API使用量

### 核心优势

* **💰 减少API调用** - 避免基于猜测的错误代码生成
* **✅ 更少错误** - 行动前澄清，减少错误代码
* **⏱️ 更快迭代** - 快速确认胜过调试错误
* **🎮 更好协作** - 单向指令变为双向对话
* **🚀 提升效率** - 把 Cursor 500次请求变2500次

## 📦 安装

### 前置条件

* **Python 3.10+**
* **uv 包管理器**
* **ffmpeg 和 ffprobe**（用于视频分析）

### 安装 uv

```bash
# Windows
pip install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS
brew install uv
```

### 安装 ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# 下载 https://ffmpeg.org/download.html
```

### 获取代码

```bash
git clone https://github.com/zengxiaolou/interactive-feedback-mcp.git
cd interactive-feedback-mcp
```

### 环境配置

```bash
# 复制配置文件模板
cp config.env.example config.env

# 编辑配置文件，填入您的API密钥
nano config.env
```

## ⚙️ 配置

### 1. MCP 客户端配置

#### Cursor 配置

在 `mcp.json` 文件中添加：

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "uv",
      "args": ["--directory", "/path/to/interactive-feedback-mcp", "run", "server.py"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback", "video_analysis"]
    }
  }
}
```

#### Claude Desktop 配置

在 `claude_desktop_config.json` 文件中添加：

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "uv", 
      "args": ["--directory", "/path/to/interactive-feedback-mcp", "run", "server.py"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback", "video_analysis"]
    }
  }
}
```

**⚠️ 重要**: 将 `/path/to/interactive-feedback-mcp` 替换为实际克隆路径

### 2. AI 助手规则配置

在 **Cursor Settings > Rules > User Rules** 中添加：

```
如果需求或指令不清楚，请使用 interactive_feedback 工具向用户询问澄清问题后再继续，不要做假设。尽可能通过 interactive_feedback MCP 工具向用户提供预定义选项以便快速决策。

每当您即将完成用户请求时，请调用 interactive_feedback 工具请求用户反馈后再结束流程。如果反馈为空，您可以结束请求，不要循环调用工具。
```

### 3. 环境配置文件

编辑 `config.env` 文件：

```env
# Gemini AI API 配置
GEMINI_API_KEY=你的_gemini_api_密钥
GEMINI_API_URL=https://你的_gemini_api_端点

# AI 分析配置
AI_ANALYSIS_TIMEOUT=30
AI_ANALYSIS_RETRY_COUNT=2

# 调试配置
DEBUG_MODE=false
LOG_LEVEL=INFO
```

## 🚀 使用方法

### 交互反馈

```
请使用 interactive_feedback 询问我需要什么类型的数据库设计
```

### 视频分析

```
请使用 video_analysis 工具分析这个演示视频：/path/to/demo.mp4
```

### 图片处理

```
请分析这张截图中的代码错误（支持拖拽上传图片）
```

### 高级用法

```bash
# 指定视频分析类型
请分析这个代码教学视频，使用 code 类型分析：/path/to/tutorial.mp4

# 自定义参数
分析视频 /path/to/demo.mp4，参数：分析类型=ui，最大帧数=8，包含元数据=是
```

## 🛠️ 工具说明

### interactive_feedback

智能交互反馈工具，支持：

* ✅ Markdown 格式消息显示
* 🎯 预定义选项快速选择
* 🖼️ 图片上传和粘贴支持
* 📁 文件引用系统（`@filename`）
* 💾 自动保存草稿和智能建议
* 🎨 现代化三栏布局界面

**参数**：

* `message` (必需): 问题或消息内容
* `predefined_options` (可选): 预定义选项列表
* `project_root` (可选): 项目根目录路径

### video_analysis

视频内容分析工具，支持：

* 📹 多种视频格式支持
* 🤖 AI 驱动的内容理解
* 🎞️ 智能帧提取和分析
* 📊 详细元数据提取

**参数**：

* `video_path` (必需): 视频文件路径
* `analysis_type` (可选): 分析类型 (demo/code/ui/general)
* `max_frames` (可选): 最大帧数 (1-10)
* `include_metadata` (可选): 是否包含元数据

## 📖 使用示例

### 基础交互

```bash
# AI 询问用户澄清需求
请使用 interactive_feedback 询问我希望实现什么功能

# 视频内容分析
请分析这个产品演示视频：/Users/demo/product_demo.mp4
```

### 高级功能

```bash
# 带选项的交互
请使用 interactive_feedback 询问我的数据库偏好，选项包括：MySQL、PostgreSQL、MongoDB

# 代码视频分析
请分析这个Python教程视频，使用code类型：/tutorials/python_basics.mp4
```

## 🎨 界面特性

### 三栏式布局

* **左侧面板**: 💬 消息内容显示（支持Markdown）
* **中间面板**: 🎯 智能推荐选项（支持多选）
* **右侧面板**: 📊 项目信息（实时Git状态）

### 增强功能

* 🖼️ **图片预览**: 拖拽上传，实时预览
* 📝 **输入框**: 180px高度，支持多行输入
* 🎨 **毛玻璃效果**: 现代化界面设计
* 🌍 **中文优化**: 完美支持中文字体显示
* 📱 **响应式设计**: 自适应不同屏幕尺寸

## 🔧 开发与测试

### 运行测试

```bash
# 测试视频分析功能
python test_video_analysis_mcp.py

# 测试完整功能
uv run server.py
```

### 开发环境

```bash
# 安装开发依赖
uv sync

# 启动开发模式
DEBUG_MODE=true uv run server.py
```

## 🎯 性能优化

### 视频处理优化

* ⚡ 自动帧缩放到 640x360
* 🔄 并行帧提取（4线程）
* 🎯 智能间隔提取关键帧
* 📦 大文件自动优化参数

### 缓存机制

* 🗂️ 多层缓存系统
* 🔄 智能缓存失效
* ⚡ 预加载常用组件
* 📊 性能监控

## 🐛 故障排除

### 常见问题

**1. "视频分析器不可用"**

```bash
# 检查 ffmpeg 安装
ffmpeg -version
ffprobe -version
```

**2. "配置加载失败"**

```bash
# 检查配置文件
cat config.env
# 确保 API 密钥正确配置
```

**3. "MCP 连接失败"**

```bash
# 检查路径配置
# 确保 uv 可执行
# 验证权限设置
```

**4. "界面乱码问题"**

已内置中文字体优化，支持：
- macOS: PingFang SC, Hiragino Sans GB
- Windows: Microsoft YaHei, SimHei
- 自动编码检测和转换

### 调试模式

```bash
DEBUG_MODE=true uv run server.py
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南

1. 🍴 Fork 本仓库
2. 🌟 创建功能分支
3. 💾 提交更改
4. 📤 推送到分支
5. 🔄 创建 Pull Request

## 📊 项目统计

* **语言**: Python 100.0%
* **许可证**: MIT License
* **支持平台**: macOS, Windows, Linux
* **AI工具支持**: Cursor, Claude Desktop, Windsurf

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

* **原始开发**: Fábio Ferreira (@fabiomlferreira)
* **功能增强**: Pau Oliva (@pof)
* **UI 优化**: kele527 (@kele527)
* **视频分析**: 增强版集成
* **界面重构**: zengxiaolou (@zengxiaolou)

---

**🚀 立即开始使用，体验AI驱动的智能开发工作流！**

> 让每一次与AI的交互都更加精准、高效、智能。
