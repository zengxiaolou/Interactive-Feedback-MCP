#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visual Configuration Manager for Interactive Feedback MCP
可视化配置管理器 - 提供直观的设置界面
"""

import os
import sys
from typing import Dict, Any, Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QSpinBox, QSlider, QCheckBox,
    QPushButton, QColorDialog, QFileDialog, QTextEdit,
    QGroupBox, QTabWidget, QFormLayout, QButtonGroup,
    QRadioButton, QProgressBar, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QPixmap, QPainter

# 导入项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from styles.enhanced_theme_manager import get_theme_manager, ThemeType
from utils.logging_system import get_logger

logger = get_logger('visual_config')

class ColorPickerButton(QPushButton):
    """颜色选择按钮"""
    colorChanged = Signal(str)
    
    def __init__(self, initial_color: str = "#FFFFFF"):
        super().__init__()
        self.current_color = initial_color
        self.setFixedSize(40, 30)
        self.clicked.connect(self._pick_color)
        self._update_button_style()
    
    def _pick_color(self):
        """打开颜色选择对话框"""
        color = QColorDialog.getColor(QColor(self.current_color), self)
        if color.isValid():
            self.current_color = color.name()
            self.colorChanged.emit(self.current_color)
            self._update_button_style()
    
    def _update_button_style(self):
        """更新按钮样式"""
        self.setStyleSheet(f"""
        QPushButton {{
            background-color: {self.current_color};
            border: 2px solid #666;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            border-color: #999;
        }}
        """)
    
    def set_color(self, color: str):
        """设置颜色"""
        self.current_color = color
        self._update_button_style()

class AnimatedFrame(QFrame):
    """带动画效果的框架"""
    
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def show_animated(self):
        """显示动画"""
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.show()
        self.animation.start()
    
    def hide_animated(self):
        """隐藏动画"""
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.hide)
        self.animation.start()

class ThemePreviewWidget(QWidget):
    """主题预览小部件"""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 150)
        self.theme_manager = get_theme_manager()
        self.current_theme = self.theme_manager.get_current_theme()
        
    def set_theme(self, theme_type: ThemeType):
        """设置预览主题"""
        self.current_theme = self.theme_manager.themes[theme_type]
        self.update()
    
    def paintEvent(self, event):
        """绘制主题预览"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        bg_color = QColor(self.current_theme.colors.background)
        if bg_color.alpha() == 0:
            bg_color.setAlpha(255)
        painter.fillRect(self.rect(), bg_color)
        
        # 表面层
        surface_color = QColor(self.current_theme.colors.surface)
        if surface_color.alpha() == 0:
            surface_color.setAlpha(255)
        painter.fillRect(10, 10, 180, 130, surface_color)
        
        # 主色调条
        primary_color = QColor(self.current_theme.colors.primary)
        painter.fillRect(20, 20, 160, 15, primary_color)
        
        # 次要色调条
        secondary_color = QColor(self.current_theme.colors.secondary)
        painter.fillRect(20, 40, 160, 10, secondary_color)
        
        # 强调色点
        accent_color = QColor(self.current_theme.colors.accent)
        painter.fillRect(20, 55, 30, 30, accent_color)
        painter.fillRect(60, 55, 30, 30, accent_color)
        painter.fillRect(100, 55, 30, 30, accent_color)
        
        # 文本示例
        painter.setPen(QColor(self.current_theme.colors.text_primary))
        painter.drawText(20, 105, "主要文本")
        
        painter.setPen(QColor(self.current_theme.colors.text_secondary))
        painter.drawText(20, 125, "次要文本")

class VisualConfigManager(QWidget):
    """可视化配置管理器"""
    
    configChanged = Signal(str, object)  # 配置项名称, 新值
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.config_values = {}
        self.change_callbacks = {}
        
        self.setWindowTitle("Interactive Feedback MCP - 配置管理")
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
        self._load_current_config()
        self._connect_signals()
        
        logger.info("可视化配置管理器初始化完成")
    
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🎨 Interactive Feedback MCP 配置中心")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 8px;
                background: rgba(45, 45, 45, 0.9);
            }
            QTabBar::tab {
                background: rgba(60, 60, 60, 0.8);
                color: white;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: rgba(76, 175, 80, 0.8);
            }
        """)
        
        # 添加各个配置页面
        self._create_theme_tab()
        self._create_ui_tab()
        self._create_performance_tab()
        self._create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        self._create_action_buttons(layout)
    
    def _create_theme_tab(self):
        """创建主题配置页面"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # 主题选择区域
        theme_group = QGroupBox("🎨 主题选择")
        theme_layout = QVBoxLayout(theme_group)
        
        # 主题选择下拉框
        theme_selection_layout = QHBoxLayout()
        theme_label = QLabel("当前主题:")
        self.theme_combo = QComboBox()
        
        # 填充主题选项
        themes = self.theme_manager.get_available_themes()
        for theme_id, theme_name in themes.items():
            self.theme_combo.addItem(theme_name, theme_id)
        
        # 主题预览
        self.theme_preview = ThemePreviewWidget()
        
        theme_selection_layout.addWidget(theme_label)
        theme_selection_layout.addWidget(self.theme_combo)
        theme_selection_layout.addStretch()
        theme_selection_layout.addWidget(self.theme_preview)
        
        theme_layout.addLayout(theme_selection_layout)
        
        # 自定义颜色区域
        colors_group = QGroupBox("🌈 自定义颜色")
        colors_layout = QGridLayout(colors_group)
        
        self.color_pickers = {}
        color_labels = [
            ("primary", "主色调", 0, 0),
            ("secondary", "次要色", 0, 1),
            ("accent", "强调色", 0, 2),
            ("background", "背景色", 1, 0),
            ("surface", "表面色", 1, 1),
            ("text_primary", "主要文本", 1, 2),
            ("success", "成功色", 2, 0),
            ("warning", "警告色", 2, 1),
            ("error", "错误色", 2, 2)
        ]
        
        for color_key, color_name, row, col in color_labels:
            label = QLabel(color_name)
            picker = ColorPickerButton()
            self.color_pickers[color_key] = picker
            
            colors_layout.addWidget(label, row * 2, col)
            colors_layout.addWidget(picker, row * 2 + 1, col)
        
        theme_layout.addWidget(colors_group)
        layout.addWidget(theme_group)
        
        # 主题效果设置
        effects_group = QGroupBox("✨ 视觉效果")
        effects_layout = QFormLayout(effects_group)
        
        # 模糊半径
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 50)
        self.blur_slider.setValue(15)
        blur_label = QLabel("模糊半径: 15px")
        self.blur_slider.valueChanged.connect(
            lambda v: blur_label.setText(f"模糊半径: {v}px")
        )
        
        # 透明度
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(85)
        opacity_label = QLabel("透明度: 85%")
        self.opacity_slider.valueChanged.connect(
            lambda v: opacity_label.setText(f"透明度: {v}%")
        )
        
        # 圆角半径
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0, 30)
        self.radius_spin.setValue(12)
        self.radius_spin.setSuffix("px")
        
        effects_layout.addRow(blur_label, self.blur_slider)
        effects_layout.addRow(opacity_label, self.opacity_slider)
        effects_layout.addRow("圆角半径:", self.radius_spin)
        
        layout.addWidget(effects_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🎨 主题设置")
    
    def _create_ui_tab(self):
        """创建UI配置页面"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 字体设置
        font_group = QGroupBox("🔤 字体设置")
        font_layout = QFormLayout(font_group)
        
        # 字体族
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
            "SimHei", "STHeiti", "Arial", "Helvetica", "Roboto"
        ])
        
        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 24)
        self.font_size_spin.setValue(14)
        self.font_size_spin.setSuffix("px")
        
        # 字体权重
        self.font_weight_combo = QComboBox()
        self.font_weight_combo.addItems(["正常", "粗体"])
        
        font_layout.addRow("字体族:", self.font_family_combo)
        font_layout.addRow("字体大小:", self.font_size_spin)
        font_layout.addRow("字体权重:", self.font_weight_combo)
        
        layout.addWidget(font_group)
        
        # 布局设置
        layout_group = QGroupBox("📐 布局设置")
        layout_layout = QFormLayout(layout_group)
        
        # 窗口尺寸
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 2560)
        self.window_width_spin.setValue(1400)
        self.window_width_spin.setSuffix("px")
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 1600)
        self.window_height_spin.setValue(1200)
        self.window_height_spin.setSuffix("px")
        
        # 面板比例
        self.panel_ratio_1 = QSpinBox()
        self.panel_ratio_1.setRange(20, 60)
        self.panel_ratio_1.setValue(40)
        self.panel_ratio_1.setSuffix("%")
        
        self.panel_ratio_2 = QSpinBox()
        self.panel_ratio_2.setRange(20, 60) 
        self.panel_ratio_2.setValue(40)
        self.panel_ratio_2.setSuffix("%")
        
        self.panel_ratio_3 = QSpinBox()
        self.panel_ratio_3.setRange(15, 40)
        self.panel_ratio_3.setValue(20)
        self.panel_ratio_3.setSuffix("%")
        
        # 响应式设计
        self.responsive_checkbox = QCheckBox("启用响应式设计")
        self.responsive_checkbox.setChecked(True)
        
        layout_layout.addRow("窗口宽度:", self.window_width_spin)
        layout_layout.addRow("窗口高度:", self.window_height_spin)
        layout_layout.addRow("左侧面板:", self.panel_ratio_1)
        layout_layout.addRow("中间面板:", self.panel_ratio_2)
        layout_layout.addRow("右侧面板:", self.panel_ratio_3)
        layout_layout.addRow("", self.responsive_checkbox)
        
        layout.addWidget(layout_group)
        
        # 动画设置
        animation_group = QGroupBox("🎬 动画效果")
        animation_layout = QFormLayout(animation_group)
        
        # 动画开关
        self.animation_enabled_checkbox = QCheckBox("启用动画效果")
        self.animation_enabled_checkbox.setChecked(True)
        
        # 动画时长
        self.animation_duration_spin = QSpinBox()
        self.animation_duration_spin.setRange(100, 1000)
        self.animation_duration_spin.setValue(300)
        self.animation_duration_spin.setSuffix("ms")
        
        # 动画类型
        self.animation_type_combo = QComboBox()
        self.animation_type_combo.addItems([
            "缓入缓出", "线性", "缓入", "缓出", "弹性"
        ])
        
        animation_layout.addRow("", self.animation_enabled_checkbox)
        animation_layout.addRow("动画时长:", self.animation_duration_spin)
        animation_layout.addRow("动画类型:", self.animation_type_combo)
        
        layout.addWidget(animation_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🎨 界面设置")
    
    def _create_performance_tab(self):
        """创建性能配置页面"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 性能监控
        monitor_group = QGroupBox("📊 性能监控")
        monitor_layout = QFormLayout(monitor_group)
        
        # 启动时间阈值
        self.startup_threshold_spin = QSpinBox()
        self.startup_threshold_spin.setRange(500, 5000)
        self.startup_threshold_spin.setValue(2000)
        self.startup_threshold_spin.setSuffix("ms")
        
        # 响应时间阈值
        self.response_threshold_spin = QSpinBox()
        self.response_threshold_spin.setRange(50, 1000)
        self.response_threshold_spin.setValue(100)
        self.response_threshold_spin.setSuffix("ms")
        
        # 内存使用阈值
        self.memory_threshold_spin = QSpinBox()
        self.memory_threshold_spin.setRange(50, 500)
        self.memory_threshold_spin.setValue(100)
        self.memory_threshold_spin.setSuffix("MB")
        
        # 性能监控开关
        self.performance_monitoring_checkbox = QCheckBox("启用性能监控")
        self.performance_monitoring_checkbox.setChecked(True)
        
        monitor_layout.addRow("启动时间阈值:", self.startup_threshold_spin)
        monitor_layout.addRow("响应时间阈值:", self.response_threshold_spin)
        monitor_layout.addRow("内存使用阈值:", self.memory_threshold_spin)
        monitor_layout.addRow("", self.performance_monitoring_checkbox)
        
        layout.addWidget(monitor_group)
        
        # 优化设置
        optimization_group = QGroupBox("⚡ 性能优化")
        optimization_layout = QFormLayout(optimization_group)
        
        # 缓存设置
        self.cache_enabled_checkbox = QCheckBox("启用缓存")
        self.cache_enabled_checkbox.setChecked(True)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 200)
        self.cache_size_spin.setValue(50)
        self.cache_size_spin.setSuffix("MB")
        
        # 并发设置
        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setRange(1, 8)
        self.max_workers_spin.setValue(4)
        
        # 预加载设置
        self.preload_checkbox = QCheckBox("预加载常用资源")
        self.preload_checkbox.setChecked(False)
        
        optimization_layout.addRow("", self.cache_enabled_checkbox)
        optimization_layout.addRow("缓存大小:", self.cache_size_spin)
        optimization_layout.addRow("最大工作线程:", self.max_workers_spin)
        optimization_layout.addRow("", self.preload_checkbox)
        
        layout.addWidget(optimization_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⚡ 性能设置")
    
    def _create_advanced_tab(self):
        """创建高级配置页面"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 日志设置
        logging_group = QGroupBox("📋 日志设置")
        logging_layout = QFormLayout(logging_group)
        
        # 日志级别
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        
        # 日志文件大小
        self.log_size_spin = QSpinBox()
        self.log_size_spin.setRange(1, 100)
        self.log_size_spin.setValue(10)
        self.log_size_spin.setSuffix("MB")
        
        # 备份数量
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(1, 20)
        self.backup_count_spin.setValue(5)
        
        # 控制台输出
        self.console_output_checkbox = QCheckBox("启用控制台输出")
        self.console_output_checkbox.setChecked(True)
        
        logging_layout.addRow("日志级别:", self.log_level_combo)
        logging_layout.addRow("单文件大小:", self.log_size_spin)
        logging_layout.addRow("备份文件数:", self.backup_count_spin)
        logging_layout.addRow("", self.console_output_checkbox)
        
        layout.addWidget(logging_group)
        
        # 安全设置
        security_group = QGroupBox("🔒 安全设置")
        security_layout = QFormLayout(security_group)
        
        # 输入验证
        self.input_validation_checkbox = QCheckBox("启用输入验证")
        self.input_validation_checkbox.setChecked(True)
        
        # 文件访问限制
        self.file_access_checkbox = QCheckBox("限制文件访问")
        self.file_access_checkbox.setChecked(False)
        
        # 网络访问
        self.network_access_checkbox = QCheckBox("允许网络访问")
        self.network_access_checkbox.setChecked(True)
        
        security_layout.addRow("", self.input_validation_checkbox)
        security_layout.addRow("", self.file_access_checkbox)
        security_layout.addRow("", self.network_access_checkbox)
        
        layout.addWidget(security_group)
        
        # 开发者选项
        dev_group = QGroupBox("🛠️ 开发者选项")
        dev_layout = QFormLayout(dev_group)
        
        # 调试模式
        self.debug_mode_checkbox = QCheckBox("启用调试模式")
        self.debug_mode_checkbox.setChecked(False)
        
        # 详细日志
        self.verbose_logging_checkbox = QCheckBox("详细日志记录")
        self.verbose_logging_checkbox.setChecked(False)
        
        # 性能分析
        self.profiling_checkbox = QCheckBox("启用性能分析")
        self.profiling_checkbox.setChecked(False)
        
        dev_layout.addRow("", self.debug_mode_checkbox)
        dev_layout.addRow("", self.verbose_logging_checkbox)
        dev_layout.addRow("", self.profiling_checkbox)
        
        layout.addWidget(dev_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🛠️ 高级设置")
    
    def _create_action_buttons(self, layout):
        """创建操作按钮"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 应用按钮
        self.apply_button = QPushButton("✅ 应用设置")
        self.apply_button.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45A049;
            }
        """)
        self.apply_button.clicked.connect(self._apply_settings)
        
        # 重置按钮
        self.reset_button = QPushButton("🔄 重置默认")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #F57C00;
            }
        """)
        self.reset_button.clicked.connect(self._reset_settings)
        
        # 导出按钮
        self.export_button = QPushButton("📤 导出配置")
        self.export_button.clicked.connect(self._export_config)
        
        # 导入按钮
        self.import_button = QPushButton("📥 导入配置")
        self.import_button.clicked.connect(self._import_config)
        
        # 关闭按钮
        self.close_button = QPushButton("❌ 关闭")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _load_current_config(self):
        """加载当前配置"""
        try:
            # 加载主题配置
            current_theme = self.theme_manager.get_current_theme()
            theme_index = self.theme_combo.findData(self.theme_manager.current_theme.value)
            if theme_index >= 0:
                self.theme_combo.setCurrentIndex(theme_index)
            
            # 设置颜色选择器
            colors = current_theme.colors
            for color_key, picker in self.color_pickers.items():
                if hasattr(colors, color_key):
                    picker.set_color(getattr(colors, color_key))
            
            # 设置效果参数
            self.blur_slider.setValue(current_theme.blur_radius)
            self.opacity_slider.setValue(int(current_theme.opacity * 100))
            self.radius_spin.setValue(current_theme.border_radius)
            
            # 设置字体参数
            self.font_family_combo.setCurrentText(current_theme.font_family)
            self.font_size_spin.setValue(current_theme.font_size)
            
            logger.info("配置加载完成")
            
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
    
    def _connect_signals(self):
        """连接信号"""
        # 主题切换
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        
        # 颜色变化
        for color_key, picker in self.color_pickers.items():
            picker.colorChanged.connect(
                lambda color, key=color_key: self._on_color_changed(key, color)
            )
    
    def _on_theme_changed(self, theme_name):
        """主题切换处理"""
        try:
            theme_id = self.theme_combo.currentData()
            for theme_type in ThemeType:
                if theme_type.value == theme_id:
                    self.theme_manager.set_theme(theme_type)
                    self.theme_preview.set_theme(theme_type)
                    self._load_current_config()
                    break
            
            logger.info(f"主题切换为: {theme_name}")
            
        except Exception as e:
            logger.error(f"主题切换失败: {e}")
    
    def _on_color_changed(self, color_key: str, color: str):
        """颜色变化处理"""
        logger.info(f"颜色 {color_key} 变更为: {color}")
        # 这里可以实时预览颜色变化
    
    def _apply_settings(self):
        """应用设置"""
        try:
            # 应用主题设置
            theme_id = self.theme_combo.currentData()
            for theme_type in ThemeType:
                if theme_type.value == theme_id:
                    self.theme_manager.set_theme(theme_type)
                    break
            
            # 发出配置变化信号
            self.configChanged.emit("theme_applied", theme_id)
            
            logger.info("设置应用成功")
            
        except Exception as e:
            logger.error(f"应用设置失败: {e}")
    
    def _reset_settings(self):
        """重置设置"""
        try:
            # 重置为默认主题
            self.theme_manager.set_theme(ThemeType.ENHANCED_GLASSMORPHISM)
            self._load_current_config()
            
            logger.info("设置重置完成")
            
        except Exception as e:
            logger.error(f"重置设置失败: {e}")
    
    def _export_config(self):
        """导出配置"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出配置", "config_export.json", "JSON Files (*.json)"
            )
            if file_path:
                # 导出当前主题
                current_theme_type = self.theme_manager.current_theme
                success = self.theme_manager.export_theme(current_theme_type, file_path)
                if success:
                    logger.info(f"配置导出成功: {file_path}")
                else:
                    logger.error("配置导出失败")
                    
        except Exception as e:
            logger.error(f"导出配置异常: {e}")
    
    def _import_config(self):
        """导入配置"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "导入配置", "", "JSON Files (*.json)"
            )
            if file_path:
                theme_type = self.theme_manager.import_theme(file_path)
                if theme_type:
                    # 刷新主题列表
                    self.theme_combo.clear()
                    themes = self.theme_manager.get_available_themes()
                    for theme_id, theme_name in themes.items():
                        self.theme_combo.addItem(theme_name, theme_id)
                    
                    # 设置为导入的主题
                    self.theme_manager.set_theme(theme_type)
                    self._load_current_config()
                    
                    logger.info(f"配置导入成功: {file_path}")
                else:
                    logger.error("配置导入失败")
                    
        except Exception as e:
            logger.error(f"导入配置异常: {e}")

# 便利函数
def show_config_manager(parent=None) -> VisualConfigManager:
    """显示配置管理器"""
    config_manager = VisualConfigManager(parent)
    config_manager.show()
    return config_manager 