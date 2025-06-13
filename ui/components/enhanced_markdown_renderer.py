#!/usr/bin/env python3
"""
Enhanced Markdown Renderer for Interactive Feedback MCP
增强的Markdown渲染器 - 方案A实现
"""

import re
import hashlib
from typing import Dict, Optional
from urllib.parse import urlparse

try:
    import markdown
    from markdown.extensions import codehilite, fenced_code, tables, toc
    from pygments.formatters import HtmlFormatter
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.util import ClassNotFound
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("⚠️ python-markdown 或 pygments 未安装，使用基础渲染")

from PySide6.QtWidgets import QTextBrowser, QApplication
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

class EnhancedMarkdownRenderer:
    """增强的Markdown渲染器"""
    
    def __init__(self):
        self.cache = {}
        self.max_cache_size = 100
        
        if MARKDOWN_AVAILABLE:
            self._setup_markdown()
        else:
            self.md = None
    
    def _setup_markdown(self):
        """设置markdown渲染器"""
        self.md = markdown.Markdown(
            extensions=[
                'codehilite',      # 代码高亮
                'fenced_code',     # 围栏代码块
                'tables',          # 表格支持
                'toc',             # 目录生成
                'admonition',      # 警告框
                'attr_list',       # 属性列表
                'def_list',        # 定义列表
                'footnotes',       # 脚注
                'nl2br',           # 换行转换
                'sane_lists',      # 智能列表
                'smarty',          # 智能标点
                'abbr',            # 缩写
                'meta',            # 元数据
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True,
                    'pygments_style': 'monokai',
                    'linenums': False,
                    'guess_lang': True
                },
                'toc': {
                    'permalink': True,
                    'permalink_title': '链接到此标题'
                }
            }
        )
        
        # 获取Pygments CSS样式
        self.pygments_css = HtmlFormatter(style='monokai').get_style_defs('.highlight')
    
    def render(self, text: str) -> str:
        """渲染markdown文本为HTML"""
        if not text:
            return ""
        
        # 检查缓存
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.cache:
            return self.cache[text_hash]
        
        if MARKDOWN_AVAILABLE and self.md:
            html = self._render_with_markdown(text)
        else:
            html = self._render_basic(text)
        
        # 添加到缓存
        if len(self.cache) >= self.max_cache_size:
            # 移除最旧的缓存项
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[text_hash] = html
        return html
    
    def _render_with_markdown(self, text: str) -> str:
        """使用python-markdown渲染"""
        try:
            # 确保文本是正确的编码
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            
            # 重置markdown实例
            self.md.reset()
            
            # 渲染markdown
            html_content = self.md.convert(text)
            
            # 包装在完整的HTML中
            full_html = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    {self._get_custom_css()}
                    {self.pygments_css}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            return full_html
            
        except Exception as e:
            print(f"⚠️ Markdown渲染失败: {e}")
            return self._render_basic(text)
    
    def _render_basic(self, text: str) -> str:
        """基础渲染（回退方案）"""
        # 确保文本是正确的编码
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='replace')
            
        # 简单的文本到HTML转换
        html = text.replace('\n', '<br>')
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        html = html.replace('*', '<em>').replace('*', '</em>')
        html = html.replace('`', '<code>').replace('`', '</code>')
        
        return f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>{self._get_custom_css()}</style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
    
    def _get_custom_css(self) -> str:
        """获取自定义CSS样式"""
        return """
        body {
            font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'SimHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: transparent;
            color: #ffffff;
            line-height: 1.6;
            margin: 0;
            padding: 16px;
            font-size: 14px;
        }
        
        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {
            color: #2196F3;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        
        h1 { font-size: 24px; border-bottom: 2px solid rgba(33, 150, 243, 0.3); padding-bottom: 8px; }
        h2 { font-size: 20px; border-bottom: 1px solid rgba(33, 150, 243, 0.2); padding-bottom: 6px; }
        h3 { font-size: 18px; }
        h4 { font-size: 16px; }
        h5 { font-size: 14px; }
        h6 { font-size: 13px; }
        
        /* 段落样式 */
        p {
            margin: 12px 0;
            text-align: justify;
        }
        
        /* 代码块样式 */
        .highlight {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            border-left: 4px solid #2196F3;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            overflow-x: auto;
        }
        
        .highlight pre {
            margin: 0;
            font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #f8f8f2;
        }
        
        /* 行内代码 */
        code {
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
            font-size: 13px;
            color: #ff6b6b;
        }
        
        /* 表格样式 */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            overflow: hidden;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        th, td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        th {
            background: rgba(33, 150, 243, 0.2);
            font-weight: 600;
            color: #2196F3;
            font-size: 13px;
        }
        
        tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        /* 引用块样式 */
        blockquote {
            margin: 16px 0;
            padding: 16px 20px;
            background: rgba(156, 39, 176, 0.1);
            border-left: 4px solid #9C27B0;
            border-radius: 0 8px 8px 0;
            backdrop-filter: blur(10px);
            position: relative;
            font-style: italic;
        }
        
        blockquote p {
            margin: 0;
        }
        
        /* 列表样式 */
        ul, ol {
            margin: 12px 0;
            padding-left: 24px;
        }
        
        li {
            margin: 6px 0;
        }
        
        /* 链接样式 */
        a {
            color: #64B5F6;
            text-decoration: none;
            border-bottom: 1px solid rgba(100, 181, 246, 0.3);
            transition: all 0.2s ease;
        }
        
        a:hover {
            color: #2196F3;
            border-bottom-color: #2196F3;
        }
        
        /* 警告框样式 */
        .admonition {
            margin: 16px 0;
            padding: 16px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        
        .admonition.note {
            background: rgba(33, 150, 243, 0.1);
            border-left: 4px solid #2196F3;
        }
        
        .admonition.warning {
            background: rgba(255, 152, 0, 0.1);
            border-left: 4px solid #FF9800;
        }
        
        .admonition.danger {
            background: rgba(244, 67, 54, 0.1);
            border-left: 4px solid #F44336;
        }
        
        .admonition-title {
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        /* 分隔线 */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.3), transparent);
            margin: 24px 0;
        }
        
        /* 脚注 */
        .footnote {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
        }
        
        /* 任务列表 */
        .task-list-item {
            list-style: none;
        }
        
        .task-list-item input[type="checkbox"] {
            margin-right: 8px;
        }
        """

class EnhancedTextBrowser(QTextBrowser):
    """增强的文本浏览器，支持高级markdown渲染"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.renderer = EnhancedMarkdownRenderer()
        self.setOpenExternalLinks(False)  # 我们自己处理链接
        self.anchorClicked.connect(self._handle_link_click)
        
        # 设置基础样式，包含中文字体
        self.setStyleSheet("""
            QTextBrowser {
                background: transparent;
                border: none;
                selection-background-color: rgba(33, 150, 243, 0.3);
                font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'SimHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
        """)
    
    def set_markdown_content(self, markdown_text: str):
        """设置markdown内容"""
        html = self.renderer.render(markdown_text)
        self.setHtml(html)
    
    def _handle_link_click(self, url: QUrl):
        """处理链接点击"""
        url_string = url.toString()
        
        if url.scheme() in ['http', 'https']:
            # 外部链接用浏览器打开
            QDesktopServices.openUrl(url)
        elif url.scheme() == 'file':
            # 本地文件链接
            QDesktopServices.openUrl(url)
        elif url.scheme() == 'mailto':
            # 邮件链接
            QDesktopServices.openUrl(url)
        else:
            # 内部锚点链接
            fragment = url.fragment()
            if fragment:
                self.scrollToAnchor(fragment)
            else:
                # 可能是相对链接，尝试作为锚点处理
                self.scrollToAnchor(url_string.lstrip('#'))
    
    def get_renderer_info(self) -> Dict[str, any]:
        """获取渲染器信息"""
        return {
            'markdown_available': MARKDOWN_AVAILABLE,
            'cache_size': len(self.renderer.cache),
            'max_cache_size': self.renderer.max_cache_size,
            'extensions': [
                'codehilite', 'fenced_code', 'tables', 'toc',
                'admonition', 'attr_list', 'def_list', 'footnotes',
                'nl2br', 'sane_lists', 'smarty', 'abbr', 'meta'
            ] if MARKDOWN_AVAILABLE else []
        } 