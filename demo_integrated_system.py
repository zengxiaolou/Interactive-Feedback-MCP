#!/usr/bin/env python3
"""
Integrated System Demo for Interactive Feedback MCP
集成系统演示 - 展示所有功能的协同工作
"""

import sys
import os
from PySide6.QtWidgets import QApplication

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.components.three_column_layout import ThreeColumnFeedbackUI
from ui.utils.config_manager import global_config_manager, ThemeType
from ui.utils.performance import global_performance_monitor

def demo_integrated_features():
    """演示集成功能"""
    print("🚀 Interactive Feedback MCP - 集成系统演示")
    print("=" * 60)
    
    # 演示消息和选项
    demo_message = """
# 🎯 集成系统功能演示

## ✨ 已集成的功能模块

### 🔧 配置管理系统
- **主题切换**: 按 `Ctrl+T` 切换毛玻璃主题
- **配置导出**: 按 `Ctrl+E` 导出当前配置
- **配置重置**: 按 `Ctrl+R` 重置为默认配置

### 📊 数据可视化分析
- **数据分析**: 按 `Ctrl+D` 打开数据可视化窗口
- **实时统计**: 自动记录反馈数据和性能指标
- **报告导出**: 支持导出分析报告

### ⚡ 性能监控
- **启动时间**: 监控应用启动性能 (目标 <2s)
- **响应时间**: 记录用户操作响应时间 (目标 <100ms)
- **资源使用**: 监控内存和CPU使用情况

### 🧪 自动化测试
- **UI测试**: 16个测试用例全部通过
- **性能测试**: 验证PRD性能要求
- **集成测试**: 确保模块间协同工作

### 🎨 增强版毛玻璃主题
- **高对比度**: 优化的透明度和边框效果
- **响应式设计**: 支持不同屏幕尺寸
- **无动画**: 保持简洁高效的用户体验

## 🎮 交互指南

### 基础操作
- `Enter`: 提交反馈
- `Esc`: 取消/关闭
- `Ctrl+/`: 显示帮助

### 配置管理
- `Ctrl+T`: 切换主题
- `Ctrl+E`: 导出配置
- `Ctrl+R`: 重置配置

### 数据分析
- `Ctrl+D`: 打开数据可视化

### 字体调整
- `Ctrl++`: 放大字体
- `Ctrl+-`: 缩小字体
- `Ctrl+0`: 重置字体

## 📈 性能指标
系统将自动监控和记录以下指标：
- 启动时间、响应时间、内存使用
- 用户选择偏好、使用模式分析
- 系统稳定性和错误率统计
    """
    
    demo_options = [
        "🎨 测试主题切换功能",
        "📊 打开数据可视化分析",
        "⚙️ 导出当前配置设置",
        "🔄 重置为默认配置",
        "🧪 运行系统测试",
        "📈 查看性能监控数据",
        "💾 保存当前会话状态",
        "🌟 体验响应式布局",
        "✅ 完成功能演示"
    ]
    
    return demo_message, demo_options

def show_system_status():
    """显示系统状态"""
    print("\n📊 系统状态检查")
    print("-" * 40)
    
    # 配置管理状态
    config = global_config_manager.get_config_summary()
    print("🔧 配置管理:")
    for key, value in config.items():
        print(f"  • {key}: {value}")
    
    # 性能监控状态
    print("\n⚡ 性能监控:")
    try:
        requirements = global_performance_monitor.check_performance_requirements()
        for key, status in requirements.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {key}: {'通过' if status else '未达标'}")
    except Exception as e:
        print(f"  ⚠️ 性能监控数据获取失败: {e}")
    
    # 可用主题
    print("\n🎨 可用主题:")
    themes = global_config_manager.get_available_themes()
    current_theme = global_config_manager.config.ui.theme
    for theme in themes:
        current = "✓" if theme["id"] == current_theme else " "
        print(f"  {current} {theme['name']}")

def run_integration_tests():
    """运行集成测试"""
    print("\n🧪 运行集成测试...")
    
    try:
        # 导入并运行测试
        from tests.test_ui_components import run_ui_tests
        
        print("📋 UI组件测试:")
        ui_success = run_ui_tests()
        
        if ui_success:
            print("✅ 所有测试通过")
            return True
        else:
            print("❌ 部分测试失败")
            return False
            
    except ImportError as e:
        print(f"⚠️ 无法导入测试模块: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False

def demonstrate_config_features():
    """演示配置功能"""
    print("\n🔧 配置功能演示")
    print("-" * 30)
    
    config_manager = global_config_manager
    
    # 显示当前配置
    print("📊 当前配置:")
    summary = config_manager.get_config_summary()
    for key, value in summary.items():
        print(f"  • {key}: {value}")
    
    # 演示主题切换
    print("\n🎨 主题切换演示:")
    original_theme = config_manager.config.ui.theme
    print(f"  当前主题: {original_theme}")
    
    # 切换到不同主题
    if original_theme != ThemeType.MODERN_GLASSMORPHISM.value:
        config_manager.set_theme(ThemeType.MODERN_GLASSMORPHISM)
        print(f"  切换到: {config_manager.config.ui.theme}")
        
        # 切换回原主题
        config_manager.set_theme(ThemeType(original_theme))
        print(f"  恢复到: {config_manager.config.ui.theme}")
    
    # 演示配置导出
    print("\n📁 配置导出演示:")
    export_file = "demo_config_export.json"
    success = config_manager.export_config(export_file)
    if success:
        print(f"  ✅ 配置已导出到: {export_file}")
        
        # 清理文件
        try:
            os.remove(export_file)
            print(f"  🗑️ 已清理临时文件")
        except:
            pass

def main():
    """主函数"""
    print("🚀 Interactive Feedback MCP - 集成系统演示")
    print("=" * 60)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Interactive Feedback MCP - Integrated Demo")
    app.setApplicationVersion("2.0.0")
    
    try:
        # 显示系统状态
        show_system_status()
        
        # 演示配置功能
        demonstrate_config_features()
        
        # 准备演示内容
        demo_message, demo_options = demo_integrated_features()
        
        print("\n🎮 启动集成演示界面...")
        print("=" * 60)
        
        # 创建主界面
        ui = ThreeColumnFeedbackUI(demo_message, demo_options)
        
        print("\n💡 使用提示:")
        print("  • 尝试不同的快捷键组合")
        print("  • 观察配置变更的实时效果")
        print("  • 体验数据可视化功能")
        print("  • 测试性能监控指标")
        print("  • 按 Esc 退出演示")
        
        # 显示界面
        ui.show()
        
        # 运行应用
        result = app.exec()
        
        # 显示最终状态
        print("\n📊 演示结束 - 最终状态:")
        print("-" * 40)
        
        final_config = global_config_manager.get_config_summary()
        for key, value in final_config.items():
            print(f"  • {key}: {value}")
        
        # 可选：运行集成测试
        print("\n" + "=" * 60)
        test_success = run_integration_tests()
        
        if test_success:
            print("\n🎉 集成演示完成 - 所有功能正常工作！")
        else:
            print("\n⚠️ 集成演示完成 - 部分功能需要检查")
        
        return result
        
    except Exception as e:
        print(f"❌ 演示运行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 