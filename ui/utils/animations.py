"""
Enhanced UI Animation System for Interactive Feedback MCP
Provides smooth transitions, easing functions, and animation management
"""

from PySide6.QtCore import (QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, 
                           QSequentialAnimationGroup, QTimer, QObject, Signal, Property)
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PySide6.QtGui import QColor
from typing import Dict, List, Callable, Optional, Any
import time

class AnimationConfig:
    """Animation configuration constants"""
    
    # Duration settings (milliseconds)
    FAST = 150
    NORMAL = 250
    SLOW = 400
    VERY_SLOW = 600
    
    # Easing curves
    EASE_IN_OUT = QEasingCurve.Type.InOutCubic
    EASE_IN = QEasingCurve.Type.InCubic
    EASE_OUT = QEasingCurve.Type.OutCubic
    BOUNCE = QEasingCurve.Type.OutBounce
    ELASTIC = QEasingCurve.Type.OutElastic
    
    # Common animation properties
    OPACITY = b"windowOpacity"
    GEOMETRY = b"geometry"
    SIZE = b"size"
    POSITION = b"pos"

class AnimationManager(QObject):
    """Central animation management system"""
    
    animation_started = Signal(str)
    animation_finished = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.active_animations: Dict[str, QPropertyAnimation] = {}
        self.animation_groups: Dict[str, Any] = {}
        self.performance_monitor = None
        
    def create_fade_animation(self, widget: QWidget, start_opacity: float = 0.0, 
                            end_opacity: float = 1.0, duration: int = AnimationConfig.NORMAL,
                            easing: QEasingCurve.Type = AnimationConfig.EASE_IN_OUT) -> QPropertyAnimation:
        """Create fade in/out animation"""
        
        # Ensure widget has opacity effect
        if not widget.graphicsEffect():
            opacity_effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(opacity_effect)
            opacity_effect.setOpacity(start_opacity)
        
        animation = QPropertyAnimation(widget.graphicsEffect(), b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(easing)
        
        return animation
    
    def create_slide_animation(self, widget: QWidget, start_pos: tuple, end_pos: tuple,
                             duration: int = AnimationConfig.NORMAL,
                             easing: QEasingCurve.Type = AnimationConfig.EASE_IN_OUT) -> QPropertyAnimation:
        """Create slide animation"""
        
        animation = QPropertyAnimation(widget, AnimationConfig.POSITION)
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(easing)
        
        return animation
    
    def create_scale_animation(self, widget: QWidget, start_size: tuple, end_size: tuple,
                             duration: int = AnimationConfig.NORMAL,
                             easing: QEasingCurve.Type = AnimationConfig.EASE_IN_OUT) -> QPropertyAnimation:
        """Create scale animation"""
        
        animation = QPropertyAnimation(widget, AnimationConfig.SIZE)
        animation.setDuration(duration)
        animation.setStartValue(start_size)
        animation.setEndValue(end_size)
        animation.setEasingCurve(easing)
        
        return animation
    
    def create_parallel_group(self, animations: List[QPropertyAnimation], 
                            group_name: str = None) -> QParallelAnimationGroup:
        """Create parallel animation group"""
        
        group = QParallelAnimationGroup()
        for animation in animations:
            group.addAnimation(animation)
        
        if group_name:
            self.animation_groups[group_name] = group
            group.finished.connect(lambda: self.animation_finished.emit(group_name))
        
        return group
    
    def create_sequential_group(self, animations: List[QPropertyAnimation],
                              group_name: str = None) -> QSequentialAnimationGroup:
        """Create sequential animation group"""
        
        group = QSequentialAnimationGroup()
        for animation in animations:
            group.addAnimation(animation)
        
        if group_name:
            self.animation_groups[group_name] = group
            group.finished.connect(lambda: self.animation_finished.emit(group_name))
        
        return group
    
    def start_animation(self, animation_name: str, animation: QPropertyAnimation):
        """Start and track animation"""
        
        if animation_name in self.active_animations:
            self.active_animations[animation_name].stop()
        
        self.active_animations[animation_name] = animation
        animation.finished.connect(lambda: self._on_animation_finished(animation_name))
        
        self.animation_started.emit(animation_name)
        animation.start()
    
    def stop_animation(self, animation_name: str):
        """Stop specific animation"""
        
        if animation_name in self.active_animations:
            self.active_animations[animation_name].stop()
            del self.active_animations[animation_name]
    
    def stop_all_animations(self):
        """Stop all active animations"""
        
        for animation in self.active_animations.values():
            animation.stop()
        self.active_animations.clear()
        
        for group in self.animation_groups.values():
            if hasattr(group, 'stop'):
                group.stop()
        self.animation_groups.clear()
    
    def _on_animation_finished(self, animation_name: str):
        """Handle animation completion"""
        
        if animation_name in self.active_animations:
            del self.active_animations[animation_name]
        
        self.animation_finished.emit(animation_name)

class TransitionEffects:
    """Pre-defined transition effects for common UI patterns"""
    
    @staticmethod
    def fade_in_widget(widget: QWidget, duration: int = AnimationConfig.NORMAL) -> QPropertyAnimation:
        """Fade in widget smoothly"""
        
        manager = AnimationManager()
        animation = manager.create_fade_animation(widget, 0.0, 1.0, duration)
        return animation
    
    @staticmethod
    def fade_out_widget(widget: QWidget, duration: int = AnimationConfig.NORMAL) -> QPropertyAnimation:
        """Fade out widget smoothly"""
        
        manager = AnimationManager()
        animation = manager.create_fade_animation(widget, 1.0, 0.0, duration)
        return animation
    
    @staticmethod
    def slide_in_from_left(widget: QWidget, distance: int = 300, 
                          duration: int = AnimationConfig.NORMAL) -> QPropertyAnimation:
        """Slide widget in from left"""
        
        current_pos = widget.pos()
        start_pos = (current_pos.x() - distance, current_pos.y())
        
        manager = AnimationManager()
        animation = manager.create_slide_animation(widget, start_pos, current_pos, duration)
        return animation
    
    @staticmethod
    def slide_in_from_right(widget: QWidget, distance: int = 300,
                           duration: int = AnimationConfig.NORMAL) -> QPropertyAnimation:
        """Slide widget in from right"""
        
        current_pos = widget.pos()
        start_pos = (current_pos.x() + distance, current_pos.y())
        
        manager = AnimationManager()
        animation = manager.create_slide_animation(widget, start_pos, current_pos, duration)
        return animation
    
    @staticmethod
    def bounce_in(widget: QWidget, duration: int = AnimationConfig.SLOW) -> QParallelAnimationGroup:
        """Bounce in effect with scale and fade"""
        
        manager = AnimationManager()
        
        # Scale animation
        current_size = widget.size()
        scale_animation = manager.create_scale_animation(
            widget, (0, 0), (current_size.width(), current_size.height()), 
            duration, AnimationConfig.BOUNCE
        )
        
        # Fade animation
        fade_animation = manager.create_fade_animation(widget, 0.0, 1.0, duration)
        
        return manager.create_parallel_group([scale_animation, fade_animation])
    
    @staticmethod
    def elastic_scale(widget: QWidget, scale_factor: float = 1.1,
                     duration: int = AnimationConfig.NORMAL) -> QSequentialAnimationGroup:
        """Elastic scale effect (scale up then back)"""
        
        manager = AnimationManager()
        current_size = widget.size()
        
        # Scale up
        scale_up = manager.create_scale_animation(
            widget, 
            (current_size.width(), current_size.height()),
            (int(current_size.width() * scale_factor), int(current_size.height() * scale_factor)),
            duration // 2, AnimationConfig.EASE_OUT
        )
        
        # Scale back
        scale_back = manager.create_scale_animation(
            widget,
            (int(current_size.width() * scale_factor), int(current_size.height() * scale_factor)),
            (current_size.width(), current_size.height()),
            duration // 2, AnimationConfig.EASE_IN
        )
        
        return manager.create_sequential_group([scale_up, scale_back])

class InteractionAnimations:
    """Animations for user interactions"""
    
    def __init__(self, animation_manager: AnimationManager):
        self.manager = animation_manager
        self.hover_animations: Dict[QWidget, QPropertyAnimation] = {}
    
    def setup_hover_animation(self, widget: QWidget, hover_scale: float = 1.05,
                            duration: int = AnimationConfig.FAST):
        """Setup hover animation for widget"""
        
        original_size = widget.size()
        
        def on_enter():
            if widget in self.hover_animations:
                self.hover_animations[widget].stop()
            
            hover_size = (int(original_size.width() * hover_scale), 
                         int(original_size.height() * hover_scale))
            animation = self.manager.create_scale_animation(
                widget, (original_size.width(), original_size.height()), 
                hover_size, duration, AnimationConfig.EASE_OUT
            )
            
            self.hover_animations[widget] = animation
            animation.start()
        
        def on_leave():
            if widget in self.hover_animations:
                self.hover_animations[widget].stop()
            
            animation = self.manager.create_scale_animation(
                widget, widget.size(), 
                (original_size.width(), original_size.height()),
                duration, AnimationConfig.EASE_IN
            )
            
            self.hover_animations[widget] = animation
            animation.start()
        
        # Connect to widget events (would need custom widget implementation)
        return on_enter, on_leave
    
    def setup_click_animation(self, widget: QWidget, click_scale: float = 0.95,
                            duration: int = AnimationConfig.FAST):
        """Setup click animation for widget"""
        
        def on_click():
            original_size = widget.size()
            click_size = (int(original_size.width() * click_scale),
                         int(original_size.height() * click_scale))
            
            # Scale down
            scale_down = self.manager.create_scale_animation(
                widget, (original_size.width(), original_size.height()),
                click_size, duration // 2, AnimationConfig.EASE_IN
            )
            
            # Scale back up
            scale_up = self.manager.create_scale_animation(
                widget, click_size,
                (original_size.width(), original_size.height()),
                duration // 2, AnimationConfig.EASE_OUT
            )
            
            group = self.manager.create_sequential_group([scale_down, scale_up])
            group.start()
        
        return on_click

class PerformanceOptimizedAnimations:
    """Performance-optimized animation utilities"""
    
    def __init__(self):
        self.animation_cache: Dict[str, QPropertyAnimation] = {}
        self.last_frame_time = time.time()
        self.target_fps = 60
        self.frame_budget = 1.0 / self.target_fps
    
    def should_animate(self) -> bool:
        """Check if we should run animations based on performance"""
        
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Skip animations if we're dropping frames
        return frame_time <= self.frame_budget * 1.5
    
    def get_cached_animation(self, cache_key: str, factory_func: Callable) -> QPropertyAnimation:
        """Get cached animation or create new one"""
        
        if cache_key not in self.animation_cache:
            self.animation_cache[cache_key] = factory_func()
        
        return self.animation_cache[cache_key]
    
    def clear_cache(self):
        """Clear animation cache"""
        
        for animation in self.animation_cache.values():
            if animation.state() == QPropertyAnimation.State.Running:
                animation.stop()
        
        self.animation_cache.clear()

# Global animation manager instance
global_animation_manager = AnimationManager()
global_interaction_animations = InteractionAnimations(global_animation_manager)
global_performance_animations = PerformanceOptimizedAnimations() 