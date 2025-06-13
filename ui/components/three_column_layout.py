# Three Column Layout Component for Interactive Feedback MCP
# 三栏式布局组件

import os
import sys
import subprocess
from typing import Optional, List, TypedDict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QTextBrowser, QFrame,
    QScrollArea, QApplication, QTextEdit, QSplitter
)
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QIcon, QShortcut, QKeySequence, QFont

from ..widgets.feedback_text_edit import FeedbackTextEdit
from ..styles.glassmorphism import GlassmorphismStyles
from ..styles.modern_glassmorphism import ModernGlassmorphismTheme
from ..components.text_processing import TextProcessor

class FeedbackResult(TypedDict):
    interactive_feedback: str
    images: List[str]

class ThreeColumnFeedbackUI(QMainWindow):
    """三栏式交互反馈主窗口"""
    
    def __init__(self, prompt: str, predefined_options: Optional[List[str]] = None):
        super().__init__()
        self.prompt = prompt
        self.predefined_options = predefined_options or []
        self.feedback_result = None
        
        # 初始化文本处理器
        self.text_processor = TextProcessor()
        
        # Git和项目信息
        self.project_info = self._get_project_info()
        self.git_info = self._get_git_info()
        
        self._setup_window()
        self._load_settings()
        self._create_ui()
        self._setup_shortcuts()

    def _setup_window(self):
        """设置窗口基本属性"""
        self.setWindowTitle("Interactive Feedback MCP | admin - Enhanced Context")
        
        # 设置图标
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(script_dir, "images", "feedback.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 设置窗口属性
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.95)
        
        # 应用现代化毛玻璃主窗口样式
        self.setStyleSheet(ModernGlassmorphismTheme.get_main_window_style())

    def _load_settings(self):
        """加载设置"""
        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")
        self.line_height = self._load_line_height()
        
        # 设置窗口大小和位置 - 参考enhanced_feedback_ui的尺寸
        screen = QApplication.primaryScreen().geometry()
        window_height = min(1200, int(screen.height() * 0.85))  # 最大1200高度
        window_width = min(1600, int(screen.width() * 0.85))   # 最大1600宽度
        
        self.resize(window_width, window_height)
        self.setMinimumSize(1200, 800)  # 参考UI的最小尺寸
        
        # 窗口居中
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.move(x, y)

    def _create_ui(self):
        """创建三栏式用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # 中央widget使用透明背景，由主窗口提供背景
        
        # 主布局 - 参考enhanced_feedback_ui的水平布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)  # 参考UI的边距
        main_layout.setSpacing(5)  # 参考UI的间距
        
        # 创建三个栏目
        left_panel = self._create_left_panel()    # 消息内容
        center_panel = self._create_center_panel() # 智能推荐选项
        right_panel = self._create_right_panel()   # 项目信息
        
        # 按照参考UI的比例：左侧占2份，中间占2份，右侧占1份
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(center_panel, 2)
        main_layout.addWidget(right_panel, 1)

    def _create_left_panel(self):
        """创建左侧消息内容面板"""
        panel = QFrame()
        panel.setStyleSheet(ModernGlassmorphismTheme.get_panel_style())
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题 - 使用现代化样式
        title = QLabel("💬 消息内容")
        title.setStyleSheet(ModernGlassmorphismTheme.get_title_style('#4CAF50'))
        layout.addWidget(title)
        
        # 消息文本区域 - 使用现代化样式
        self.description_text = QTextBrowser()
        self.description_text.setStyleSheet(ModernGlassmorphismTheme.get_text_browser_style())
        self.description_text.setMaximumHeight(400)
        self._update_description_text()
        layout.addWidget(self.description_text)
        
        # 布局改进建议
        layout_label = QLabel("🎨 布局行为改进")
        layout_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px; margin-top: 10px;")
        layout.addWidget(layout_label)
        
        layout_improvements = QTextBrowser()
        layout_improvements.setStyleSheet(GlassmorphismStyles.text_browser())
        layout_improvements.setMaximumHeight(200)
        layout_improvements.setHtml(self._get_layout_improvements())
        layout.addWidget(layout_improvements)
        
        # 项目上下文
        context_label = QLabel("📁 项目上下文 (已更新)")
        context_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px; margin-top: 10px;")
        layout.addWidget(context_label)
        
        context_text = QTextBrowser()
        context_text.setStyleSheet(GlassmorphismStyles.text_browser())
        context_text.setMaximumHeight(150)
        context_text.setHtml(self._get_project_context())
        layout.addWidget(context_text)
        
        layout.addStretch()
        return panel

    def _create_center_panel(self):
        """创建中间智能推荐选项面板"""
        panel = QFrame()
        panel.setStyleSheet(ModernGlassmorphismTheme.get_panel_style())
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题 - 使用现代化样式
        title = QLabel("🎯 选择操作")
        title.setStyleSheet(ModernGlassmorphismTheme.get_title_style('#FF9800'))
        layout.addWidget(title)
        
        # 创建选项列表
        self.option_checkboxes = []
        if self.predefined_options:
            for i, option in enumerate(self.predefined_options, 1):
                checkbox_frame = QFrame()
                checkbox_frame.setStyleSheet("""
                    QFrame {
                        background: rgba(255, 255, 255, 0.03);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 6px;
                        padding: 8px;
                        margin: 2px 0px;
                    }
                    QFrame:hover {
                        background: rgba(255, 255, 255, 0.06);
                        border: 1px solid rgba(33, 150, 243, 0.3);
                    }
                """)
                
                checkbox_layout = QHBoxLayout(checkbox_frame)
                checkbox_layout.setContentsMargins(8, 5, 8, 5)
                
                # 序号标签
                number_label = QLabel(f"{i}.")
                number_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 12px;")
                number_label.setFixedWidth(20)
                
                # 复选框 - 使用现代化样式
                checkbox = QCheckBox(option)
                checkbox.setStyleSheet(ModernGlassmorphismTheme.get_checkbox_style())
                
                checkbox_layout.addWidget(number_label)
                checkbox_layout.addWidget(checkbox)
                
                self.option_checkboxes.append(checkbox)
                layout.addWidget(checkbox_frame)
        
        # 添加一些默认的智能推荐选项
        default_options = [
            "🔄 结束本轮对话",
            "💬 结束本轮对话"
        ]
        
        for i, option in enumerate(default_options, len(self.predefined_options) + 1):
            checkbox_frame = QFrame()
            checkbox_frame.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 6px;
                    padding: 8px;
                    margin: 2px 0px;
                }
            """)
            
            checkbox_layout = QHBoxLayout(checkbox_frame)
            checkbox_layout.setContentsMargins(8, 5, 8, 5)
            
            number_label = QLabel(f"{i}.")
            number_label.setStyleSheet("color: #666; font-size: 12px;")
            number_label.setFixedWidth(20)
            
            checkbox = QCheckBox(option)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #999;
                    spacing: 8px;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 3px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    background: rgba(255, 255, 255, 0.05);
                }
            """)
            
            checkbox_layout.addWidget(number_label)
            checkbox_layout.addWidget(checkbox)
            layout.addWidget(checkbox_frame)
        
        # 提示文本
        hint_label = QLabel("💡 提示：您可以选择多个选项进行组合操作")
        hint_label.setStyleSheet("color: #666; font-size: 11px; margin-top: 10px;")
        layout.addWidget(hint_label)
        
        layout.addStretch()
        return panel

    def _create_right_panel(self):
        """创建右侧项目信息面板"""
        panel = QFrame()
        panel.setStyleSheet(ModernGlassmorphismTheme.get_panel_style())
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题 - 使用现代化样式
        title = QLabel("🏗️ 项目上下文")
        title.setStyleSheet(ModernGlassmorphismTheme.get_title_style('#2196F3'))
        layout.addWidget(title)
        
        # 项目基础信息
        self._add_project_info_section(layout)
        
        # Git状态信息
        self._add_git_info_section(layout)
        
        # 项目活动信息
        self._add_project_activity_section(layout)
        
        # 自定义输入框
        self._add_custom_input_section(layout)
        
        return panel

    def _add_project_info_section(self, layout):
        """添加项目基础信息部分"""
        info_label = QLabel("🏗️ 项目基础")
        info_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 13px;")
        layout.addWidget(info_label)
        
        info_frame = QFrame()
        info_frame.setStyleSheet(ModernGlassmorphismTheme.get_info_section_style())
        
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(5)
        
        # 项目信息
        project_info = [
            ("名称:", "admin"),
            ("类型:", "unknown"),
            ("文件数:", "93"),
            ("大小:", "2.64 MB"),
            ("路径:", "/Documents/work/prototype/admin")
        ]
        
        for label, value in project_info:
            row = QHBoxLayout()
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #ccc; font-size: 11px;")
            label_widget.setFixedWidth(50)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #fff; font-size: 11px;")
            
            row.addWidget(label_widget)
            row.addWidget(value_widget)
            row.addStretch()
            info_layout.addLayout(row)
        
        layout.addWidget(info_frame)

    def _add_git_info_section(self, layout):
        """添加Git状态信息部分"""
        git_label = QLabel("🌿 Git状态")
        git_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px; margin-top: 10px;")
        layout.addWidget(git_label)
        
        git_frame = QFrame()
        git_frame.setStyleSheet(ModernGlassmorphismTheme.get_info_section_style())
        
        git_layout = QVBoxLayout(git_frame)
        git_layout.setSpacing(5)
        
        # Git信息
        git_info = [
            ("分支:", "main"),
            ("修改文件:", "1个"),
            ("未跟踪:", "3个"),
            ("最后提交:", "重要更新: 集成AI对话框架\n完善一些..."),
            ("作者:", "zengxiaoyu"),
            ("时间:", "17 hours ago")
        ]
        
        for label, value in git_info:
            row_layout = QVBoxLayout() if label == "最后提交:" else QHBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #ccc; font-size: 11px;")
            if isinstance(row_layout, QHBoxLayout):
                label_widget.setFixedWidth(50)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #fff; font-size: 11px;")
            if label == "最后提交:":
                value_widget.setWordWrap(True)
                value_widget.setMaximumHeight(40)
            
            if isinstance(row_layout, QHBoxLayout):
                row_layout.addWidget(label_widget)
                row_layout.addWidget(value_widget)
                row_layout.addStretch()
                git_layout.addLayout(row_layout)
            else:
                git_layout.addWidget(label_widget)
                git_layout.addWidget(value_widget)
        
        layout.addWidget(git_frame)

    def _add_project_activity_section(self, layout):
        """添加项目活动信息部分"""
        activity_label = QLabel("📊 项目活动")
        activity_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 13px; margin-top: 10px;")
        layout.addWidget(activity_label)
        
        activity_frame = QFrame()
        activity_frame.setStyleSheet(ModernGlassmorphismTheme.get_info_section_style())
        
        activity_layout = QVBoxLayout(activity_frame)
        activity_layout.setSpacing(5)
        
        # 活动信息
        activity_info = [
            ("最近修改:", "5个文件 (24小时内)"),
            ("大文件:", "2个 (>100KB)"),
            ("语言:", "中"),
            ("文档类型:", "html(75), md(7), misc(2)"),
            ("重要文件:", "quick-menu.html, md...")
        ]
        
        for label, value in activity_info:
            row = QHBoxLayout()
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #ccc; font-size: 11px;")
            label_widget.setFixedWidth(60)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #fff; font-size: 11px;")
            value_widget.setWordWrap(True)
            
            row.addWidget(label_widget)
            row.addWidget(value_widget)
            activity_layout.addLayout(row)
        
        layout.addWidget(activity_frame)

    def _add_custom_input_section(self, layout):
        """添加自定义输入部分"""
        input_label = QLabel("✏️ 自定义输入")
        input_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px; margin-top: 15px;")
        layout.addWidget(input_label)
        
        # 自定义文本输入
        self.custom_input = FeedbackTextEdit()
        self.custom_input.setStyleSheet(GlassmorphismStyles.text_edit())
        self.custom_input.setMaximumHeight(100)
        self.custom_input.setPlaceholderText("输入自定义文本或反馈，支持粘贴图片/链接 | Shift+Enter换行")
        layout.addWidget(self.custom_input)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        submit_btn = QPushButton("✅ 提交 (ENTER)")
        submit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(76, 175, 80, 0.8),
                    stop:1 rgba(56, 142, 60, 0.8));
                color: white;
                border: 1px solid rgba(76, 175, 80, 0.6);
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(76, 175, 80, 0.9),
                    stop:1 rgba(56, 142, 60, 0.9));
            }
        """)
        submit_btn.clicked.connect(self._submit_feedback)
        
        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(244, 67, 54, 0.8),
                    stop:1 rgba(198, 40, 40, 0.8));
                color: white;
                border: 1px solid rgba(244, 67, 54, 0.6);
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(244, 67, 54, 0.9),
                    stop:1 rgba(198, 40, 40, 0.9));
            }
        """)
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(submit_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def _get_layout_improvements(self):
        """获取布局改进建议"""
        return """
        <div style="color: #ccc; font-size: 12px; line-height: 1.4;">
        <p><strong style="color: #4CAF50;">✅ CSS Grid布局优化:</strong></p>
        <ul style="margin: 5px 0; padding-left: 15px;">
        <li>网格布局定义: repeat(auto-fit, minmax(100px, 1fr)) → repeat(auto-fill, 100px)</li>
        <li>新增网格对齐: justify-content: start</li>
        <li>最小网格定义尺寸: width: 100px</li>
        <li>文字居中对齐: text-align: center</li>
        </ul>
        
        <p><strong style="color: #4CAF50;">🎨 布局行为改进:</strong></p>
        <ul style="margin: 5px 0; padding-left: 15px;">
        <li>按钮样式优化和响应性提升</li>
        <li>固定100px宽度，排列整齐</li>
        <li>保持12x间距，美观排版</li>
        <li>自动换行时的间距对齐</li>
        </ul>
        </div>
        """

    def _get_project_context(self):
        """获取项目上下文信息"""
        return """
        <div style="color: #ccc; font-size: 12px; line-height: 1.4;">
        <p><strong style="color: #4CAF50;">📁 项目名称:</strong> admin (管理后台项目)</p>
        <p><strong style="color: #4CAF50;">🔧 配置状态:</strong> 无需安装依赖或动态配置</p>
        <p><strong style="color: #4CAF50;">📍 在用户目录:</strong> 创建或复制相关网格布局对齐</p>
        <p><strong style="color: #4CAF50;">🎯 按钮尺寸:</strong> 100px × 自适应高度</p>
        <p><strong style="color: #4CAF50;">🎨 解决方案:</strong> 严格定义网格布局和网格布局</p>
        </div>
        """

    def _get_project_info(self):
        """获取项目基础信息"""
        try:
            cwd = os.getcwd()
            return {
                "name": os.path.basename(cwd),
                "path": cwd,
                "files": len([f for f in os.listdir(cwd) if os.path.isfile(f)]) if os.path.exists(cwd) else 0
            }
        except:
            return {"name": "unknown", "path": "unknown", "files": 0}

    def _get_git_info(self):
        """获取Git状态信息"""
        try:
            # 获取当前分支
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True, timeout=5)
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # 获取状态
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, text=True, timeout=5)
            modified_files = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
            
            # 获取最后提交
            log_result = subprocess.run(['git', 'log', '-1', '--pretty=format:%s'], 
                                      capture_output=True, text=True, timeout=5)
            last_commit = log_result.stdout.strip() if log_result.returncode == 0 else "No commits"
            
            return {
                "branch": branch,
                "modified_files": modified_files,
                "last_commit": last_commit
            }
        except:
            return {"branch": "unknown", "modified_files": 0, "last_commit": "unknown"}

    def _setup_shortcuts(self):
        """设置快捷键"""
        # 字体缩放快捷键
        zoom_in = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in.activated.connect(lambda: self.adjust_font_size(1.1))

        zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out.activated.connect(lambda: self.adjust_font_size(0.9))

        reset_font = QShortcut(QKeySequence("Ctrl+0"), self)
        reset_font.activated.connect(self.reset_font_size)

    def _update_description_text(self):
        """更新描述文本内容"""
        if self.text_processor.is_markdown(self.prompt):
            html_content = self.text_processor.convert_markdown_to_html(self.prompt, self.line_height)
        else:
            html_content = self.text_processor.convert_text_to_html(self.prompt, self.line_height)
        
        self.description_text.setHtml(html_content)

    def adjust_font_size(self, factor: float):
        """调整字体大小"""
        app = QApplication.instance()
        current_font = app.font()
        new_size = max(8, int(current_font.pointSize() * factor))
        current_font.setPointSize(new_size)
        app.setFont(current_font)

    def reset_font_size(self):
        """重置字体大小"""
        app = QApplication.instance()
        default_font = app.font()
        default_font.setPointSize(15)
        app.setFont(default_font)

    def _load_line_height(self) -> float:
        """加载行高设置"""
        self.settings.beginGroup("AppearanceSettings")
        line_height = self.settings.value("lineHeight", 1.3, type=float)
        self.settings.endGroup()
        return line_height

    def _submit_feedback(self):
        """提交反馈"""
        feedback_text = self.custom_input.toPlainText().strip()
        selected_options = []

        # 获取选中的预定义选项
        if self.option_checkboxes:
            for i, checkbox in enumerate(self.option_checkboxes):
                if checkbox.isChecked():
                    selected_options.append(self.predefined_options[i])

        # 获取图片数据
        image_data = self.custom_input.get_image_data()
        images = [img['base64'] for img in image_data] if image_data else []

        # 组合反馈内容
        combined_feedback = []
        if selected_options:
            combined_feedback.append("选择的选项:")
            for option in selected_options:
                combined_feedback.append(f"- {option}")
        
        if feedback_text:
            if combined_feedback:
                combined_feedback.append("\n自定义反馈:")
            combined_feedback.append(feedback_text)

        final_feedback = "\n".join(combined_feedback) if combined_feedback else "无反馈内容"

        self.feedback_result = FeedbackResult(
            interactive_feedback=final_feedback,
            images=images
        )
        
        self.close()

    def closeEvent(self, event):
        """关闭事件处理"""
        event.accept()

    def run(self) -> FeedbackResult:
        """运行UI并返回结果"""
        self.show()
        return self.feedback_result 