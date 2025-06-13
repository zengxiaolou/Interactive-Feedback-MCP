#!/usr/bin/env python3
"""
Configuration Management Demo for Interactive Feedback MCP
配置管理系统演示脚本
"""

import sys
import os
from PySide6.QtWidgets import QApplication

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.utils.config_manager import (
    global_config_manager, ThemeType, LanguageType, 
    ThemeManager, ConfigManager
)
from ui.components.three_column_layout import ThreeColumnFeedbackUI

def demo_config_operations():
    """演示配置操作"""
    print("🔧 配置管理系统演示")
    print("=" * 50)
    
    config_manager = global_config_manager
    
    # 显示当前配置
    print("\n📊 当前配置摘要:")
    summary = config_manager.get_config_summary()
    for key, value in summary.items():
        print(f"  • {key}: {value}")
    
    # 验证配置
    print("\n🔍 配置验证:")
    issues = config_manager.validate_config()
    if issues:
        print("  ❌ 发现问题:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  ✅ 配置验证通过")
    
    # 显示可用主题
    print("\n🎨 可用主题:")
    themes = config_manager.get_available_themes()
    for theme in themes:
        current = "✓" if theme["id"] == config_manager.config.ui.theme else " "
        print(f"  {current} {theme['name']}: {theme['description']}")
    
    # 显示可用语言
    print("\n🌐 可用语言:")
    languages = config_manager.get_available_languages()
    for lang in languages:
        current = "✓" if lang["id"] == config_manager.config.ui.language else " "
        print(f"  {current} {lang['native']}")
    
    return config_manager

def demo_theme_switching():
    """演示主题切换"""
    print("\n🎨 主题切换演示")
    print("-" * 30)
    
    config_manager = global_config_manager
    
    # 创建UI实例
    demo_message = """
# 🔧 配置管理系统演示

## 🎨 主题切换功能
- 支持多种毛玻璃主题
- 实时切换无需重启
- 配置自动保存

## 🌐 多语言支持
- 简体中文
- English
- 日本語
- 한국어

## ⚙️ 配置管理
- 导入/导出配置
- 配置验证
- 自动备份
    """
    
    demo_options = [
        "🎨 切换到现代毛玻璃主题",
        "🌟 切换到经典毛玻璃主题", 
        "🌐 切换语言设置",
        "📁 导出当前配置",
        "📂 导入配置文件",
        "🔄 重置为默认配置",
        "✅ 完成配置演示"
    ]
    
    ui = ThreeColumnFeedbackUI(demo_message, demo_options)
    
    # 连接主题变更信号
    def on_theme_changed(theme):
        print(f"🎨 主题已切换为: {theme}")
        # 重新应用主题到UI
        theme_type = ThemeType(theme)
        ThemeManager.apply_theme(ui, theme_type)
    
    config_manager.theme_changed.connect(on_theme_changed)
    
    # 连接语言变更信号
    def on_language_changed(language):
        print(f"🌐 语言已切换为: {language}")
    
    config_manager.language_changed.connect(on_language_changed)
    
    return ui, config_manager

def demo_config_export_import():
    """演示配置导入导出"""
    print("\n📁 配置导入导出演示")
    print("-" * 30)
    
    config_manager = global_config_manager
    
    # 导出配置
    export_path = "demo_config_export.json"
    success = config_manager.export_config(export_path)
    if success:
        print(f"✅ 配置已导出到: {export_path}")
        
        # 显示导出的配置内容
        try:
            import json
            with open(export_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            print("\n📄 导出的配置内容:")
            print(json.dumps(config_data, indent=2, ensure_ascii=False)[:500] + "...")
        except Exception as e:
            print(f"读取配置文件失败: {e}")
    
    # 模拟配置修改
    print("\n🔧 模拟配置修改...")
    original_theme = config_manager.config.ui.theme
    original_font_size = config_manager.config.ui.font_size
    
    # 修改主题和字体
    config_manager.set_theme(ThemeType.MODERN_GLASSMORPHISM)
    config_manager.set_font_size(16)
    
    print(f"  • 主题: {original_theme} → {config_manager.config.ui.theme}")
    print(f"  • 字体大小: {original_font_size} → {config_manager.config.ui.font_size}")
    
    # 重新导入原配置
    print(f"\n📂 重新导入原配置...")
    success = config_manager.import_config(export_path)
    if success:
        print(f"  • 主题: {config_manager.config.ui.theme}")
        print(f"  • 字体大小: {config_manager.config.ui.font_size}")
    
    # 清理临时文件
    try:
        os.remove(export_path)
        print(f"🗑️ 已清理临时文件: {export_path}")
    except:
        pass

def run_tests():
    """运行测试"""
    print("\n🧪 运行配置管理测试...")
    
    try:
        # 运行UI测试
        from tests.test_ui_components import run_ui_tests
        print("\n📋 运行UI组件测试:")
        ui_success = run_ui_tests()
        
        if ui_success:
            print("✅ UI测试通过")
        else:
            print("❌ UI测试失败")
            
    except ImportError as e:
        print(f"⚠️ 无法导入测试模块: {e}")
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")

def main():
    """主函数"""
    print("🚀 Interactive Feedback MCP - 配置管理系统演示")
    print("=" * 60)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Interactive Feedback MCP - Config Demo")
    app.setApplicationVersion("2.0.0")
    
    try:
        # 演示配置操作
        config_manager = demo_config_operations()
        
        # 演示配置导入导出
        demo_config_export_import()
        
        # 演示主题切换
        ui, config_manager = demo_theme_switching()
        
        print("\n🎮 交互指南:")
        print("  • 选择不同选项体验配置功能")
        print("  • 观察主题切换效果")
        print("  • 配置会自动保存")
        print("  • 按 Esc 退出演示")
        
        # 显示UI
        ui.show()
        
        # 运行应用
        result = app.exec()
        
        # 显示最终配置状态
        print("\n📊 最终配置状态:")
        final_summary = config_manager.get_config_summary()
        for key, value in final_summary.items():
            print(f"  • {key}: {value}")
        
        # 运行测试（可选）
        print("\n" + "=" * 60)
        run_tests()
        
        return result
        
    except Exception as e:
        print(f"❌ 演示运行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 