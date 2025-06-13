"""
Advanced Interaction System for Interactive Feedback MCP
Provides intelligent shortcuts, gesture recognition, context menus, and drag-drop functionality
"""

from PySide6.QtCore import (QObject, Signal, QTimer, QPoint, QRect, QMimeData, 
                           QPropertyAnimation, QEasingCurve, Qt, QEvent)
from PySide6.QtWidgets import (QWidget, QMenu, QApplication, QToolTip, QGraphicsDropShadowEffect)
from PySide6.QtGui import (QKeySequence, QCursor, QDrag, QPainter, QPixmap, 
                          QMouseEvent, QKeyEvent, QWheelEvent, QAction, QShortcut)
from typing import Dict, List, Callable, Optional, Tuple, Any
import time
import json
from dataclasses import dataclass
from enum import Enum

class GestureType(Enum):
    """Types of gestures supported"""
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PINCH_IN = "pinch_in"
    PINCH_OUT = "pinch_out"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    CIRCLE_CLOCKWISE = "circle_cw"
    CIRCLE_COUNTER_CLOCKWISE = "circle_ccw"

@dataclass
class GestureEvent:
    """Gesture event data"""
    gesture_type: GestureType
    start_pos: QPoint
    end_pos: QPoint
    duration: float
    velocity: float
    confidence: float

class SmartShortcutManager(QObject):
    """Intelligent shortcut management with context awareness"""
    
    shortcut_triggered = Signal(str, dict)
    
    def __init__(self, parent_widget: QWidget):
        super().__init__()
        self.parent_widget = parent_widget
        self.shortcuts: Dict[str, QShortcut] = {}
        self.context_shortcuts: Dict[str, Dict[str, QShortcut]] = {}
        self.current_context = "default"
        self.shortcut_history: List[Tuple[str, float]] = []
        self.learning_enabled = True
        
    def register_shortcut(self, key_sequence: str, action_name: str, 
                         callback: Callable, context: str = "default",
                         description: str = "", priority: int = 0):
        """Register a smart shortcut with context awareness"""
        
        if context not in self.context_shortcuts:
            self.context_shortcuts[context] = {}
        
        shortcut = QShortcut(QKeySequence(key_sequence), self.parent_widget)
        shortcut.activated.connect(lambda: self._on_shortcut_activated(action_name, callback))
        
        self.context_shortcuts[context][action_name] = shortcut
        
        # Store metadata
        shortcut.action_name = action_name
        shortcut.description = description
        shortcut.priority = priority
        shortcut.usage_count = 0
        shortcut.last_used = 0
        
    def set_context(self, context: str):
        """Switch shortcut context"""
        
        # Disable current context shortcuts
        if self.current_context in self.context_shortcuts:
            for shortcut in self.context_shortcuts[self.current_context].values():
                shortcut.setEnabled(False)
        
        # Enable new context shortcuts
        self.current_context = context
        if context in self.context_shortcuts:
            for shortcut in self.context_shortcuts[context].values():
                shortcut.setEnabled(True)
    
    def get_available_shortcuts(self) -> List[Dict[str, Any]]:
        """Get list of available shortcuts in current context"""
        
        shortcuts = []
        if self.current_context in self.context_shortcuts:
            for action_name, shortcut in self.context_shortcuts[self.current_context].items():
                shortcuts.append({
                    'action': action_name,
                    'key': shortcut.key().toString(),
                    'description': getattr(shortcut, 'description', ''),
                    'usage_count': getattr(shortcut, 'usage_count', 0),
                    'priority': getattr(shortcut, 'priority', 0)
                })
        
        return sorted(shortcuts, key=lambda x: (x['priority'], x['usage_count']), reverse=True)
    
    def suggest_shortcuts(self, action_pattern: str) -> List[str]:
        """Suggest shortcuts based on usage patterns"""
        
        if not self.learning_enabled:
            return []
        
        # Analyze usage patterns
        recent_actions = [action for action, timestamp in self.shortcut_history 
                         if time.time() - timestamp < 300]  # Last 5 minutes
        
        suggestions = []
        for action in recent_actions:
            if action_pattern.lower() in action.lower():
                suggestions.append(action)
        
        return list(set(suggestions))[:5]  # Top 5 unique suggestions
    
    def _on_shortcut_activated(self, action_name: str, callback: Callable):
        """Handle shortcut activation with learning"""
        
        # Update usage statistics
        if self.current_context in self.context_shortcuts:
            if action_name in self.context_shortcuts[self.current_context]:
                shortcut = self.context_shortcuts[self.current_context][action_name]
                shortcut.usage_count = getattr(shortcut, 'usage_count', 0) + 1
                shortcut.last_used = time.time()
        
        # Record for learning
        self.shortcut_history.append((action_name, time.time()))
        if len(self.shortcut_history) > 100:  # Keep last 100 actions
            self.shortcut_history = self.shortcut_history[-100:]
        
        # Execute callback
        try:
            callback()
            self.shortcut_triggered.emit(action_name, {'context': self.current_context})
        except Exception as e:
            print(f"Error executing shortcut {action_name}: {e}")

class GestureRecognizer(QObject):
    """Advanced gesture recognition system"""
    
    gesture_detected = Signal(GestureEvent)
    
    def __init__(self, widget: QWidget):
        super().__init__()
        self.widget = widget
        self.touch_points: List[QPoint] = []
        self.gesture_start_time = 0
        self.gesture_threshold = 50  # Minimum distance for gesture
        self.long_press_duration = 800  # ms
        self.double_tap_interval = 300  # ms
        self.last_tap_time = 0
        self.last_tap_pos = QPoint()
        
        # Install event filter
        widget.installEventFilter(self)
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Filter and process gesture events"""
        
        if obj != self.widget:
            return False
        
        if event.type() == QEvent.Type.MouseButtonPress:
            self._handle_mouse_press(event)
        elif event.type() == QEvent.Type.MouseMove:
            self._handle_mouse_move(event)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self._handle_mouse_release(event)
        elif event.type() == QEvent.Type.Wheel:
            self._handle_wheel_event(event)
        
        return False
    
    def _handle_mouse_press(self, event: QMouseEvent):
        """Handle mouse press for gesture start"""
        
        self.touch_points = [event.pos()]
        self.gesture_start_time = time.time()
        
        # Check for double tap
        current_time = time.time() * 1000
        if (current_time - self.last_tap_time < self.double_tap_interval and
            (event.pos() - self.last_tap_pos).manhattanLength() < 20):
            
            gesture = GestureEvent(
                GestureType.DOUBLE_TAP,
                event.pos(),
                event.pos(),
                0,
                0,
                0.9
            )
            self.gesture_detected.emit(gesture)
        
        self.last_tap_time = current_time
        self.last_tap_pos = event.pos()
    
    def _handle_mouse_move(self, event: QMouseEvent):
        """Handle mouse move for gesture tracking"""
        
        if not self.touch_points:
            return
        
        self.touch_points.append(event.pos())
        
        # Limit tracking points
        if len(self.touch_points) > 50:
            self.touch_points = self.touch_points[-50:]
    
    def _handle_mouse_release(self, event: QMouseEvent):
        """Handle mouse release for gesture completion"""
        
        if not self.touch_points:
            return
        
        duration = time.time() - self.gesture_start_time
        start_pos = self.touch_points[0]
        end_pos = event.pos()
        distance = (end_pos - start_pos).manhattanLength()
        
        # Check for long press
        if duration > self.long_press_duration / 1000 and distance < 20:
            gesture = GestureEvent(
                GestureType.LONG_PRESS,
                start_pos,
                end_pos,
                duration,
                0,
                0.8
            )
            self.gesture_detected.emit(gesture)
            return
        
        # Check for swipe gestures
        if distance > self.gesture_threshold:
            velocity = distance / duration if duration > 0 else 0
            gesture_type = self._classify_swipe(start_pos, end_pos)
            
            if gesture_type:
                gesture = GestureEvent(
                    gesture_type,
                    start_pos,
                    end_pos,
                    duration,
                    velocity,
                    0.7
                )
                self.gesture_detected.emit(gesture)
        
        self.touch_points.clear()
    
    def _handle_wheel_event(self, event: QWheelEvent):
        """Handle wheel events for zoom gestures"""
        
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Pinch gesture simulation with Ctrl+Wheel
            gesture_type = GestureType.PINCH_OUT if event.angleDelta().y() > 0 else GestureType.PINCH_IN
            
            gesture = GestureEvent(
                gesture_type,
                event.position().toPoint(),
                event.position().toPoint(),
                0,
                abs(event.angleDelta().y()),
                0.6
            )
            self.gesture_detected.emit(gesture)
    
    def _classify_swipe(self, start: QPoint, end: QPoint) -> Optional[GestureType]:
        """Classify swipe direction"""
        
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        if abs(dx) > abs(dy):
            return GestureType.SWIPE_RIGHT if dx > 0 else GestureType.SWIPE_LEFT
        else:
            return GestureType.SWIPE_DOWN if dy > 0 else GestureType.SWIPE_UP

class ContextMenuManager(QObject):
    """Advanced context menu system with dynamic content"""
    
    menu_action_triggered = Signal(str, dict)
    
    def __init__(self, widget: QWidget):
        super().__init__()
        self.widget = widget
        self.menu_providers: Dict[str, Callable] = {}
        self.current_context = {}
        
        # Install event filter for right-click
        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        widget.customContextMenuRequested.connect(self._show_context_menu)
    
    def register_menu_provider(self, context_type: str, provider: Callable):
        """Register a context menu provider"""
        self.menu_providers[context_type] = provider
    
    def set_context(self, context: Dict[str, Any]):
        """Set current context for menu generation"""
        self.current_context = context
    
    def _show_context_menu(self, position: QPoint):
        """Show context menu at position"""
        
        menu = QMenu(self.widget)
        menu.setStyleSheet(self._get_menu_style())
        
        # Add context-specific items
        context_type = self.current_context.get('type', 'default')
        if context_type in self.menu_providers:
            items = self.menu_providers[context_type](self.current_context)
            self._populate_menu(menu, items)
        
        # Add common items
        self._add_common_items(menu)
        
        # Show menu
        global_pos = self.widget.mapToGlobal(position)
        action = menu.exec(global_pos)
        
        if action:
            self.menu_action_triggered.emit(action.text(), self.current_context)
    
    def _populate_menu(self, menu: QMenu, items: List[Dict[str, Any]]):
        """Populate menu with items"""
        
        for item in items:
            if item.get('separator'):
                menu.addSeparator()
            else:
                action = QAction(item['text'], menu)
                action.setEnabled(item.get('enabled', True))
                if 'icon' in item:
                    action.setIcon(item['icon'])
                if 'shortcut' in item:
                    action.setShortcut(QKeySequence(item['shortcut']))
                
                menu.addAction(action)
    
    def _add_common_items(self, menu: QMenu):
        """Add common menu items"""
        
        menu.addSeparator()
        
        # Help action
        help_action = QAction("Help", menu)
        help_action.setShortcut(QKeySequence("F1"))
        menu.addAction(help_action)
        
        # Settings action
        settings_action = QAction("Settings", menu)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        menu.addAction(settings_action)
    
    def _get_menu_style(self) -> str:
        """Get menu stylesheet"""
        
        return """
        QMenu {
            background-color: rgba(30, 30, 30, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 4px;
            color: white;
        }
        
        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
            margin: 1px;
        }
        
        QMenu::item:selected {
            background-color: rgba(33, 150, 243, 0.3);
        }
        
        QMenu::item:disabled {
            color: rgba(255, 255, 255, 0.5);
        }
        
        QMenu::separator {
            height: 1px;
            background-color: rgba(255, 255, 255, 0.2);
            margin: 4px 8px;
        }
        """

class DragDropManager(QObject):
    """Advanced drag and drop functionality"""
    
    drag_started = Signal(QMimeData)
    drop_completed = Signal(QMimeData, QPoint)
    
    def __init__(self, widget: QWidget):
        super().__init__()
        self.widget = widget
        self.drag_threshold = 10
        self.drag_start_pos = QPoint()
        self.is_dragging = False
        
        # Enable drag and drop
        widget.setAcceptDrops(True)
        widget.installEventFilter(self)
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Filter drag and drop events"""
        
        if obj != self.widget:
            return False
        
        if event.type() == QEvent.Type.MouseButtonPress:
            self.drag_start_pos = event.pos()
            self.is_dragging = False
        elif event.type() == QEvent.Type.MouseMove:
            if (event.buttons() & Qt.MouseButton.LeftButton and
                not self.is_dragging and
                (event.pos() - self.drag_start_pos).manhattanLength() > self.drag_threshold):
                self._start_drag(event.pos())
        elif event.type() == QEvent.Type.DragEnter:
            self._handle_drag_enter(event)
        elif event.type() == QEvent.Type.Drop:
            self._handle_drop(event)
        
        return False
    
    def _start_drag(self, pos: QPoint):
        """Start drag operation"""
        
        self.is_dragging = True
        
        # Create drag object
        drag = QDrag(self.widget)
        mime_data = QMimeData()
        
        # Set drag data (customize based on context)
        mime_data.setText("Dragged content")
        drag.setMimeData(mime_data)
        
        # Create drag pixmap
        pixmap = self._create_drag_pixmap()
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
        
        # Execute drag
        self.drag_started.emit(mime_data)
        result = drag.exec(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
    
    def _create_drag_pixmap(self) -> QPixmap:
        """Create pixmap for drag operation"""
        
        pixmap = QPixmap(100, 50)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(Qt.GlobalColor.blue)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawRoundedRect(0, 0, 100, 50, 10, 10)
        painter.drawText(10, 30, "Dragging...")
        painter.end()
        
        return pixmap
    
    def _handle_drag_enter(self, event):
        """Handle drag enter event"""
        
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def _handle_drop(self, event):
        """Handle drop event"""
        
        if event.mimeData().hasText():
            self.drop_completed.emit(event.mimeData(), event.pos())
            event.acceptProposedAction()

class SmartTooltipManager(QObject):
    """Intelligent tooltip system with context awareness"""
    
    def __init__(self):
        super().__init__()
        self.tooltips: Dict[QWidget, Dict[str, Any]] = {}
        self.show_timer = QTimer()
        self.hide_timer = QTimer()
        self.show_delay = 500  # ms
        self.hide_delay = 3000  # ms
        
        self.show_timer.setSingleShot(True)
        self.hide_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self._show_tooltip)
        self.hide_timer.timeout.connect(self._hide_tooltip)
        
        self.current_widget = None
        self.current_pos = QPoint()
    
    def register_tooltip(self, widget: QWidget, text: str, 
                        rich_content: str = None, delay: int = None):
        """Register smart tooltip for widget"""
        
        self.tooltips[widget] = {
            'text': text,
            'rich_content': rich_content,
            'delay': delay or self.show_delay,
            'usage_count': 0,
            'last_shown': 0
        }
        
        widget.installEventFilter(self)
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Filter tooltip events"""
        
        if obj not in self.tooltips:
            return False
        
        if event.type() == QEvent.Type.Enter:
            self.current_widget = obj
            self.current_pos = QCursor.pos()
            delay = self.tooltips[obj]['delay']
            self.show_timer.start(delay)
        elif event.type() == QEvent.Type.Leave:
            self.show_timer.stop()
            self.hide_timer.start(self.hide_delay)
        
        return False
    
    def _show_tooltip(self):
        """Show intelligent tooltip"""
        
        if not self.current_widget or self.current_widget not in self.tooltips:
            return
        
        tooltip_data = self.tooltips[self.current_widget]
        tooltip_data['usage_count'] += 1
        tooltip_data['last_shown'] = time.time()
        
        # Show appropriate tooltip content
        if tooltip_data['rich_content']:
            # Could implement rich tooltip widget here
            QToolTip.showText(self.current_pos, tooltip_data['text'])
        else:
            QToolTip.showText(self.current_pos, tooltip_data['text'])
    
    def _hide_tooltip(self):
        """Hide tooltip"""
        QToolTip.hideText()

# Global instances
global_shortcut_manager = None
global_gesture_recognizer = None
global_context_menu_manager = None
global_drag_drop_manager = None
global_tooltip_manager = SmartTooltipManager()

def initialize_advanced_interactions(widget: QWidget) -> Dict[str, Any]:
    """Initialize all advanced interaction systems for a widget"""
    
    global global_shortcut_manager, global_gesture_recognizer
    global global_context_menu_manager, global_drag_drop_manager
    
    managers = {
        'shortcuts': SmartShortcutManager(widget),
        'gestures': GestureRecognizer(widget),
        'context_menu': ContextMenuManager(widget),
        'drag_drop': DragDropManager(widget),
        'tooltips': global_tooltip_manager
    }
    
    # Update global references
    global_shortcut_manager = managers['shortcuts']
    global_gesture_recognizer = managers['gestures']
    global_context_menu_manager = managers['context_menu']
    global_drag_drop_manager = managers['drag_drop']
    
    return managers 