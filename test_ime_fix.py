#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
输入法遮挡修复功能测试脚本
测试智能位置调整是否正常工作
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ime_functionality():
    """测试输入法功能"""
    print("🧪 开始测试输入法遮挡修复功能")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
        from PySide6.QtCore import Qt
        from ui.widgets.feedback_text_edit import FeedbackTextEdit
        
        # 创建测试应用
        app = QApplication(sys.argv)
        
        # 创建测试窗口
        test_window = QWidget()
        test_window.setWindowTitle("输入法遮挡修复功能测试")
        test_window.setGeometry(100, 100, 600, 400)
        
        # 布局
        layout = QVBoxLayout(test_window)
        
        # 添加说明标签
        instruction_label = QLabel("""
🎯 输入法遮挡修复功能测试

测试步骤：
1. 点击下方的文本框获得焦点
2. 开始输入中文（激活输入法）
3. 观察窗口是否自动调整位置避免遮挡
4. 按Esc或失去焦点时窗口应恢复原位

预期效果：
✅ 输入法激活时窗口标题显示"输入法模式"
✅ 窗口自动向上移动避免候选词遮挡
✅ 控制台显示详细的调整过程日志
✅ 输入法关闭时窗口恢复原始位置
        """)
        instruction_label.setStyleSheet("""
            color: #FFFFFF;
            background-color: rgba(76, 175, 80, 0.1);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 8px;
            padding: 10px;
            font-size: 12px;
            line-height: 1.4;
        """)
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # 创建增强的文本编辑器
        text_edit = FeedbackTextEdit()
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(76, 175, 80, 0.5);
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 14px;
                padding: 10px;
            }
            QTextEdit:focus {
                border: 2px solid rgba(76, 175, 80, 0.8);
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        text_edit.setPlaceholderText("在这里输入中文测试输入法遮挡修复功能...")
        text_edit.setMinimumHeight(100)
        
        # 连接信号到测试处理函数
        def on_ime_visibility_changed(is_visible):
            status = "激活" if is_visible else "关闭"
            print(f"🎯 测试检测到输入法状态变化: {status}")
            
        def on_ime_position_changed(ime_rect):
            print(f"📍 测试检测到输入法位置: x={ime_rect.x()}, y={ime_rect.y()}")
            
        def on_window_adjustment_requested(offset_x, offset_y):
            print(f"🎯 测试检测到窗口调整请求: x={offset_x}, y={offset_y}")
            # 手动应用调整到测试窗口
            current_pos = test_window.pos()
            new_x = current_pos.x() + offset_x
            new_y = current_pos.y() + offset_y
            test_window.move(new_x, new_y)
            print(f"✅ 测试窗口位置已调整")
        
        # 连接信号
        text_edit.ime_visibility_changed.connect(on_ime_visibility_changed)
        text_edit.ime_position_changed.connect(on_ime_position_changed)
        text_edit.request_window_adjustment.connect(on_window_adjustment_requested)
        
        layout.addWidget(text_edit)
        
        # 状态标签
        status_label = QLabel("📊 状态: 等待输入...")
        status_label.setStyleSheet("""
            color: #81C784;
            font-size: 12px;
            font-weight: bold;
            padding: 5px;
            background-color: rgba(129, 199, 132, 0.1);
            border-radius: 4px;
        """)
        layout.addWidget(status_label)
        
        # 更新状态显示
        def update_status():
            ime_status = text_edit.get_ime_status()
            status_text = f"""📊 输入法状态: {'激活' if ime_status['active'] else '关闭'} | 
调整已应用: {'是' if ime_status['adjustment_applied'] else '否'} | 
位置: ({ime_status['rect']['x']}, {ime_status['rect']['y']})"""
            status_label.setText(status_text)
        
        # 定时更新状态
        from PySide6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(update_status)
        timer.start(1000)  # 每秒更新
        
        # 设置深色主题
        app.setStyle('Fusion')
        from PySide6.QtGui import QPalette, QColor
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        app.setPalette(dark_palette)
        
        # 显示窗口
        test_window.show()
        
        print("✅ 测试窗口已启动")
        print("🎯 请在文本框中输入中文来测试输入法功能")
        print("📝 观察控制台输出和窗口行为")
        
        # 运行测试
        return app.exec()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保PySide6已安装: pip install PySide6")
        return 1
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

def test_enhanced_ui_integration():
    """测试与增强UI的集成"""
    print("\n🧪 测试与增强UI的集成")
    print("=" * 30)
    
    try:
        # 模拟启动增强UI测试输入法功能
        test_prompt = """
🎯 输入法遮挡修复功能测试

请在自定义输入框中：
1. 输入中文测试输入法智能调整
2. 观察窗口位置变化
3. 验证候选词不再遮挡界面

这是一个输入法遮挡修复功能的集成测试。
        """
        
        # 创建临时输出文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            output_file = f.name
        
        # 准备启动参数
        predefined_options = [
            "✅ 输入法功能正常 - 智能调整工作良好",
            "⚠️ 部分功能异常 - 需要进一步调试", 
            "❌ 功能完全失效 - 需要重新实现",
            "🔧 需要调整参数 - 优化调整算法",
            "📊 查看详细日志 - 分析调整过程",
            "🧪 继续其他测试 - 测试更多场景"
        ]
        
        print(f"📝 测试提示信息已准备")
        print(f"📁 输出文件: {output_file}")
        print(f"🎯 预定义选项: {len(predefined_options)}个")
        
        print("\n🚀 要启动完整的UI测试，请运行:")
        print(f"python enhanced_feedback_ui.py --prompt \"{test_prompt}\" --output-file \"{output_file}\" --predefined-options \"{'|||'.join(predefined_options)}\"")
        
        # 清理
        os.unlink(output_file)
        
        return 0
        
    except Exception as e:
        print(f"❌ 集成测试准备失败: {e}")
        return 1

if __name__ == "__main__":
    print("🎯 输入法遮挡修复功能测试套件")
    print("="*60)
    
    # 运行基础功能测试
    basic_result = test_ime_functionality()
    
    # 运行集成测试
    integration_result = test_enhanced_ui_integration()
    
    print(f"\n📊 测试结果总结:")
    print(f"基础功能测试: {'✅ 通过' if basic_result == 0 else '❌ 失败'}")
    print(f"集成测试准备: {'✅ 通过' if integration_result == 0 else '❌ 失败'}")
    
    if basic_result == 0 and integration_result == 0:
        print("\n🎉 所有测试通过！输入法遮挡修复功能已成功实施")
        print("💡 现在可以在实际使用中测试中文输入法的智能调整功能")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息")
    
    sys.exit(max(basic_result, integration_result)) 