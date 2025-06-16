"""
Configuration Management System for Interactive Feedback MCP
配置管理系统 - 支持配置导入导出、主题切换、用户偏好设置
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from PySide6.QtCore import QSettings, QObject, Signal
from PySide6.QtWidgets import QApplication

class ThemeType(Enum):
    """主题类型枚举 - 强制深色模式"""
    GLASSMORPHISM = "glassmorphism"
    MODERN_GLASSMORPHISM = "modern_glassmorphism"
    ENHANCED_GLASSMORPHISM = "enhanced_glassmorphism"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"

class LanguageType(Enum):
    """语言类型枚举"""
    CHINESE = "zh_CN"
    ENGLISH = "en_US"
    JAPANESE = "ja_JP"
    KOREAN = "ko_KR"

@dataclass
class UIConfig:
    """UI配置数据类"""
    theme: str = ThemeType.ENHANCED_GLASSMORPHISM.value
    language: str = LanguageType.CHINESE.value
    font_family: str = "PingFang SC"
    font_size: int = 14
    window_width: int = 1400
    window_height: int = 1200
    window_opacity: float = 0.95
    panel_ratios: List[int] = None
    auto_save: bool = True
    show_tooltips: bool = True
    enable_animations: bool = False  # 默认关闭动画
    
    def __post_init__(self):
        if self.panel_ratios is None:
            self.panel_ratios = [40, 40, 20]

@dataclass
class PerformanceConfig:
    """性能配置数据类"""
    max_startup_time: float = 2.0
    max_response_time: float = 100.0
    max_memory_usage: float = 100.0
    enable_monitoring: bool = True
    monitoring_interval: int = 1000
    cache_size: int = 100
    
@dataclass
class ShortcutConfig:
    """快捷键配置数据类"""
    submit: str = "Return"
    cancel: str = "Escape"
    help: str = "Ctrl+/"
    font_increase: str = "Ctrl+="
    font_decrease: str = "Ctrl+-"
    font_reset: str = "Ctrl+0"
    option_1: str = "Ctrl+1"
    option_2: str = "Ctrl+2"
    option_3: str = "Ctrl+3"
    option_4: str = "Ctrl+4"
    option_5: str = "Ctrl+5"

@dataclass
class AppConfig:
    """应用程序完整配置"""
    ui: UIConfig = None
    performance: PerformanceConfig = None
    shortcuts: ShortcutConfig = None
    version: str = "1.0.0"
    last_updated: str = ""
    
    def __post_init__(self):
        if self.ui is None:
            self.ui = UIConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.shortcuts is None:
            self.shortcuts = ShortcutConfig()

class ConfigManager(QObject):
    """配置管理器"""
    
    config_changed = Signal(str, object)  # 配置变更信号
    theme_changed = Signal(str)  # 主题变更信号
    language_changed = Signal(str)  # 语言变更信号
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")
        self.config = AppConfig()
        self.config_file_path = self._get_config_file_path()
        self._load_config()
    
    def _get_config_file_path(self) -> str:
        """获取配置文件路径"""
        app_data_dir = os.path.expanduser("~/.interactive_feedback_mcp")
        os.makedirs(app_data_dir, exist_ok=True)
        return os.path.join(app_data_dir, "config.json")
    
    def _load_config(self):
        """加载配置"""
        try:
            # 首先尝试从JSON文件加载
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._apply_config_data(config_data)
            else:
                # 从QSettings加载（向后兼容）
                self._load_from_qsettings()
        except Exception as e:
            print(f"配置加载失败，使用默认配置: {e}")
            self.config = AppConfig()
    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """应用配置数据"""
        try:
            # 更新UI配置
            if 'ui' in config_data:
                ui_data = config_data['ui']
                self.config.ui = UIConfig(**ui_data)
            
            # 更新性能配置
            if 'performance' in config_data:
                perf_data = config_data['performance']
                self.config.performance = PerformanceConfig(**perf_data)
            
            # 更新快捷键配置
            if 'shortcuts' in config_data:
                shortcut_data = config_data['shortcuts']
                self.config.shortcuts = ShortcutConfig(**shortcut_data)
            
            # 更新版本信息
            self.config.version = config_data.get('version', '1.0.0')
            self.config.last_updated = config_data.get('last_updated', '')
            
        except Exception as e:
            print(f"配置数据应用失败: {e}")
    
    def _load_from_qsettings(self):
        """从QSettings加载配置（向后兼容）"""
        # UI设置
        self.config.ui.theme = self.settings.value("ui/theme", ThemeType.ENHANCED_GLASSMORPHISM.value)
        self.config.ui.language = self.settings.value("ui/language", LanguageType.CHINESE.value)
        self.config.ui.font_size = int(self.settings.value("ui/font_size", 14))
        self.config.ui.window_width = int(self.settings.value("ui/window_width", 1400))
        self.config.ui.window_height = int(self.settings.value("ui/window_height", 1200))
        
        # 性能设置
        self.config.performance.enable_monitoring = self.settings.value("performance/enable_monitoring", True, type=bool)
        self.config.performance.monitoring_interval = int(self.settings.value("performance/monitoring_interval", 1000))
    
    def save_config(self):
        """保存配置"""
        try:
            # 更新时间戳
            import datetime
            self.config.last_updated = datetime.datetime.now().isoformat()
            
            # 保存到JSON文件
            config_data = asdict(self.config)
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # 同时保存到QSettings（向后兼容）
            self._save_to_qsettings()
            
            print(f"✅ 配置已保存到: {self.config_file_path}")
            
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    
    def _save_to_qsettings(self):
        """保存到QSettings"""
        # UI设置
        self.settings.setValue("ui/theme", self.config.ui.theme)
        self.settings.setValue("ui/language", self.config.ui.language)
        self.settings.setValue("ui/font_size", self.config.ui.font_size)
        self.settings.setValue("ui/window_width", self.config.ui.window_width)
        self.settings.setValue("ui/window_height", self.config.ui.window_height)
        
        # 性能设置
        self.settings.setValue("performance/enable_monitoring", self.config.performance.enable_monitoring)
        self.settings.setValue("performance/monitoring_interval", self.config.performance.monitoring_interval)
        
        self.settings.sync()
    
    def export_config(self, file_path: str) -> bool:
        """导出配置到文件"""
        try:
            config_data = asdict(self.config)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已导出到: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 配置导出失败: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """从文件导入配置"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ 配置文件不存在: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 备份当前配置
            backup_path = self.config_file_path + ".backup"
            self.export_config(backup_path)
            
            # 应用新配置
            self._apply_config_data(config_data)
            self.save_config()
            
            print(f"✅ 配置已从 {file_path} 导入")
            self.config_changed.emit("all", self.config)
            return True
            
        except Exception as e:
            print(f"❌ 配置导入失败: {e}")
            return False
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = AppConfig()
        self.save_config()
        self.config_changed.emit("reset", self.config)
        print("✅ 配置已重置为默认值")
    
    def set_theme(self, theme: ThemeType):
        """设置主题"""
        old_theme = self.config.ui.theme
        self.config.ui.theme = theme.value
        
        if old_theme != theme.value:
            self.save_config()
            self.theme_changed.emit(theme.value)
            self.config_changed.emit("theme", theme.value)
            print(f"🎨 主题已切换为: {theme.value}")
    
    def set_language(self, language: LanguageType):
        """设置语言"""
        old_language = self.config.ui.language
        self.config.ui.language = language.value
        
        if old_language != language.value:
            self.save_config()
            self.language_changed.emit(language.value)
            self.config_changed.emit("language", language.value)
            print(f"🌐 语言已切换为: {language.value}")
    
    def set_font_size(self, size: int):
        """设置字体大小"""
        if 8 <= size <= 32:
            self.config.ui.font_size = size
            self.save_config()
            self.config_changed.emit("font_size", size)
            
            # 应用到应用程序
            app = QApplication.instance()
            if app:
                font = app.font()
                font.setPointSize(size)
                app.setFont(font)
    
    def set_window_size(self, width: int, height: int):
        """设置窗口尺寸"""
        self.config.ui.window_width = max(1000, width)
        self.config.ui.window_height = max(700, height)
        self.save_config()
        self.config_changed.emit("window_size", (width, height))
    
    def set_panel_ratios(self, ratios: List[int]):
        """设置面板比例"""
        if len(ratios) == 3 and sum(ratios) == 100:
            self.config.ui.panel_ratios = ratios
            self.save_config()
            self.config_changed.emit("panel_ratios", ratios)
    
    def toggle_animations(self):
        """切换动画开关"""
        self.config.ui.enable_animations = not self.config.ui.enable_animations
        self.save_config()
        self.config_changed.emit("animations", self.config.ui.enable_animations)
        print(f"🎬 动画效果: {'开启' if self.config.ui.enable_animations else '关闭'}")
    
    def get_available_themes(self) -> List[Dict[str, str]]:
        """获取可用主题列表 - 强制深色模式"""
        return [
            {"id": ThemeType.ENHANCED_GLASSMORPHISM.value, "name": "增强版毛玻璃", "description": "高对比度毛玻璃效果 - 深色模式"},
            {"id": ThemeType.MODERN_GLASSMORPHISM.value, "name": "现代毛玻璃", "description": "现代风格毛玻璃效果 - 深色模式"},
            {"id": ThemeType.GLASSMORPHISM.value, "name": "经典毛玻璃", "description": "经典毛玻璃效果 - 深色模式"},
            {"id": ThemeType.DARK.value, "name": "深色主题", "description": "纯深色界面主题"},
            {"id": ThemeType.HIGH_CONTRAST.value, "name": "高对比度", "description": "高对比度深色主题"}
        ]
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """获取可用语言列表"""
        return [
            {"id": LanguageType.CHINESE.value, "name": "简体中文", "native": "简体中文"},
            {"id": LanguageType.ENGLISH.value, "name": "English", "native": "English"},
            {"id": LanguageType.JAPANESE.value, "name": "日本語", "native": "日本語"},
            {"id": LanguageType.KOREAN.value, "name": "한국어", "native": "한국어"}
        ]
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "theme": self.config.ui.theme,
            "language": self.config.ui.language,
            "font_size": self.config.ui.font_size,
            "window_size": f"{self.config.ui.window_width}x{self.config.ui.window_height}",
            "animations": self.config.ui.enable_animations,
            "monitoring": self.config.performance.enable_monitoring,
            "version": self.config.version,
            "last_updated": self.config.last_updated
        }
    
    def validate_config(self) -> List[str]:
        """验证配置有效性"""
        issues = []
        
        # 检查主题
        valid_themes = [theme.value for theme in ThemeType]
        if self.config.ui.theme not in valid_themes:
            issues.append(f"无效的主题: {self.config.ui.theme}")
        
        # 检查语言
        valid_languages = [lang.value for lang in LanguageType]
        if self.config.ui.language not in valid_languages:
            issues.append(f"无效的语言: {self.config.ui.language}")
        
        # 检查字体大小
        if not (8 <= self.config.ui.font_size <= 32):
            issues.append(f"字体大小超出范围: {self.config.ui.font_size}")
        
        # 检查窗口尺寸
        if self.config.ui.window_width < 1000 or self.config.ui.window_height < 700:
            issues.append(f"窗口尺寸过小: {self.config.ui.window_width}x{self.config.ui.window_height}")
        
        # 检查面板比例
        if len(self.config.ui.panel_ratios) != 3 or sum(self.config.ui.panel_ratios) != 100:
            issues.append(f"面板比例无效: {self.config.ui.panel_ratios}")
        
        return issues

class ThemeManager:
    """主题管理器"""
    
    @staticmethod
    def get_theme_style(theme_type: ThemeType) -> str:
        """根据主题类型获取样式 - 强制深色模式"""
        if theme_type == ThemeType.ENHANCED_GLASSMORPHISM:
            from ..styles.enhanced_glassmorphism import EnhancedGlassmorphismTheme
            return EnhancedGlassmorphismTheme.get_main_window_style()
        elif theme_type == ThemeType.MODERN_GLASSMORPHISM:
            from ..styles.modern_glassmorphism import ModernGlassmorphismTheme
            return ModernGlassmorphismTheme.get_main_window_style()
        elif theme_type == ThemeType.GLASSMORPHISM:
            from ..styles.glassmorphism import GlassmorphismStyles
            return GlassmorphismStyles.main_window()
        elif theme_type == ThemeType.DARK:
            # 使用增强版毛玻璃作为深色主题
            from ..styles.enhanced_glassmorphism import EnhancedGlassmorphismTheme
            return EnhancedGlassmorphismTheme.get_main_window_style()
        elif theme_type == ThemeType.HIGH_CONTRAST:
            # 使用增强版毛玻璃作为高对比度主题
            from ..styles.enhanced_glassmorphism import EnhancedGlassmorphismTheme
            return EnhancedGlassmorphismTheme.get_main_window_style()
        else:
            # 默认使用增强版毛玻璃 (深色)
            from ..styles.enhanced_glassmorphism import EnhancedGlassmorphismTheme
            return EnhancedGlassmorphismTheme.get_main_window_style()
    
    @staticmethod
    def apply_theme(widget, theme_type: ThemeType):
        """应用主题到组件"""
        style = ThemeManager.get_theme_style(theme_type)
        widget.setStyleSheet(style)

# 全局配置管理器实例
global_config_manager = ConfigManager() 