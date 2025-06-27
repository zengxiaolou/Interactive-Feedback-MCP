#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Theme Manager for Interactive Feedback MCP
增强主题管理器 - 支持多种主题和动态切换
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path

class ThemeType(Enum):
    """主题类型枚举"""
    ENHANCED_GLASSMORPHISM = "enhanced_glassmorphism"
    MODERN_DARK = "modern_dark"
    NORDIC_BLUE = "nordic_blue"
    WARM_AMBER = "warm_amber"
    CYBERPUNK = "cyberpunk"
    MINIMALIST = "minimalist"
    HIGH_CONTRAST = "high_contrast"

@dataclass
class ColorScheme:
    """颜色方案数据类"""
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    success: str
    warning: str
    error: str
    info: str

@dataclass
class ThemeConfig:
    """主题配置数据类"""
    name: str
    display_name: str
    colors: ColorScheme
    blur_radius: int = 15
    opacity: float = 0.85
    border_radius: int = 12
    font_family: str = "PingFang SC"
    font_size: int = 14
    animation_duration: int = 300
    custom_properties: Dict[str, Any] = None

class EnhancedThemeManager:
    """增强主题管理器"""
    
    def __init__(self):
        self.themes = self._initialize_themes()
        self.current_theme = ThemeType.ENHANCED_GLASSMORPHISM
        self._load_user_preferences()
    
    def _initialize_themes(self) -> Dict[ThemeType, ThemeConfig]:
        """初始化所有主题"""
        themes = {}
        
        # 1. 增强毛玻璃主题（默认）
        themes[ThemeType.ENHANCED_GLASSMORPHISM] = ThemeConfig(
            name="enhanced_glassmorphism",
            display_name="增强毛玻璃",
            colors=ColorScheme(
                primary="#4CAF50",
                secondary="#2196F3", 
                accent="#FF9800",
                background="rgba(25, 25, 25, 0.95)",
                surface="rgba(45, 45, 45, 0.9)",
                text_primary="#FFFFFF",
                text_secondary="#CCCCCC",
                success="#4CAF50",
                warning="#FF9800",
                error="#F44336",
                info="#2196F3"
            ),
            blur_radius=15,
            opacity=0.85
        )
        
        # 2. 现代深色主题
        themes[ThemeType.MODERN_DARK] = ThemeConfig(
            name="modern_dark",
            display_name="现代深色",
            colors=ColorScheme(
                primary="#6366F1",
                secondary="#8B5CF6",
                accent="#F59E0B",
                background="#111827",
                surface="#1F2937",
                text_primary="#F9FAFB",
                text_secondary="#D1D5DB",
                success="#10B981",
                warning="#F59E0B",
                error="#EF4444",
                info="#3B82F6"
            ),
            blur_radius=10,
            opacity=0.95,
            border_radius=8
        )
        
        # 3. 北欧蓝主题
        themes[ThemeType.NORDIC_BLUE] = ThemeConfig(
            name="nordic_blue",
            display_name="北欧蓝调",
            colors=ColorScheme(
                primary="#5E81AC",
                secondary="#81A1C1",
                accent="#EBCB8B",
                background="#2E3440",
                surface="#3B4252",
                text_primary="#ECEFF4",
                text_secondary="#D8DEE9",
                success="#A3BE8C",
                warning="#EBCB8B",
                error="#BF616A",
                info="#88C0D0"
            ),
            blur_radius=12,
            opacity=0.9
        )
        
        # 4. 暖色琥珀主题
        themes[ThemeType.WARM_AMBER] = ThemeConfig(
            name="warm_amber",
            display_name="暖色琥珀",
            colors=ColorScheme(
                primary="#F59E0B",
                secondary="#D97706",
                accent="#EF4444",
                background="#1C1917",
                surface="#292524",
                text_primary="#FEF3C7",
                text_secondary="#FCD34D",
                success="#84CC16",
                warning="#F59E0B",
                error="#EF4444",
                info="#06B6D4"
            ),
            blur_radius=20,
            opacity=0.8
        )
        
        # 5. 赛博朋克主题
        themes[ThemeType.CYBERPUNK] = ThemeConfig(
            name="cyberpunk",
            display_name="赛博朋克",
            colors=ColorScheme(
                primary="#00FFFF",
                secondary="#FF00FF",
                accent="#FFFF00",
                background="#0A0A0A",
                surface="#1A1A1A",
                text_primary="#00FF00",
                text_secondary="#00CCCC",
                success="#00FF00",
                warning="#FFFF00",
                error="#FF0080",
                info="#00FFFF"
            ),
            blur_radius=25,
            opacity=0.7,
            animation_duration=500
        )
        
        # 6. 极简主义主题
        themes[ThemeType.MINIMALIST] = ThemeConfig(
            name="minimalist",
            display_name="极简主义",
            colors=ColorScheme(
                primary="#000000",
                secondary="#666666",
                accent="#999999",
                background="#FAFAFA",
                surface="#FFFFFF",
                text_primary="#000000",
                text_secondary="#666666",
                success="#4CAF50",
                warning="#FF9800",
                error="#F44336",
                info="#2196F3"
            ),
            blur_radius=5,
            opacity=1.0,
            border_radius=4
        )
        
        # 7. 高对比度主题（无障碍友好）
        themes[ThemeType.HIGH_CONTRAST] = ThemeConfig(
            name="high_contrast",
            display_name="高对比度",
            colors=ColorScheme(
                primary="#FFFFFF",
                secondary="#FFFF00",
                accent="#00FFFF",
                background="#000000",
                surface="#1A1A1A",
                text_primary="#FFFFFF",
                text_secondary="#FFFF00",
                success="#00FF00",
                warning="#FFFF00",
                error="#FF0000",
                info="#00FFFF"
            ),
            blur_radius=0,
            opacity=1.0,
            border_radius=0,
            font_size=16  # 更大的字体提高可读性
        )
        
        return themes
    
    def get_current_theme(self) -> ThemeConfig:
        """获取当前主题配置"""
        return self.themes[self.current_theme]
    
    def set_theme(self, theme_type: ThemeType) -> bool:
        """设置主题"""
        if theme_type in self.themes:
            self.current_theme = theme_type
            self._save_user_preferences()
            return True
        return False
    
    def get_available_themes(self) -> Dict[str, str]:
        """获取可用主题列表"""
        return {
            theme_type.value: config.display_name 
            for theme_type, config in self.themes.items()
        }
    
    def generate_stylesheet(self, theme_type: Optional[ThemeType] = None) -> str:
        """生成主题样式表"""
        theme = self.themes[theme_type or self.current_theme]
        
        return f"""
        /* {theme.display_name} 主题样式 */
        QMainWindow {{
            background: {theme.colors.background};
            color: {theme.colors.text_primary};
            font-family: '{theme.font_family}';
            font-size: {theme.font_size}px;
        }}
        
        QFrame {{
            background: {theme.colors.surface};
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: {theme.border_radius}px;
            backdrop-filter: blur({theme.blur_radius}px);
        }}
        
        QLabel {{
            color: {theme.colors.text_primary};
            background: transparent;
        }}
        
        QPushButton {{
            background: {theme.colors.primary};
            color: {theme.colors.text_primary};
            border: none;
            border-radius: {theme.border_radius // 2}px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background: {theme.colors.secondary};
        }}
        
        QPushButton:pressed {{
            background: {theme.colors.accent};
        }}
        
        QTextEdit, QTextBrowser {{
            background: rgba(0, 0, 0, 0.3);
            color: {theme.colors.text_primary};
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: {theme.border_radius}px;
            padding: 12px;
        }}
        
        QCheckBox {{
            color: {theme.colors.text_primary};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {theme.colors.secondary};
            background: transparent;
        }}
        
        QCheckBox::indicator:checked {{
            background: {theme.colors.primary};
            border-color: {theme.colors.primary};
        }}
        
        QScrollBar:vertical {{
            background: rgba(255, 255, 255, 0.1);
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: {theme.colors.secondary};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {theme.colors.primary};
        }}
        
        .success {{
            color: {theme.colors.success};
        }}
        
        .warning {{
            color: {theme.colors.warning};
        }}
        
        .error {{
            color: {theme.colors.error};
        }}
        
        .info {{
            color: {theme.colors.info};
        }}
        """
    
    def get_theme_colors(self, theme_type: Optional[ThemeType] = None) -> ColorScheme:
        """获取主题颜色方案"""
        theme = self.themes[theme_type or self.current_theme]
        return theme.colors
    
    def create_custom_theme(self, name: str, display_name: str, colors: ColorScheme, 
                          **kwargs) -> ThemeType:
        """创建自定义主题"""
        # 创建自定义主题类型
        custom_theme_type = ThemeType(f"custom_{name}")
        
        # 创建主题配置
        theme_config = ThemeConfig(
            name=name,
            display_name=display_name,
            colors=colors,
            **kwargs
        )
        
        # 添加到主题列表
        self.themes[custom_theme_type] = theme_config
        
        return custom_theme_type
    
    def export_theme(self, theme_type: ThemeType, file_path: str) -> bool:
        """导出主题配置"""
        try:
            theme = self.themes[theme_type]
            theme_data = {
                'name': theme.name,
                'display_name': theme.display_name,
                'colors': {
                    'primary': theme.colors.primary,
                    'secondary': theme.colors.secondary,
                    'accent': theme.colors.accent,
                    'background': theme.colors.background,
                    'surface': theme.colors.surface,
                    'text_primary': theme.colors.text_primary,
                    'text_secondary': theme.colors.text_secondary,
                    'success': theme.colors.success,
                    'warning': theme.colors.warning,
                    'error': theme.colors.error,
                    'info': theme.colors.info
                },
                'blur_radius': theme.blur_radius,
                'opacity': theme.opacity,
                'border_radius': theme.border_radius,
                'font_family': theme.font_family,
                'font_size': theme.font_size,
                'animation_duration': theme.animation_duration
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def import_theme(self, file_path: str) -> Optional[ThemeType]:
        """导入主题配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            colors = ColorScheme(**theme_data['colors'])
            
            return self.create_custom_theme(
                name=theme_data['name'],
                display_name=theme_data['display_name'],
                colors=colors,
                blur_radius=theme_data.get('blur_radius', 15),
                opacity=theme_data.get('opacity', 0.85),
                border_radius=theme_data.get('border_radius', 12),
                font_family=theme_data.get('font_family', 'PingFang SC'),
                font_size=theme_data.get('font_size', 14),
                animation_duration=theme_data.get('animation_duration', 300)
            )
        except Exception:
            return None
    
    def _load_user_preferences(self):
        """加载用户偏好设置"""
        try:
            config_dir = Path.home() / '.interactive_feedback_mcp'
            config_file = config_dir / 'theme_preferences.json'
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    theme_name = prefs.get('current_theme')
                    if theme_name:
                        for theme_type in ThemeType:
                            if theme_type.value == theme_name:
                                self.current_theme = theme_type
                                break
        except Exception:
            pass  # 使用默认主题
    
    def _save_user_preferences(self):
        """保存用户偏好设置"""
        try:
            config_dir = Path.home() / '.interactive_feedback_mcp'
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / 'theme_preferences.json'
            
            prefs = {
                'current_theme': self.current_theme.value,
                'last_updated': str(Path(__file__).stat().st_mtime)
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # 静默失败
    
    def get_responsive_font_size(self, base_size: int, screen_width: int) -> int:
        """根据屏幕宽度计算响应式字体大小"""
        if screen_width < 1200:
            return max(10, base_size - 2)
        elif screen_width > 1920:
            return base_size + 2
        else:
            return base_size
    
    def get_responsive_spacing(self, base_spacing: int, screen_width: int) -> int:
        """根据屏幕宽度计算响应式间距"""
        if screen_width < 1200:
            return max(4, base_spacing - 4)
        elif screen_width > 1920:
            return base_spacing + 4
        else:
            return base_spacing

# 全局主题管理器实例
theme_manager = EnhancedThemeManager()

def get_theme_manager() -> EnhancedThemeManager:
    """获取主题管理器实例"""
    return theme_manager 