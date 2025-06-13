# UI 模块说明

## 📁 文件结构

```
ui/
├── __init__.py                 # UI模块初始化
├── README.md                   # 本说明文档
├── components/                 # 主要组件
│   ├── __init__.py
│   ├── main_window.py         # 主窗口组件
│   └── text_processing.py     # 文本处理组件
├── styles/                     # 样式定义
│   ├── __init__.py
│   ├── glassmorphism.py       # 毛玻璃样式
│   └── dark_theme.py          # 深色主题
└── widgets/                    # 自定义控件
    ├── __init__.py
    └── feedback_text_edit.py   # 支持图片粘贴的文本编辑器
```

## 🎨 样式系统

### 毛玻璃效果 (Glassmorphism)
- **文件**: `styles/glassmorphism.py`
- **特性**: 半透明背景、渐变边框、现代化视觉效果
- **组件覆盖**: 主窗口、文本区域、按钮、复选框等

### 深色主题
- **文件**: `styles/dark_theme.py`
- **功能**: 提供统一的深色主题调色板

## 🧩 组件架构

### 主窗口 (FeedbackUI)
- **文件**: `components/main_window.py`
- **职责**: 
  - 窗口管理和布局
  - 用户交互处理
  - 设置保存/加载
  - 快捷键管理

### 文本处理器 (TextProcessor)
- **文件**: `components/text_processing.py`
- **功能**:
  - Markdown 检测和转换
  - HTML 格式化
  - 文本预处理

### 自定义文本编辑器 (FeedbackTextEdit)
- **文件**: `widgets/feedback_text_edit.py`
- **特性**:
  - 图片粘贴支持
  - Base64 编码
  - 快捷键支持 (Ctrl+Enter)

## 🔧 使用方法

### 基本使用
```python
from ui.components.main_window import FeedbackUI

# 创建UI实例
ui = FeedbackUI("您的提示文本", ["选项1", "选项2"])

# 运行UI并获取结果
result = ui.run()
```

### 样式自定义
```python
from ui.styles.glassmorphism import GlassmorphismStyles

# 获取特定组件的样式
button_style = GlassmorphismStyles.submit_button()
```

## 🎯 设计原则

1. **模块化**: 每个组件职责单一，便于维护
2. **可扩展**: 样式和组件可独立扩展
3. **可复用**: 组件可在不同场景下复用
4. **清晰分离**: 样式、逻辑、数据处理分离

## 🚀 扩展指南

### 添加新样式
1. 在 `styles/` 目录下创建新的样式文件
2. 在 `styles/__init__.py` 中导入
3. 在组件中应用样式

### 添加新组件
1. 在 `components/` 或 `widgets/` 目录下创建组件文件
2. 继承适当的Qt基类
3. 应用相应的样式
4. 在 `__init__.py` 中导出

### 修改现有样式
- 直接修改 `styles/glassmorphism.py` 中的相应方法
- 样式会自动应用到所有使用该样式的组件

## 📝 注意事项

- Qt样式系统不支持CSS3的 `backdrop-filter` 属性
- 使用 `rgba` 透明度和渐变实现毛玻璃效果
- 所有样式都经过跨平台测试
- 支持高DPI显示屏 