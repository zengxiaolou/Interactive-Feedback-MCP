#!/usr/bin/env python3
"""
图片预览功能演示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from ui.components.three_column_layout import ThreeColumnFeedbackUI

def main():
    """主演示函数"""
    app = QApplication(sys.argv)
    
    # 创建演示窗口
    demo_prompt = """
# 🖼️ 图片预览功能演示

欢迎使用Interactive Feedback MCP的图片预览功能！

## 📋 测试步骤：
1. **复制图片**：截图或复制任意图片文件
2. **粘贴图片**：在右侧输入框中按 `Ctrl+V` 粘贴
3. **查看预览**：图片会自动在中间栏显示预览
4. **管理图片**：可以添加多张图片，点击❌删除不需要的图片
5. **提交测试**：选择下方选项提交，查看图片是否正确传输

## ✨ 功能特点：
- 🎯 **智能缩放**：自动调整图片大小适应预览区域
- 🔄 **多图支持**：支持粘贴多张图片，水平排列显示
- 🗑️ **便捷删除**：每张图片都有独立的删除按钮
- 📱 **高DPI支持**：在高分辨率屏幕上显示清晰
- 💾 **Base64编码**：图片自动转换为Base64格式传输

## 🎨 UI设计：
- 采用玻璃拟态设计风格
- 半透明背景，优雅的视觉效果
- 响应式布局，适应不同窗口大小
"""
    
    demo_options = [
        "✅ 图片粘贴功能测试通过",
        "✅ 图片预览显示正常", 
        "✅ 多图片管理功能正常",
        "✅ 删除功能工作正常",
        "✅ 图片传输功能正常",
        "🔄 需要进一步优化",
        "❌ 发现问题需要修复",
        "📝 提供改进建议",
        "🎯 测试其他功能",
        "✨ 功能完美，结束测试"
    ]
    
    # 创建UI实例
    ui = ThreeColumnFeedbackUI(demo_prompt, demo_options)
    
    # 设置窗口标题
    ui.setWindowTitle("🖼️ Interactive Feedback MCP - 图片预览功能演示")
    
    # 显示窗口
    ui.show()
    
    # 运行应用
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 