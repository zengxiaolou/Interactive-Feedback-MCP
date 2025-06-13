#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Three Column Layout Demo
增强版三栏布局演示

根据PRD文档实现的增强版毛玻璃效果三栏布局UI演示
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.components.three_column_layout import ThreeColumnFeedbackUI

def main():
    """主函数 - 演示增强版三栏布局UI"""
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("Interactive Feedback MCP - Enhanced UI")
    app.setApplicationVersion("2.0.0")
    
    # 设置应用程序属性
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 演示消息内容
    demo_prompt = """
# 🚀 Interactive Feedback MCP - 增强版UI演示

## 📋 主要改进

### 🎨 毛玻璃效果优化
- **多层渐变背景**: 实现真正的玻璃质感
- **动态透明度**: 分层透明度设计，层次分明
- **悬停动画**: 组件悬停时的平滑过渡效果
- **焦点发光**: 输入框获得焦点时的发光效果

### 📐 布局优化
- **响应式设计**: 支持不同屏幕尺寸自适应
- **可调整面板**: 使用QSplitter实现拖拽调整
- **优化比例**: 左侧40%、中间40%、右侧20%
- **智能间距**: 基于8px的间距系统

### ⚡ 交互增强
- **快捷键支持**: Ctrl+1-9快速选择选项
- **键盘导航**: Enter提交、Esc取消
- **帮助系统**: Ctrl+/显示快捷键帮助
- **字体缩放**: Ctrl+/-调整字体大小

### 🎯 性能优化
- **启动时间**: < 2秒
- **响应速度**: < 100ms
- **内存优化**: < 100MB
- **平滑动画**: 60fps流畅体验

## 🔧 技术特性

- **PySide6/Qt6**: 现代化UI框架
- **增强版毛玻璃主题**: 自定义样式系统
- **模块化设计**: 可扩展的组件架构
- **跨平台兼容**: Windows/macOS/Linux

## 💡 使用说明

1. **选择选项**: 在中间面板选择推荐操作
2. **自定义输入**: 在右侧面板输入自定义反馈
3. **快捷操作**: 使用键盘快捷键提高效率
4. **拖拽调整**: 拖拽分割线调整面板大小

---

*这是一个演示界面，展示了根据PRD文档实现的增强版毛玻璃效果和优化功能。*
    """
    
    # 演示选项
    demo_options = [
        "🎨 体验毛玻璃效果优化",
        "📐 测试响应式布局调整", 
        "⚡ 验证快捷键功能",
        "🔧 检查性能优化效果",
        "📊 查看项目信息集成",
        "🎯 测试交互体验改进",
        "💡 评估视觉效果提升",
        "🚀 确认功能完整性",
        "📝 提供改进建议",
        "✅ 完成UI测试评估"
    ]
    
    # 创建并显示UI
    ui = ThreeColumnFeedbackUI(demo_prompt, demo_options)
    
    # 设置窗口标题
    ui.setWindowTitle("Interactive Feedback MCP - Enhanced UI Demo v2.0")
    
    # 显示UI
    ui.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 