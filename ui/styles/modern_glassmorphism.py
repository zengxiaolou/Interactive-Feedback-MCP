# Modern Glassmorphism Theme for Interactive Feedback MCP
# 现代化毛玻璃主题样式

class ModernGlassmorphismTheme:
    """现代化毛玻璃主题"""
    
    # 颜色配置
    COLORS = {
        # 主色调 - 渐变蓝绿
        'primary': '#00D4FF',
        'primary_dark': '#0099CC',
        'primary_light': '#66E0FF',
        
        # 背景色 - 深色系
        'bg_primary': '#1a1a1a',
        'bg_secondary': '#2d2d2d',
        'bg_tertiary': '#3a3a3a',
        'bg_card': '#404040',
        
        # 文字颜色
        'text_primary': '#ffffff',
        'text_secondary': '#cccccc',
        'text_muted': '#999999',
        'text_accent': '#00D4FF',
        
        # 状态颜色
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'info': '#2196F3',
        
        # 边框和分隔线
        'border': '#555555',
        'border_light': '#666666',
        'divider': '#333333',
    }
    
    @staticmethod
    def get_main_window_style():
        """获取主窗口样式 - 现代化毛玻璃设计"""
        return f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(26, 26, 26, 0.95),
                    stop:0.5 rgba(45, 45, 45, 0.90),
                    stop:1 rgba(58, 58, 58, 0.95));
                color: {ModernGlassmorphismTheme.COLORS['text_primary']};
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            QWidget {{
                background-color: transparent;
                color: {ModernGlassmorphismTheme.COLORS['text_primary']};
                font-family: 'SF Pro Display', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', sans-serif;
            }}
        """
    
    @staticmethod
    def get_panel_style():
        """获取面板样式 - 毛玻璃拟态效果"""
        return f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 16px;
                margin: 5px;
                backdrop-filter: blur(20px);
            }}
            
            QFrame:hover {{
                border-color: rgba(0, 212, 255, 0.3);
                background: rgba(255, 255, 255, 0.12);
            }}
        """
    
    @staticmethod
    def get_title_style(color='#4CAF50'):
        """获取标题样式"""
        return f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {color};
                padding: 10px;
                border-bottom: 2px solid {color};
                margin-bottom: 10px;
                min-height: 24px;
                max-height: 24px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px 8px 0px 0px;
            }}
        """
    
    @staticmethod
    def get_text_browser_style():
        """获取文本浏览器样式 - 现代化设计"""
        return f"""
            QTextBrowser {{
                border: 2px solid {ModernGlassmorphismTheme.COLORS['border']};
                border-radius: 12px;
                padding: 20px;
                background: rgba(255, 255, 255, 0.08);
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
                line-height: 1.6;
                color: {ModernGlassmorphismTheme.COLORS['text_primary']};
                selection-background-color: rgba(0, 212, 255, 0.3);
            }}
            
            QTextBrowser:focus {{
                border-color: {ModernGlassmorphismTheme.COLORS['primary']};
                background: rgba(255, 255, 255, 0.12);
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
            }}
            
            QTextBrowser a {{
                color: {ModernGlassmorphismTheme.COLORS['primary']};
                text-decoration: underline;
            }}
            
            QTextBrowser a:hover {{
                color: {ModernGlassmorphismTheme.COLORS['primary_light']};
            }}
            
            QTextBrowser code {{
                background-color: rgba(30, 30, 30, 0.8);
                color: #7dd3fc;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 2px 4px;
                font-family: 'Cascadia Code', 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }}
            
            QTextBrowser pre {{
                background-color: rgba(30, 30, 30, 0.8);
                color: #e5e5e5;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 12px;
                margin: 8px 0;
                font-family: 'Cascadia Code', 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                line-height: 1.4;
            }}
        """ + ModernGlassmorphismTheme.get_scrollbar_style()
    
    @staticmethod
    def get_text_edit_style():
        """获取文本编辑器样式"""
        return f"""
            QTextEdit {{
                border: 2px solid {ModernGlassmorphismTheme.COLORS['border']};
                border-radius: 12px;
                padding: 15px;
                background: rgba(255, 255, 255, 0.08);
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
                color: {ModernGlassmorphismTheme.COLORS['text_primary']};
                selection-background-color: rgba(0, 212, 255, 0.3);
            }}
            
            QTextEdit:focus {{
                border-color: {ModernGlassmorphismTheme.COLORS['primary']};
                background: rgba(255, 255, 255, 0.12);
                box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
            }}
        """ + ModernGlassmorphismTheme.get_scrollbar_style()
    
    @staticmethod
    def get_checkbox_style():
        """获取复选框样式 - 现代化设计"""
        return f"""
            QCheckBox {{
                color: {ModernGlassmorphismTheme.COLORS['text_primary']};
                spacing: 10px;
                padding: 8px;
                font-size: 13px;
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 6px;
                border: 2px solid {ModernGlassmorphismTheme.COLORS['border']};
                background: rgba(255, 255, 255, 0.05);
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {ModernGlassmorphismTheme.COLORS['primary']};
                background: rgba(0, 212, 255, 0.1);
            }}
            
            QCheckBox::indicator:checked {{
                background: {ModernGlassmorphismTheme.COLORS['primary']};
                border-color: {ModernGlassmorphismTheme.COLORS['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTEiIHZpZXdCb3g9IjAgMCAxNCAxMSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEgNS41TDUgOS41TDEzIDEuNSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }}
            
            QCheckBox:hover {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }}
        """
    
    @staticmethod
    def get_button_style(color_type='primary'):
        """获取按钮样式 - 现代按钮设计"""
        if color_type == 'primary':
            bg_color = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {ModernGlassmorphismTheme.COLORS['primary']}, stop:1 {ModernGlassmorphismTheme.COLORS['primary_dark']})"
            border_color = ModernGlassmorphismTheme.COLORS['primary']
        elif color_type == 'success':
            bg_color = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {ModernGlassmorphismTheme.COLORS['success']}, stop:1 #388E3C)"
            border_color = ModernGlassmorphismTheme.COLORS['success']
        elif color_type == 'error':
            bg_color = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {ModernGlassmorphismTheme.COLORS['error']}, stop:1 #C62828)"
            border_color = ModernGlassmorphismTheme.COLORS['error']
        else:
            bg_color = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #666666, stop:1 #555555)"
            border_color = "#666666"
        
        return f"""
            QPushButton {{
                background: {bg_color};
                color: white;
                border: 1px solid {border_color};
                padding: 12px 24px;
                font-size: 13px;
                font-weight: 600;
                border-radius: 10px;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(255, 255, 255, 0.1), 
                    stop:1 rgba(255, 255, 255, 0.05));
                border-color: {ModernGlassmorphismTheme.COLORS['primary_light']};
                box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
            }}
            
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(0, 0, 0, 0.1), 
                    stop:1 rgba(0, 0, 0, 0.05));
            }}
        """
    
    @staticmethod
    def get_info_section_style():
        """获取信息区域样式"""
        return f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0px;
            }}
            
            QLabel {{
                color: {ModernGlassmorphismTheme.COLORS['text_secondary']};
                font-size: 11px;
                background: transparent;
                border: none;
                padding: 2px 0px;
            }}
        """
    
    @staticmethod
    def get_scrollbar_style():
        """获取滚动条样式 - 现代滚动条"""
        return f"""
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.05);
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background: {ModernGlassmorphismTheme.COLORS['primary']};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {ModernGlassmorphismTheme.COLORS['primary_light']};
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
            }}
            
            QScrollBar:horizontal {{
                background: rgba(255, 255, 255, 0.05);
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {ModernGlassmorphismTheme.COLORS['primary']};
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }}
        """ 