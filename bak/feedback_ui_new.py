# Interactive Feedback MCP - Enhanced UI with Three Column Layout
# 交互式反馈MCP - 三栏式布局增强版UI

import sys
import os
from typing import Optional, List, TypedDict

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.components.three_column_layout import ThreeColumnFeedbackUI

class FeedbackResult(TypedDict):
    interactive_feedback: str
    images: List[str]

def show_interactive_feedback(
    message: str,
    predefined_options: Optional[List[str]] = None
) -> FeedbackResult:
    """
    显示三栏式交互反馈界面
    
    Args:
        message: 要显示的消息内容
        predefined_options: 预定义选项列表
        
    Returns:
        FeedbackResult: 包含用户反馈和图片的结果
    """
    # 创建应用程序实例
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setApplicationName("Interactive Feedback MCP")
        app.setApplicationVersion("4.2")
        app.setOrganizationName("Interactive Feedback MCP")
        
        # 设置默认字体
        font = QFont("SF Pro Display", 15)
        if not font.exactMatch():
            font = QFont("Segoe UI", 15)
        if not font.exactMatch():
            font = QFont("Arial", 15)
        app.setFont(font)
        
        # 启用高DPI支持
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建并显示三栏式UI
    ui = ThreeColumnFeedbackUI(message, predefined_options)
    result = ui.run()
    
    return result

def main():
    """主函数 - 用于测试"""
    # 测试消息
    test_message = """
## 🎯 三栏式布局设计实现

### 📊 智能分析结果
- **意图识别**: 界面设计优化 (置信度: 95%)
- **紧急程度**: 3/5 (界面改进)
- **技术栈**: PySide6, CSS, 毛玻璃效果
- **预估复杂度**: 中等

### 💡 设计要求
根据提供的设计图，需要实现三栏式布局：
- **左栏**: 消息内容和上下文相关数据
- **中栏**: 智能推荐选项
- **右栏**: MCP项目信息、git状态、自定义输入框和按钮

### 🎨 视觉效果
- 保持毛玻璃效果
- 现代化的界面设计
- 响应式布局
- 优雅的交互体验

### 🔧 技术实现
- 使用QSplitter实现三栏分割
- 保持现有的毛玻璃样式系统
- 集成项目信息和Git状态显示
- 支持自定义输入和多选操作
    """
    
    # 测试选项
    test_options = [
        "🔄 进一步优化三栏布局比例",
        "🎨 调整毛玻璃效果透明度",
        "📱 优化响应式设计",
        "🔍 添加更多项目信息展示",
        "⚡ 优化界面性能和流畅度",
        "🎯 完善用户交互体验",
        "📊 集成更多数据可视化",
        "🛠️ 添加自定义主题选项",
        "🔧 优化代码结构和模块化",
        "📝 完善文档和使用说明"
    ]
    
    # 显示界面
    result = show_interactive_feedback(test_message, test_options)
    
    # 输出结果
    print("=== 用户反馈结果 ===")
    print(f"反馈内容: {result['interactive_feedback']}")
    print(f"图片数量: {len(result['images'])}")
    
    return result

if __name__ == "__main__":
    main() 