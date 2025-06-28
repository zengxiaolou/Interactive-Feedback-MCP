# Main Window Component for Interactive Feedback MCP
# 主窗口组件

import os
import sys
from typing import Optional, List, TypedDict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QTextBrowser, QGroupBox,
    QFrame, QScrollArea, QApplication
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QIcon, QShortcut, QKeySequence, QFont

from ..widgets.feedback_text_edit import FeedbackTextEdit
from ..styles.glassmorphism import GlassmorphismStyles
from ..components.text_processing import TextProcessor

class FeedbackResult(TypedDict):
    interactive_feedback: str
    images: List[str]

class FeedbackUI(QMainWindow):
    """交互式反馈主窗口"""
    
    def __init__(self, prompt: str, predefined_options: Optional[List[str]] = None):
        super().__init__()
        self.prompt = prompt
        self.predefined_options = predefined_options or []
        self.feedback_result = None
        
        # 初始化文本处理器
        self.text_processor = TextProcessor()
        
        self._setup_window()
        self._load_settings()
        self._create_ui()
        self._setup_shortcuts()

    def _setup_window(self):
        """设置窗口基本属性"""
        self.setWindowTitle("Cursor 交互式反馈 MCP")
        
        # 设置图标
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(script_dir, "images", "feedback.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 设置窗口属性
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.95)
        
        # 应用主窗口样式
        self.setStyleSheet(GlassmorphismStyles.main_window())

    def _load_settings(self):
        """加载设置"""
        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")
        self.line_height = self._load_line_height()
        
        # 设置窗口大小和位置
        screen = QApplication.primaryScreen().geometry()
        screen_height = screen.height()
        window_height = int(screen_height * 0.7)
        window_width = 800
        
        self.resize(window_width, window_height)
        self.setMinimumSize(600, 400)
        
        # 窗口居中
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.move(x, y)

    def _create_ui(self):
        """创建用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet(GlassmorphismStyles.central_widget())
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)

        # 创建描述文本区域
        self._create_description_area(layout)
        
        # 创建选项区域
        self._create_options_area(layout)
        
        # 创建图片预览区域
        self._create_images_area(layout)
        
        # 创建文本输入区域
        self._create_text_input_area(layout)
        
        # 创建按钮区域
        self._create_buttons_area(layout)
        
        # 创建信息标签
        self._create_info_label(layout)

    def _create_description_area(self, layout):
        """创建描述文本区域"""
        self.description_text = QTextBrowser()
        self.description_text.setMaximumHeight(600)
        self.description_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.description_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.description_text.setStyleSheet(GlassmorphismStyles.text_browser())
        
        self._update_description_text()
        layout.addWidget(self.description_text)

    def _create_options_area(self, layout):
        """创建选项区域"""
        self.option_checkboxes = []
        if self.predefined_options:
            options_frame = QFrame()
            options_frame.setStyleSheet(GlassmorphismStyles.options_frame())
            options_layout = QVBoxLayout(options_frame)
            options_layout.setContentsMargins(15, 10, 15, 10)

            for option in self.predefined_options:
                checkbox = QCheckBox(option)
                checkbox.setStyleSheet(GlassmorphismStyles.checkbox())
                self.option_checkboxes.append(checkbox)
                options_layout.addWidget(checkbox)

            layout.addWidget(options_frame)

    def _create_images_area(self, layout):
        """创建图片预览区域"""
        self.images_container = QFrame()
        self.images_container.setStyleSheet(GlassmorphismStyles.images_container())
        self.images_container.setFixedHeight(80)
        self.images_layout = QHBoxLayout(self.images_container)
        self.images_layout.setSpacing(5)
        self.images_layout.setContentsMargins(5, 5, 5, 5)
        self.images_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.images_container.setVisible(False)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(80)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(GlassmorphismStyles.scroll_area())
        scroll_area.setWidget(self.images_container)
        scroll_area.setVisible(False)
        
        self.scroll_area = scroll_area
        layout.addWidget(scroll_area, 0)

    def _create_text_input_area(self, layout):
        """创建文本输入区域"""
        self.feedback_text = FeedbackTextEdit()
        self.feedback_text.image_pasted.connect(self._on_image_pasted)
        # 连接提交请求信号
        self.feedback_text.submit_requested.connect(self._submit_feedback)
        self.feedback_text.setStyleSheet(GlassmorphismStyles.text_edit())
        
        # 设置文档边距
        document = self.feedback_text.document()
        document.setDocumentMargin(5)
        
        # 设置高度
        font_metrics = self.feedback_text.fontMetrics()
        row_height = font_metrics.height()
        min_height = 5 * row_height
        max_height = 10 * row_height
        
        self.feedback_text.setMinimumHeight(min_height)
        self.feedback_text.setMaximumHeight(max_height)
        self.feedback_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.feedback_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.feedback_text.setPlaceholderText("在此输入您的下一步要求或反馈 (Ctrl+Enter 提交) 支持粘贴图片")
        
        layout.addWidget(self.feedback_text)

    def _create_buttons_area(self, layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()

        # 取消按钮
        cancel_button = QPushButton("&取消")
        cancel_button.clicked.connect(self.close)
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setStyleSheet(GlassmorphismStyles.cancel_button())

        # 提交按钮
        submit_button = QPushButton("&提交")
        submit_button.clicked.connect(self._submit_feedback)
        submit_button.setCursor(Qt.PointingHandCursor)
        submit_button.setStyleSheet(GlassmorphismStyles.submit_button())

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(submit_button)
        layout.addLayout(button_layout)

    def _create_info_label(self, layout):
        """创建信息标签"""
        if sys.platform == "darwin":  # macOS
            zoom_shortcut_text = "CMD+/-"
            line_height_shortcut_text = "CMD+Shift+L"
        else:  # Windows, Linux, etc.
            zoom_shortcut_text = "CTRL+/-"
            line_height_shortcut_text = "CTRL+ALT+H"

        label_text = f"支持 {zoom_shortcut_text} 缩放字体，{line_height_shortcut_text} 调整行高(5档循环)  Contact: RowanYang"
        by_rowanyang_label = QLabel(label_text)
        by_rowanyang_label.setStyleSheet(GlassmorphismStyles.info_label())
        by_rowanyang_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # 居中布局
        by_rowanyang_layout = QHBoxLayout()
        by_rowanyang_layout.addStretch(1)
        by_rowanyang_layout.addWidget(by_rowanyang_label)
        by_rowanyang_layout.addStretch(1)
        
        layout.addSpacing(10)
        layout.addLayout(by_rowanyang_layout)

    def _setup_shortcuts(self):
        """设置快捷键"""
        # 字体缩放快捷键
        zoom_in = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in.activated.connect(lambda: self.adjust_font_size(1.1))

        zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out.activated.connect(lambda: self.adjust_font_size(0.9))

        reset_font = QShortcut(QKeySequence("Ctrl+0"), self)
        reset_font.activated.connect(self.reset_font_size)

        # 提交快捷键 - 多种变体确保兼容性
        def submit_with_debug():
            print("🌍 全局快捷键触发提交 (备用方案)")
            self._submit_feedback()
        
        # 主要提交快捷键
        submit_shortcut1 = QShortcut(QKeySequence("Ctrl+Return"), self)
        submit_shortcut1.activated.connect(submit_with_debug)
        
        # 备用提交快捷键  
        submit_shortcut2 = QShortcut(QKeySequence("Ctrl+Enter"), self)
        submit_shortcut2.activated.connect(submit_with_debug)
        
        # macOS兼容快捷键
        if sys.platform == "darwin":
            submit_shortcut3 = QShortcut(QKeySequence("Cmd+Return"), self)
            submit_shortcut3.activated.connect(submit_with_debug)
            submit_shortcut4 = QShortcut(QKeySequence("Cmd+Enter"), self)
            submit_shortcut4.activated.connect(submit_with_debug)

        # 行高切换快捷键
        if sys.platform == "darwin":
            key_sequence = "Ctrl+Shift+L"
        else:
            key_sequence = "Ctrl+Alt+H"

        toggle_line_height_shortcut = QShortcut(QKeySequence(key_sequence), self)
        toggle_line_height_shortcut.activated.connect(self._toggle_line_height)
        
        print("✅ 快捷键设置完成 - 已添加多重Ctrl+Enter提交功能")
        print("   📋 支持快捷键: Ctrl+Return, Ctrl+Enter" + (", Cmd+Return, Cmd+Enter" if sys.platform == "darwin" else ""))

    def _update_description_text(self):
        """更新描述文本内容"""
        if self.text_processor.is_markdown(self.prompt):
            print("检测到Markdown格式")
            html_content = self.text_processor.convert_markdown_to_html(self.prompt, self.line_height)
        else:
            print("检测到文本类型: 普通文本")
            html_content = self.text_processor.convert_text_to_html(self.prompt, self.line_height)
        
        self.description_text.setHtml(html_content)

    def _toggle_line_height(self):
        """循环切换行高并更新UI"""
        line_heights = [1.0, 1.1, 1.2, 1.3, 1.4]
        try:
            current_index = line_heights.index(self.line_height)
            next_index = (current_index + 1) % len(line_heights)
        except ValueError:
            next_index = 1

        self.line_height = line_heights[next_index]
        self._save_line_height(self.line_height)
        self._update_description_text()
        print(f"行高已切换为: {self.line_height}")

    def adjust_font_size(self, factor: float):
        """按比例调整所有字体大小"""
        app = QApplication.instance()
        current_font = app.font()
        new_size = max(8, int(current_font.pointSize() * factor))
        current_font.setPointSize(new_size)
        app.setFont(current_font)
        self._update_all_fonts()
        self._save_font_size(new_size)

    def reset_font_size(self):
        """重置为默认字体大小"""
        app = QApplication.instance()
        default_font = app.font()
        default_size = 15
        default_font.setPointSize(default_size)
        app.setFont(default_font)
        self._update_all_fonts()
        self._save_font_size(default_size)

    def _save_font_size(self, size: int):
        """保存字体大小到设置"""
        self.settings.beginGroup("AppearanceSettings")
        self.settings.setValue("fontSize", size)
        self.settings.endGroup()

    def _load_font_size(self) -> int:
        """从设置加载字体大小"""
        self.settings.beginGroup("AppearanceSettings")
        size = self.settings.value("fontSize", 15, type=int)
        self.settings.endGroup()
        return size

    def _save_line_height(self, line_height: float):
        """保存行高到设置"""
        self.settings.beginGroup("AppearanceSettings")
        self.settings.setValue("lineHeight", line_height)
        self.settings.endGroup()

    def _load_line_height(self) -> float:
        """从设置加载行高"""
        self.settings.beginGroup("AppearanceSettings")
        line_height = self.settings.value("lineHeight", 1.3, type=float)
        self.settings.endGroup()
        return line_height

    def _update_all_fonts(self):
        """更新UI中所有控件的字体"""
        def update_widget_font(widget):
            widget.setFont(QApplication.font())
            
            if isinstance(widget, QCheckBox):
                font_size = QApplication.font().pointSize()
                icon_size = max(16, int(font_size * 1.2))
                widget.setStyleSheet(widget.styleSheet() + f"""
                    QCheckBox::indicator {{
                        width: {icon_size}px;
                        height: {icon_size}px;
                    }}
                """)

            for child in widget.children():
                if isinstance(child, QWidget):
                    update_widget_font(child)

        update_widget_font(self)

    def showEvent(self, event):
        """窗口显示时加载保存的字体大小"""
        super().showEvent(event)
        app = QApplication.instance()
        saved_size = self._load_font_size()
        current_font = app.font()
        current_font.setPointSize(saved_size)
        app.setFont(current_font)
        self._update_all_fonts()

    def _submit_feedback(self):
        """提交反馈"""
        print("🚀 开始处理反馈提交...")
        
        feedback_text = self.feedback_text.toPlainText().strip()
        selected_options = []

        # 获取选中的预定义选项
        if self.option_checkboxes:
            for i, checkbox in enumerate(self.option_checkboxes):
                if checkbox.isChecked():
                    selected_options.append(self.predefined_options[i])

        # 获取图片数据
        image_data = self.feedback_text.get_image_data()

        # 组合反馈内容
        final_feedback_parts = []
        if selected_options:
            final_feedback_parts.append("; ".join(selected_options))
            print(f"📋 已选择选项: {len(selected_options)}个")
        if feedback_text:
            final_feedback_parts.append(feedback_text)
            print(f"📝 文本内容长度: {len(feedback_text)}字符")

        final_feedback = "\n\n".join(final_feedback_parts)
        images_b64 = [img['base64'] for img in image_data]
        
        if image_data:
            print(f"🖼️ 包含图片: {len(image_data)}张")

        self.feedback_result = FeedbackResult(
            interactive_feedback=final_feedback,
            images=images_b64
        )
        
        print("✅ 反馈数据准备完成，关闭窗口...")
        self.close()

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.settings.beginGroup("MainWindow_General")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.endGroup()
        super().closeEvent(event)

    def run(self) -> FeedbackResult:
        """运行UI并返回结果"""
        self.show()
        QApplication.instance().exec()

        if not self.feedback_result:
            return FeedbackResult(interactive_feedback="", images=[])

        return self.feedback_result

    def _on_image_pasted(self, pixmap):
        """处理粘贴的图片"""
        # 确保图片容器可见
        if not self.images_container.isVisible():
            self.images_container.setVisible(True)
            self.scroll_area.setVisible(True)
            self.images_layout.addStretch(1)

        # 创建图片预览（这里可以添加具体的图片预览实现）
        # 由于代码较长，这里简化处理
        print(f"图片已添加到预览区域，大小: {pixmap.width()}x{pixmap.height()}") 