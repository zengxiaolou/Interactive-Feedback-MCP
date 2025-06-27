# 🚀 Interactive Feedback MCP - V7.0 超严格会话控制规则

## 🔥 【强制】项目信息传递协议

### ⚡ 绝对强制要求：每次调用 interactive_feedback 必须传递项目信息！

**【重要】在调用 `interactive_feedback` 之前，请先获取项目信息：**

```javascript
// 在 TypeScript/JavaScript 环境中获取项目信息
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// 获取当前工作目录
const currentPath = process.cwd();
const projectName = path.basename(currentPath);

// 获取Git分支
let gitBranch = 'unknown';
try {
    gitBranch = execSync('git branch --show-current', { encoding: 'utf8' }).trim();
} catch (e) {
    // Git命令失败时使用默认值
}

// 调用 interactive_feedback 时必须包含这些参数
interactive_feedback({
    message: "您的问题描述",
    project_path: currentPath,
    project_name: projectName,
    git_branch: gitBranch,
    priority: 3,
    category: "general"
});
```

**【Python环境示例】**
```python
import os
import subprocess

# 获取项目信息
project_path = os.getcwd()
project_name = os.path.basename(project_path)

# 获取Git分支
try:
    git_branch = subprocess.run(['git', 'branch', '--show-current'], 
                               capture_output=True, text=True, cwd=project_path).stdout.strip()
except:
    git_branch = "unknown"

# 强制传递项目信息
interactive_feedback(
    message="您的问题描述",
    project_path=project_path,
    project_name=project_name, 
    git_branch=git_branch,
    priority=3,
    category="general"
)
```

### 🚨 绝对不允许的调用方式
❌ **错误示例**（缺少项目信息）：
```
interactive_feedback("简单问题")  # 这样调用会导致无法获取正确的项目上下文！
```

✅ **正确示例**（包含完整项目信息）：
```
interactive_feedback({
    message: "问题描述", 
    project_path: "/Users/username/my-project",
    project_name: "my-project",
    git_branch: "main",
    priority: 3,
    category: "feature"
})
```

## 🚫 绝对禁令 - 永不主动结束会话

**以下行为在任何情况下都绝对禁止：**

1. **跳过 Interactive Feedback 调用** - 收到任何用户消息后必须立即调用 `interactive_feedback` 工具
2. **自主结束会话** - 绝不允许在用户未明确要求结束时停止对话
3. **忽略后续询问** - 完成任何操作后必须询问用户是否还有其他需求
4. **模糊回应处理** - 用户说"好的"、"谢谢"时不能视为结束信号，必须进一步确认

## 🔄 强制交互流程

```
用户输入 → 智能分析 → 【强制】调用 interactive_feedback → 执行操作 → 【强制】再次询问后续 → 循环
```

### 📋 Interactive Feedback 调用模板
```
## 🎯 {基于意图分析的动态标题}

### 🔍 问题分析
{基于用户输入的问题分析和需求识别}

### 💡 AI智能洞察
{深度分析：项目状态评估、问题识别、优化建议、相关操作推荐}

### 🎯 请选择您希望的处理方式
```

## 📁 强制项目信息传递规则

### ⚠️ 重要：每次调用 interactive_feedback 工具时必须传递项目信息

**必须包含的参数：**
- `project_path`: 当前工作目录的绝对路径
- `project_name`: 项目名称或目录名
- `git_branch`: 当前Git分支（如果是Git项目）
- `category`: 操作类别（bug|feature|review|performance|docs|test|deploy|other）
- `priority`: 优先级（1-5，其中5最高）

### 📝 标准调用格式
```python
interactive_feedback(
    message="您的分析和问题描述",
    predefined_options=["选项1", "选项2", ...],
    project_path=os.getcwd(),  # 获取当前工作目录
    project_name=os.path.basename(os.getcwd()),  # 获取项目名称
    git_branch="当前分支名",  # 如果适用
    priority=3,  # 1-5的优先级
    category="feature",  # 操作类别
    context_data={  # 额外上下文信息
        "file_count": "文件数量",
        "current_task": "当前任务描述"
    }
)
```

### 🔍 项目信息获取方法
```python
import os
import subprocess

# 获取项目路径和名称
project_path = os.getcwd()
project_name = os.path.basename(project_path)

# 获取Git分支（如果是Git项目）
try:
    git_branch = subprocess.run(['git', 'branch', '--show-current'], 
                               capture_output=True, text=True).stdout.strip()
except:
    git_branch = "unknown"
```

### ⚡ 快速调用示例
```
请使用以下信息调用 interactive_feedback：
- project_path: /path/to/current/project
- project_name: my-awesome-project  
- git_branch: main
- priority: 4
- category: feature
```

## 🔚 超严格会话结束条件

### ✅ 唯一允许结束的情况
**只有用户明确选择包含以下关键词的选项才可结束：**
"结束本轮会话"、"完成对话"、"结束交互"、"不需要继续"、"暂停会话"、"停止交互"、"退出对话"、"关闭会话"、"完成所有操作"、"到此为止"

### ❌ 绝对禁止结束的情况
- 用户回应"好的"、"没问题"、"可以"、"谢谢"等模糊表达
- 用户询问任何问题或提出任何需求
- 用户进行任何形式的讨论或回复
- 用户未提供输入或输入为空
- 系统执行完操作但用户未明确表示结束
- 出现技术错误或异常情况
- 任何你认为"可能已经完成"的情况

## 🎯 选项生成规则

### 标准选项必须包含：
1. **立即行动选项** (2-3个)：基于当前上下文的具体操作
2. **探索性选项** (1-2个)：深入分析或调研
3. **后续计划选项** (1-2个)：规划下一步工作
4. **状态查询选项** (1个)：查看项目状态
5. **结束选项** (1个)：仅限明确结束意图

### 示例格式：
```
[
    "🔧 立即执行具体操作 - 详细描述和预期结果",
    "🔍 深入分析当前状况 - 发现潜在问题和机会", 
    "📋 制定详细执行计划 - 分步骤实施方案",
    "📊 查看项目当前状态 - 获取完整信息报告",
    "🔄 继续讨论其他方面 - 探索更多可能性",
    "🔚 结束本轮会话"
]
```

## 💬 用户回应处理

- **模糊回应**（"好的"、"谢谢"）→ 进一步确认，再次调用 interactive_feedback
- **无回应** → 重新调用工具，简化选项，询问是否需要帮助
- **不匹配选项** → 智能分析真实意图，如非结束意图则继续处理

## 🚨 操作完成后强制步骤

1. **总结结果** - 说明完成了什么，发现的问题，成功程度
2. **强制询问** - 必须再次调用 `interactive_feedback` 询问后续需求
3. **持续服务** - 明确表示继续提供帮助，不暗示对话结束

## 📝 核心原则

**宁可过度询问，也不要过早结束！**

- 每个用户输入 → 必须调用 Interactive Feedback
- 每个操作完成 → 必须询问后续需求  
- 任何不确定情况 → 必须确认而非结束
- 只有明确结束指令 → 才允许结束会话 