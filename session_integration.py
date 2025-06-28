#!/usr/bin/env python3
"""
会话指标收集系统与Interactive Feedback MCP集成脚本
将指标收集无缝集成到现有的MCP服务器中
"""

import json
import os
from typing import Dict, Any, Optional
from session_metrics_collector import SessionMetricsCollector, SessionAnalyzer

class IntegratedSessionTracker:
    """集成会话追踪器"""
    
    def __init__(self):
        self.collector = SessionMetricsCollector()
        self.analyzer = SessionAnalyzer()
        self.current_project_info = None
        self.auto_tracking_enabled = True
        
    def start_tracking_for_project(self, project_path: str, project_name: str, git_branch: str = "main"):
        """为指定项目开始追踪"""
        self.current_project_info = {
            "project_path": project_path,
            "project_name": project_name,
            "git_branch": git_branch
        }
        
        if self.auto_tracking_enabled:
            self.collector.start_session(project_path, project_name, git_branch)
            print(f"🎯 已启动项目 {project_name} 的会话追踪")
    
    def record_interactive_feedback_call(self, message: str, category: str = "general", 
                                       priority: int = 3, **kwargs):
        """记录Interactive Feedback调用"""
        if not self.auto_tracking_enabled:
            return
            
        # 自动启动追踪（如果还没有启动的话）
        if not self.collector.current_session and self.current_project_info:
            self.collector.start_session(
                self.current_project_info["project_path"],
                self.current_project_info["project_name"],
                self.current_project_info["git_branch"]
            )
        
        # 记录Interactive Feedback调用
        self.collector.record_interactive_feedback_call(category, priority)
        
        # 分析消息内容（检测用户意图）
        message_length = len(message)
        if message_length > 1000:
            interaction_type = "complex_query"
        elif any(keyword in message.lower() for keyword in ['help', 'how', 'what', 'why']):
            interaction_type = "question"
        elif any(keyword in message.lower() for keyword in ['fix', 'bug', 'error', 'problem']):
            interaction_type = "issue_report"
        elif any(keyword in message.lower() for keyword in ['create', 'add', 'build', 'make']):
            interaction_type = "feature_request"
        else:
            interaction_type = "general"
        
        # 记录用户交互
        self.collector.record_user_message(message, interaction_type)
        
        # 检测项目切换
        if kwargs.get('project_path') and kwargs['project_path'] != self.current_project_info.get('project_path'):
            self._handle_project_switch(kwargs['project_path'], kwargs.get('project_name', 'unknown'))
    
    def record_ai_response_with_tools(self, tool_calls: list):
        """记录AI回复和工具调用"""
        if not self.auto_tracking_enabled or not self.collector.current_session:
            return
            
        # 构建工具调用列表
        tool_names = []
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                tool_names.append(tool_call.get('function', {}).get('name', 'unknown'))
            elif hasattr(tool_call, 'function'):
                tool_names.append(tool_call.function.name)
            else:
                tool_names.append(str(tool_call))
        
        # 模拟AI回复（实际中可以传入真实的回复文本）
        response_text = f"已执行 {len(tool_names)} 个工具调用"
        self.collector.record_ai_response(response_text, tool_names)
    
    def analyze_current_session_quality(self) -> Dict[str, Any]:
        """分析当前会话质量"""
        if not self.collector.current_session:
            return {"error": "没有活动会话"}
        
        metrics = self.collector.get_current_metrics()
        if not metrics:
            return {"error": "无法获取会话指标"}
        
        # 计算质量指标
        quality_score = 0
        quality_factors = []
        
        # 交互频率评估
        if metrics['duration_seconds'] > 0:
            interaction_rate = (metrics['user_messages_count'] + metrics['ai_responses_count']) / (metrics['duration_seconds'] / 60)  # 每分钟交互次数
            if interaction_rate > 2:
                quality_score += 20
                quality_factors.append("高交互频率")
            elif interaction_rate > 1:
                quality_score += 10
                quality_factors.append("适中交互频率")
        
        # Interactive Feedback使用评估
        if metrics['interactive_feedback_calls'] > 0:
            feedback_ratio = metrics['interactive_feedback_calls'] / max(metrics['ai_responses_count'], 1)
            if feedback_ratio > 0.8:
                quality_score += 30
                quality_factors.append("高频反馈调用")
            elif feedback_ratio > 0.5:
                quality_score += 20
                quality_factors.append("适量反馈调用")
            else:
                quality_score += 10
                quality_factors.append("低频反馈调用")
        
        # 工具使用评估
        if metrics['tool_calls_count'] > 0:
            quality_score += 15
            quality_factors.append("工具调用活跃")
        
        # 内容丰富度评估
        avg_message_length = metrics['total_user_chars'] / max(metrics['user_messages_count'], 1)
        if avg_message_length > 100:
            quality_score += 15
            quality_factors.append("内容详细")
        elif avg_message_length > 50:
            quality_score += 10
            quality_factors.append("内容适中")
        
        # 风险因素评估
        risk_count = len(metrics.get('risk_indicators', []))
        if risk_count > 3:
            quality_score -= 20
            quality_factors.append("高风险模式")
        elif risk_count > 1:
            quality_score -= 10
            quality_factors.append("中等风险")
        
        # 确定质量等级
        if quality_score >= 70:
            quality_level = "优秀"
        elif quality_score >= 50:
            quality_level = "良好"
        elif quality_score >= 30:
            quality_level = "一般"
        else:
            quality_level = "需改进"
        
        return {
            "session_id": metrics['session_id'][:8],
            "duration_minutes": round(metrics['duration_seconds'] / 60, 1),
            "quality_score": quality_score,
            "quality_level": quality_level,
            "quality_factors": quality_factors,
            "interaction_summary": {
                "user_messages": metrics['user_messages_count'],
                "ai_responses": metrics['ai_responses_count'],
                "tool_calls": metrics['tool_calls_count'],
                "feedback_calls": metrics['interactive_feedback_calls']
            },
            "risk_indicators": metrics.get('risk_indicators', []),
            "categories": metrics.get('session_categories', [])
        }
    
    def get_project_analysis_report(self, project_name: str) -> Dict[str, Any]:
        """获取项目分析报告"""
        return self.analyzer.analyze_project_sessions(project_name)
    
    def _handle_project_switch(self, new_project_path: str, new_project_name: str):
        """处理项目切换"""
        if self.collector.current_session:
            self.collector.end_session("project_switched")
        
        self.current_project_info = {
            "project_path": new_project_path,
            "project_name": new_project_name,
            "git_branch": "main"  # 默认分支
        }
        
        self.collector.start_session(new_project_path, new_project_name, "main")
        print(f"🔄 已切换到项目 {new_project_name}")
    
    def end_tracking(self, reason: str = "user_ended"):
        """结束追踪"""
        if self.collector.current_session:
            self.collector.end_session(reason)
            print(f"📊 会话追踪已结束: {reason}")
    
    def toggle_auto_tracking(self, enabled: bool = True):
        """切换自动追踪模式"""
        self.auto_tracking_enabled = enabled
        status = "启用" if enabled else "禁用"
        print(f"🎯 自动追踪已{status}")

# 全局集成追踪器实例
integrated_tracker = IntegratedSessionTracker()

def setup_integrated_tracking(project_path: str, project_name: str, git_branch: str = "main"):
    """设置集成追踪"""
    integrated_tracker.start_tracking_for_project(project_path, project_name, git_branch)

def track_interactive_feedback(message: str, category: str = "general", priority: int = 3, **kwargs):
    """追踪Interactive Feedback调用"""
    integrated_tracker.record_interactive_feedback_call(message, category, priority, **kwargs)

def track_tool_execution(tool_calls: list):
    """追踪工具执行"""
    integrated_tracker.record_ai_response_with_tools(tool_calls)

def get_session_quality_report() -> Dict[str, Any]:
    """获取会话质量报告"""
    return integrated_tracker.analyze_current_session_quality()

def get_project_report(project_name: str) -> Dict[str, Any]:
    """获取项目报告"""
    return integrated_tracker.get_project_analysis_report(project_name)

def end_tracking_session(reason: str = "user_ended"):
    """结束追踪会话"""
    integrated_tracker.end_tracking(reason)

# MCP服务器集成装饰器
def with_session_tracking(func):
    """装饰器：为MCP工具函数添加会话追踪"""
    def wrapper(*args, **kwargs):
        # 在工具调用前记录
        tool_name = func.__name__
        
        # 执行原始函数
        result = func(*args, **kwargs)
        
        # 在工具调用后记录
        track_tool_execution([tool_name])
        
        return result
    
    return wrapper

if __name__ == "__main__":
    # 演示集成追踪
    print("🎯 集成会话追踪系统演示")
    
    # 设置项目追踪
    setup_integrated_tracking(
        "/Users/ruler/Documents/study/interactive-feedback-mcp",
        "interactive-feedback-mcp",
        "main"
    )
    
    # 模拟Interactive Feedback调用
    track_interactive_feedback(
        "帮我修复图片粘贴功能的bug",
        category="bug",
        priority=4
    )
    
    # 模拟工具调用
    track_tool_execution(["read_file", "search_replace", "run_terminal_cmd"])
    
    # 获取质量报告
    quality_report = get_session_quality_report()
    print(f"\n📊 会话质量报告:")
    print(f"质量等级: {quality_report.get('quality_level', 'unknown')}")
    print(f"质量评分: {quality_report.get('quality_score', 0)}")
    print(f"持续时长: {quality_report.get('duration_minutes', 0)}分钟")
    
    # 结束追踪
    end_tracking_session("demo_completed")
    
    print("✅ 演示完成") 