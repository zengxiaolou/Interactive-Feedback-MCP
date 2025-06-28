# Custom Text Edit Widget for Interactive Feedback MCP
# 自定义文本编辑器组件

import base64
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import QTextEdit, QApplication, QWidget
from PySide6.QtCore import Qt, Signal, QBuffer, QIODevice, QRect, QPoint, QTimer
from PySide6.QtGui import QKeyEvent, QPixmap, QInputMethodEvent, QTextCursor

class FeedbackTextEdit(QTextEdit):
    """支持图片粘贴和智能输入法处理的自定义文本编辑器"""
    
    # 图片处理常量
    DEFAULT_MAX_IMAGE_WIDTH = 1624
    DEFAULT_MAX_IMAGE_HEIGHT = 1624
    DEFAULT_IMAGE_FORMAT = "PNG"
    
    # 输入法处理常量
    IME_CANDIDATE_HEIGHT = 120  # 输入法候选框预估高度
    IME_ADJUST_MARGIN = 20      # 调整边距
    IME_CHECK_DELAY = 50        # 输入法状态检查延迟(ms)

    # 定义类级别的信号
    image_pasted = Signal(QPixmap)
    ime_position_changed = Signal(QRect)  # 输入法位置变化信号
    ime_visibility_changed = Signal(bool)  # 输入法显示/隐藏信号
    request_window_adjustment = Signal(int, int)  # 请求窗口位置调整信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_data: List[Dict[str, Any]] = []
        
        # 输入法状态跟踪
        self.ime_active = False
        self.ime_rect = QRect()
        self.original_window_pos: Optional[QPoint] = None
        self.ime_adjustment_applied = False
        
        # 延迟检查定时器
        self.ime_check_timer = QTimer()
        self.ime_check_timer.setSingleShot(True)
        self.ime_check_timer.timeout.connect(self._check_ime_position)
        
        # 启用输入法查询
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        
        print("✅ FeedbackTextEdit初始化完成，输入法处理已启用")

    def inputMethodEvent(self, event: QInputMethodEvent):
        """处理输入法事件 - 核心输入法遮挡检测"""
        try:
            # 调用父类处理
            super().inputMethodEvent(event)
            
            # 检测输入法状态变化
            was_active = self.ime_active
            is_active = bool(event.preeditString() or event.commitString())
            
            if is_active != was_active:
                self.ime_active = is_active
                self.ime_visibility_changed.emit(is_active)
                print(f"🎯 输入法状态变化: {'激活' if is_active else '关闭'}")
            
            # 如果输入法激活，延迟检查位置
            if is_active:
                self.ime_check_timer.start(self.IME_CHECK_DELAY)
            else:
                self._restore_window_position()
                
        except Exception as e:
            print(f"❌ 输入法事件处理错误: {e}")

    def inputMethodQuery(self, query):
        """提供输入法查询信息"""
        try:
            # PySide6中使用Qt.InputMethodQuery的枚举值
            from PySide6.QtCore import Qt
            
            if hasattr(Qt, 'ImCursorRectangle'):
                cursor_rect_query = Qt.ImCursorRectangle
                micro_focus_query = getattr(Qt, 'ImMicroFocus', Qt.ImCursorRectangle)
                selection_query = getattr(Qt, 'ImCurrentSelection', None)
            else:
                # 使用Qt.InputMethodQuery枚举
                cursor_rect_query = Qt.InputMethodQuery.ImCursorRectangle if hasattr(Qt.InputMethodQuery, 'ImCursorRectangle') else 1
                micro_focus_query = getattr(Qt.InputMethodQuery, 'ImMicroFocus', cursor_rect_query) if hasattr(Qt, 'InputMethodQuery') else cursor_rect_query
                selection_query = getattr(Qt.InputMethodQuery, 'ImCurrentSelection', None) if hasattr(Qt, 'InputMethodQuery') else None
            
            if query == cursor_rect_query or query == micro_focus_query:
                # 返回光标矩形位置
                cursor_rect = self.cursorRect()
                return cursor_rect
            elif selection_query and query == selection_query:
                # 返回当前选择
                return self.textCursor().selectedText()
            
            return super().inputMethodQuery(query)
            
        except Exception as e:
            print(f"⚠️ 输入法查询异常: {e}")
            # 发生异常时返回光标位置作为默认值
            try:
                return self.cursorRect()
            except:
                return super().inputMethodQuery(query)

    def _check_ime_position(self):
        """检查输入法候选框位置并执行智能调整"""
        try:
            if not self.ime_active:
                return
                
            # 获取光标位置
            cursor_rect = self.cursorRect()
            if cursor_rect.isNull():
                return
                
            # 计算全局光标位置
            global_cursor_pos = self.mapToGlobal(cursor_rect.bottomLeft())
            
            # 预估输入法候选框位置
            ime_rect = QRect(
                global_cursor_pos.x(),
                global_cursor_pos.y(),
                200,  # 预估宽度
                self.IME_CANDIDATE_HEIGHT
            )
            
            # 检测是否需要调整
            if self._should_adjust_window(ime_rect):
                adjustment = self._calculate_adjustment(ime_rect)
                if adjustment != (0, 0):
                    self._apply_window_adjustment(adjustment)
                    print(f"🎯 应用窗口调整: x={adjustment[0]}, y={adjustment[1]}")
            
            # 更新输入法矩形并发射信号
            self.ime_rect = ime_rect
            self.ime_position_changed.emit(ime_rect)
            
        except Exception as e:
            print(f"❌ 输入法位置检查错误: {e}")

    def _should_adjust_window(self, ime_rect: QRect) -> bool:
        """判断是否需要调整窗口位置"""
        try:
            main_window = self.window()
            if not main_window:
                return False
                
            # 获取主窗口几何信息
            window_rect = main_window.geometry()
            
            # 检查输入法是否与窗口重叠
            overlap = window_rect.intersected(ime_rect)
            
            # 如果重叠区域高度超过阈值，需要调整
            return not overlap.isEmpty() and overlap.height() > 30
            
        except Exception as e:
            print(f"❌ 窗口调整判断错误: {e}")
            return False

    def _calculate_adjustment(self, ime_rect: QRect) -> tuple[int, int]:
        """计算最佳的窗口调整量"""
        try:
            main_window = self.window()
            if not main_window:
                return (0, 0)
                
            window_rect = main_window.geometry()
            screen = QApplication.primaryScreen()
            screen_rect = screen.availableGeometry()
            
            # 计算向上移动的距离
            overlap_bottom = ime_rect.bottom()
            window_bottom = window_rect.bottom()
            
            if overlap_bottom > window_bottom:
                # 输入法在窗口下方，不需要调整
                return (0, 0)
            
            # 计算需要向上移动的距离
            move_up = ime_rect.height() + self.IME_ADJUST_MARGIN
            
            # 确保不会移出屏幕顶部
            new_y = window_rect.y() - move_up
            if new_y < screen_rect.y():
                move_up = window_rect.y() - screen_rect.y()
            
            return (0, -move_up)
            
        except Exception as e:
            print(f"❌ 调整量计算错误: {e}")
            return (0, 0)

    def _apply_window_adjustment(self, adjustment: tuple[int, int]):
        """应用窗口位置调整"""
        try:
            main_window = self.window()
            if not main_window or self.ime_adjustment_applied:
                return
                
            # 保存原始位置
            if self.original_window_pos is None:
                self.original_window_pos = main_window.pos()
            
            # 计算新位置
            current_pos = main_window.pos()
            new_pos = QPoint(
                current_pos.x() + adjustment[0],
                current_pos.y() + adjustment[1]
            )
            
            # 移动窗口
            main_window.move(new_pos)
            self.ime_adjustment_applied = True
            
            # 发射调整请求信号
            self.request_window_adjustment.emit(adjustment[0], adjustment[1])
            
        except Exception as e:
            print(f"❌ 窗口调整应用错误: {e}")

    def _restore_window_position(self):
        """恢复窗口原始位置"""
        try:
            if not self.ime_adjustment_applied or self.original_window_pos is None:
                return
                
            main_window = self.window()
            if main_window:
                main_window.move(self.original_window_pos)
                print("🔄 恢复窗口原始位置")
            
            self.original_window_pos = None
            self.ime_adjustment_applied = False
            
        except Exception as e:
            print(f"❌ 窗口位置恢复错误: {e}")

    def focusInEvent(self, event):
        """获得焦点时重置输入法状态"""
        super().focusInEvent(event)
        self.ime_active = False
        print("🎯 文本框获得焦点，重置输入法状态")

    def focusOutEvent(self, event):
        """失去焦点时恢复窗口位置"""
        super().focusOutEvent(event)
        self._restore_window_position()
        self.ime_active = False
        print("🔄 文本框失去焦点，恢复窗口位置")

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件，支持Enter提交，Shift+Enter换行"""
        if event.key() == Qt.Key_Return:
            if event.modifiers() == Qt.ShiftModifier:
                # Shift+Enter: 换行
                super().keyPressEvent(event)
                return
            else:
                # Enter: 提交操作
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

    def get_ime_status(self) -> Dict[str, Any]:
        """获取输入法状态信息（用于调试）"""
        return {
            'active': self.ime_active,
            'rect': {
                'x': self.ime_rect.x(),
                'y': self.ime_rect.y(),
                'width': self.ime_rect.width(),
                'height': self.ime_rect.height()
            },
            'adjustment_applied': self.ime_adjustment_applied,
            'original_pos': {
                'x': self.original_window_pos.x() if self.original_window_pos else None,
                'y': self.original_window_pos.y() if self.original_window_pos else None
            } if self.original_window_pos else None
        } 