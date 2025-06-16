#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Feedback UI for Interactive Feedback MCP
增强版交互反馈UI - MCP服务器专用入口

根据PRD文档实现的增强版毛玻璃效果三栏布局UI
支持命令行参数和JSON结果输出
"""

import sys
import os
import json
import argparse

# 强制设置UTF-8编码
import locale
import codecs

# 设置默认编码
if sys.platform.startswith('win'):
    # Windows系统特殊处理
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 设置locale
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        pass

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.components.three_column_layout import ThreeColumnFeedbackUI

def main():
    """主函数 - 处理命令行参数并运行增强版UI"""
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Enhanced Interactive Feedback UI')
    parser.add_argument('--prompt', required=True, help='The prompt message to display')
    parser.add_argument('--output-file', required=True, help='Output file for the result')
    parser.add_argument('--predefined-options', default='', help='Predefined options separated by |||')
    
    args = parser.parse_args()
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 强制设置Qt应用程序编码（PySide6中QTextCodec已弃用）
    try:
        # PySide6中不再需要QTextCodec，默认就是UTF-8
        pass
    except:
        pass
    
    # 先设置临时应用程序名称，稍后会更新
    app.setApplicationName("Interactive Feedback MCP")
    app.setApplicationVersion("2.0.0")
    
    # 设置应用程序图标（用于Dock显示）
    from PySide6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), "ui", "resources", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        print(f"✅ 应用程序图标已设置: {icon_path}")
    else:
        print(f"⚠️ 应用程序图标文件不存在: {icon_path}")
    
    # 设置应用程序属性
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 强制设置深色模式，不受系统主题影响
    app.setStyle('Fusion')  # 使用Fusion样式避免系统主题影响
    from PySide6.QtGui import QPalette, QColor
    
    # 设置强制深色调色板
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    
    app.setPalette(dark_palette)
    
    # 禁用系统主题跟随，强制保持深色模式
    try:
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'  # 防止系统缩放影响
        os.environ['QT_SCALE_FACTOR'] = '1'  # 固定缩放比例
        # 禁用系统主题检测
        app.setProperty("_q_noSystemThemeChange", True)
    except Exception as e:
        print(f"⚠️ 设置系统主题隔离失败: {e}")
    
    print("🌙 强制深色模式已启用，不受系统主题影响")
    
    # 进一步强化深色模式设置，防止系统主题覆盖
    try:
        # 强制设置所有可能的深色相关属性
        app.setProperty("_q_unifiedTitleAndToolBarOnMac", False)
        app.setProperty("_qt_mac_wants_layer", True)
        
        # 禁用所有可能的系统主题检测
        from PySide6.QtCore import QSettings
        settings = QSettings()
        settings.setValue("appearance/color_scheme", "dark")
        settings.setValue("appearance/force_dark_mode", True)
        settings.sync()
        
        # 验证调色板是否正确应用
        current_palette = app.palette()
        window_color = current_palette.color(QPalette.Window)
        if window_color.red() > 128:  # 如果仍然是浅色
            print("⚠️ 检测到系统覆盖，重新应用深色调色板")
            app.setPalette(dark_palette)  # 重新应用
        
        print(f"📊 最终Window背景色: {current_palette.color(QPalette.Window).name()}")
        print(f"📊 最终Text文字色: {current_palette.color(QPalette.WindowText).name()}")
        
    except Exception as e:
        print(f"⚠️ 强化深色模式设置时出现警告: {e}")
    
    # 设置中文字体支持
    from PySide6.QtGui import QFont
    default_font = QFont()
    chinese_fonts = ['PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'SimHei', 'STHeiti']
    for font_name in chinese_fonts:
        default_font.setFamily(font_name)
        if QFont(font_name).exactMatch():
            break
    else:
        default_font = app.font()
    
    default_font.setPointSize(14)
    app.setFont(default_font)
    
    # 处理预定义选项
    predefined_options = []
    if args.predefined_options:
        predefined_options = args.predefined_options.split('|||')
        predefined_options = [opt.strip() for opt in predefined_options if opt.strip()]
    
    # 创建并显示UI
    ui = ThreeColumnFeedbackUI(args.prompt, predefined_options)
    
    # 获取调用方项目名称作为标题的一部分
    caller_project_name = ui._get_caller_project_name()
    app_title = f"Interactive Feedback MCP - {caller_project_name}"
    
    # 更新应用程序名称和窗口标题
    app.setApplicationName(app_title)
    ui.setWindowTitle(app_title)
    
    # 运行UI并获取结果
    ui.show()
    app.exec()
    
    # 获取反馈结果
    result = ui.feedback_result
    
    # 如果没有结果，创建默认结果
    if result is None:
        result = {
            'interactive_feedback': '',
            'images': []
        }
    
    # 将结果写入输出文件
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return 0
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 