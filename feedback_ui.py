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

                            # 生成一个唯一URL用于在界面中显示
                            timestamp_ms = QDateTime.currentMSecsSinceEpoch()
                            image_url = QUrl(f"image://pasted_image_{timestamp_ms}")

                            try:
                                # 处理视网膜屏幕：根据设备像素比调整图像
                                if self.device_pixel_ratio > 1.0:
                                    # 对于视网膜屏幕，创建更高分辨率的图像
                                    high_res_image = image

                                    # 获取原始尺寸
                                    original_width = high_res_image.width()
                                    original_height = high_res_image.height()

                                    # 计算逻辑尺寸（显示尺寸）
                                    logical_width = original_width / self.device_pixel_ratio
                                    logical_height = original_height / self.device_pixel_ratio

                                    # 将图片添加到文档资源中以便显示
                                    self.document().addResource(QTextDocument.ImageResource, image_url, high_res_image)

                                    # 在光标位置插入图片，但设置逻辑尺寸
                                    cursor = self.textCursor()
                                    image_format = QTextImageFormat()
                                    image_format.setName(image_url.toString())
                                    image_format.setWidth(logical_width)
                                    image_format.setHeight(logical_height)
                                    cursor.insertImage(image_format)
                                else:
                                    # 非视网膜屏幕，正常处理
                                    self.document().addResource(QTextDocument.ImageResource, image_url, image)

                                    # 在光标位置插入图片
                                    cursor = self.textCursor()
                                    image_format = QTextImageFormat()
                                    image_format.setName(image_url.toString())
                                    cursor.insertImage(image_format)
                            except Exception as e:
                                print(f"处理图片显示时出错: {e}")
                                cursor = self.textCursor()
                                cursor.insertText(f"[图片显示失败: {str(e)}]")
                        else:
                            # 如果转换失败，插入错误信息
                            cursor = self.textCursor()
                            cursor.insertText("[图片处理失败: 转换为Base64失败]")
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

    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """使用markdown库将markdown转换为HTML"""
        try:
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

            # 应用自定义样式
            styled_html = f"""
            <div style="
                line-height: 1.2;
                color: #ccc;
                font-family: system-ui, -apple-system, sans-serif;
            ">
                {html}
            </div>
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
            </style>
            """

            return styled_html

        except ImportError:
            # Fallback if markdown library is not installed
            # Log that markdown library is not found and basic conversion is used.
            print("Markdown library not found. Using basic HTML escaping for description.")
            return f'<div style="color: white; line-height: 1.5;">{markdown_text.replace("<", "&lt;").replace(">", "&gt;")}</div>'
        except Exception as e:
            # Fallback for any other error during markdown conversion
            print(f"Error during markdown conversion: {e}. Using basic HTML escaping.")
            return f'<div style="color: white; line-height: 1.5;">{markdown_text.replace("<", "&lt;").replace(">", "&gt;")}</div>'

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20,20,20,20)

        # Description text area (from self.prompt) - Support multiline, selectable and copyable with markdown support
        self.description_text = QTextEdit()
        self.description_text.setHtml(self._convert_markdown_to_html(self.prompt))  # 使用HTML来渲染markdown
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
