#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重构后的UI演示脚本
展示毛玻璃效果和模块化结构
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# 导入重构后的UI组件
from ui.components.main_window import FeedbackUI
from ui.styles.dark_theme import DarkThemeStyles

def demo_basic_ui():
    """演示基本UI功能"""
    prompt = """## 🎨 重构后的毛玻璃UI演示

### ✨ 新特性
- **模块化架构**: 组件、样式、工具分离
- **毛玻璃效果**: 现代化的半透明视觉效果
- **响应式设计**: 支持不同屏幕尺寸
- **主题系统**: 统一的深色主题

### 🔧 技术栈
- **PySide6**: 现代Qt界面框架
- **模块化设计**: 便于维护和扩展
- **CSS样式**: 丰富的视觉效果

### 🎯 请选择您的操作"""

    options = [
        "✨ 查看毛玻璃效果",
        "📁 了解文件结构", 
        "🎨 测试样式系统",
        "🔧 体验交互功能",
        "👍 满意当前实现"
    ]

    return prompt, options

def demo_markdown_ui():
    """演示Markdown渲染功能"""
    prompt = """# 📝 Markdown渲染演示

## 支持的语法

### 文本格式
- **粗体文本**
- *斜体文本*
- `行内代码`

### 列表
1. 有序列表项目1
2. 有序列表项目2
   - 嵌套无序列表
   - 另一个嵌套项目

### 代码块
```python
def hello_world():
    print("Hello, World!")
    return "毛玻璃效果很棒！"
```

### 引用
> 这是一个引用块
> 支持多行引用

### 表格
| 功能 | 状态 | 说明 |
|------|------|------|
| 毛玻璃效果 | ✅ | 已实现 |
| 模块化架构 | ✅ | 已完成 |
| 响应式设计 | ✅ | 支持 |

---

**请选择您要测试的功能：**"""

    options = [
        "🎨 测试更多样式效果",
        "📱 测试响应式布局",
        "🖼️ 测试图片粘贴功能",
        "⌨️ 测试快捷键功能"
    ]

    return prompt, options

def run_demo(demo_type="basic"):
    """运行演示"""
    # 设置应用程序
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication.instance() or QApplication(sys.argv)
    app.setPalette(DarkThemeStyles.get_dark_mode_palette(app))
    app.setStyle("Fusion")
    
    # 设置字体
    font = app.font()
    font.setPointSize(15)
    app.setFont(font)
    
    # 选择演示内容
    if demo_type == "markdown":
        prompt, options = demo_markdown_ui()
    else:
        prompt, options = demo_basic_ui()
    
    # 创建并运行UI
    ui = FeedbackUI(prompt, options)
    result = ui.run()
    
    # 显示结果
    if result and result['interactive_feedback']:
        print(f"\n✅ 用户反馈: {result['interactive_feedback']}")
        if result['images']:
            print(f"📷 包含图片: {len(result['images'])} 张")
    else:
        print("\n❌ 用户取消了操作")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        demo_type = sys.argv[1]
    else:
        demo_type = "basic"
    
    print(f"🚀 启动 {demo_type} 演示...")
    run_demo(demo_type)

if __name__ == "__main__":
    main() 