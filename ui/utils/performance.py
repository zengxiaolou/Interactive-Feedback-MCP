# Performance Optimization Utilities
# 性能优化工具模块

import time
import psutil
import os
from typing import Dict, Any
from PySide6.QtCore import QTimer, QObject, Signal

class PerformanceMonitor(QObject):
    """性能监控器 - 实现PRD文档中的性能要求"""
    
    # 性能指标信号
    performance_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self.process = psutil.Process(os.getpid())
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_metrics)
        self.metrics = {}
        
    def start_monitoring(self, interval_ms: int = 1000):
        """开始性能监控"""
        self.timer.start(interval_ms)
        
    def stop_monitoring(self):
        """停止性能监控"""
        self.timer.stop()
        
    def _update_metrics(self):
        """更新性能指标"""
        try:
            # 内存使用情况
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # CPU使用率
            cpu_percent = self.process.cpu_percent()
            
            # 运行时间
            runtime = time.time() - self.start_time
            
            # 线程数
            thread_count = self.process.num_threads()
            
            self.metrics = {
                'memory_mb': round(memory_mb, 2),
                'cpu_percent': round(cpu_percent, 2),
                'runtime_seconds': round(runtime, 2),
                'thread_count': thread_count,
                'startup_time': self.get_startup_time()
            }
            
            self.performance_updated.emit(self.metrics)
            
        except Exception as e:
            print(f"Performance monitoring error: {e}")
    
    def get_startup_time(self) -> float:
        """获取启动时间"""
        return round(time.time() - self.start_time, 2)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前性能指标"""
        return self.metrics.copy()
    
    def check_performance_requirements(self) -> Dict[str, bool]:
        """检查是否满足PRD文档中的性能要求"""
        requirements = {
            'startup_time_ok': self.get_startup_time() < 2.0,  # < 2秒
            'memory_usage_ok': self.metrics.get('memory_mb', 0) < 100,  # < 100MB
            'cpu_usage_ok': self.metrics.get('cpu_percent', 0) < 5,  # < 5% (空闲状态)
        }
        return requirements

class ResponseTimeTracker:
    """响应时间跟踪器 - 监控UI响应速度"""
    
    def __init__(self):
        self.response_times = []
        self.max_records = 100  # 保留最近100次记录
        
    def start_timing(self) -> float:
        """开始计时"""
        return time.time()
    
    def end_timing(self, start_time: float, operation: str = "unknown") -> float:
        """结束计时并记录"""
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        self.response_times.append({
            'operation': operation,
            'time_ms': response_time,
            'timestamp': time.time()
        })
        
        # 保持记录数量限制
        if len(self.response_times) > self.max_records:
            self.response_times.pop(0)
            
        return response_time
    
    def get_average_response_time(self) -> float:
        """获取平均响应时间"""
        if not self.response_times:
            return 0.0
        return sum(r['time_ms'] for r in self.response_times) / len(self.response_times)
    
    def check_response_requirement(self) -> bool:
        """检查是否满足响应时间要求 (< 100ms)"""
        avg_time = self.get_average_response_time()
        return avg_time < 100.0
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        if not self.response_times:
            return {'status': 'no_data'}
            
        times = [r['time_ms'] for r in self.response_times]
        return {
            'average_ms': round(self.get_average_response_time(), 2),
            'min_ms': round(min(times), 2),
            'max_ms': round(max(times), 2),
            'total_operations': len(self.response_times),
            'meets_requirement': self.check_response_requirement()
        }

# 全局性能监控实例
global_performance_monitor = PerformanceMonitor()
global_response_tracker = ResponseTimeTracker() 