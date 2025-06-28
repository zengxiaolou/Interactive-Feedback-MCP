#!/usr/bin/env python3
"""
会话数据分析工具 - Session Analysis Tool
命令行工具，用于分析项目会话数据和生成报告
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from session_metrics_collector import SessionAnalyzer
from session_integration import get_project_report

class SessionAnalysisTool:
    """会话分析工具"""
    
    def __init__(self, log_dir: str = "logs"):
        self.analyzer = SessionAnalyzer(log_dir)
        self.log_dir = Path(log_dir)
    
    def list_projects(self):
        """列出所有有记录的项目"""
        projects = self.analyzer.get_all_projects()
        
        if not projects:
            print("📋 没有找到任何项目记录")
            return
        
        print("📋 已记录的项目列表:")
        print("=" * 50)
        
        for i, project in enumerate(projects, 1):
            project_dir = self.log_dir / f"project_{project}"
            summary_file = project_dir / "sessions_summary.jsonl"
            
            if summary_file.exists():
                # 统计会话数量
                session_count = 0
                with open(summary_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            session_count += 1
                
                print(f"{i:2d}. {project} ({session_count} 会话)")
            else:
                print(f"{i:2d}. {project} (无会话记录)")
    
    def analyze_project(self, project_name: str, detailed: bool = False):
        """分析指定项目"""
        print(f"📊 分析项目: {project_name}")
        print("=" * 50)
        
        report = get_project_report(project_name)
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        # 基础统计
        print("📈 基础统计:")
        print(f"  总会话数: {report['total_sessions']}")
        print(f"  自动终止会话: {report['auto_terminated_sessions']}")
        print(f"  自动终止率: {report['auto_termination_rate']:.1%}")
        print(f"  平均会话时长: {report['average_duration_seconds']:.1f} 秒")
        print(f"  平均用户消息数: {report['average_user_messages']:.1f}")
        print(f"  平均工具调用数: {report['average_tool_calls']:.1f}")
        
        # 风险分析
        print("\n⚠️ 风险分析:")
        print(f"  高风险会话: {report['high_risk_sessions']}")
        print(f"  高风险率: {report['high_risk_rate']:.1%}")
        
        # 类别分布
        print("\n📊 类别分布:")
        categories = report['category_distribution']
        if categories:
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count}")
        else:
            print("  无类别数据")
        
        # 详细信息
        if detailed:
            print("\n📋 最近会话:")
            for session in report['recent_sessions']:
                start_time = datetime.fromisoformat(session['start_time']).strftime("%m-%d %H:%M")
                duration = session.get('duration_seconds', 0)
                status = "🔴 自动终止" if session.get('auto_terminated', False) else "🟢 正常结束"
                print(f"  {start_time} | {duration:.0f}s | {status} | {session.get('end_reason', 'unknown')}")
    
    def compare_projects(self, project_names: List[str]):
        """对比多个项目"""
        print("📊 项目对比分析")
        print("=" * 60)
        
        reports = {}
        for project in project_names:
            report = get_project_report(project)
            if "error" not in report:
                reports[project] = report
        
        if not reports:
            print("❌ 没有找到有效的项目数据")
            return
        
        # 对比表格
        print(f"{'项目名称':<20} {'会话数':<8} {'自动终止率':<10} {'平均时长(s)':<12} {'高风险率':<10}")
        print("-" * 60)
        
        for project, report in reports.items():
            print(f"{project:<20} {report['total_sessions']:<8} "
                  f"{report['auto_termination_rate']:.1%:<10} "
                  f"{report['average_duration_seconds']:<12.1f} "
                  f"{report['high_risk_rate']:.1%:<10}")
    
    def find_problematic_patterns(self, project_name: str):
        """寻找问题模式"""
        print(f"🔍 分析项目 {project_name} 的问题模式")
        print("=" * 50)
        
        project_dir = self.log_dir / f"project_{project_name}"
        if not project_dir.exists():
            print(f"❌ 项目 {project_name} 的日志不存在")
            return
        
        # 分析事件日志
        event_log_file = project_dir / "session_events.jsonl"
        if event_log_file.exists():
            interruptions = []
            feedback_calls = []
            
            with open(event_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        if event['event_type'] == 'session_interrupted':
                            interruptions.append(event)
                        elif event['event_type'] == 'interactive_feedback_called':
                            feedback_calls.append(event)
            
            print(f"🚨 会话中断事件: {len(interruptions)}")
            for interruption in interruptions[-5:]:  # 显示最近5次
                timestamp = datetime.fromisoformat(interruption['timestamp']).strftime("%m-%d %H:%M")
                reason = interruption['data'].get('reason', 'unknown')
                print(f"  {timestamp} - {reason}")
            
            print(f"\n📞 Interactive Feedback调用: {len(feedback_calls)}")
            category_stats = {}
            for call in feedback_calls:
                category = call['data'].get('category', 'unknown')
                category_stats[category] = category_stats.get(category, 0) + 1
            
            for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count}")
        
        # 分析完整会话文件
        auto_terminated_sessions = []
        for session_file in project_dir.glob("session_*.json"):
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                if session_data.get('auto_terminated', False):
                    auto_terminated_sessions.append(session_data)
        
        if auto_terminated_sessions:
            print(f"\n💥 自动终止会话分析 ({len(auto_terminated_sessions)} 个):")
            
            # 统计终止原因
            end_reasons = {}
            for session in auto_terminated_sessions:
                reason = session.get('end_reason', 'unknown')
                end_reasons[reason] = end_reasons.get(reason, 0) + 1
            
            print("  终止原因统计:")
            for reason, count in sorted(end_reasons.items(), key=lambda x: x[1], reverse=True):
                print(f"    {reason}: {count}")
            
            # 分析风险指标
            all_risk_indicators = []
            for session in auto_terminated_sessions:
                all_risk_indicators.extend(session.get('risk_indicators', []))
            
            if all_risk_indicators:
                risk_stats = {}
                for indicator in all_risk_indicators:
                    risk_stats[indicator] = risk_stats.get(indicator, 0) + 1
                
                print("  常见风险指标:")
                for indicator, count in sorted(risk_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"    {indicator}: {count}")
    
    def generate_summary_report(self):
        """生成总体摘要报告"""
        print("📊 总体摘要报告")
        print("=" * 50)
        
        projects = self.analyzer.get_all_projects()
        if not projects:
            print("❌ 没有找到任何项目数据")
            return
        
        total_sessions = 0
        total_auto_terminated = 0
        total_duration = 0
        all_categories = []
        
        print("📋 项目概览:")
        for project in projects:
            report = get_project_report(project)
            if "error" not in report:
                sessions = report['total_sessions']
                auto_terminated = report['auto_terminated_sessions']
                avg_duration = report['average_duration_seconds']
                
                total_sessions += sessions
                total_auto_terminated += auto_terminated
                total_duration += avg_duration * sessions
                all_categories.extend(report['category_distribution'].keys())
                
                print(f"  {project}: {sessions} 会话, {auto_terminated} 自动终止")
        
        if total_sessions > 0:
            print(f"\n📈 总体统计:")
            print(f"  总会话数: {total_sessions}")
            print(f"  总自动终止数: {total_auto_terminated}")
            print(f"  全局自动终止率: {total_auto_terminated/total_sessions:.1%}")
            print(f"  平均会话时长: {total_duration/total_sessions:.1f} 秒")
            
            # 活跃类别
            unique_categories = set(all_categories)
            print(f"  活跃类别数: {len(unique_categories)}")
            print(f"  类别列表: {', '.join(sorted(unique_categories))}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="会话数据分析工具")
    parser.add_argument("command", choices=["list", "analyze", "compare", "patterns", "summary"],
                       help="分析命令")
    parser.add_argument("--project", "-p", help="项目名称")
    parser.add_argument("--projects", "-ps", nargs="+", help="多个项目名称（用于对比）")
    parser.add_argument("--detailed", "-d", action="store_true", help="详细分析")
    parser.add_argument("--log-dir", default="logs", help="日志目录路径")
    
    args = parser.parse_args()
    
    tool = SessionAnalysisTool(args.log_dir)
    
    try:
        if args.command == "list":
            tool.list_projects()
        
        elif args.command == "analyze":
            if not args.project:
                print("❌ 请指定项目名称 (--project)")
                sys.exit(1)
            tool.analyze_project(args.project, args.detailed)
        
        elif args.command == "compare":
            if not args.projects or len(args.projects) < 2:
                print("❌ 请指定至少两个项目名称 (--projects)")
                sys.exit(1)
            tool.compare_projects(args.projects)
        
        elif args.command == "patterns":
            if not args.project:
                print("❌ 请指定项目名称 (--project)")
                sys.exit(1)
            tool.find_problematic_patterns(args.project)
        
        elif args.command == "summary":
            tool.generate_summary_report()
            
    except KeyboardInterrupt:
        print("\n👋 分析已取消")
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 