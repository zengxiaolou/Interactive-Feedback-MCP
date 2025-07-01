#!/usr/bin/env python3
"""
手动测试调用来源字段功能
通过启动server并手动发送请求
"""

import subprocess
import json
import time
import sys
import os

def create_test_request():
    """创建测试请求"""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "interactive_feedback",
            "arguments": {
                "message": "🧪 测试调用来源字段功能 - 请检查回复中是否包含调用来源信息",
                "project_path": "/Users/ruler/Documents/study/interactive-feedback-mcp",
                "project_name": "interactive-feedback-mcp", 
                "git_branch": "main",
                "priority": 3,
                "category": "test",
                "predefined_options": [
                    "✅ 确认看到调用来源信息",
                    "❌ 没有看到调用来源信息",
                    "🔄 重新测试"
                ]
            }
        }
    }

def test_with_caller_source(caller_source):
    """测试指定调用来源"""
    print(f"\n🧪 测试调用来源: {caller_source}")
    print("=" * 50)
    
    # 启动server进程
    cmd = [
        "uv", "run", "server.py", 
        "--caller-source", caller_source,
        "--debug"
    ]
    
    print(f"🚀 启动命令: {' '.join(cmd)}")
    
    # 创建输入数据
    init_request = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    
    test_request = create_test_request()
    
    # 准备输入数据
    input_data = (
        json.dumps(init_request) + "\n" +
        json.dumps(initialized_notification) + "\n" +
        json.dumps(test_request) + "\n"
    )
    
    try:
        # 启动进程并发送数据
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/Users/ruler/Documents/study/interactive-feedback-mcp"
        )
        
        print("📤 发送请求...")
        stdout, stderr = process.communicate(input=input_data, timeout=10)
        
        print("📥 服务器响应:")
        if stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get('id') == 1:  # 我们的测试请求
                            result = response.get('result')
                            if result:
                                print(f"✅ 收到回复:")
                                if isinstance(result, list):
                                    for item in result:
                                        if isinstance(item, str):
                                            print(item)
                                            print("-" * 40)
                                elif isinstance(result, str):
                                    print(result)
                                    print("-" * 40)
                                
                                # 检查调用来源信息
                                result_str = str(result)
                                if caller_source.upper() in result_str:
                                    print(f"✅ 成功: 找到调用来源 '{caller_source.upper()}'")
                                else:
                                    print(f"❌ 失败: 未找到调用来源 '{caller_source.upper()}'")
                                    
                                return True
                            else:
                                print(f"📄 响应: {response}")
                    except json.JSONDecodeError:
                        if "error" not in line.lower():
                            print(f"📝 输出: {line}")
        
        if stderr:
            print("⚠️ 错误输出:")
            print(stderr)
            
        return False
        
    except subprocess.TimeoutExpired:
        print("⏰ 进程超时")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 Interactive Feedback MCP - 手动测试调用来源字段")
    print("=" * 60)
    
    # 测试一个调用来源作为示例
    test_sources = ['augment', 'cursor']
    
    for source in test_sources:
        success = test_with_caller_source(source)
        if success:
            print(f"🎉 {source} 测试成功!")
        else:
            print(f"⚠️ {source} 测试可能需要手动验证")
        
        time.sleep(2)  # 等待2秒再测试下一个

if __name__ == "__main__":
    main()
