#!/usr/bin/env python3
"""
Interactive Feedback MCP 应用图标生成器
生成不同尺寸的应用图标
"""

import os
from PySide6.QtGui import QPainter, QPixmap, QColor, QFont, QPen, QBrush, QLinearGradient
from PySide6.QtCore import Qt, QRect

class IconGenerator:
    """应用图标生成器"""
    
    def __init__(self):
        self.base_color = QColor(33, 150, 243)  # 主蓝色
        self.accent_color = QColor(156, 39, 176)  # 紫色
        self.background_color = QColor(18, 18, 18)  # 深色背景
        
    def create_app_icon(self, size: int = 256) -> QPixmap:
        """创建应用主图标"""
        # 为高DPI屏幕创建2倍分辨率的图标
        actual_size = size * 2
        pixmap = QPixmap(actual_size, actual_size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, actual_size, actual_size)
        gradient.setColorAt(0, self.base_color)
        gradient.setColorAt(1, self.accent_color)
        
        # 绘制圆形背景
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        margin = actual_size * 0.05
        painter.drawEllipse(int(margin), int(margin), 
                          int(actual_size - 2 * margin), int(actual_size - 2 * margin))
        
        # 绘制对话框图标
        self._draw_feedback_icon(painter, actual_size)
        
        painter.end()
        
        # 缩放到目标尺寸，保持高质量
        if actual_size != size:
            pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        return pixmap
    
    def _draw_feedback_icon(self, painter: QPainter, size: int):
        """绘制反馈对话框图标"""
        # 设置白色画笔
        painter.setPen(QPen(QColor(255, 255, 255), size * 0.02))
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        
        # 主对话框
        main_rect = QRect(int(size * 0.2), int(size * 0.25), 
                         int(size * 0.5), int(size * 0.35))
        painter.drawRoundedRect(main_rect, size * 0.05, size * 0.05)
        
        # 对话框尾巴
        from PySide6.QtCore import QPoint
        tail_points = [
            QPoint(int(size * 0.35), int(size * 0.6)),
            QPoint(int(size * 0.25), int(size * 0.7)),
            QPoint(int(size * 0.4), int(size * 0.6))
        ]
        painter.drawPolygon(tail_points)
        
        # 绘制文本线条
        painter.setPen(QPen(self.base_color, size * 0.015))
        line_y_start = size * 0.35
        line_spacing = size * 0.06
        for i in range(3):
            y = int(line_y_start + i * line_spacing)
            line_width = size * (0.35 - i * 0.05)  # 递减的线条长度
            painter.drawLine(int(size * 0.25), y, 
                           int(size * 0.25 + line_width), y)
        
        # 绘制交互元素（小圆点）
        painter.setBrush(QBrush(self.accent_color))
        painter.setPen(Qt.NoPen)
        dot_size = size * 0.03
        for i in range(3):
            x = int(size * 0.75 + i * size * 0.05)
            y = int(size * 0.3)
            painter.drawEllipse(int(x - dot_size/2), int(y - dot_size/2), 
                              int(dot_size), int(dot_size))
    
    def create_tray_icon(self, size: int = 64) -> QPixmap:
        """创建系统托盘图标（简化版）"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 简化的对话框图标
        painter.setBrush(QBrush(self.base_color))
        painter.setPen(Qt.NoPen)
        
        # 主圆形
        margin = size * 0.1
        painter.drawEllipse(int(margin), int(margin), 
                          int(size - 2 * margin), int(size - 2 * margin))
        
        # 白色对话框
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        dialog_size = size * 0.4
        dialog_x = (size - dialog_size) / 2
        dialog_y = size * 0.25
        painter.drawRoundedRect(int(dialog_x), int(dialog_y), 
                              int(dialog_size), int(dialog_size * 0.8), 
                              size * 0.05, size * 0.05)
        
        painter.end()
        return pixmap
    
    def save_icons(self, output_dir: str = "ui/resources/icons"):
        """保存不同尺寸的图标"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 应用图标 - 不同尺寸，包含macOS Dock需要的高分辨率版本
        sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
        for size in sizes:
            icon = self.create_app_icon(size)
            icon.save(os.path.join(output_dir, f"app_icon_{size}.png"))
        
        # 系统托盘图标
        tray_icon = self.create_tray_icon(64)
        tray_icon.save(os.path.join(output_dir, "tray_icon.png"))
        
        # 主图标（默认）
        main_icon = self.create_app_icon(256)
        main_icon.save(os.path.join(output_dir, "app_icon.png"))
        
        print(f"✅ 图标已保存到: {output_dir}")
        print(f"📁 生成的图标文件:")
        for size in sizes:
            print(f"   - app_icon_{size}.png")
        print(f"   - tray_icon.png")
        print(f"   - app_icon.png (主图标)")

def main():
    """主函数 - 生成所有图标"""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    generator = IconGenerator()
    generator.save_icons()
    
    print("\n🎨 Interactive Feedback MCP 图标生成完成！")

if __name__ == "__main__":
    main() 