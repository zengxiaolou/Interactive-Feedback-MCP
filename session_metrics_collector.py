#!/usr/bin/env python3
"""
会话指标收集器 - Session Metrics Collector
轻量级会话数据收集系统，支持按项目分类的日志记录
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import uuid

@dataclass
class SessionMetrics:
    """会话指标数据类"""
    session_id: str
    project_path: str
    project_name: str
    git_branch: str
    start_time: str
    last_activity_time: str
    duration_seconds: float
    
    # 交互指标
    user_messages_count: int = 0
    ai_responses_count: int = 0
    tool_calls_count: int = 0
    interactive_feedback_calls: int = 0
    
    # 内容指标
    total_user_chars: int = 0
    total_ai_chars: int = 0
    code_blocks_count: int = 0
    images_pasted_count: int = 0
    files_operated_count: int = 0
    
    # 模式指标
    interaction_types: List[str] = None
    session_categories: List[str] = None
    risk_indicators: List[str] = None
    
    # 结束指标
    session_ended: bool = False
    end_reason: str = ""
    auto_terminated: bool = False
    
    def __post_init__(self):
        if self.interaction_types is None:
            self.interaction_types = []
        if self.session_categories is None:
            self.session_categories = []
        if self.risk_indicators is None:
            self.risk_indicators = []

class SessionMetricsCollector:
    """会话指标收集器"""
    
    def __init__(self, base_log_dir: str = "logs"):
        self.base_log_dir = Path(base_log_dir)
        self.current_session: Optional[SessionMetrics] = None
        self.session_start_time = None
        
        # 确保日志目录存在
        self.base_log_dir.mkdir(exist_ok=True)
        
        # 风险模式识别
        self.risk_patterns = {
            'completion_language': [
                '任务完成', '修复完成', '问题解决', '到此为止',
                '就这些了', '没有其他', '已经处理完毕', '都搞定了'
            ],
            'ending_phrases': [
                '如果还有问题', '如果需要帮助', '如果有其他需求',
                '祝您使用愉快', '希望这能帮到您'
            ],
            'technical_completion': [
                '测试通过', '代码提交', '功能正常', '部署成功',
                '验证完成', '检查无误'
            ]
        }
        
    def start_session(self, project_path: str, project_name: str, git_branch: str = "main"):
        """开始新的会话监控"""
        if self.current_session:
            self.end_session("new_session_started")
            
        session_id = self._generate_session_id(project_path)
        now = datetime.now().isoformat()
        
        self.current_session = SessionMetrics(
            session_id=session_id,
            project_path=project_path,
            project_name=project_name,
            git_branch=git_branch,
            start_time=now,
            last_activity_time=now,
            duration_seconds=0.0
        )
        
        self.session_start_time = time.time()
        self._log_session_event("session_started", {"session_id": session_id})
        
        print(f"📊 会话监控开始: {session_id[:8]}... 项目: {project_name}")
        
    def record_user_message(self, message: str, message_type: str = "text"):
        """记录用户消息"""
        if not self.current_session:
            return
            
        self.current_session.user_messages_count += 1
        self.current_session.total_user_chars += len(message)
        
        # 检测内容类型
        if '```' in message:
            self.current_session.code_blocks_count += 1
            
        if message_type == "image":
            self.current_session.images_pasted_count += 1
            
        # 更新交互类型
        if message_type not in self.current_session.interaction_types:
            self.current_session.interaction_types.append(message_type)
            
        self._update_activity_time()
        
    def record_ai_response(self, response: str, tool_calls: List[str] = None):
        """记录AI回复"""
        if not self.current_session:
            return
            
        self.current_session.ai_responses_count += 1
        self.current_session.total_ai_chars += len(response)
        
        # 记录工具调用
        if tool_calls:
            self.current_session.tool_calls_count += len(tool_calls)
            for tool in tool_calls:
                if tool.startswith('edit_file') or tool.startswith('search_replace'):
                    self.current_session.files_operated_count += 1
                    
        # 检测风险模式
        self._analyze_risk_patterns(response)
        
        self._update_activity_time()
        
    def record_interactive_feedback_call(self, category: str, priority: int):
        """记录Interactive Feedback调用"""
        if not self.current_session:
            return
            
        self.current_session.interactive_feedback_calls += 1
        
        # 记录会话类别
        if category not in self.current_session.session_categories:
            self.current_session.session_categories.append(category)
            
        self._update_activity_time()
        self._log_session_event("interactive_feedback_called", {
            "category": category,
            "priority": priority,
            "call_count": self.current_session.interactive_feedback_calls
        })
        
    def record_session_interruption(self, reason: str = "unknown"):
        """记录会话中断"""
        if not self.current_session:
            return
            
        self.current_session.risk_indicators.append(f"interruption_{reason}")
        self._log_session_event("session_interrupted", {"reason": reason})
        
    def end_session(self, reason: str = "user_ended"):
        """结束会话监控"""
        if not self.current_session:
            return
            
        self.current_session.session_ended = True
        self.current_session.end_reason = reason
        self.current_session.auto_terminated = reason.startswith("auto_")
        
        # 计算总时长
        if self.session_start_time:
            self.current_session.duration_seconds = time.time() - self.session_start_time
            
        # 保存会话数据
        self._save_session_data()
        
        print(f"📊 会话监控结束: {reason}, 时长: {self.current_session.duration_seconds:.1f}秒")
        
        self.current_session = None
        self.session_start_time = None
        
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """获取当前会话指标"""
        if not self.current_session:
            return None
            
        # 更新持续时长
        if self.session_start_time:
            self.current_session.duration_seconds = time.time() - self.session_start_time
            
        return asdict(self.current_session)
        
    def _generate_session_id(self, project_path: str) -> str:
        """生成会话ID"""
        timestamp = datetime.now().isoformat()
        unique_str = f"{project_path}_{timestamp}_{uuid.uuid4().hex[:8]}"
        return hashlib.md5(unique_str.encode()).hexdigest()
        
    def _update_activity_time(self):
        """更新最后活动时间"""
        if self.current_session:
            self.current_session.last_activity_time = datetime.now().isoformat()
            
    def _analyze_risk_patterns(self, text: str):
        """分析风险模式"""
        if not self.current_session:
            return
            
        text_lower = text.lower()
        
        for pattern_type, patterns in self.risk_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    risk_indicator = f"{pattern_type}_{pattern.replace(' ', '_')}"
                    if risk_indicator not in self.current_session.risk_indicators:
                        self.current_session.risk_indicators.append(risk_indicator)
                        
    def _get_project_log_dir(self) -> Path:
        """获取项目专用日志目录"""
        if not self.current_session:
            return self.base_log_dir
            
        # 使用项目名称创建子目录
        project_log_dir = self.base_log_dir / f"project_{self.current_session.project_name}"
        project_log_dir.mkdir(exist_ok=True)
        return project_log_dir
        
    def _log_session_event(self, event_type: str, data: Dict[str, Any]):
        """记录会话事件"""
        if not self.current_session:
            return
            
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session.session_id,
            "project_name": self.current_session.project_name,
            "event_type": event_type,
            "data": data
        }
        
        # 写入项目专用的事件日志
        project_log_dir = self._get_project_log_dir()
        event_log_file = project_log_dir / "session_events.jsonl"
        
        with open(event_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
            
    def _save_session_data(self):
        """保存会话数据"""
        if not self.current_session:
            return
            
        project_log_dir = self._get_project_log_dir()
        
        # 保存完整会话数据
        session_file = project_log_dir / f"session_{self.current_session.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.current_session), f, ensure_ascii=False, indent=2)
            
        # 追加到会话摘要日志
        summary_file = project_log_dir / "sessions_summary.jsonl"
        summary_data = {
            "session_id": self.current_session.session_id,
            "start_time": self.current_session.start_time,
            "duration_seconds": self.current_session.duration_seconds,
            "user_messages": self.current_session.user_messages_count,
            "ai_responses": self.current_session.ai_responses_count,
            "tool_calls": self.current_session.tool_calls_count,
            "interactive_feedback_calls": self.current_session.interactive_feedback_calls,
            "categories": self.current_session.session_categories,
            "risk_indicators_count": len(self.current_session.risk_indicators),
            "auto_terminated": self.current_session.auto_terminated,
            "end_reason": self.current_session.end_reason
        }
        
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(summary_data, ensure_ascii=False) + '\n')

class SessionAnalyzer:
    """会话数据分析器"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        
    def analyze_project_sessions(self, project_name: str) -> Dict[str, Any]:
        """分析指定项目的会话数据"""
        project_log_dir = self.log_dir / f"project_{project_name}"
        
        if not project_log_dir.exists():
            return {"error": f"项目 {project_name} 的日志不存在"}
            
        summary_file = project_log_dir / "sessions_summary.jsonl"
        if not summary_file.exists():
            return {"error": f"项目 {project_name} 的摘要日志不存在"}
            
        sessions = []
        with open(summary_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    sessions.append(json.loads(line))
                    
        if not sessions:
            return {"error": "没有找到会话数据"}
            
        # 统计分析
        total_sessions = len(sessions)
        auto_terminated = sum(1 for s in sessions if s.get('auto_terminated', False))
        avg_duration = sum(s.get('duration_seconds', 0) for s in sessions) / total_sessions
        avg_messages = sum(s.get('user_messages', 0) for s in sessions) / total_sessions
        avg_tool_calls = sum(s.get('tool_calls', 0) for s in sessions) / total_sessions
        
        # 风险统计
        high_risk_sessions = sum(1 for s in sessions if s.get('risk_indicators_count', 0) > 3)
        
        # 类别统计
        all_categories = []
        for s in sessions:
            all_categories.extend(s.get('categories', []))
        category_counts = {}
        for cat in all_categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        return {
            "project_name": project_name,
            "analysis_time": datetime.now().isoformat(),
            "total_sessions": total_sessions,
            "auto_terminated_sessions": auto_terminated,
            "auto_termination_rate": auto_terminated / total_sessions if total_sessions > 0 else 0,
            "average_duration_seconds": avg_duration,
            "average_user_messages": avg_messages,
            "average_tool_calls": avg_tool_calls,
            "high_risk_sessions": high_risk_sessions,
            "high_risk_rate": high_risk_sessions / total_sessions if total_sessions > 0 else 0,
            "category_distribution": category_counts,
            "recent_sessions": sessions[-5:] if len(sessions) >= 5 else sessions
        }
        
    def get_all_projects(self) -> List[str]:
        """获取所有有日志记录的项目"""
        projects = []
        for item in self.log_dir.iterdir():
            if item.is_dir() and item.name.startswith("project_"):
                project_name = item.name[8:]  # 移除 "project_" 前缀
                projects.append(project_name)
        return projects

# 全局收集器实例
session_collector = SessionMetricsCollector()

def start_monitoring(project_path: str, project_name: str, git_branch: str = "main"):
    """开始监控会话"""
    session_collector.start_session(project_path, project_name, git_branch)
    
def record_user_interaction(message: str, message_type: str = "text"):
    """记录用户交互"""
    session_collector.record_user_message(message, message_type)
    
def record_ai_interaction(response: str, tool_calls: List[str] = None):
    """记录AI交互"""
    session_collector.record_ai_response(response, tool_calls or [])
    
def record_feedback_call(category: str, priority: int = 3):
    """记录Interactive Feedback调用"""
    session_collector.record_interactive_feedback_call(category, priority)
    
def end_monitoring(reason: str = "user_ended"):
    """结束监控"""
    session_collector.end_session(reason)
    
def get_current_metrics() -> Optional[Dict[str, Any]]:
    """获取当前指标"""
    return session_collector.get_current_metrics()

if __name__ == "__main__":
    # 测试示例
    print("📊 会话指标收集器测试")
    
    # 开始监控
    start_monitoring("/test/project", "test-project", "main")
    
    # 模拟交互
    record_user_interaction("帮我修复一个bug", "text")
    record_ai_interaction("我来帮你分析这个问题", ["read_file", "edit_file"])
    record_feedback_call("bug", 4)
    
    # 获取当前指标
    metrics = get_current_metrics()
    if metrics:
        print(f"当前会话时长: {metrics['duration_seconds']:.1f}秒")
        print(f"用户消息数: {metrics['user_messages_count']}")
        print(f"AI回复数: {metrics['ai_responses_count']}")
        print(f"工具调用数: {metrics['tool_calls_count']}")
    
    # 结束监控
    end_monitoring("test_completed")
    
    print("✅ 测试完成") 