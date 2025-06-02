# Interactive Feedback MCP UI
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by Pau Oliva (https://x.com/pof) with ideas from https://github.com/ttommyth/interactive-mcp
import os
import sys
import json
import argparse
import base64
import uuid
import re  # 将re导入移至顶部
from datetime import datetime
from typing import Optional, TypedDict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QGroupBox,
    QFrame, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QSettings, QUrl, QDateTime, QBuffer, QIODevice
from PySide6.QtGui import QTextCursor, QIcon, QKeyEvent, QPalette, QColor, QTextImageFormat, QTextDocument, QPixmap

class FeedbackResult(TypedDict):
    interactive_feedback: str
    images: List[str]

def get_dark_mode_palette(app: QApplication):
    darkPalette = app.palette()
    darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ToolTipText, Qt.white)
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.BrightText, Qt.red)
    darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    darkPalette.setColor(QPalette.HighlightedText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.PlaceholderText, QColor(127, 127, 127))
    return darkPalette

class FeedbackTextEdit(QTextEdit):
    # 图片处理常量
    DEFAULT_MAX_IMAGE_WIDTH = 1624
    DEFAULT_MAX_IMAGE_HEIGHT = 1624
    DEFAULT_IMAGE_FORMAT = "PNG"

    # 定义类级别的信号
    image_pasted = Signal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_data = []   # 保存图片的Base64数据列表
        # 获取设备的像素比例
        self.device_pixel_ratio = QApplication.primaryScreen().devicePixelRatio()
        # 图片压缩参数
        self.max_image_width = self.DEFAULT_MAX_IMAGE_WIDTH  # 最大宽度
        self.max_image_height = self.DEFAULT_MAX_IMAGE_HEIGHT  # 最大高度
        self.image_format = self.DEFAULT_IMAGE_FORMAT  # 图片格式

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            # Find the parent FeedbackUI instance and call submit
            parent = self.parent()
            while parent and not isinstance(parent, FeedbackUI):
                parent = parent.parent()
            if parent:
                parent._submit_feedback()
        else:
            super().keyPressEvent(event)

    def _convert_image_to_base64(self, image):
        """将图片转换为 Base64 编码字符串"""
        try:
            # 将图片转换为QPixmap
            if not isinstance(image, QPixmap):
                pixmap = QPixmap.fromImage(image)
            else:
                pixmap = image

            # 创建字节缓冲区
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)

            pixmap.save(buffer, self.image_format)
            file_extension = self.image_format.lower()  # 使用小写的格式名作为扩展名

            # 获取字节数据并转换为base64
            byte_array = buffer.data()
            base64_string = base64.b64encode(byte_array).decode('utf-8')
            buffer.close()

            # 返回Base64数据和文件扩展名
            return {
                'data': base64_string,
                'extension': file_extension
            }
        except Exception as e:
            print(f"转换图片为Base64时出错: {e}")
            return None

    # Add this method to handle pasting content, including images
    def insertFromMimeData(self, source_data):
        """
        Handle pasting from mime data, explicitly checking for image data.
        支持视网膜屏幕(Retina Display)的高DPI显示
        """
        try:
            if source_data.hasImage():
                # If the mime data contains an image, convert to Base64
                image = source_data.imageData()
                if image:
                    try:
                        # 使用原始图片，不进行压缩
                        # 转换图片为Base64编码
                        image_result = self._convert_image_to_base64(image)

                        if image_result:
                            # 生成唯一的文件名用于标识
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            unique_id = str(uuid.uuid4())[:8]
                            filename = f"pasted_image_{timestamp}_{unique_id}.{image_result['extension']}"

                            # 保存Base64数据
                            image_info = {
                                'base64': image_result['data'],
                                'filename': filename
                            }
                            self.image_data.append(image_info)

                            # 发出信号，通知上层组件有新图片被粘贴
                            if isinstance(image, QPixmap):
                                pixmap = image
                            else:
                                pixmap = QPixmap.fromImage(image)
                            self.image_pasted.emit(pixmap)

                    except Exception as e:
                        print(f"处理图片时出错: {e}")
                        cursor = self.textCursor()
                        cursor.insertText(f"[图片处理失败: {str(e)}]")
                else:
                    cursor = self.textCursor()
                    cursor.insertText("[图片处理失败: 无效的图片数据]")
            elif source_data.hasHtml():
                # If the mime data contains HTML, insert it as HTML
                super().insertFromMimeData(source_data)
            elif source_data.hasText():
                # If the mime data contains plain text, insert it as plain text
                super().insertFromMimeData(source_data)
            else:
                # For other types, call the base class method
                super().insertFromMimeData(source_data)
        except Exception as e:
            print(f"处理粘贴内容时出错: {e}")
            # 尝试使用基类方法处理
            try:
                super().insertFromMimeData(source_data)
            except:
                cursor = self.textCursor()
                cursor.insertText(f"[粘贴内容失败: {str(e)}]")

    def get_image_data(self):
        """返回图片数据列表（包含Base64编码）"""
        return self.image_data.copy()

class FeedbackUI(QMainWindow):
    # 缓存Markdown实例
    _markdown_instance = None

    def __init__(self, prompt: str, predefined_options: Optional[List[str]] = None):
        super().__init__()
        self.prompt = prompt
        self.predefined_options = predefined_options or []

        self.feedback_result = None

        self.setWindowTitle("Cursor 交互式反馈 MCP")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "images", "feedback.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")

        # Load general UI settings for the main window (geometry, state)
        self.settings.beginGroup("MainWindow_General")

        # 设置窗口大小为屏幕高度的60%，宽度保持800
        screen = QApplication.primaryScreen().geometry()
        screen_height = screen.height()
        window_height = int(screen_height * 0.6)  # 屏幕高度的60%
        window_width = 800

        # 设置窗口的初始大小，但允许用户调整
        self.resize(window_width, window_height)

        # 设置最小窗口尺寸，防止UI元素挤在一起
        self.setMinimumSize(600, 400)

        # 窗口居中显示
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.move(x, y)

        self.settings.endGroup() # End "MainWindow_General" group

        self._create_ui()

    def _preprocess_text(self, text: str) -> str:
        """
        预处理文本，处理转义字符问题
        """
        # 记录原始文本（用于调试）
        print(f"原始文本: {repr(text)}")

        # 这里判断文本中是否包含字面上的 \n（反斜杠 + n）
        # 需要先处理真正的转义序列，然后再处理字面上的 "\n" 字符串

        # 1. 如果文本不包含真正的换行符，但包含 \n 字符序列，则需要替换
        if '\n' not in text and '\\n' in text:
            print("处理字面上的 \\n 字符序列")
            text = text.replace('\\n', '\n')
            text = text.replace('\\t', '\t')
            text = text.replace('\\r', '\r')

        # 2. 替换 Markdown 中的硬换行标记
        text = text.replace('  \n', '\n')

        print(f"预处理后文本: {repr(text)}")
        return text

    def _is_markdown(self, text: str) -> bool:
        """
        检测文本是否可能是Markdown格式
        通过检查常见Markdown语法特征来判断
        """
        # 如果文本为空，不视为Markdown
        if not text or text.strip() == "":
            return False

        # 预处理文本，处理转义字符
        text = self._preprocess_text(text)

        # 检查常见的Markdown语法特征
        markdown_patterns = [
            r'^#{1,6}\s+.+',                  # 标题: # 标题文本
            r'\*\*.+?\*\*',                   # 粗体: **文本**
            r'\*.+?\*',                       # 斜体: *文本*
            r'_.+?_',                         # 斜体: _文本_
            r'`[^`]+`',                       # 行内代码: `代码`
            r'^\s*```',                       # 代码块: ```
            r'^\s*>',                         # 引用: > 文本
            r'^\s*[-*+]\s+',                  # 无序列表: - 项目 或 * 项目 或 + 项目
            r'^\s*\d+\.\s+',                  # 有序列表: 1. 项目
            r'\[.+?\]\(.+?\)',                # 链接: [文本](URL)
            r'!\[.+?\]\(.+?\)',               # 图片: ![alt](URL)
            r'\|.+\|.+\|',                    # 表格
            r'^-{3,}$',                       # 水平线: ---
            r'^={3,}$',                       # 水平线: ===
        ]

        # 遍历文本的每一行，检查是否包含Markdown语法特征
        lines = text.split('\n')
        markdown_features_count = 0

        for line in lines:
            for pattern in markdown_patterns:
                if re.search(pattern, line, re.MULTILINE):
                    markdown_features_count += 1
                    # 如果发现明确的Markdown特征，立即返回True
                    if pattern in [r'^#{1,6}\s+.+', r'^\s*```', r'^\s*>', r'^\s*[-*+]\s+', r'^\s*\d+\.\s+', r'\|.+\|.+\|', r'^-{3,}$', r'^={3,}$']:
                        return True

        # 如果文本中包含一定数量的Markdown特征，则视为Markdown
        # 这里根据特征数量和文本长度的比例来判断
        # 如果特征数量超过2个或特征密度较高，则视为Markdown
        return markdown_features_count >= 2 or (markdown_features_count > 0 and markdown_features_count / len(lines) > 0.1)

    def _convert_text_to_html(self, text: str) -> str:
        """
        将普通文本转换为HTML格式
        保留换行和空格，并进行基本的HTML转义
        """
        # 预处理文本，处理转义字符
        text = self._preprocess_text(text)

        # HTML转义
        escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # 保留换行
        html_text = escaped_text.replace("\n", "<br>")

        # 应用样式，去除多余的缩进
        styled_html = f"""<div style="
            line-height: 1.5;
            color: #ccc;
            font-family: system-ui, -apple-system, sans-serif;
            white-space: pre-wrap;
        ">{html_text}</div>"""

        return styled_html

    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """使用markdown库将markdown转换为HTML"""
        try:
            # 预处理文本，处理转义字符
            markdown_text = self._preprocess_text(markdown_text)

            import markdown
            from markdown.extensions import codehilite, tables, toc

            # 配置markdown扩展
            extensions = ['extra', 'codehilite', 'toc']

            # 使用缓存的Markdown实例或创建新实例
            if FeedbackUI._markdown_instance is None:
                FeedbackUI._markdown_instance = markdown.Markdown(extensions=extensions)

            # 重置实例以确保状态清空
            FeedbackUI._markdown_instance.reset()

            # 转换markdown到HTML
            html = FeedbackUI._markdown_instance.convert(markdown_text)

            # 应用自定义样式，去除多余的缩进
            styled_html = f"""<div style="
                line-height: 1.2;
                color: #ccc;
                font-family: system-ui, -apple-system, sans-serif;
            ">{html}</div>
            <style>
                /* 标题样式 */
                h1 {{ color: #FF9800; margin: 20px 0 15px 0; font-size: 1.3em; }}
                h2 {{ color: #2196F3; margin: 15px 0 10px 0; font-size: 1.2em; }}
                h3 {{ color: #4CAF50; margin: 10px 0 5px 0; font-size: 1.1em; }}

                /* 列表样式 */
                ul {{ margin: 6px 0; padding-left: 20px; }}
                li {{ margin: 4px 0; }}

                /* 代码样式 */
                code {{
                    background-color: rgba(255,255,255,0.1);
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 0.9em;
                }}

                pre {{
                    background-color: rgba(255,255,255,0.05);
                    padding: 12px;
                    border-radius: 6px;
                    overflow-x: auto;
                    border-left: 4px solid #2196F3;
                }}

                /* 段落样式 */
                p {{ margin: 4px 0; }}

                /* 强调样式 */
                strong {{ color: #FFD54F; }}
                em {{ color: #81C784; }}

                /* 表格样式 */
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 10px 0;
                }}
                th, td {{
                    border: 1px solid #444;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: rgba(255,255,255,0.1);
                    font-weight: bold;
                }}
            </style>"""

            return styled_html

        except ImportError:
            # Fallback if markdown library is not installed
            # Log that markdown library is not found and basic conversion is used.
            print("Markdown library not found. Using basic HTML escaping for description.")
            return self._convert_text_to_html(markdown_text)
        except Exception as e:
            # Fallback for any other error during markdown conversion
            print(f"Error during markdown conversion: {e}. Using basic HTML escaping.")
            return self._convert_text_to_html(markdown_text)

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15,12,15,10)

        # Description text area (from self.prompt) - Support multiline, selectable and copyable with markdown support
        self.description_text = QTextEdit()

        # 如果是从命令行参数传入的文本，可能需要特殊处理
        if isinstance(self.prompt, str) and self.prompt.startswith('"') and self.prompt.endswith('"'):
            # 去除引号
            self.prompt = self.prompt[1:-1]

        try:
            # 尝试检测并处理Markdown
            is_markdown = self._is_markdown(self.prompt)

            # 记录日志，帮助调试
            print(f"检测到文本类型: {'Markdown' if is_markdown else '普通文本'}")

            if is_markdown:
                # 尝试使用Markdown库渲染
                try:
                    import markdown
                    self.description_text.setHtml(self._convert_markdown_to_html(self.prompt))
                    print("使用Markdown库渲染成功")
                except ImportError:
                    print("未找到Markdown库，回退到普通文本渲染")
                    self.description_text.setHtml(self._convert_text_to_html(self.prompt))
                except Exception as e:
                    print(f"Markdown渲染失败: {e}，回退到普通文本渲染")
                    self.description_text.setHtml(self._convert_text_to_html(self.prompt))
            else:
                # 使用普通文本渲染
                self.description_text.setHtml(self._convert_text_to_html(self.prompt))
                print("使用普通文本渲染")
        except Exception as e:
            # 如果出现任何错误，回退到最基本的文本显示
            print(f"文本处理过程中出现错误: {e}")

            # 尝试直接将转义字符转换为实际字符后设置为纯文本
            try:
                processed_text = self._preprocess_text(self.prompt)
                self.description_text.setPlainText(processed_text)
                print("使用纯文本显示（预处理后）")
            except:
                # 最后的回退方案
                self.description_text.setPlainText(self.prompt)
                print("使用纯文本显示（原始文本）")

        self.description_text.setReadOnly(True)  # 设置为只读，但可以选择和复制
        self.description_text.setMaximumHeight(600)  # 设置最大高度，防止按钮溢出屏幕
        self.description_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 需要时显示滚动条
        self.description_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Increase font size for description text
        font = self.description_text.font()
        font.setPointSize(font.pointSize() + 3) # Increase font size by 4 points
        self.description_text.setFont(font)

        # 设置样式，让它看起来更像信息展示区域而不是输入框
        self.description_text.setStyleSheet(
            "QTextEdit {"
            "  border: 1px solid #444444;"
            "  border-radius: 8px;"
            "  padding: 15px;margin-bottom:5px;"
            "  background-color: rgba(255, 255, 255, 0.05);"
            "}"
            "QTextEdit:focus {"
            "  border: 1px solid #2196F3;"
            "}"
        )

        layout.addWidget(self.description_text)

        # Add predefined options if any
        self.option_checkboxes = []
        if self.predefined_options and len(self.predefined_options) > 0:
            options_frame = QFrame()
            options_layout = QVBoxLayout(options_frame)
            options_layout.setContentsMargins(0,5,0,5)

            for option in self.predefined_options:
                checkbox = QCheckBox(option)
                # Increase font size for checkboxes
                font = checkbox.font()
                font.setPointSize(font.pointSize() + 3)
                checkbox.setFont(font)
                self.option_checkboxes.append(checkbox)
                options_layout.addWidget(checkbox)

            layout.addWidget(options_frame)

        # 图片预览区域
        self.images_container = QFrame()
        self.images_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        self.images_container.setFixedHeight(80)  # 使用固定高度
        self.images_layout = QHBoxLayout(self.images_container)
        self.images_layout.setSpacing(5)  # 减少图片间距
        self.images_layout.setContentsMargins(0, 0, 0, 5)  # 移除内边距
        self.images_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 图片左对齐且垂直居中
        self.images_container.setVisible(False)  # 默认隐藏

        # 添加水平滚动支持
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(80)  # 使用固定高度
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)  # 无边框
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
            QScrollBar:horizontal {
                height: 8px;
                background: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #666;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        scroll_area.setWidget(self.images_container)
        scroll_area.setVisible(False)  # 默认隐藏滚动区域
        self.scroll_area = scroll_area  # 保存引用以便控制可见性
        layout.addWidget(scroll_area, 0)  # 使用0作为拉伸因子，防止自动拉伸
        # 减小滚动区域与其他元素之间的间距
        layout.setSpacing(2)  # 设置整体布局的间距更小

        # Free-form text feedback
        self.feedback_text = FeedbackTextEdit()
        # 连接图片粘贴信号
        self.feedback_text.image_pasted.connect(self._on_image_pasted)
        # Increase font size and apply modern border to text edit
        font = self.feedback_text.font()
        font.setPointSize(font.pointSize() + 3)
        self.feedback_text.setFont(font)
        self.feedback_text.setStyleSheet(
            "QTextEdit {"
            "  border-radius: 15px;"
            "  padding: 15px;"
            "  margin: 0 0 10px 0;"
            "  border: 1px solid #444444;"
            "}"
        )

        # 设置最小和最大高度，以及滚动策略
        font_metrics = self.feedback_text.fontMetrics()
        row_height = font_metrics.height()
        padding = self.feedback_text.contentsMargins().top() + self.feedback_text.contentsMargins().bottom() + 5

        # 最小高度：5行文本
        min_height = 5 * row_height + padding
        # 最大高度：10行文本，防止输入框过高
        max_height = 10 * row_height + padding

        self.feedback_text.setMinimumHeight(min_height)
        self.feedback_text.setMaximumHeight(max_height)
        self.feedback_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 需要时显示滚动条
        self.feedback_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.feedback_text.setPlaceholderText("在此输入您的下一步要求或反馈 (Ctrl+Enter 提交)")

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Create the submit button
        submit_button = QPushButton("&提交")
        submit_button.clicked.connect(self._submit_feedback)

        # Create the cancel button
        cancel_button = QPushButton("&取消")
        cancel_button.clicked.connect(self.close) # Connect cancel button to close the window

        # Add buttons to the horizontal layout
        button_layout.addWidget(cancel_button) # Put cancel on the left
        button_layout.addWidget(submit_button) # Put submit on the right

        # Apply modern style and increase size for the submit button
        submit_button.setStyleSheet(
            "QPushButton {"
            "  padding: 10px 20px;"
            "  font-size: 14px;"
            "  border-radius: 5px;"
            "  background-color: #2196F3; /* Blue */"
            "  color: white;"
            "  border: none;"
            "}"
            "QPushButton:hover {"
            "  background-color: #1976D2;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #1565C0;"
            "}"
        )

        # Apply modern style and increase size for the cancel button
        cancel_button.setStyleSheet(
            "QPushButton {"
            "  padding: 10px 20px;"
            "  font-size: 14px;"
            "  border-radius: 5px;"
            "  background-color: #9E9E9E; /* Grey */"
            "  color: white;"
            "  border: none;"
            "}"
            "QPushButton:hover {"
            "  background-color: #757575;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #616161;"
            "}"
        )

        layout.addWidget(self.feedback_text)
        layout.addLayout(button_layout)
        # 增加一行文本 ： by rowanyang 居中显示，允许选中和复制文本
        by_rowanyang_label = QLabel("Contact: RowanYang")
        font = by_rowanyang_label.font()
        font.setPointSize(font.pointSize() - 2)  # Decrease font size by 2 points
        by_rowanyang_label.setFont(font)
        by_rowanyang_label.setStyleSheet("color: gray;")
        by_rowanyang_label.setTextInteractionFlags(Qt.TextSelectableByMouse) # Allow text selection

        # Create a QHBoxLayout to align "By RowanYang" to the center
        by_rowanyang_layout = QHBoxLayout()
        by_rowanyang_layout.addStretch(1)
        by_rowanyang_layout.addWidget(by_rowanyang_label)
        by_rowanyang_layout.addStretch(1)
        layout.addSpacing(10) # 为 "By RowanYang" 文本布局添加上边距
        layout.addLayout(by_rowanyang_layout)

    def _submit_feedback(self):
        feedback_text = self.feedback_text.toPlainText().strip()
        selected_options = []

        # Get selected predefined options if any
        if self.option_checkboxes:
            for i, checkbox in enumerate(self.option_checkboxes):
                if checkbox.isChecked():
                    selected_options.append(self.predefined_options[i])

        # Get Base64 image data
        image_data = self.feedback_text.get_image_data()

        # Combine selected options and feedback text
        final_feedback_parts = []

        # Add selected options
        if selected_options:
            final_feedback_parts.append("; ".join(selected_options))

        # Add user's text feedback
        if feedback_text:
            final_feedback_parts.append(feedback_text)

        # Join with a newline if both parts exist
        final_feedback = "\n\n".join(final_feedback_parts)
        images_b64 = [img['base64'] for img in image_data]

        self.feedback_result = FeedbackResult(
            interactive_feedback=final_feedback,
            images=images_b64
        )
        self.close()

    def closeEvent(self, event):
        # Save general UI settings for the main window (geometry, state)
        self.settings.beginGroup("MainWindow_General")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.endGroup()

        super().closeEvent(event)

    def run(self) -> FeedbackResult:
        self.show()
        QApplication.instance().exec()

        if not self.feedback_result:
            return FeedbackResult(interactive_feedback="")

        return self.feedback_result

    # 添加处理图片粘贴的方法
    def _on_image_pasted(self, pixmap):
        """处理粘贴的图片，显示在图片预览区域"""
        # 确保图片容器可见
        if not self.images_container.isVisible():
            self.images_container.setVisible(True)
            self.scroll_area.setVisible(True)  # 同时显示滚动区域
            # 只有第一次显示容器时添加一个弹性空间，确保所有图片靠左对齐
            self.images_layout.addStretch(1)

        # 获取原始图片尺寸
        original_width = pixmap.width()
        original_height = pixmap.height()

        # 固定高度，稍微降低高度确保完整显示
        target_height = 80  # 进一步降低图片高度至40

        # 计算保持宽高比的缩放尺寸
        scaled_width = int(original_width * (target_height / original_height))

        # 创建一个容器帧用于放置图片和删除按钮
        image_frame = QFrame()
        image_frame.setMinimumWidth(scaled_width)
        image_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)

        # 使用QGridLayout，完全没有间距
        frame_layout = QGridLayout(image_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # 创建图片标签
        image_label = QLabel()
        image_label.setStyleSheet("border: none; background: transparent;")
        image_label.setScaledContents(False)
        image_label.setAlignment(Qt.AlignCenter)

        # 确保图片容器有足够空间但不超出
        image_label.setMinimumSize(scaled_width, target_height)
        image_label.setMaximumSize(scaled_width, target_height)

        # 缩放图片，保持宽高比，确保完整显示（contain模式）
        scaled_pixmap = pixmap.scaled(
            scaled_width,
            target_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # 支持视网膜屏幕
        device_pixel_ratio = QApplication.primaryScreen().devicePixelRatio()
        if device_pixel_ratio > 1.0:
            # 对于高DPI屏幕，创建更高分辨率的pixmap
            hires_scaled_width = int(scaled_width * device_pixel_ratio)
            hires_target_height = int(target_height * device_pixel_ratio)

            hires_pixmap = pixmap.scaled(
                hires_scaled_width,
                hires_target_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # 设置设备像素比
            hires_pixmap.setDevicePixelRatio(device_pixel_ratio)
            image_label.setPixmap(hires_pixmap)
        else:
            image_label.setPixmap(scaled_pixmap)

        # 删除按钮，悬浮在右上角
        delete_button = QPushButton("×")
        delete_button.setFixedSize(18, 18)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 0.7);
                color: white;
                border-radius: 9px;
                font-weight: bold;
                border: none;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: red;
            }
        """)

        # 删除图片的功能
        def delete_image():
            # 获取图片索引
            index = self.images_layout.indexOf(image_frame)
            if index >= 0:
                # 从布局中移除
                widget = self.images_layout.itemAt(index).widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

                    # 从图片数据列表中删除
                    if index < len(self.feedback_text.image_data):
                        del self.feedback_text.image_data[index]

                    # 检查是否还有图片
                    has_images = False
                    for i in range(self.images_layout.count()):
                        item = self.images_layout.itemAt(i)
                        if item and not item.spacerItem() and item.widget():
                            has_images = True
                            break

                    # 如果没有图片了，隐藏容器和滚动区域
                    if not has_images:
                        self.images_container.setVisible(False)
                        self.scroll_area.setVisible(False)

        delete_button.clicked.connect(delete_image)

        # 将图片和删除按钮添加到布局
        frame_layout.addWidget(image_label, 0, 0)
        frame_layout.addWidget(delete_button, 0, 0, Qt.AlignTop | Qt.AlignRight)

        # 添加到图片布局，确保在弹性空间之前插入
        if self.images_layout.count() > 0:
            # 找到弹性空间的索引
            stretch_index = -1
            for i in range(self.images_layout.count()):
                if self.images_layout.itemAt(i).spacerItem():
                    stretch_index = i
                    break

            if stretch_index >= 0:
                # 在弹性空间之前插入图片
                self.images_layout.insertWidget(stretch_index, image_frame)
            else:
                # 如果没有找到弹性空间，直接添加到末尾
                self.images_layout.addWidget(image_frame)
        else:
            # 如果布局为空，直接添加图片
            self.images_layout.addWidget(image_frame)

def feedback_ui(prompt: str, predefined_options: Optional[List[str]] = None, output_file: Optional[str] = None) -> Optional[FeedbackResult]:
    app = QApplication.instance() or QApplication()
    app.setPalette(get_dark_mode_palette(app))
    app.setStyle("Fusion")

    # 处理从命令行传入的参数中可能包含的转义字符
    if isinstance(prompt, str) and '\\' in prompt:
        try:
            # 尝试解析可能的Python字符串字面量
            # 注意：这里我们不使用eval，而是手动处理常见的转义序列
            prompt = prompt.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
            print(f"预处理命令行参数: {repr(prompt)}")
        except Exception as e:
            print(f"预处理命令行参数时出错: {e}")

    ui = FeedbackUI(prompt, predefined_options)
    result = ui.run()

    if output_file and result:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        # Save the result to the output file
        with open(output_file, "w") as f:
            json.dump(result, f)
        return None

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行反馈 UI")
    parser.add_argument("--prompt", default="我已经根据您的请求完成了修改。", help="要向用户显示的提示信息")
    parser.add_argument("--predefined-options", default="", help="竖线分隔的预设选项列表 (|||)")
    parser.add_argument("--output-file", help="保存反馈结果的 JSON 文件路径")
    args = parser.parse_args()

    predefined_options = [opt for opt in args.predefined_options.split("|||") if opt] if args.predefined_options else None

    result = feedback_ui(args.prompt, predefined_options, args.output_file)
    if result:
        print(f"\n收到的反馈:\n{result['interactive_feedback']}")
    sys.exit(0)
