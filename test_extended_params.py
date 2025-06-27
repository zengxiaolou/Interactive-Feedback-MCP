#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试扩展的Interactive Feedback参数功能
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import interactive_feedback

def test_basic_parameters():
    """测试基础参数"""
    print("🧪 测试基础参数...")
    
    try:
        result = interactive_feedback(
            message="这是一个基础参数测试",
            predefined_options=["选项1", "选项2", "取消测试"]
        )
        print(f"✅ 基础参数测试成功: {type(result)}")
        return True
    except Exception as e:
        print(f"❌ 基础参数测试失败: {e}")
        return False

def test_extended_parameters():
    """测试扩展参数"""
    print("🧪 测试扩展参数...")
    
    try:
        result = interactive_feedback(
            message="这是一个扩展参数测试",
            predefined_options=["高优先级选项", "性能优化选项", "取消测试"],
            project_path="/custom/project/path",
            project_name="测试项目",
            git_branch="feature/test-branch",
            priority=5,
            category="performance",
            context_data={
                "test_type": "扩展参数测试",
                "feature": "interactive_feedback",
                "version": "v7.0",
                "author": "AI Assistant"
            }
        )
        print(f"✅ 扩展参数测试成功: {type(result)}")
        return True
    except Exception as e:
        print(f"❌ 扩展参数测试失败: {e}")
        return False

def test_all_categories():
    """测试所有分类"""
    print("🧪 测试所有分类...")
    
    categories = ["bug", "feature", "review", "performance", "docs", "test", "deploy", "other"]
    
    for category in categories:
        try:
            print(f"  测试分类: {category}")
            result = interactive_feedback(
                message=f"测试{category}分类",
                predefined_options=[f"{category}选项", "跳过"],
                priority=3,
                category=category,
                context_data={"category_test": category}
            )
            print(f"  ✅ {category}分类测试成功")
        except Exception as e:
            print(f"  ❌ {category}分类测试失败: {e}")
            return False
    
    return True

def test_priority_levels():
    """测试所有优先级"""
    print("🧪 测试所有优先级...")
    
    for priority in range(1, 6):
        try:
            print(f"  测试优先级: {priority}")
            result = interactive_feedback(
                message=f"测试优先级{priority}",
                predefined_options=[f"优先级{priority}选项", "跳过"],
                priority=priority,
                category="test",
                context_data={"priority_test": priority}
            )
            print(f"  ✅ 优先级{priority}测试成功")
        except Exception as e:
            print(f"  ❌ 优先级{priority}测试失败: {e}")
            return False
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始Interactive Feedback扩展参数测试...")
    print("=" * 50)
    
    tests = [
        ("基础参数测试", test_basic_parameters),
        ("扩展参数测试", test_extended_parameters),
        ("分类测试", test_all_categories),
        ("优先级测试", test_priority_levels)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📋 {name}")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✅ {name} 通过")
        else:
            print(f"❌ {name} 失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查实现")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 