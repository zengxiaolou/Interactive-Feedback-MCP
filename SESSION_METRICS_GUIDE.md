# 📊 会话指标收集系统使用指南

## 🎯 系统概述

会话指标收集系统是一个轻量级的数据收集和分析工具，专门为Interactive Feedback MCP设计，用于：

- **收集会话数据**：自动记录用户交互、AI回复、工具调用等关键指标
- **项目维度分类**：按项目路径自动分类存储，便于项目间对比分析
- **风险模式识别**：自动检测可能导致会话意外终止的语言模式
- **质量分析**：评估会话质量，识别改进点

## 🚀 快速开始

### 1. 系统组件

```
session_metrics_collector.py   # 核心收集器
session_integration.py         # 集成追踪器  
session_analysis_tool.py       # 分析工具
```

### 2. 基础使用

```python
from session_integration import setup_integrated_tracking, track_interactive_feedback

# 开始监控项目
setup_integrated_tracking(
    project_path="/path/to/your/project",
    project_name="your-project-name",
    git_branch="main"
)

# 记录Interactive Feedback调用
track_interactive_feedback(
    message="用户的问题或请求",
    category="bug",  # bug|feature|review|performance|docs|test|deploy|other
    priority=4       # 1-5 优先级
)
```

## 📊 数据收集指标

### 时间维度指标
- **会话开始时间**：记录会话启动时刻
- **会话持续时长**：总交互时间
- **交互间隔时间**：用户响应频率
- **最后活动时间**：会话活跃度

### 交互维度指标
- **用户消息数量**：用户输入次数
- **AI回复数量**：AI响应次数
- **工具调用次数**：执行的工具操作数
- **Interactive Feedback调用数**：反馈界面使用频率

### 内容维度指标
- **消息字符长度**：交互内容丰富度
- **代码块数量**：技术交互复杂度
- **图片粘贴次数**：多媒体使用情况
- **文件操作次数**：项目操作活跃度

### 风险维度指标
- **结束性语言检测**：识别可能导致会话终止的表达
- **技术完成信号**：检测"任务完成"类暗示
- **交互模式分析**：识别异常的交互模式

## 🏗️ 集成到现有系统

### 方法1：装饰器集成

```python
from session_integration import with_session_tracking

@with_session_tracking
def your_mcp_tool_function():
    # 您的工具函数实现
    pass
```

### 方法2：手动集成

```python
from session_integration import (
    setup_integrated_tracking,
    track_interactive_feedback,
    track_tool_execution,
    end_tracking_session
)

# 在MCP服务器启动时
setup_integrated_tracking(project_path, project_name, git_branch)

# 在interactive_feedback工具被调用时
def interactive_feedback_tool(message, **kwargs):
    # 记录调用
    track_interactive_feedback(message, **kwargs)
    
    # 原有的工具逻辑
    result = original_interactive_feedback(message, **kwargs)
    
    return result

# 在其他工具被调用时
def any_tool_function():
    result = original_tool_function()
    
    # 记录工具调用
    track_tool_execution([tool_name])
    
    return result

# 在会话结束时
end_tracking_session("user_ended")
```

## 📈 数据分析

### 命令行分析工具

```bash
# 列出所有项目
python session_analysis_tool.py list

# 分析特定项目
python session_analysis_tool.py analyze --project your-project-name

# 详细分析
python session_analysis_tool.py analyze --project your-project-name --detailed

# 对比多个项目
python session_analysis_tool.py compare --projects project1 project2 project3

# 查找问题模式
python session_analysis_tool.py patterns --project your-project-name

# 生成总体报告
python session_analysis_tool.py summary
```

### 编程接口分析

```python
from session_integration import get_session_quality_report, get_project_report

# 获取当前会话质量报告
quality_report = get_session_quality_report()
print(f"质量等级: {quality_report['quality_level']}")
print(f"质量评分: {quality_report['quality_score']}")

# 获取项目分析报告
project_report = get_project_report("your-project-name")
print(f"总会话数: {project_report['total_sessions']}")
print(f"自动终止率: {project_report['auto_termination_rate']:.1%}")
```

## 📁 数据存储结构

```
logs/
├── project_interactive-feedback-mcp/
│   ├── session_events.jsonl           # 实时事件日志
│   ├── sessions_summary.jsonl         # 会话摘要日志
│   ├── session_[session_id].json      # 完整会话数据
│   └── ...
├── project_your-project/
│   ├── session_events.jsonl
│   ├── sessions_summary.jsonl
│   └── ...
└── ...
```

### 数据格式示例

**会话摘要数据**：
```json
{
  "session_id": "d72e54cf...",
  "start_time": "2024-06-28T20:08:45.123456",
  "duration_seconds": 125.5,
  "user_messages": 3,
  "ai_responses": 3,
  "tool_calls": 5,
  "interactive_feedback_calls": 2,
  "categories": ["bug", "feature"],
  "risk_indicators_count": 1,
  "auto_terminated": false,
  "end_reason": "user_ended"
}
```

**事件日志数据**：
```json
{
  "timestamp": "2024-06-28T20:08:45.123456",
  "session_id": "d72e54cf...",
  "project_name": "interactive-feedback-mcp",
  "event_type": "interactive_feedback_called",
  "data": {
    "category": "bug",
    "priority": 4,
    "call_count": 1
  }
}
```

## 🔍 风险模式识别

系统自动识别以下风险模式：

### 结束性语言模式
- "任务完成"、"修复完成"、"问题解决"
- "到此为止"、"就这些了"、"没有其他"
- "已经处理完毕"、"都搞定了"

### 礼貌性结束短语
- "如果还有问题"、"如果需要帮助"
- "祝您使用愉快"、"希望这能帮到您"

### 技术完成信号
- "测试通过"、"代码提交"、"功能正常"
- "部署成功"、"验证完成"、"检查无误"

## 📊 质量评估标准

### 质量评分算法

```python
质量评分 = 交互频率得分 (0-20分)
         + 反馈使用得分 (0-30分)  
         + 工具使用得分 (0-15分)
         + 内容丰富度得分 (0-15分)
         - 风险因素扣分 (0-20分)
```

### 质量等级
- **优秀** (70-100分)：高质量交互，用户满意度高
- **良好** (50-69分)：正常交互，有改进空间
- **一般** (30-49分)：基础交互，需要优化
- **需改进** (0-29分)：存在问题，需要关注

## 🛠️ 自定义配置

### 自定义风险模式

```python
from session_metrics_collector import SessionMetricsCollector

collector = SessionMetricsCollector()

# 添加自定义风险模式
collector.risk_patterns['custom_patterns'] = [
    '您的自定义模式1',
    '您的自定义模式2'
]
```

### 自定义指标

```python
# 扩展SessionMetrics数据类
@dataclass
class CustomSessionMetrics(SessionMetrics):
    custom_metric1: int = 0
    custom_metric2: str = ""
```

## 🔧 故障排除

### 常见问题

**Q: 为什么没有生成日志文件？**
A: 确保已正确调用`setup_integrated_tracking()`初始化追踪

**Q: 如何删除历史数据？**
A: 直接删除`logs/`目录下对应的项目文件夹

**Q: 分析工具报错找不到项目？**
A: 检查项目名称是否正确，使用`list`命令查看可用项目

**Q: 如何禁用自动追踪？**
A: 调用`integrated_tracker.toggle_auto_tracking(False)`

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志输出
from session_integration import integrated_tracker
integrated_tracker.collector.debug_mode = True
```

## 🚀 最佳实践

### 1. 项目初始化
在项目开始时立即调用追踪设置，确保完整数据收集

### 2. 分类规范
使用标准化的类别名称：`bug`、`feature`、`review`、`performance`、`docs`、`test`、`deploy`、`other`

### 3. 定期分析
建议每周运行一次`summary`命令，了解总体趋势

### 4. 问题定位
出现会话质量问题时，使用`patterns`命令深度分析

### 5. 数据清理
定期备份和清理旧的日志数据，保持系统性能

## 📚 扩展阅读

- [MCP协议文档](https://github.com/modelcontextprotocol/python-sdk)
- [数据分析最佳实践](https://docs.python.org/3/library/json.html)
- [PySide6界面开发](https://doc.qt.io/qtforpython/)

---

## 🎯 总结

会话指标收集系统提供了强大而灵活的会话数据收集和分析能力，帮助您：

✅ **了解用户行为**：深入理解用户交互模式  
✅ **提升会话质量**：识别和解决会话质量问题  
✅ **预防意外终止**：通过风险模式识别提前预警  
✅ **项目间对比**：横向对比不同项目的使用情况  
✅ **数据驱动优化**：基于真实数据优化用户体验  

通过持续的数据收集和分析，您可以不断改进Interactive Feedback MCP的用户体验，提供更稳定、更智能的AI助手服务。 