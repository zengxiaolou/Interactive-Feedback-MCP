# Enhanced Glassmorphism Theme for Interactive Feedback MCP
# 增强版毛玻璃主题样式

class EnhancedGlassmorphismTheme:
    """增强版毛玻璃效果主题"""
    
    # 色彩系统定义
    COLORS = {
        # 主要颜色
        'primary': '#2196F3',      # 蓝色 - 主要操作
        'secondary': '#4CAF50',    # 绿色 - 成功状态
        'accent': '#FF9800',       # 橙色 - 警告提示
        'error': '#F44336',        # 红色 - 错误状态
        
        # 背景颜色 - 提高对比度
        'bg_primary': 'rgba(15, 20, 30, 0.90)',
        'bg_secondary': 'rgba(255, 255, 255, 0.15)',
        'bg_tertiary': 'rgba(255, 255, 255, 0.10)',
        
        # 文本颜色
        'text_primary': '#FFFFFF',
        'text_secondary': '#CCCCCC',
        'text_muted': '#999999',
        
        # 边框和高光 - 提高对比度
        'border_primary': 'rgba(255, 255, 255, 0.25)',
        'border_secondary': 'rgba(255, 255, 255, 0.15)',
        'highlight': 'rgba(255, 255, 255, 0.35)',
    }
    
    @classmethod
    def get_main_window_style(cls):
        """主窗口样式 - 强制深色毛玻璃效果"""
        return f"""
        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(15, 20, 30, 1.0),
                stop:0.3 rgba(25, 35, 45, 1.0),
                stop:0.7 rgba(20, 30, 40, 1.0),
                stop:1 rgba(10, 15, 25, 1.0));
            border: 2px solid {cls.COLORS['border_primary']};
            border-radius: 20px;
            color: {cls.COLORS['text_primary']};
        }}
        
        QMainWindow::title {{
            background: transparent;
            color: {cls.COLORS['text_primary']};
            font-weight: 600;
            font-size: 14px;
        }}
        
        /* 强制所有子组件使用深色背景 */
        QWidget {{
            background-color: rgba(25, 30, 40, 1.0);
            color: {cls.COLORS['text_primary']};
        }}
        """
    
    @classmethod
    def get_panel_style(cls):
        """面板样式 - 优化的深色毛玻璃背景（更亮更美观）"""
        return f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(60, 70, 80, 0.88),
                stop:0.2 rgba(55, 65, 75, 0.85),
                stop:0.5 rgba(50, 60, 70, 0.82),
                stop:0.8 rgba(55, 65, 75, 0.85),
                stop:1 rgba(60, 70, 80, 0.88));
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            margin: 4px;
            color: {cls.COLORS['text_primary']};
        }}
        
        QFrame:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(70, 80, 90, 0.92),
                stop:0.2 rgba(65, 75, 85, 0.90),
                stop:0.5 rgba(60, 70, 80, 0.88),
                stop:0.8 rgba(65, 75, 85, 0.90),
                stop:1 rgba(70, 80, 90, 0.92));
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        """
    
    @classmethod
    def get_title_style(cls, color=None):
        """标题样式 - 带发光效果"""
        title_color = color or cls.COLORS['primary']
        return f"""
        QLabel {{
            color: {title_color};
            font-size: 16px;
            font-weight: 700;
            padding: 8px 12px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.15),
                stop:0.5 rgba(255, 255, 255, 0.10),
                stop:1 rgba(255, 255, 255, 0.15));
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            margin-bottom: 8px;
        }}
        """
    
    @classmethod
    def get_text_browser_style(cls):
        """文本浏览器样式 - 内阴影效果"""
        return f"""
        QTextBrowser {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 0, 0, 0.5),
                stop:0.1 rgba(0, 0, 0, 0.45),
                stop:0.9 rgba(0, 0, 0, 0.45),
                stop:1 rgba(0, 0, 0, 0.5));
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border_secondary']};
            border-radius: 12px;
            padding: 12px;
            font-size: 13px;
            line-height: 1.5;
            selection-background-color: rgba(33, 150, 243, 0.3);
        }}
        
        QTextBrowser:focus {{
            border: 2px solid {cls.COLORS['primary']};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 0, 0, 0.45),
                stop:0.1 rgba(0, 0, 0, 0.4),
                stop:0.9 rgba(0, 0, 0, 0.4),
                stop:1 rgba(0, 0, 0, 0.45));
        }}
        
        QScrollBar:vertical {{
            background: rgba(255, 255, 255, 0.05);
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.2),
                stop:0.5 rgba(255, 255, 255, 0.15),
                stop:1 rgba(255, 255, 255, 0.2));
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.3),
                stop:0.5 rgba(255, 255, 255, 0.25),
                stop:1 rgba(255, 255, 255, 0.3));
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
    
    @classmethod
    def get_checkbox_style(cls):
        """复选框样式 - 现代化设计"""
        return f"""
        QCheckBox {{
            color: {cls.COLORS['text_primary']};
            font-size: 13px;
            font-weight: 500;
            spacing: 10px;
            padding: 8px;
        }}
        
        QCheckBox:hover {{
            color: {cls.COLORS['primary']};
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {cls.COLORS['border_primary']};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 255, 255, 0.08),
                stop:1 rgba(255, 255, 255, 0.04));
        }}
        
        QCheckBox::indicator:hover {{
            border: 2px solid {cls.COLORS['primary']};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(33, 150, 243, 0.15),
                stop:1 rgba(33, 150, 243, 0.08));
        }}
        
        QCheckBox::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {cls.COLORS['primary']},
                stop:1 rgba(21, 101, 192, 1));
            border: 2px solid {cls.COLORS['primary']};
        }}
        
        QCheckBox::indicator:checked:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(33, 150, 243, 0.9),
                stop:1 rgba(21, 101, 192, 0.9));
        }}
        """
    
    @classmethod
    def get_checkbox_frame_style(cls):
        """复选框容器样式 - 用户指定背景色"""
        return f"""
        QFrame {{
            background: #323a42;
            border: 1px solid {cls.COLORS['border_secondary']};
            border-radius: 8px;
            padding: 6px;
            margin: 3px 0px;
        }}
        
        QFrame:hover {{
            background: #3a4249;
            border: 1px solid {cls.COLORS['primary']};
            transform: translateY(-1px);
        }}
        """
    
    @classmethod
    def get_text_edit_style(cls):
        """文本编辑器样式 - 焦点发光效果"""
        return f"""
        QTextEdit {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 0, 0, 0.35),
                stop:1 rgba(0, 0, 0, 0.25));
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border_secondary']};
            border-radius: 10px;
            padding: 10px;
            font-size: 13px;
            line-height: 1.4;
            selection-background-color: rgba(33, 150, 243, 0.3);
        }}
        
        QTextEdit:focus {{
            border: 2px solid {cls.COLORS['primary']};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 0, 0, 0.4),
                stop:1 rgba(0, 0, 0, 0.3));
            box-shadow: 0 0 20px rgba(33, 150, 243, 0.3);
        }}
        
        QTextEdit:hover {{
            border: 1px solid {cls.COLORS['border_primary']};
        }}
        """
    
    @classmethod
    def get_button_style(cls, button_type='primary'):
        """按钮样式 - 渐变和悬停效果"""
        if button_type == 'primary':
            base_color = cls.COLORS['primary']
            hover_color = 'rgba(33, 150, 243, 0.9)'
        elif button_type == 'secondary':
            base_color = cls.COLORS['secondary']
            hover_color = 'rgba(76, 175, 80, 0.9)'
        elif button_type == 'error':
            base_color = cls.COLORS['error']
            hover_color = 'rgba(244, 67, 54, 0.9)'
        else:
            base_color = cls.COLORS['primary']
            hover_color = 'rgba(33, 150, 243, 0.9)'
        
        return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {base_color},
                stop:1 rgba({base_color[4:-1]}, 0.8));
            color: white;
            border: 1px solid rgba({base_color[4:-1]}, 0.6);
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 600;
            min-height: 16px;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {hover_color},
                stop:1 rgba({base_color[4:-1]}, 0.9));
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba({base_color[4:-1]}, 0.3);
        }}
        
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba({base_color[4:-1]}, 0.7),
                stop:1 rgba({base_color[4:-1]}, 0.9));
            transform: translateY(0px);
        }}
        
        QPushButton:disabled {{
            background: rgba(255, 255, 255, 0.1);
            color: {cls.COLORS['text_muted']};
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        """
    
    @classmethod
    def get_info_section_style(cls):
        """信息区域样式 - 内嵌效果"""
        return f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 0, 0, 0.2),
                stop:0.5 rgba(0, 0, 0, 0.15),
                stop:1 rgba(0, 0, 0, 0.2));
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 8px;
            margin: 4px 0px;
        }}
        
        QFrame:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 0, 0, 0.25),
                stop:0.5 rgba(0, 0, 0, 0.2),
                stop:1 rgba(0, 0, 0, 0.25));
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        """
    
    @classmethod
    def get_label_style(cls, color=None, size='normal'):
        """标签样式"""
        label_color = color or cls.COLORS['text_secondary']
        
        size_map = {
            'small': '11px',
            'normal': '13px',
            'large': '15px',
            'title': '16px'
        }
        
        font_size = size_map.get(size, '13px')
        
        return f"""
        QLabel {{
            color: {label_color};
            font-size: {font_size};
            font-weight: 500;
            padding: 2px 4px;
        }}
        """
    
    @classmethod
    def get_splitter_style(cls):
        """分割器样式"""
        return f"""
        QSplitter::handle {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.1),
                stop:0.5 rgba(255, 255, 255, 0.15),
                stop:1 rgba(255, 255, 255, 0.1));
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 3px;
            margin: 2px;
        }}
        
        QSplitter::handle:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(33, 150, 243, 0.2),
                stop:0.5 rgba(33, 150, 243, 0.3),
                stop:1 rgba(33, 150, 243, 0.2));
            border: 1px solid {cls.COLORS['primary']};
        }}
        
        QSplitter::handle:pressed {{
            background: {cls.COLORS['primary']};
        }}
        """
    
    @classmethod
    def get_animation_css(cls):
        """CSS动画定义（用于支持动画的组件）"""
        return """
        /* 悬停动画 */
        .hover-lift {
            transition: transform 0.2s ease-in-out;
        }
        
        .hover-lift:hover {
            transform: translateY(-2px);
        }
        
        /* 焦点发光动画 */
        .focus-glow {
            transition: box-shadow 0.3s ease-in-out;
        }
        
        .focus-glow:focus {
            box-shadow: 0 0 20px rgba(33, 150, 243, 0.4);
        }
        
        /* 渐入动画 */
        .fade-in {
            animation: fadeIn 0.3s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        """ 