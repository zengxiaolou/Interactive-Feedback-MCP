#!/usr/bin/env python3
"""
快捷键测试演示
测试新的快捷键逻辑：Enter发送，Shift+Enter换行
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from ui.components.three_column_layout import ThreeColumnFeedbackUI

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建测试消息
    test_message = """
    🎯 快捷键测试演示
    
    请测试以下快捷键功能：
    
    ✅ Enter键：直接发送消息
    🔄 Shift+Enter：换行（不发送）
    ❌ Esc键：取消/关闭窗口
    
    在下方的自定义输入框中测试这些快捷键！
    """
    
    # 创建选项
    options = [
        "✅ Enter键发送功能正常",
        "🔄 Shift+Enter换行功能正常", 
        "❌ Esc取消功能正常",
        "🎯 两栏布局显示正常",
        "💬 所有功能都工作正常"
    ]
    
    # 创建UI
    ui = ThreeColumnFeedbackUI(test_message, options)
    
    print("🚀 快捷键测试演示启动")
    print("📝 请在自定义输入框中测试：")
    print("   • Enter键：发送消息")
    print("   • Shift+Enter：换行")
    print("   • Esc键：关闭窗口")
    
    # 运行UI
    result = ui.run()
    
    if result:
        print("\n✅ 测试结果:")
        print(f"📝 反馈内容: {result['interactive_feedback']}")
        if result['images']:
            print(f"🖼️ 图片数量: {len(result['images'])}")
    else:
        print("\n❌ 用户取消了操作")

if __name__ == "__main__":
    main() 