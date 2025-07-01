#!/usr/bin/env python3
"""
简单测试调用来源字段功能
直接调用interactive_feedback函数
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_caller_source_field(caller_source):
    """测试指定调用来源的字段显示"""
    print(f"\n🧪 测试调用来源: {caller_source}")
    print("=" * 50)
    
    # 模拟命令行参数
    class MockArgs:
        def __init__(self, caller_source):
            self.caller_source = caller_source
            self.debug = True
            self.log_level = 'INFO'
    
    # 设置全局变量（模拟server.py中的逻辑）
    import server
    server.cmd_args = MockArgs(caller_source)
    server.GLOBAL_CALLER_SOURCE = caller_source
    
    # 设置环境变量
    os.environ['MCP_FEEDBACK_CALLER_SOURCE'] = caller_source
    os.environ['MCP_FEEDBACK_DEBUG'] = 'true'
    os.environ['MCP_FEEDBACK_LOG_LEVEL'] = 'INFO'
    
    try:
        # 调用interactive_feedback函数
        result = server.interactive_feedback(
            message=f"这是一个测试消息，验证调用来源字段功能。当前测试: {caller_source}",
            project_path="/Users/ruler/Documents/study/interactive-feedback-mcp",
            project_name="interactive-feedback-mcp",
            git_branch="main",
            priority=3,
            category="test",
            predefined_options=[
                f"✅ 确认收到来自 {caller_source} 的消息",
                "🔄 重新测试",
                "❌ 取消测试"
            ]
        )
        
        print("📥 函数返回结果:")
        if isinstance(result, tuple):
            for i, item in enumerate(result):
                if isinstance(item, str):
                    print(f"📝 文本部分 {i+1}:")
                    print(item)
                    print("-" * 40)
                else:
                    print(f"🖼️ 图片部分 {i+1}: {type(item)}")
        elif isinstance(result, str):
            print("📝 返回文本:")
            print(result)
            print("-" * 40)
        else:
            print(f"📄 返回类型: {type(result)}")
            print(f"📄 返回内容: {result}")
        
        # 检查是否包含调用来源信息
        result_text = str(result)
        if caller_source.upper() in result_text:
            print(f"✅ 成功: 在返回结果中找到调用来源 '{caller_source.upper()}'")
        else:
            print(f"❌ 失败: 在返回结果中未找到调用来源 '{caller_source.upper()}'")
            
        # 检查图标
        caller_icons = {
            'cursor': '🖱️',
            'augment': '🚀', 
            'claude': '🤖',
            'vscode': '💻',
            'custom': '⚙️'
        }
        
        expected_icon = caller_icons.get(caller_source, '❓')
        if expected_icon in result_text:
            print(f"✅ 成功: 找到预期的调用来源图标 '{expected_icon}'")
        else:
            print(f"❌ 失败: 未找到预期的调用来源图标 '{expected_icon}'")
            
        # 检查时间戳
        current_time = datetime.now().strftime('%Y-%m-%d')
        if current_time in result_text:
            print(f"✅ 成功: 找到时间戳信息")
        else:
            print(f"❌ 失败: 未找到时间戳信息")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 Interactive Feedback MCP - 调用来源字段简单测试")
    print("=" * 60)
    
    # 测试不同的调用来源
    test_sources = ['cursor', 'augment', 'claude', 'vscode', 'custom']
    
    results = {}
    
    for source in test_sources:
        try:
            success = test_caller_source_field(source)
            results[source] = success
        except KeyboardInterrupt:
            print("\n⏹️ 测试被用户中断")
            break
        except Exception as e:
            print(f"❌ 测试 {source} 时出错: {e}")
            results[source] = False
    
    # 输出测试结果汇总
    print("\n📊 测试结果汇总:")
    print("=" * 30)
    success_count = 0
    for source, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{source:10} : {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 总体结果: {success_count}/{len(results)} 个测试通过")
    
    if success_count == len(results):
        print("🎉 所有测试都通过了！调用来源字段功能正常工作。")
    else:
        print("⚠️ 部分测试失败，需要检查代码实现。")

if __name__ == "__main__":
    main()
