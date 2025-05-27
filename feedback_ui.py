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
from datetime import datetime
from typing import Optional, TypedDict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QGroupBox,
    QFrame
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QSettings, QUrl, QDateTime, QBuffer, QIODevice
from PySide6.QtGui import QTextCursor, QIcon, QKeyEvent, QPalette, QColor, QTextImageFormat, QTextDocument, QPixmap

class FeedbackResult(TypedDict):
    interactive_feedback: str

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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_data = []   # 保存图片的Base64数据列表

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
            from PySide6.QtCore import QBuffer, QIODevice
            from PySide6.QtGui import QPixmap

            # 将图片转换为QPixmap（如果不是的话）
            if not isinstance(image, QPixmap):
                pixmap = QPixmap.fromImage(image)
            else:
                pixmap = image

            # 创建字节缓冲区
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)

            # 将pixmap保存到缓冲区为PNG格式
            pixmap.save(buffer, "PNG")

            # 获取字节数据并转换为base64
            byte_array = buffer.data()
            base64_string = base64.b64encode(byte_array).decode('utf-8')
            buffer.close()

            return base64_string
        except Exception as e:
            print(f"转换图片为Base64时出错: {e}")
            return None

    # Add this method to handle pasting content, including images
    def insertFromMimeData(self, source_data):
        """
        Handle pasting from mime data, explicitly checking for image data.
        """
        if source_data.hasImage():
            # If the mime data contains an image, convert to Base64
            image = source_data.imageData()
            if image:
                # 转换图片为Base64编码
                base64_data = self._convert_image_to_base64(image)

                if base64_data:
                    # 生成唯一的文件名用于标识
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"pasted_image_{timestamp}_{unique_id}.png"

                    # 保存Base64数据
                    image_info = {
                        'base64': base64_data,
                        'filename': filename
                    }
                    self.image_data.append(image_info)

                    # 生成一个唯一URL用于在界面中显示
                    timestamp_ms = QDateTime.currentMSecsSinceEpoch()
                    image_url = QUrl(f"image://pasted_image_{timestamp_ms}")

                    # 将图片添加到文档资源中以便显示
                    self.document().addResource(QTextDocument.ImageResource, image_url, image)

                    # 在光标位置插入图片
                    cursor = self.textCursor()
                    image_format = QTextImageFormat()
                    # image_format.setToolTip(f"图片已添加: {filename}")
                    image_format.setName(image_url.toString())
                    cursor.insertImage(image_format)

                    # 在图片后添加一个换行和简要信息
                    # cursor.insertText(f"\n[图片已添加: {filename}]\n")
                else:
                    # 如果转换失败，插入错误信息
                    cursor = self.textCursor()
                    cursor.insertText("[图片处理失败]")
        elif source_data.hasHtml():
            # If the mime data contains HTML, insert it as HTML
            super().insertFromMimeData(source_data)
        elif source_data.hasText():
            # If the mime data contains plain text, insert it as plain text
            super().insertFromMimeData(source_data)
        else:
            # For other types, call the base class method
            super().insertFromMimeData(source_data)

    def get_image_data(self):
        """返回图片数据列表（包含Base64编码）"""
        return self.image_data.copy()

class FeedbackUI(QMainWindow):
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

        # 固定窗口大小，不允许调整
        self.setFixedSize(window_width, window_height)

        # 窗口居中显示
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.move(x, y)

        self.settings.endGroup() # End "MainWindow_General" group

        self._create_ui()

    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """使用markdown库将markdown转换为HTML"""
        try:
            import markdown
            from markdown.extensions import codehilite, tables, toc

            # 配置markdown扩展
            extensions = ['extra', 'codehilite', 'toc']

            # 创建markdown实例
            md = markdown.Markdown(extensions=extensions)

            # 转换markdown到HTML
            html = md.convert(markdown_text)

            # 应用自定义样式
            styled_html = f"""
            <div style="
                line-height: 1.6;
                color: white;
                font-family: system-ui, -apple-system, sans-serif;
            ">
                {html}
            </div>
            <style>
                /* 标题样式 */
                h1 {{ color: #FF9800; margin: 20px 0 15px 0; font-size: 1.5em; }}
                h2 {{ color: #2196F3; margin: 15px 0 10px 0; font-size: 1.3em; }}
                h3 {{ color: #4CAF50; margin: 10px 0 5px 0; font-size: 1.1em; }}

                /* 列表样式 */
                ul {{ margin: 10px 0; padding-left: 20px; }}
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
                p {{ margin: 8px 0; }}

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
            </style>
            """

            return styled_html

        except ImportError:
            # 如果markdown库未安装，回退到简单转换
            return self._simple_markdown_to_html(markdown_text)
        except Exception as e:
            # 如果转换出错，显示原始文本
            return f'<div style="color: white; line-height: 1.5;">{markdown_text.replace("<", "&lt;").replace(">", "&gt;")}</div>'

    def _simple_markdown_to_html(self, markdown_text: str) -> str:
        """简单的markdown到HTML转换，作为后备方案"""
        import re

        html = markdown_text

        # HTML转义
        html = html.replace('<', '&lt;').replace('>', '&gt;')

        # 替换换行符为HTML换行
        html = html.replace('\n', '<br>')

        # 处理粗体 **text** -> <b>text</b>
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #FFD54F;">\1</strong>', html)

        # 处理斜体 *text* -> <i>text</i>
        html = re.sub(r'\*(.*?)\*', r'<em style="color: #81C784;">\1</em>', html)

        # 处理代码块 `code` -> <code>code</code>
        html = re.sub(r'`([^`]+)`', r'<code style="background-color: rgba(255,255,255,0.1); padding: 2px 4px; border-radius: 3px; font-family: monospace;">\1</code>', html)

        # 处理标题
        html = re.sub(r'^### (.*?)$', r'<h3 style="color: #4CAF50; margin: 10px 0 5px 0;">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2 style="color: #2196F3; margin: 15px 0 10px 0;">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1 style="color: #FF9800; margin: 20px 0 15px 0;">\1</h1>', html, flags=re.MULTILINE)

        # 处理列表项 - text -> <li>text</li>
        html = re.sub(r'^- (.*?)$', r'<li style="margin: 2px 0;">\1</li>', html, flags=re.MULTILINE)

        # 处理✅表情符号和特殊字符
        html = html.replace('✅', '<span style="color: #4CAF50;">✅</span>')
        html = html.replace('🔧', '<span style="color: #FF9800;">🔧</span>')
        html = html.replace('🎯', '<span style="color: #2196F3;">🎯</span>')

        # 包装在div中并设置基础样式
        html = f'<div style="line-height: 1.5; color: white;">{html}</div>'

        return html

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20,20,20,20)

        # Description text area (from self.prompt) - Support multiline, selectable and copyable with markdown support
        self.description_text = QTextEdit()
        self.description_text.setHtml(self._convert_markdown_to_html(self.prompt))  # 使用HTML来渲染markdown
        self.description_text.setReadOnly(True)  # 设置为只读，但可以选择和复制
        self.description_text.setMaximumHeight(400)  # 设置最大高度，防止按钮溢出屏幕
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
            "  padding: 15px;"
            "  margin: 0 0 15px 0;"
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
            options_layout.setContentsMargins(0,0,0,0)

            for option in self.predefined_options:
                checkbox = QCheckBox(option)
                # Increase font size for checkboxes
                font = checkbox.font()
                font.setPointSize(font.pointSize() + 3)
                checkbox.setFont(font)
                self.option_checkboxes.append(checkbox)
                options_layout.addWidget(checkbox)

            layout.addWidget(options_frame)



        # Free-form text feedback
        self.feedback_text = FeedbackTextEdit()
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

        # Add image information with Base64 data if any
        if image_data:
            image_info_parts = ["包含的图片:"]
            for i, img_info in enumerate(image_data, 1):
                image_info_parts.append(f"\n图片 {i}: Base64数据: data:image/png;base64,{img_info['base64']}")
                image_info_parts.append("")  # 空行分隔
            final_feedback_parts.append("\n".join(image_info_parts))

        # Join with a newline if both parts exist
        final_feedback = "\n\n".join(final_feedback_parts)

        self.feedback_result = FeedbackResult(
            interactive_feedback=final_feedback,
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

def feedback_ui(prompt: str, predefined_options: Optional[List[str]] = None, output_file: Optional[str] = None) -> Optional[FeedbackResult]:
    app = QApplication.instance() or QApplication()
    app.setPalette(get_dark_mode_palette(app))
    app.setStyle("Fusion")
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
