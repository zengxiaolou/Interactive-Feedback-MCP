#!/usr/bin/env python3
"""
Interactive Feedback MCP 图标管理器
管理和加载应用图标资源
"""

import os
from typing import Optional
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize

class IconManager:
    """应用图标管理器"""
    
    def __init__(self):
        self.icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        self._icon_cache = {}
        
    def get_app_icon(self, size: Optional[int] = None) -> QIcon:
        """获取应用主图标"""
        if size is None:
            # 返回多尺寸图标
            icon = QIcon()
            sizes = [16, 32, 48, 64, 128, 256, 512]
            for s in sizes:
                icon_path = os.path.join(self.icons_dir, f"app_icon_{s}.png")
                if os.path.exists(icon_path):
                    icon.addFile(icon_path, QSize(s, s))
            return icon
        else:
            # 返回指定尺寸的图标
            icon_path = os.path.join(self.icons_dir, f"app_icon_{size}.png")
            if os.path.exists(icon_path):
                return QIcon(icon_path)
            else:
                # 回退到主图标
                main_icon_path = os.path.join(self.icons_dir, "app_icon.png")
                if os.path.exists(main_icon_path):
                    return QIcon(main_icon_path)
        
        return QIcon()  # 空图标
    
    def get_tray_icon(self) -> QIcon:
        """获取系统托盘图标"""
        tray_icon_path = os.path.join(self.icons_dir, "tray_icon.png")
        if os.path.exists(tray_icon_path):
            return QIcon(tray_icon_path)
        return self.get_app_icon(64)  # 回退到应用图标
    
    def get_pixmap(self, name: str, size: Optional[int] = None) -> QPixmap:
        """获取图标的QPixmap对象"""
        if name == "app_icon":
            if size:
                icon_path = os.path.join(self.icons_dir, f"app_icon_{size}.png")
            else:
                icon_path = os.path.join(self.icons_dir, "app_icon.png")
        elif name == "tray_icon":
            icon_path = os.path.join(self.icons_dir, "tray_icon.png")
        else:
            return QPixmap()
        
        if os.path.exists(icon_path):
            return QPixmap(icon_path)
        return QPixmap()
    
    def is_available(self) -> bool:
        """检查图标资源是否可用"""
        main_icon_path = os.path.join(self.icons_dir, "app_icon.png")
        return os.path.exists(main_icon_path)
    
    def get_icon_info(self) -> dict:
        """获取图标信息"""
        info = {
            "icons_dir": self.icons_dir,
            "available": self.is_available(),
            "files": []
        }
        
        if os.path.exists(self.icons_dir):
            for file in os.listdir(self.icons_dir):
                if file.endswith('.png'):
                    file_path = os.path.join(self.icons_dir, file)
                    file_size = os.path.getsize(file_path)
                    info["files"].append({
                        "name": file,
                        "size": file_size,
                        "path": file_path
                    })
        
        return info

# 全局图标管理器实例
icon_manager = IconManager() 