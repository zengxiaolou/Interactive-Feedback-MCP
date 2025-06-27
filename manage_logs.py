#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive Feedback MCP - 日志管理工具
提供查看、清理、分析日志的命令行工具
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.utils.logging_system import (
    get_log_summary, cleanup_logs, configure_logging,
    init_logging, get_logger
)

def show_log_summary():
    """显示日志摘要"""
    print("📊 Interactive Feedback MCP - 日志系统摘要")
    print("=" * 60)
    
    try:
        summary = get_log_summary()
        
        print(f"📁 日志目录: {summary['log_directory']}")
        print(f"🔢 总错误数: {summary['total_errors']}")
        print(f"⚠️  总警告数: {summary['total_warnings']}")
        print()
        
        print("📋 日志文件:")
        for filename, info in summary['log_files'].items():
            if 'error' in info:
                print(f"  ❌ {filename}: {info['error']}")
            else:
                print(f"  📄 {filename}:")
                print(f"     大小: {info['size_mb']:.2f} MB ({info['size']} bytes)")
                print(f"     行数: {info['lines']}")
                print(f"     修改时间: {info['modified']}")
        
        print()
        
        # 性能统计
        perf_stats = summary.get('performance_stats', {})
        if perf_stats:
            print("⚡ 性能统计:")
            print(f"  总操作数: {perf_stats['total_operations']}")
            print(f"  平均耗时: {perf_stats['avg_duration']:.3f}s")
            print(f"  最大耗时: {perf_stats['max_duration']:.3f}s")
            print(f"  慢操作数: {perf_stats['slow_operations']}")
            
            if perf_stats.get('operations_breakdown'):
                print("  操作分解:")
                for op, stats in perf_stats['operations_breakdown'].items():
                    print(f"    {op}: {stats['count']}次, 平均{stats['avg_duration']:.3f}s")
        
    except Exception as e:
        print(f"❌ 获取日志摘要失败: {e}")

def cleanup_old_logs(days: int = 30):
    """清理旧日志"""
    print(f"🧹 清理 {days} 天前的日志文件...")
    try:
        cleanup_logs(days)
        print("✅ 日志清理完成")
    except Exception as e:
        print(f"❌ 日志清理失败: {e}")

def view_recent_logs(log_type: str = "main", lines: int = 50):
    """查看最近的日志"""
    log_dir = Path("logs")
    
    log_files = {
        "main": "interactive_feedback_mcp.log",
        "error": "errors.log", 
        "performance": "performance.log",
        "context": "project_context.log"
    }
    
    if log_type not in log_files:
        print(f"❌ 不支持的日志类型: {log_type}")
        print(f"支持的类型: {', '.join(log_files.keys())}")
        return
    
    log_file = log_dir / log_files[log_type]
    
    if not log_file.exists():
        print(f"❌ 日志文件不存在: {log_file}")
        return
    
    print(f"📖 查看最近 {lines} 行日志: {log_type}")
    print("=" * 60)
    
    try:
        # 使用tail命令查看最后几行
        if sys.platform.startswith('win'):
            # Windows没有tail命令，使用Python实现
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                for line in recent_lines:
                    print(line.rstrip())
        else:
            # Unix/Linux/macOS使用tail命令
            subprocess.run(['tail', '-n', str(lines), str(log_file)])
    except Exception as e:
        print(f"❌ 读取日志文件失败: {e}")

def search_logs(pattern: str, log_type: str = "main"):
    """搜索日志"""
    log_dir = Path("logs")
    
    log_files = {
        "main": "interactive_feedback_mcp.log",
        "error": "errors.log",
        "performance": "performance.log", 
        "context": "project_context.log",
        "all": "*.log"
    }
    
    if log_type not in log_files:
        print(f"❌ 不支持的日志类型: {log_type}")
        return
    
    print(f"🔍 在 {log_type} 日志中搜索: {pattern}")
    print("=" * 60)
    
    try:
        if log_type == "all":
            # 搜索所有日志文件
            for log_file in log_dir.glob("*.log"):
                print(f"\n📄 {log_file.name}:")
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern.lower() in line.lower():
                            print(f"  {line_num}: {line.rstrip()}")
        else:
            log_file = log_dir / log_files[log_type]
            if not log_file.exists():
                print(f"❌ 日志文件不存在: {log_file}")
                return
            
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                found = False
                for line_num, line in enumerate(f, 1):
                    if pattern.lower() in line.lower():
                        print(f"{line_num}: {line.rstrip()}")
                        found = True
                
                if not found:
                    print("❌ 未找到匹配的日志条目")
                    
    except Exception as e:
        print(f"❌ 搜索日志失败: {e}")

def analyze_errors():
    """分析错误日志"""
    log_dir = Path("logs")
    error_file = log_dir / "errors.log"
    
    if not error_file.exists():
        print("❌ 错误日志文件不存在")
        return
    
    print("🔍 错误日志分析")
    print("=" * 60)
    
    try:
        error_types = {}
        error_count = 0
        
        with open(error_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if ' - ERROR - ' in line:
                    error_count += 1
                    # 提取错误类型
                    try:
                        error_part = line.split(' - ERROR - ')[1]
                        if 'Error:' in error_part:
                            error_type = error_part.split('Error:')[1].split('|')[0].strip()
                        else:
                            error_type = error_part.split('|')[0].strip()[:50]
                        
                        error_types[error_type] = error_types.get(error_type, 0) + 1
                    except:
                        error_types['未分类错误'] = error_types.get('未分类错误', 0) + 1
        
        print(f"📊 总错误数: {error_count}")
        print("\n🏷️  错误类型分布:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {count:3d}x {error_type}")
            
    except Exception as e:
        print(f"❌ 分析错误日志失败: {e}")

def monitor_logs():
    """实时监控日志"""
    log_dir = Path("logs")
    main_log = log_dir / "interactive_feedback_mcp.log"
    
    if not main_log.exists():
        print("❌ 主日志文件不存在")
        return
    
    print("📺 实时监控日志 (按 Ctrl+C 退出)")
    print("=" * 60)
    
    try:
        if sys.platform.startswith('win'):
            print("⚠️ Windows系统不支持实时监控，请使用其他命令")
            return
        else:
            # 使用tail -f命令实时监控
            subprocess.run(['tail', '-f', str(main_log)])
    except KeyboardInterrupt:
        print("\n✅ 监控已停止")
    except Exception as e:
        print(f"❌ 监控日志失败: {e}")

def export_logs(output_file: str = None):
    """导出日志"""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"logs_export_{timestamp}.zip"
    
    print(f"📦 导出日志到: {output_file}")
    
    try:
        import zipfile
        log_dir = Path("logs")
        
        if not log_dir.exists():
            print("❌ 日志目录不存在")
            return
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for log_file in log_dir.glob("*.log*"):
                zip_file.write(log_file, log_file.name)
                print(f"  ✅ 已添加: {log_file.name}")
        
        print(f"✅ 日志导出完成: {output_file}")
        
    except Exception as e:
        print(f"❌ 导出日志失败: {e}")

def configure_log_level(level: str):
    """配置日志级别"""
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if level.upper() not in valid_levels:
        print(f"❌ 无效的日志级别: {level}")
        print(f"支持的级别: {', '.join(valid_levels)}")
        return
    
    print(f"⚙️ 设置日志级别为: {level.upper()}")
    
    try:
        configure_logging({'level': level.upper()})
        print("✅ 日志级别设置成功")
    except Exception as e:
        print(f"❌ 设置日志级别失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Interactive Feedback MCP 日志管理工具')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 摘要命令
    subparsers.add_parser('summary', help='显示日志摘要')
    
    # 清理命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧日志')
    cleanup_parser.add_argument('--days', type=int, default=30, help='清理多少天前的日志 (默认: 30)')
    
    # 查看命令
    view_parser = subparsers.add_parser('view', help='查看最近的日志')
    view_parser.add_argument('--type', choices=['main', 'error', 'performance', 'context'], 
                           default='main', help='日志类型 (默认: main)')
    view_parser.add_argument('--lines', type=int, default=50, help='显示行数 (默认: 50)')
    
    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索日志')
    search_parser.add_argument('pattern', help='搜索模式')
    search_parser.add_argument('--type', choices=['main', 'error', 'performance', 'context', 'all'],
                             default='main', help='日志类型 (默认: main)')
    
    # 分析命令
    subparsers.add_parser('analyze', help='分析错误日志')
    
    # 监控命令
    subparsers.add_parser('monitor', help='实时监控日志')
    
    # 导出命令
    export_parser = subparsers.add_parser('export', help='导出日志')
    export_parser.add_argument('--output', help='输出文件名')
    
    # 配置命令
    config_parser = subparsers.add_parser('config', help='配置日志系统')
    config_parser.add_argument('--level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                             help='设置日志级别')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化日志系统
    init_logging()
    
    # 执行命令
    if args.command == 'summary':
        show_log_summary()
    elif args.command == 'cleanup':
        cleanup_old_logs(args.days)
    elif args.command == 'view':
        view_recent_logs(args.type, args.lines)
    elif args.command == 'search':
        search_logs(args.pattern, args.type)
    elif args.command == 'analyze':
        analyze_errors()
    elif args.command == 'monitor':
        monitor_logs()
    elif args.command == 'export':
        export_logs(args.output)
    elif args.command == 'config':
        if args.level:
            configure_log_level(args.level)
        else:
            print("❌ 请指定配置选项")

if __name__ == "__main__":
    main() 