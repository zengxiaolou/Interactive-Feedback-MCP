# Custom Text Edit Widget for Interactive Feedback MCP
# 自定义文本编辑器组件

import base64
import uuid
from datetime import datetime
from typing import List, Dict, Any

from PySide6.QtWidgets import QTextEdit, QApplication
from PySide6.QtCore import Qt, Signal, QBuffer, QIODevice
from PySide6.QtGui import QKeyEvent, QPixmap

class FeedbackTextEdit(QTextEdit):
    """支持图片粘贴的自定义文本编辑器"""
    
    # 图片处理常量
    DEFAULT_MAX_IMAGE_WIDTH = 1624
    DEFAULT_MAX_IMAGE_HEIGHT = 1624
    DEFAULT_IMAGE_FORMAT = "PNG"

    # 定义类级别的信号
    image_pasted = Signal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_data: List[Dict[str, Any]] = []

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件，支持Ctrl+Enter提交"""
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            # 触发提交操作
            parent_window = self.window()
            if hasattr(parent_window, '_submit_feedback'):
                parent_window._submit_feedback()
            return
        super().keyPressEvent(event)

    def _convert_image_to_base64(self, image):
        """将图片转换为Base64编码"""
        try:
            # 如果是QPixmap，直接使用
            if isinstance(image, QPixmap):
                pixmap = image
            else:
                # 尝试从其他格式转换
                pixmap = QPixmap(image)

            if pixmap.isNull():
                print("无法加载图片")
                return None

            # 调整图片大小
            if (pixmap.width() > self.DEFAULT_MAX_IMAGE_WIDTH or 
                pixmap.height() > self.DEFAULT_MAX_IMAGE_HEIGHT):
                pixmap = pixmap.scaled(
                    self.DEFAULT_MAX_IMAGE_WIDTH,
                    self.DEFAULT_MAX_IMAGE_HEIGHT,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

            # 转换为Base64
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, self.DEFAULT_IMAGE_FORMAT)
            image_data = buffer.data()
            buffer.close()

            base64_data = base64.b64encode(image_data).decode('utf-8')
            return base64_data

        except Exception as e:
            print(f"图片转换失败: {e}")
            return None

    def insertFromMimeData(self, source_data):
        """处理粘贴操作，支持图片粘贴"""
        if source_data.hasImage():
            # 处理图片粘贴
            image = source_data.imageData()
            if image:
                try:
                    # 转换为QPixmap
                    pixmap = QPixmap.fromImage(image)
                    if not pixmap.isNull():
                        # 转换为Base64并存储
                        base64_data = self._convert_image_to_base64(pixmap)
                        if base64_data:
                            # 生成唯一ID和时间戳
                            image_id = str(uuid.uuid4())
                            timestamp = datetime.now().isoformat()

                            # 存储图片数据
                            self.image_data.append({
                                'id': image_id,
                                'base64': base64_data,
                                'timestamp': timestamp,
                                'format': self.DEFAULT_IMAGE_FORMAT,
                                'width': pixmap.width(),
                                'height': pixmap.height()
                            })

                            # 发射信号，通知主窗口显示图片预览
                            self.image_pasted.emit(pixmap)

                            print(f"图片已粘贴并转换为Base64，大小: {pixmap.width()}x{pixmap.height()}")
                            return  # 不插入图片到文本中，只存储数据

                except Exception as e:
                    print(f"处理粘贴图片时出错: {e}")

        # 处理其他类型的粘贴（文本等）
        super().insertFromMimeData(source_data)

    def get_image_data(self):
        """获取所有图片数据的副本"""
        return self.image_data.copy() 