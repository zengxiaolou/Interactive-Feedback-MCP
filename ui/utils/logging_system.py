#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive Feedback MCP - 完整日志系统
支持多级别日志、文件轮转、配置管理和性能监控
"""

import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading
import time
import traceback

@dataclass
class LogConfig:
    """日志配置类"""
    # 基础配置
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # 文件配置
    log_dir: str = "logs"
    log_filename: str = "interactive_feedback_mcp.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    # 控制台配置
    console_enabled: bool = True
    console_level: str = "INFO"
    console_format: str = "%(levelname)s - %(name)s - %(message)s"
    
    # 性能监控配置
    performance_enabled: bool = True
    performance_filename: str = "performance.log"
    slow_query_threshold: float = 1.0  # 秒
    
    # 错误追踪配置
    error_filename: str = "errors.log"
    error_detail_enabled: bool = True
    
    # 项目上下文配置
    project_context_enabled: bool = True
    project_context_filename: str = "project_context.log"

class LoggerManager:
    """日志管理器 - 单例模式"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = LogConfig()
            self.loggers: Dict[str, logging.Logger] = {}
            self.handlers: Dict[str, logging.Handler] = {}
            self.performance_data = []
            self.error_count = 0
            self.warning_count = 0
            self.initialized = True
            self._setup_logging()
    
    def _setup_logging(self):
        """设置日志系统"""
        # 创建日志目录
        log_dir = Path(self.config.log_dir)
        log_dir.mkdir(exist_ok=True)
        
        # 设置根日志级别
        logging.getLogger().setLevel(getattr(logging, self.config.level.upper()))
        
        # 创建格式化器
        self.formatter = logging.Formatter(
            self.config.format,
            datefmt=self.config.date_format
        )
        
        self.console_formatter = logging.Formatter(
            self.config.console_format,
            datefmt=self.config.date_format
        )
        
        # 设置主日志处理器
        self._setup_main_handler()
        
        # 设置控制台处理器
        if self.config.console_enabled:
            self._setup_console_handler()
        
        # 设置性能监控处理器
        if self.config.performance_enabled:
            self._setup_performance_handler()
        
        # 设置错误处理器
        self._setup_error_handler()
        
        # 设置项目上下文处理器
        if self.config.project_context_enabled:
            self._setup_project_context_handler()
    
    def _setup_main_handler(self):
        """设置主日志文件处理器"""
        main_log_path = Path(self.config.log_dir) / self.config.log_filename
        
        # 使用RotatingFileHandler实现日志轮转
        handler = logging.handlers.RotatingFileHandler(
            main_log_path,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        handler.setFormatter(self.formatter)
        handler.setLevel(getattr(logging, self.config.level.upper()))
        
        self.handlers['main'] = handler
    
    def _setup_console_handler(self):
        """设置控制台处理器"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(self.console_formatter)
        handler.setLevel(getattr(logging, self.config.console_level.upper()))
        
        self.handlers['console'] = handler
    
    def _setup_performance_handler(self):
        """设置性能监控处理器"""
        perf_log_path = Path(self.config.log_dir) / self.config.performance_filename
        
        handler = logging.handlers.RotatingFileHandler(
            perf_log_path,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        
        # 性能日志使用特殊格式
        perf_formatter = logging.Formatter(
            "%(asctime)s - PERF - %(message)s",
            datefmt=self.config.date_format
        )
        handler.setFormatter(perf_formatter)
        handler.setLevel(logging.INFO)
        
        self.handlers['performance'] = handler
    
    def _setup_error_handler(self):
        """设置错误处理器"""
        error_log_path = Path(self.config.log_dir) / self.config.error_filename
        
        handler = logging.handlers.RotatingFileHandler(
            error_log_path,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        
        # 错误日志使用详细格式
        error_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - ERROR - %(message)s\n%(pathname)s:%(lineno)d in %(funcName)s\n",
            datefmt=self.config.date_format
        )
        handler.setFormatter(error_formatter)
        handler.setLevel(logging.ERROR)
        
        self.handlers['error'] = handler
    
    def _setup_project_context_handler(self):
        """设置项目上下文处理器"""
        context_log_path = Path(self.config.log_dir) / self.config.project_context_filename
        
        handler = logging.handlers.RotatingFileHandler(
            context_log_path,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        
        # 项目上下文日志使用JSON格式
        context_formatter = logging.Formatter(
            "%(asctime)s - CONTEXT - %(message)s",
            datefmt=self.config.date_format
        )
        handler.setFormatter(context_formatter)
        handler.setLevel(logging.INFO)
        
        self.handlers['project_context'] = handler
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志记录器"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            
            # 添加所有处理器
            for handler in self.handlers.values():
                logger.addHandler(handler)
            
            # 防止重复日志
            logger.propagate = False
            
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """记录性能数据"""
        if not self.config.performance_enabled:
            return
        
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration': duration,
            'details': details or {}
        }
        
        self.performance_data.append(perf_data)
        
        # 如果操作时间超过阈值，记录到日志
        if duration > self.config.slow_query_threshold:
            perf_logger = logging.getLogger('performance')
            perf_logger.warning(f"Slow operation: {operation} took {duration:.3f}s - {json.dumps(details, ensure_ascii=False)}")
        
        # 保持性能数据大小
        if len(self.performance_data) > 1000:
            self.performance_data = self.performance_data[-500:]
    
    def log_project_context(self, context_type: str, context_data: Dict[str, Any]):
        """记录项目上下文信息"""
        if not self.config.project_context_enabled:
            return
        
        context_logger = logging.getLogger('project_context')
        context_message = json.dumps({
            'type': context_type,
            'timestamp': datetime.now().isoformat(),
            'data': context_data
        }, ensure_ascii=False)
        
        context_logger.info(context_message)
    
    def log_error_with_context(self, logger_name: str, error: Exception, context: Dict[str, Any] = None):
        """记录错误及其上下文"""
        self.error_count += 1
        
        logger = self.get_logger(logger_name)
        error_msg = f"Error: {str(error)}"
        
        if context:
            error_msg += f" | Context: {json.dumps(context, ensure_ascii=False)}"
        
        if self.config.error_detail_enabled:
            error_msg += f" | Traceback: {traceback.format_exc()}"
        
        logger.error(error_msg)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        if not self.performance_data:
            return {}
        
        durations = [item['duration'] for item in self.performance_data]
        operations = {}
        
        for item in self.performance_data:
            op = item['operation']
            if op not in operations:
                operations[op] = []
            operations[op].append(item['duration'])
        
        stats = {
            'total_operations': len(self.performance_data),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'slow_operations': len([d for d in durations if d > self.config.slow_query_threshold]),
            'operations_breakdown': {}
        }
        
        for op, times in operations.items():
            stats['operations_breakdown'][op] = {
                'count': len(times),
                'avg_duration': sum(times) / len(times),
                'max_duration': max(times),
                'min_duration': min(times)
            }
        
        return stats
    
    def get_log_summary(self) -> Dict[str, Any]:
        """获取日志摘要"""
        log_files = {}
        log_dir = Path(self.config.log_dir)
        
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                try:
                    stat = log_file.stat()
                    log_files[log_file.name] = {
                        'size': stat.st_size,
                        'size_mb': stat.st_size / (1024 * 1024),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'lines': sum(1 for _ in open(log_file, 'r', encoding='utf-8', errors='ignore'))
                    }
                except Exception as e:
                    log_files[log_file.name] = {'error': str(e)}
        
        return {
            'log_directory': str(log_dir.absolute()),
            'log_files': log_files,
            'total_errors': self.error_count,
            'total_warnings': self.warning_count,
            'performance_stats': self.get_performance_stats()
        }
    
    def cleanup_old_logs(self, days: int = 30):
        """清理旧日志文件"""
        log_dir = Path(self.config.log_dir)
        if not log_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_files = []
        
        for log_file in log_dir.glob("*.log.*"):  # 备份日志文件
            try:
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
                    cleaned_files.append(str(log_file))
            except Exception as e:
                self.get_logger('cleanup').warning(f"Failed to clean up {log_file}: {e}")
        
        if cleaned_files:
            self.get_logger('cleanup').info(f"Cleaned up {len(cleaned_files)} old log files")
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新日志配置"""
        for key, value in new_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # 重新设置日志系统
        self._setup_logging()
        
        # 重新配置现有的日志记录器
        for logger in self.loggers.values():
            logger.handlers.clear()
            for handler in self.handlers.values():
                logger.addHandler(handler)

# 便利函数
_manager = None

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    global _manager
    if _manager is None:
        _manager = LoggerManager()
    return _manager.get_logger(name)

@contextmanager
def log_performance(operation: str, logger_name: str = 'performance', **context):
    """性能监控上下文管理器"""
    logger = get_logger(logger_name)
    start_time = time.time()
    
    try:
        logger.info(f"Starting operation: {operation}")
        yield
        duration = time.time() - start_time
        _manager.log_performance(operation, duration, context)
        logger.info(f"Completed operation: {operation} in {duration:.3f}s")
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Failed operation: {operation} after {duration:.3f}s - {str(e)}")
        _manager.log_error_with_context(logger_name, e, {
            'operation': operation,
            'duration': duration,
            **context
        })
        raise

def log_project_context(context_type: str, context_data: Dict[str, Any]):
    """记录项目上下文"""
    global _manager
    if _manager is None:
        _manager = LoggerManager()
    _manager.log_project_context(context_type, context_data)

def get_log_summary() -> Dict[str, Any]:
    """获取日志摘要"""
    global _manager
    if _manager is None:
        _manager = LoggerManager()
    return _manager.get_log_summary()

def cleanup_logs(days: int = 30):
    """清理旧日志"""
    global _manager
    if _manager is None:
        _manager = LoggerManager()
    _manager.cleanup_old_logs(days)

def configure_logging(config: Dict[str, Any]):
    """配置日志系统"""
    global _manager
    if _manager is None:
        _manager = LoggerManager()
    _manager.update_config(config)

# 替代print函数的日志记录器
def log_print(message: str, level: str = "INFO", logger_name: str = "main"):
    """替代print函数的日志记录"""
    logger = get_logger(logger_name)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message)

# 初始化日志系统
def init_logging(config: Optional[Dict[str, Any]] = None):
    """初始化日志系统"""
    global _manager
    if _manager is None:
        _manager = LoggerManager()
    
    if config:
        _manager.update_config(config)
    
    # 记录初始化信息
    logger = _manager.get_logger('system')
    logger.info("Interactive Feedback MCP 日志系统已初始化")
    logger.info(f"日志目录: {_manager.config.log_dir}")
    logger.info(f"日志级别: {_manager.config.level}")
    
    return _manager

if __name__ == "__main__":
    # 测试日志系统
    init_logging()
    
    logger = get_logger('test')
    logger.info("这是一个测试信息")
    logger.warning("这是一个测试警告")
    logger.error("这是一个测试错误")
    
    # 测试性能监控
    with log_performance("test_operation", "test"):
        import time
        time.sleep(0.1)
    
    # 测试项目上下文
    log_project_context("test_context", {
        "project": "interactive-feedback-mcp",
        "version": "1.0.0",
        "operation": "test"
    })
    
    # 打印日志摘要
    print(json.dumps(get_log_summary(), indent=2, ensure_ascii=False)) 