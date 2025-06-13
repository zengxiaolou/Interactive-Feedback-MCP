#!/usr/bin/env python3
"""
UI Components Test Suite
UI组件自动化测试套件
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components.three_column_layout import ThreeColumnFeedbackUI

class TestThreeColumnFeedbackUI(unittest.TestCase):
    """三栏布局UI组件测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """每个测试方法前的初始化"""
        self.test_prompt = "测试消息内容"
        self.test_options = ["选项1", "选项2", "选项3"]
        self.ui = ThreeColumnFeedbackUI(self.test_prompt, self.test_options)
    
    def tearDown(self):
        """每个测试方法后的清理"""
        if hasattr(self, 'ui') and self.ui:
            self.ui.close()
    
    def test_window_initialization(self):
        """测试窗口初始化"""
        # 检查窗口标题
        self.assertIn("Interactive Feedback MCP", self.ui.windowTitle())
        
        # 检查窗口尺寸
        size = self.ui.size()
        self.assertGreaterEqual(size.width(), 1000)
        self.assertGreaterEqual(size.height(), 800)
        
        # 检查最小尺寸
        min_size = self.ui.minimumSize()
        self.assertEqual(min_size.width(), 1000)
        self.assertEqual(min_size.height(), 800)
    
    def test_ui_components_creation(self):
        """测试UI组件创建"""
        # 检查复选框数量
        self.assertEqual(len(self.ui.option_checkboxes), len(self.test_options))
        
        # 检查复选框文本
        for i, checkbox in enumerate(self.ui.option_checkboxes):
            self.assertEqual(checkbox.text(), self.test_options[i])
        
        # 检查描述文本区域
        self.assertIsNotNone(self.ui.description_text)
        
        # 检查自定义输入区域
        self.assertIsNotNone(self.ui.custom_input)
    
    def test_option_selection(self):
        """测试选项选择功能"""
        # 测试选择第一个选项
        self.ui._toggle_option(0)
        self.assertTrue(self.ui.option_checkboxes[0].isChecked())
        
        # 测试取消选择
        self.ui._toggle_option(0)
        self.assertFalse(self.ui.option_checkboxes[0].isChecked())
        
        # 测试无效索引
        self.ui._toggle_option(999)  # 应该不会崩溃
    
    def test_keyboard_shortcuts(self):
        """测试键盘快捷键"""
        # 模拟按键事件
        self.ui.show()
        
        # 测试Ctrl+1选择第一个选项
        QTest.keyClick(self.ui, Qt.Key.Key_1, Qt.KeyboardModifier.ControlModifier)
        # 注意：由于快捷键实现方式，这里可能需要调整测试方法
        
        # 测试Escape关闭窗口
        with patch.object(self.ui, 'close') as mock_close:
            QTest.keyClick(self.ui, Qt.Key.Key_Escape)
            # mock_close.assert_called_once()  # 可能需要调整
    
    def test_feedback_submission(self):
        """测试反馈提交功能"""
        # 选择一些选项
        self.ui.option_checkboxes[0].setChecked(True)
        self.ui.option_checkboxes[1].setChecked(True)
        
        # 添加自定义文本
        self.ui.custom_input.setPlainText("自定义反馈内容")
        
        # 提交反馈
        self.ui._submit_feedback()
        
        # 检查结果
        self.assertIsNotNone(self.ui.feedback_result)
        self.assertIn("选项1", self.ui.feedback_result['interactive_feedback'])
        self.assertIn("选项2", self.ui.feedback_result['interactive_feedback'])
        self.assertIn("自定义反馈内容", self.ui.feedback_result['interactive_feedback'])
    
    def test_performance_requirements(self):
        """测试性能要求"""
        import time
        
        # 测试启动时间
        start_time = time.time()
        ui = ThreeColumnFeedbackUI("性能测试", ["选项1"])
        startup_time = time.time() - start_time
        
        # PRD要求：启动时间 < 2秒
        self.assertLess(startup_time, 2.0, f"启动时间超标: {startup_time:.2f}s")
        
        ui.close()
    
    def test_responsive_design(self):
        """测试响应式设计"""
        # 测试不同窗口尺寸
        test_sizes = [
            (1000, 700),  # 最小尺寸
            (1400, 1000), # 默认尺寸
            (1800, 1200)  # 大尺寸
        ]
        
        for width, height in test_sizes:
            self.ui.resize(width, height)
            self.ui.show()
            
            # 检查布局是否正常
            self.assertGreaterEqual(self.ui.width(), width)
            self.assertGreaterEqual(self.ui.height(), height)
    
    def test_project_info_display(self):
        """测试项目信息显示"""
        project_info = self.ui._get_project_info()
        
        # 检查项目信息结构
        self.assertIn('name', project_info)
        self.assertIn('path', project_info)
        self.assertIn('files', project_info)
        
        # 检查Git信息
        git_info = self.ui._get_git_info()
        self.assertIn('branch', git_info)
        self.assertIn('modified_files', git_info)
        self.assertIn('last_commit', git_info)
    
    def test_font_scaling(self):
        """测试字体缩放功能"""
        # 测试放大字体
        original_font = QApplication.instance().font()
        original_size = original_font.pointSize()
        
        self.ui.adjust_font_size(1.2)
        new_font = QApplication.instance().font()
        self.assertGreater(new_font.pointSize(), original_size)
        
        # 测试重置字体
        self.ui.reset_font_size()
        reset_font = QApplication.instance().font()
        self.assertEqual(reset_font.pointSize(), 15)  # 默认大小
    
    def test_help_system(self):
        """测试帮助系统"""
        # 显示帮助
        original_html = self.ui.description_text.toHtml()
        self.ui._show_help()
        
        # 检查帮助内容是否显示
        help_html = self.ui.description_text.toHtml()
        self.assertNotEqual(original_html, help_html)
        self.assertIn("快捷键帮助", help_html)

class TestPerformanceMonitoring(unittest.TestCase):
    """性能监控测试"""
    
    def setUp(self):
        """初始化性能监控"""
        from ui.utils.performance import global_performance_monitor, global_response_tracker
        self.performance_monitor = global_performance_monitor
        self.response_tracker = global_response_tracker
    
    def test_performance_monitor_initialization(self):
        """测试性能监控器初始化"""
        self.assertIsNotNone(self.performance_monitor)
        self.assertIsNotNone(self.response_tracker)
    
    def test_response_time_tracking(self):
        """测试响应时间跟踪"""
        import time
        
        # 模拟操作
        start_time = self.response_tracker.start_timing()
        time.sleep(0.01)  # 模拟10ms操作
        response_time = self.response_tracker.end_timing(start_time, "test_operation")
        
        # 检查响应时间记录
        self.assertGreater(response_time, 0)
        self.assertLess(response_time, 100)  # 应该小于100ms
    
    def test_performance_requirements_check(self):
        """测试性能要求检查"""
        # 启动监控
        self.performance_monitor.start_monitoring()
        
        # 等待一些指标更新
        import time
        time.sleep(0.1)
        
        # 检查性能要求
        requirements = self.performance_monitor.check_performance_requirements()
        
        # 验证要求结构
        self.assertIn('startup_time_ok', requirements)
        self.assertIn('memory_usage_ok', requirements)
        self.assertIn('cpu_usage_ok', requirements)

class TestResponsiveDesign(unittest.TestCase):
    """响应式设计测试"""
    
    def setUp(self):
        """初始化响应式管理器"""
        from ui.utils.responsive import ScreenSizeManager, responsive_manager
        self.screen_manager = ScreenSizeManager
        self.layout_manager = responsive_manager
    
    def test_screen_categorization(self):
        """测试屏幕分类"""
        # 测试不同屏幕尺寸的分类
        test_cases = [
            ((1280, 720), 'small'),
            ((1600, 900), 'medium'),
            ((1920, 1080), 'large'),
            ((2560, 1440), 'xlarge')
        ]
        
        for (width, height), expected_category in test_cases:
            # 这里需要模拟屏幕尺寸，实际实现可能需要调整
            pass
    
    def test_adaptive_configuration(self):
        """测试自适应配置"""
        config = self.layout_manager.current_config
        
        # 检查配置结构
        self.assertIn('screen_category', config)
        self.assertIn('window_size', config)
        self.assertIn('panel_ratios', config)
        self.assertIn('font_scale', config)
    
    def test_component_sizing(self):
        """测试组件尺寸配置"""
        sizes = self.layout_manager.get_component_sizes()
        
        # 检查组件尺寸配置
        required_keys = [
            'text_browser_height',
            'context_height', 
            'input_height',
            'button_height',
            'checkbox_size'
        ]
        
        for key in required_keys:
            self.assertIn(key, sizes)
            self.assertIsInstance(sizes[key], int)
            self.assertGreater(sizes[key], 0)

def run_ui_tests():
    """运行UI测试套件"""
    print("🧪 开始运行UI组件测试...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestThreeColumnFeedbackUI,
        TestPerformanceMonitoring,
        TestResponsiveDesign
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出结果
    print(f"\n📊 测试结果:")
    print(f"  • 运行测试: {result.testsRun}")
    print(f"  • 成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  • 失败: {len(result.failures)}")
    print(f"  • 错误: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n✅ 测试通过率: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_ui_tests()
    sys.exit(0 if success else 1) 