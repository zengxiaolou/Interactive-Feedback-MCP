#!/usr/bin/env python3
"""
Interactive Feedback MCP 应用图标演示
展示新设计的应用图标和界面
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from ui.components.three_column_layout import ThreeColumnFeedbackUI
from ui.resources.icon_manager import icon_manager

def main():
    """主演示函数"""
    app = QApplication(sys.argv)
    
    # 设置应用级别的图标
    if icon_manager.is_available():
        app_icon = icon_manager.get_app_icon()
        app.setWindowIcon(app_icon)
        print("🎨 应用图标已设置")
        
        # 显示图标信息
        icon_info = icon_manager.get_icon_info()
        print(f"📁 图标目录: {icon_info['icons_dir']}")
        print(f"📊 可用图标文件: {len(icon_info['files'])} 个")
        for file_info in icon_info['files']:
            print(f"   - {file_info['name']} ({file_info['size']} bytes)")
    else:
        print("❌ 图标资源不可用")
    
    # 创建演示窗口
    demo_prompt = """
# 🎨 Interactive Feedback MCP - 应用图标演示

欢迎体验全新设计的Interactive Feedback MCP应用！

## ✨ 新功能亮点：

### 🎯 专业应用图标
- **设计理念**：现代化对话反馈主题
- **视觉风格**：蓝紫渐变 + 毛玻璃效果
- **多尺寸支持**：16px - 512px 完整尺寸系列
- **系统集成**：支持任务栏、系统托盘显示

### 🎨 图标设计特色
- **主色调**：科技蓝 (#2196F3) + 活力紫 (#9C27B0)
- **核心元素**：对话框 + 交互点 + 文本线条
- **设计风格**：简约现代，识别度高
- **适用场景**：桌面应用、Web应用、移动端

### 🔧 技术实现
- **图标生成**：基于Qt绘图引擎，矢量化设计
- **资源管理**：智能缓存，多尺寸自适应
- **系统兼容**：支持Windows、macOS、Linux
- **高DPI支持**：在高分辨率屏幕上显示清晰

## 🚀 使用体验
请注意观察：
1. **窗口标题栏**的应用图标
2. **任务栏**中的应用图标
3. **系统托盘**（如果支持）的图标显示
4. 不同系统下的图标适配效果

## 💡 设计理念
图标设计体现了Interactive Feedback MCP的核心价值：
- **交互性**：对话框元素突出人机交互
- **智能化**：渐变色彩体现AI智能特性  
- **专业性**：简洁设计符合开发工具定位
- **现代感**：毛玻璃风格契合当代UI趋势
"""
    
    demo_options = [
        "🎨 图标设计很棒，视觉效果出色",
        "👍 图标在系统中显示正常",
        "🔍 需要查看不同尺寸的图标效果", 
        "🎯 图标很好地体现了应用特色",
        "💡 建议调整图标的某些设计元素",
        "🖥️ 测试在不同系统下的显示效果",
        "📱 希望看到移动端适配版本",
        "🔄 需要生成更多尺寸的图标",
        "📊 查看图标的技术实现细节",
        "✨ 图标完美，可以正式使用"
    ]
    
    # 创建UI实例
    ui = ThreeColumnFeedbackUI(demo_prompt, demo_options)
    
    # 显示窗口
    ui.show()
    
    # 运行应用
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 