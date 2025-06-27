# Interactive Feedback MCP - 扩展参数使用指南

## 🚀 概述

Interactive Feedback MCP 现在支持丰富的扩展参数，让您能够更精确地控制反馈交互的行为和显示内容。

## 📋 完整参数列表

### 基础参数（必需）
- `message` (str): 向用户显示的问题或消息
- `predefined_options` (list, 可选): 预定义选项列表

### 扩展参数（可选）
- `project_path` (str): 覆盖自动检测的项目路径
- `project_name` (str): 自定义项目名称
- `git_branch` (str): 覆盖Git分支名
- `priority` (int, 1-5): 优先级级别，默认为3
- `category` (str): 分类标识
- `context_data` (dict): 额外的上下文数据

## 🎯 优先级系统

| 级别 | 图标 | 描述 | 使用场景 |
|------|------|------|----------|
| 1 | 🔵 | 最低 | 一般询问、建议 |
| 2 | 🟢 | 较低 | 非紧急优化 |
| 3 | 🟡 | 普通 | 常规开发任务（默认） |
| 4 | 🟠 | 较高 | 重要功能、Bug修复 |
| 5 | 🔴 | 最高 | 紧急问题、生产故障 |

## 📂 分类系统

| 分类 | 图标 | 描述 |
|------|------|------|
| `bug` | 🐛 | Bug修复 |
| `feature` | ✨ | 新功能 |
| `review` | 👀 | 代码审查 |
| `performance` | ⚡ | 性能优化 |
| `docs` | 📚 | 文档 |
| `test` | 🧪 | 测试 |
| `deploy` | 🚀 | 部署 |
| `other` | 📦 | 其他 |
| `general` | 🔧 | 通用（默认） |

## 💡 使用示例

### 基础用法
```python
interactive_feedback(
    message="请选择下一步操作",
    predefined_options=["继续开发", "运行测试", "提交代码"]
)
```

### 高优先级Bug修复
```python
interactive_feedback(
    message="发现严重Bug，需要立即处理",
    predefined_options=["立即修复", "创建热修复分支", "回滚代码"],
    priority=5,
    category="bug",
    context_data={
        "bug_id": "BUG-2024-001",
        "severity": "critical",
        "affected_users": 1500
    }
)
```

### 功能开发规划
```python
interactive_feedback(
    message="新功能开发计划讨论",
    predefined_options=["开始开发", "需求细化", "技术调研", "推迟开发"],
    priority=3,
    category="feature",
    project_name="用户管理系统",
    git_branch="feature/user-management",
    context_data={
        "feature_name": "多租户支持",
        "estimated_time": "2周",
        "dependencies": ["数据库迁移", "API重构"]
    }
)
```

### 性能优化讨论
```python
interactive_feedback(
    message="系统性能分析结果",
    predefined_options=["优化数据库查询", "增加缓存", "代码重构", "扩容服务器"],
    priority=4,
    category="performance",
    context_data={
        "response_time": "2.5s",
        "target_time": "500ms",
        "bottleneck": "数据库查询",
        "cpu_usage": "85%",
        "memory_usage": "78%"
    }
)
```

### 代码审查
```python
interactive_feedback(
    message="代码审查发现的问题",
    predefined_options=["立即修复", "创建Issue", "讨论设计", "批准合并"],
    priority=3,
    category="review",
    context_data={
        "reviewer": "Senior Developer",
        "files_changed": 15,
        "lines_added": 342,
        "lines_removed": 128,
        "issues_found": 3
    }
)
```

### 部署相关
```python
interactive_feedback(
    message="生产环境部署准备",
    predefined_options=["开始部署", "再次测试", "回滚计划", "推迟部署"],
    priority=4,
    category="deploy",
    project_path="/path/to/production/project",
    git_branch="release/v2.1.0",
    context_data={
        "environment": "production",
        "version": "v2.1.0",
        "rollback_plan": "available",
        "maintenance_window": "2024-01-15 02:00-04:00"
    }
)
```

## 🎨 UI显示效果

扩展参数会在UI的右侧面板中显示：

### 反馈参数部分
- **优先级**: 显示为带颜色图标的优先级
- **分类**: 显示为带图标的分类名称
- **上下文**: 显示键值对数量和详细信息（最多3个）

### 示例显示
```
⚙️ 反馈参数
┌─────────────────────┐
│ 优先级: 🔴 最高      │
│ 分类: 🐛 Bug修复     │
│ 上下文: 4个键值对    │
│                     │
│ 📋 上下文详情:       │
│ bug_id: BUG-2024... │
│ severity: critical  │
│ affected_users: 1500│
│ ... 还有 1 个        │
└─────────────────────┘
```

## 🔄 向后兼容性

- 所有扩展参数都是可选的
- 未提供的参数使用默认值或自动检测
- 现有代码无需修改即可继续使用
- 自动检测机制作为回退方案

## 🧪 测试

使用提供的测试脚本验证功能：

```bash
python test_extended_params.py
```

测试覆盖：
- 基础参数功能
- 扩展参数功能
- 所有分类的测试
- 所有优先级的测试

## 📚 最佳实践

1. **优先级使用**：
   - 日常开发任务使用默认优先级（3）
   - 紧急问题使用高优先级（4-5）
   - 建议性内容使用低优先级（1-2）

2. **分类选择**：
   - 根据实际工作内容选择合适分类
   - 使用`general`作为通用分类
   - 自定义分类时保持简洁明了

3. **上下文数据**：
   - 提供相关的技术细节
   - 避免过多冗余信息
   - 使用清晰的键名

4. **项目信息**：
   - 通常依赖自动检测即可
   - 仅在特殊情况下手动覆盖
   - 确保路径的准确性

## 🚀 未来扩展

计划中的功能：
- 时间戳和截止日期支持
- 用户角色和权限集成
- 更多分类和优先级细分
- 自定义UI主题支持 