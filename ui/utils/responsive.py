# Responsive Design Utilities
# 响应式设计工具模块

from typing import Tuple, Dict, Any
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSize

class ScreenSizeManager:
    """屏幕尺寸管理器 - 实现响应式设计"""
    
    # 屏幕尺寸分类
    SCREEN_SIZES = {
        'small': (1280, 720),      # 小屏幕
        'medium': (1600, 900),     # 中等屏幕
        'large': (1920, 1080),     # 大屏幕
        'xlarge': (2560, 1440),    # 超大屏幕
    }
    
    # 窗口尺寸配置
    WINDOW_CONFIGS = {
        'small': {
            'size': (1000, 700),
            'min_size': (800, 600),
            'panel_ratios': [35, 40, 25],  # 小屏幕调整比例
            'font_scale': 0.9,
            'spacing': 6,
            'margins': (6, 6, 6, 6)
        },
        'medium': {
            'size': (1400, 1000),
            'min_size': (1000, 700),
            'panel_ratios': [40, 40, 20],  # 标准比例
            'font_scale': 1.0,
            'spacing': 8,
            'margins': (8, 8, 8, 8)
        },
        'large': {
            'size': (1600, 1200),
            'min_size': (1200, 800),
            'panel_ratios': [40, 40, 20],
            'font_scale': 1.1,
            'spacing': 10,
            'margins': (10, 10, 10, 10)
        },
        'xlarge': {
            'size': (1800, 1400),
            'min_size': (1400, 1000),
            'panel_ratios': [42, 38, 20],  # 大屏幕优化比例
            'font_scale': 1.2,
            'spacing': 12,
            'margins': (12, 12, 12, 12)
        }
    }
    
    @classmethod
    def get_screen_category(cls) -> str:
        """获取当前屏幕分类"""
        screen = QApplication.primaryScreen()
        if not screen:
            return 'medium'
            
        geometry = screen.geometry()
        width, height = geometry.width(), geometry.height()
        
        # 根据屏幕尺寸分类
        if width <= 1280 or height <= 720:
            return 'small'
        elif width <= 1600 or height <= 900:
            return 'medium'
        elif width <= 1920 or height <= 1080:
            return 'large'
        else:
            return 'xlarge'
    
    @classmethod
    def get_optimal_window_size(cls, screen_category: str = None) -> Tuple[int, int]:
        """获取最佳窗口尺寸"""
        if screen_category is None:
            screen_category = cls.get_screen_category()
            
        config = cls.WINDOW_CONFIGS.get(screen_category, cls.WINDOW_CONFIGS['medium'])
        return config['size']
    
    @classmethod
    def get_minimum_window_size(cls, screen_category: str = None) -> Tuple[int, int]:
        """获取最小窗口尺寸"""
        if screen_category is None:
            screen_category = cls.get_screen_category()
            
        config = cls.WINDOW_CONFIGS.get(screen_category, cls.WINDOW_CONFIGS['medium'])
        return config['min_size']
    
    @classmethod
    def get_panel_ratios(cls, screen_category: str = None) -> list:
        """获取面板比例"""
        if screen_category is None:
            screen_category = cls.get_screen_category()
            
        config = cls.WINDOW_CONFIGS.get(screen_category, cls.WINDOW_CONFIGS['medium'])
        return config['panel_ratios']
    
    @classmethod
    def get_font_scale(cls, screen_category: str = None) -> float:
        """获取字体缩放比例"""
        if screen_category is None:
            screen_category = cls.get_screen_category()
            
        config = cls.WINDOW_CONFIGS.get(screen_category, cls.WINDOW_CONFIGS['medium'])
        return config['font_scale']
    
    @classmethod
    def get_spacing_config(cls, screen_category: str = None) -> Dict[str, Any]:
        """获取间距配置"""
        if screen_category is None:
            screen_category = cls.get_screen_category()
            
        config = cls.WINDOW_CONFIGS.get(screen_category, cls.WINDOW_CONFIGS['medium'])
        return {
            'spacing': config['spacing'],
            'margins': config['margins']
        }
    
    @classmethod
    def get_responsive_config(cls, screen_category: str = None) -> Dict[str, Any]:
        """获取完整的响应式配置"""
        if screen_category is None:
            screen_category = cls.get_screen_category()
            
        config = cls.WINDOW_CONFIGS.get(screen_category, cls.WINDOW_CONFIGS['medium'])
        
        return {
            'screen_category': screen_category,
            'window_size': config['size'],
            'min_size': config['min_size'],
            'panel_ratios': config['panel_ratios'],
            'font_scale': config['font_scale'],
            'spacing': config['spacing'],
            'margins': config['margins']
        }

class AdaptiveLayoutManager:
    """自适应布局管理器"""
    
    def __init__(self):
        self.current_config = ScreenSizeManager.get_responsive_config()
        
    def update_for_screen_size(self, width: int, height: int) -> Dict[str, Any]:
        """根据屏幕尺寸更新配置"""
        # 动态确定屏幕分类
        if width <= 1280 or height <= 720:
            category = 'small'
        elif width <= 1600 or height <= 900:
            category = 'medium'
        elif width <= 1920 or height <= 1080:
            category = 'large'
        else:
            category = 'xlarge'
            
        self.current_config = ScreenSizeManager.get_responsive_config(category)
        return self.current_config
    
    def get_adaptive_font_size(self, base_size: int) -> int:
        """获取自适应字体大小"""
        scale = self.current_config['font_scale']
        return max(8, int(base_size * scale))
    
    def get_adaptive_spacing(self) -> int:
        """获取自适应间距"""
        return self.current_config['spacing']
    
    def get_adaptive_margins(self) -> Tuple[int, int, int, int]:
        """获取自适应边距"""
        return tuple(self.current_config['margins'])
    
    def should_use_compact_layout(self) -> bool:
        """是否应该使用紧凑布局"""
        return self.current_config['screen_category'] == 'small'
    
    def get_component_sizes(self) -> Dict[str, int]:
        """获取组件尺寸配置"""
        category = self.current_config['screen_category']
        
        if category == 'small':
            return {
                'text_browser_height': 300,
                'context_height': 150,
                'input_height': 80,
                'button_height': 32,
                'checkbox_size': 16
            }
        elif category == 'medium':
            return {
                'text_browser_height': 450,
                'context_height': 250,
                'input_height': 120,
                'button_height': 36,
                'checkbox_size': 18
            }
        elif category == 'large':
            return {
                'text_browser_height': 500,
                'context_height': 300,
                'input_height': 140,
                'button_height': 40,
                'checkbox_size': 20
            }
        else:  # xlarge
            return {
                'text_browser_height': 600,
                'context_height': 350,
                'input_height': 160,
                'button_height': 44,
                'checkbox_size': 22
            }

# 全局响应式管理器实例
responsive_manager = AdaptiveLayoutManager() 