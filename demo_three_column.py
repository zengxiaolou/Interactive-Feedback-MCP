#!/usr/bin/env python3
"""
三列布局毛玻璃UI演示
Demo for Three Column Layout with Glass Morphism Effects
"""

import sys
import os
from typing import List, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.components.three_column_layout import ThreeColumnFeedbackUI

def demo_three_column_ui():
    """演示三列布局UI"""
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 启用高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # 设置应用程序属性
    app.setApplicationName("Interactive Feedback MCP - Three Column Layout")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Interactive Feedback MCP")
    
    # 设置全局字体
    font = QFont("SF Pro Display", 12)
    app.setFont(font)
    
    # 创建演示数据
    prompt = """## 🎨 三列布局毛玻璃UI演示

### ✨ 新特性
- **三栏式布局**: 左侧消息内容，中间智能选项，右侧项目信息
- **现代化毛玻璃效果**: 半透明背景，模糊效果，渐变边框
- **智能上下文**: 自动获取Git状态和项目信息
- **响应式设计**: 支持不同屏幕尺寸和分辨率

### 🔧 技术栈
- **PySide6**: 现代Qt界面框架
- **模块化架构**: 组件、样式、工具分离
- **现代化主题**: 统一的深色毛玻璃主题
- **智能交互**: 多选项支持和自定义输入

### 🎯 请选择您的操作"""

    predefined_options = [
        "🎨 调整毛玻璃效果的透明度和模糊程度",
        "📐 优化三列布局的比例和间距",
        "🌈 更换主题颜色和渐变效果",
        "⚡ 提升UI响应速度和动画效果",
        "📱 适配不同屏幕尺寸和分辨率",
        "🔧 添加更多自定义配置选项",
        "🎭 实现更多视觉特效和交互动画",
        "📊 集成更多项目信息和统计数据"
    ]
    
    # 创建三列布局UI
    ui = ThreeColumnFeedbackUI(prompt, predefined_options)
    
    # 显示窗口
    ui.show()
    
    # 运行应用程序
    result = app.exec()
    
    return result

if __name__ == "__main__":
    print("🚀 启动三列布局毛玻璃UI演示...")
    result = demo_three_column_ui()
    print(f"✅ 演示结束，退出代码: {result}") 