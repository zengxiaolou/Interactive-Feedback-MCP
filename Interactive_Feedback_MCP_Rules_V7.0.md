# 🚀 Interactive Feedback MCP 项目开发规则 V7.0 - 强制交互版

## 📋 项目概述
Interactive Feedback MCP 是一个基于Python和PySide6的智能交互反馈系统，专为AI辅助开发工具（Cursor、Claude Desktop、Windsurf）设计。项目采用MCP（Model Context Protocol）架构，提供现代化毛玻璃UI界面和强大的多媒体处理能力。

---

## 🔥 核心开发原则

### 1. 【V7.0强化】强制交互协议 - 超严格会话控制
- **绝对强制规则**：收到任何用户消息后，必须立即调用 Interactive Feedback 工具，绝无例外！
- **执行顺序**：用户输入 → 智能分析 → 强制调用 Interactive Feedback → 用户确认 → 执行操作 → **强制后续交互检查**
- **会话持久化**：除非收到明确的会话结束指令，否则永远不允许结束交互循环
- **性能优先**：并行工具调用，减少等待时间，但绝不允许跳过交互环节

### 2. 【V7.0新增】项目路径自动传递机制
- **自动路径检测**：server.py自动检测调用方项目路径，无需手动配置
- **环境变量传递**：通过MCP_CALLER_CWD等环境变量自动传递项目上下文
- **智能路径验证**：自动验证项目路径有效性和权限
- **跨平台兼容**：支持Windows、macOS、Linux等不同操作系统的路径格式

### 3. 代码质量优先
- **重构优于补丁**：总是重构现有代码而非添加临时修复
- **单一职责**：每个函数、类只负责一个明确的功能
- **编辑优先**：优先编辑现有文件而不是创建新文件
- **清理规范**：删除临时文件，保持项目整洁

### 4. 深色模式强制
- **所有UI组件必须使用深色主题**
- **禁用系统主题跟随**：强制使用EnhancedGlassmorphismTheme
- **毛玻璃效果统一**：所有面板使用一致的透明度和模糊效果
- **中文字体优化**：优先使用PingFang SC、Microsoft YaHei等中文字体

---

## 🔄 【V7.0核心】超严格强制交互流程

### 🚫 绝对禁止的行为
**以下行为在任何情况下都绝对禁止：**
1. **跳过 Interactive Feedback 调用** - 无论任何理由都不允许
2. **未经确认直接执行操作** - 所有操作必须经过用户明确确认
3. **自行判断会话结束** - 只能根据用户明确指令结束
4. **忽略用户反馈** - 必须处理每一个用户输入
5. **中断交互循环** - 不允许在未收到结束指令前停止询问

### 📋 【V7.0升级】强制交互检查清单
每次收到用户输入时，必须按以下步骤执行：

#### ✅ 步骤1：智能分析（强制执行）
```
意图识别分析 {
  输入类型: [Bug报告|功能需求|代码审查|性能问题|文档需求|测试相关|部署配置|项目管理|开发工具|疑问咨询|日常对话]
  置信度: [1-5]
  紧急程度: [1-5]
  复杂度: [简单|中等|复杂]
}

上下文敏感度评估 {
  Git状态敏感: [高|中|低]
  项目类型敏感: [高|中|低] 
  文件活动敏感: [高|中|低]
  依赖敏感: [高|中|低]
  性能敏感: [高|中|低]
}

项目上下文自动获取 {
  项目路径: 从MCP_CALLER_CWD环境变量自动获取
  项目名称: 从MCP_CALLER_PROJECT_NAME环境变量自动获取
  Git信息: 从MCP_CALLER_GIT_*系列环境变量自动获取
  项目类型: 根据项目结构自动判断
}
```

#### ✅ 步骤2：强制调用 Interactive Feedback（绝不跳过）
```
必须使用以下模板调用 Interactive Feedback：

## 🎯 {基于意图分析的动态标题}

### 📊 智能分析结果
- **意图识别**: {意图类型} (置信度: {1-5}/5)
- **紧急程度**: {1-5}/5 (基于多因素评估)
- **上下文敏感度**: {高/中/低} - {敏感因素说明}
- **技术栈**: {自动识别的技术栈}
- **预估复杂度**: {简单/中等/复杂}

### 📁 项目上下文（自动增强）
- **项目名称**: {从MCP_CALLER_PROJECT_NAME自动获取}
- **项目类型**: {python_package/nodejs_project/其他}
- **工作空间路径**: {从MCP_CALLER_CWD自动获取}

### 🌿 Git状态（实时检测）
- **当前分支**: {从MCP_CALLER_GIT_BRANCH自动获取}
- **修改文件**: {从MCP_CALLER_GIT_MODIFIED_FILES自动获取} 个未提交修改
- **未跟踪文件**: {实时统计} 个新文件
- **最后提交**: {从MCP_CALLER_GIT_LAST_COMMIT自动获取，限50字符}
- **建议操作**: {基于Git状态的智能建议}

### 💡 AI智能洞察
{基于上下文和用户输入的深度分析，包括：}
- 项目当前状态评估
- 潜在问题识别  
- 优化建议
- 相关操作推荐

### 🎯 请选择您希望的处理方式

💡 您可以使用 @filename 引用项目文件获得更精确的上下文
```

#### ✅ 步骤3：用户反馈处理（强制验证）
```
用户反馈验证流程 {
  if (用户选择了预设选项) {
    执行对应操作
    继续到步骤4
  } else if (用户提供自定义输入) {
    if (包含明确结束意图) {
      执行结束流程
    } else {
      处理自定义输入
      继续到步骤4
    }
  } else if (无有效反馈) {
    重新调用 Interactive Feedback 并提供更多选项
    继续等待用户反馈
  }
}
```

#### ✅ 步骤4：操作执行后强制后续检查（V7.0新增）
```
操作完成后必须执行的检查 {
  操作状态检查 {
    是否完全完成: [是|否|部分完成]
    是否有错误: [是|否]
    是否需要后续操作: [是|否]
  }
  
  强制后续交互 {
    必须再次调用 Interactive Feedback
    询问是否还有其他需求
    提供相关后续操作选项
    绝不允许在此步骤结束会话
  }
}
```

### 🔚 【V7.0超严格】会话结束条件

#### ❌ 绝对禁止结束会话的情况
**在以下任何情况下都绝对不允许结束会话：**
- 用户回应"好的"、"没问题"、"可以"、"谢谢"等但未明确选择选项
- 用户询问任何问题或提出任何需求
- 用户进行任何形式的讨论或回复
- 用户未提供任何输入或输入为空
- 系统执行完操作但用户未明确表示结束
- 用户回应不匹配任何预设选项但未包含明确结束意图
- 出现任何技术错误或异常情况
- 用户表达困惑或需要帮助

#### ✅ 允许结束会话的唯一条件
**只有在以下情况下才可以结束会话：**

1. **明确的结束选项被选择**：
   - 用户明确选择了包含以下关键词的选项：
     - "结束本轮会话"
     - "完成对话" 
     - "结束交互"
     - "不需要继续"
     - "暂停会话"
     - "停止交互"
     - "退出"
     - "关闭"
     - "完成所有操作"
     - "到此为止"

2. **明确的结束表达被识别**：
   - 用户自定义输入中明确包含以下表达：
     - "我们结束吧"
     - "到此为止"
     - "不用继续了"
     - "今天就到这里"
     - "暂时不需要了"
     - "不要再问了"
     - "没有其他需要"
     - "都处理完了"
     - "会话结束"
     - "停止提问"

#### 🧠 【V7.0新增】结束意图智能识别算法
```python
def is_session_end_intent(user_input: str) -> bool:
    """
    V7.0 超严格会话结束意图识别
    只有在明确检测到结束意图时才返回True
    """
    # 明确结束关键词列表
    definitive_end_keywords = [
        "结束本轮会话", "完成对话", "结束交互", "不需要继续",
        "暂停会话", "停止交互", "退出", "关闭", "完成所有操作",
        "到此为止", "我们结束吧", "不用继续了", "今天就到这里",
        "暂时不需要了", "不要再问了", "没有其他需要", "都处理完了",
        "会话结束", "停止提问", "结束对话", "不再需要"
    ]
    
    # 模糊表达需要更严格的验证
    ambiguous_patterns = [
        ("好的", "结束"),  # 必须同时包含
        ("没问题", "完成"),  # 必须同时包含
        ("可以", "停止"),  # 必须同时包含
    ]
    
    user_input_lower = user_input.lower().strip()
    
    # 检查明确结束关键词
    for keyword in definitive_end_keywords:
        if keyword in user_input_lower:
            return True
    
    # 检查模糊表达（需要同时满足两个条件）
    for pattern1, pattern2 in ambiguous_patterns:
        if pattern1 in user_input_lower and pattern2 in user_input_lower:
            return True
    
    # 默认不结束
    return False
```

#### 🚨 【V7.0强制】会话继续强制机制
```python
def force_continue_session():
    """
    V7.0 强制会话继续机制
    在任何不确定的情况下都必须继续会话
    """
    # 强制后续交互检查
    must_continue_scenarios = [
        "用户回应模糊或不清晰",
        "操作执行完成但未确认后续需求", 
        "出现任何技术问题需要解决",
        "用户可能还有潜在需求",
        "系统状态发生变化需要确认",
        "用户学习或理解过程中",
        "任何形式的疑问或困惑",
    ]
    
    # 在这些情况下必须调用 Interactive Feedback
    return call_interactive_feedback_with_followup_options()
```

---

## 🛠️ 【V7.0升级】MCP工具增强规范

### server.py 工具开发标准（集成项目路径支持）
```python
@mcp.tool()
def interactive_feedback(
    message: str = Field(description="The specific question for the user"),
    predefined_options: list = Field(default=None, description="Predefined options"),
) -> Tuple[str | Image, ...]:
    """
    Request interactive feedback from the user.
    V7.0: 自动集成项目路径和上下文信息
    """
    try:
        start_time = time.time()
        
        # V7.0新增：自动获取和传递项目上下文
        caller_context = _detect_caller_project_context()
        caller_git_info = _get_caller_git_info(caller_context['cwd'])
        
        # 设置环境变量，传递项目上下文给UI
        os.environ['MCP_CALLER_CWD'] = caller_context['cwd']
        os.environ['MCP_CALLER_PROJECT_NAME'] = caller_context['name']
        os.environ['MCP_CALLER_IS_DETECTED'] = str(caller_context['is_detected'])
        os.environ['MCP_CALLER_GIT_BRANCH'] = caller_git_info['branch']
        os.environ['MCP_CALLER_GIT_MODIFIED_FILES'] = str(caller_git_info['modified_files'])
        os.environ['MCP_CALLER_GIT_LAST_COMMIT'] = caller_git_info['last_commit']
        os.environ['MCP_CALLER_IS_GIT_REPO'] = str(caller_git_info['is_git_repo'])
        
        # 调用UI界面
        result_dict = launch_feedback_ui(message, predefined_options)
        
        # 格式化返回
        txt = result_dict.get("interactive_feedback", "").strip()
        img_b64_list = result_dict.get("images", [])
        
        # 图片处理
        images = []
        for b64 in img_b64_list:
            try:
                img_bytes = base64.b64decode(b64)
                images.append(Image(data=img_bytes, format="png"))
            except Exception:
                txt += f"\n\n[warning] 有一张图片解码失败。"
        
        # V7.0性能验证
        elapsed = time.time() - start_time
        if elapsed > 2.0:
            print(f"⚠️ 工具执行时间过长: {elapsed:.2f}s")
        
        # 统一返回格式
        if txt and images:
            return (txt, *images)
        elif txt:
            return (txt,)
        elif images:
            return tuple(images)
        else:
            return ("",)
            
    except Exception as e:
        error_msg = f"交互反馈工具错误: {str(e)}"
        print(error_msg)
        return (error_msg,)
```

### 【V7.0新增】项目上下文自动检测机制
```python
def _detect_caller_project_context():
    """
    V7.0 增强版调用方项目上下文检测
    自动识别调用方项目的路径、名称、类型等信息
    """
    try:
        import psutil
        current_process = psutil.Process()
        
        # 多层级检测策略
        detection_methods = [
            _detect_from_parent_process,
            _detect_from_environment_variables, 
            _detect_from_current_directory,
            _detect_from_process_arguments,
        ]
        
        for method in detection_methods:
            try:
                context = method(current_process)
                if context and context.get('is_detected'):
                    return context
            except Exception:
                continue
        
        # 兜底策略
        return {
            'cwd': os.getcwd(),
            'name': os.path.basename(os.getcwd()),
            'type': _detect_project_type(os.getcwd()),
            'is_detected': False
        }
        
    except Exception:
        return {
            'cwd': os.getcwd(), 
            'name': 'unknown',
            'type': 'unknown',
            'is_detected': False
        }

def _detect_project_type(project_path):
    """检测项目类型"""
    indicators = {
        'python_package': ['pyproject.toml', 'setup.py', 'requirements.txt'],
        'nodejs_project': ['package.json', 'package-lock.json', 'yarn.lock'],
        'rust_project': ['Cargo.toml'],
        'go_project': ['go.mod'],
        'java_project': ['pom.xml', 'build.gradle'],
        'web_project': ['index.html', 'webpack.config.js'],
    }
    
    for project_type, files in indicators.items():
        for file in files:
            if os.path.exists(os.path.join(project_path, file)):
                return project_type
    
    return 'unknown'
```

---

## 🎨 【V7.0升级】UI开发规范

### 三栏布局增强标准
```python
class ThreeColumnFeedbackUI(QMainWindow):
    """
    V7.0 三栏布局标准 - 集成项目上下文显示
    支持自动项目路径显示和Git状态监控
    """
    
    def __init__(self, prompt: str, predefined_options: List[str] = None):
        super().__init__()
        self.project_context = self._load_project_context()
        self.panel_ratios = [40, 40, 20]  # 消息:推荐:信息
        self._setup_enhanced_three_column_layout()
        self._apply_v7_glassmorphism_theme()
        self._setup_project_context_display()
        self._setup_auto_refresh_mechanism()
    
    def _load_project_context(self):
        """从环境变量加载项目上下文"""
        return {
            'cwd': os.environ.get('MCP_CALLER_CWD', os.getcwd()),
            'name': os.environ.get('MCP_CALLER_PROJECT_NAME', 'Unknown Project'),
            'is_detected': os.environ.get('MCP_CALLER_IS_DETECTED', 'False') == 'True',
            'git_branch': os.environ.get('MCP_CALLER_GIT_BRANCH', 'unknown'),
            'git_modified_files': int(os.environ.get('MCP_CALLER_GIT_MODIFIED_FILES', '0')),
            'git_last_commit': os.environ.get('MCP_CALLER_GIT_LAST_COMMIT', 'No commits'),
            'is_git_repo': os.environ.get('MCP_CALLER_IS_GIT_REPO', 'False') == 'True',
        }
    
    def _setup_project_context_display(self):
        """设置项目上下文显示区域"""
        # 在右侧面板显示项目信息
        project_info_widget = self._create_project_info_widget()
        self.info_panel.layout().addWidget(project_info_widget)
    
    def _create_project_info_widget(self):
        """创建项目信息显示控件"""
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
        from PySide6.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 项目名称
        project_label = QLabel(f"📁 {self.project_context['name']}")
        project_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(project_label)
        
        # 项目路径（缩短显示）
        path_label = QLabel(f"📍 {self._shorten_path(self.project_context['cwd'])}")
        path_label.setToolTip(self.project_context['cwd'])  # 完整路径在工具提示中
        layout.addWidget(path_label)
        
        # Git信息
        if self.project_context['is_git_repo']:
            git_label = QLabel(f"🌿 {self.project_context['git_branch']}")
            layout.addWidget(git_label)
            
            if self.project_context['git_modified_files'] > 0:
                modified_label = QLabel(f"📝 {self.project_context['git_modified_files']} 个修改")
                modified_label.setStyleSheet("color: #FF6B6B;")
                layout.addWidget(modified_label)
        
        return widget
    
    def _shorten_path(self, path: str, max_length: int = 30) -> str:
        """缩短路径显示"""
        if len(path) <= max_length:
            return path
        
        parts = path.split(os.sep)
        if len(parts) <= 2:
            return path
        
        return f"...{os.sep}{os.sep.join(parts[-2:])}"
```

---

## 📊 【V7.0新增】会话监控与强制机制

### 会话状态监控
```python
class SessionStateMonitor:
    """V7.0 会话状态监控器"""
    
    def __init__(self):
        self.session_start_time = time.time()
        self.interaction_count = 0
        self.last_interaction_time = time.time()
        self.user_responses = []
        self.session_active = True
    
    def track_interaction(self, interaction_type: str, user_input: str = ""):
        """跟踪交互"""
        self.interaction_count += 1
        self.last_interaction_time = time.time()
        self.user_responses.append({
            'type': interaction_type,
            'input': user_input,
            'timestamp': time.time()
        })
    
    def should_force_continue(self) -> bool:
        """判断是否应该强制继续会话"""
        # 如果用户刚刚开始交互（少于3轮），强制继续
        if self.interaction_count < 3:
            return True
        
        # 如果最后一个响应不是明确的结束意图，强制继续
        if self.user_responses:
            last_response = self.user_responses[-1]['input']
            if not is_session_end_intent(last_response):
                return True
        
        return False
    
    def get_session_summary(self) -> dict:
        """获取会话摘要"""
        return {
            'duration': time.time() - self.session_start_time,
            'interaction_count': self.interaction_count,
            'last_interaction_age': time.time() - self.last_interaction_time,
            'session_active': self.session_active
        }

# 全局会话监控器实例
global_session_monitor = SessionStateMonitor()
```

### 强制交互验证机制
```python
def validate_interaction_flow(user_input: str, context: dict) -> dict:
    """
    V7.0 交互流程验证
    确保每个交互都符合强制交互协议
    """
    validation_result = {
        'is_valid': True,
        'action': 'continue',  # continue | end | retry
        'reason': '',
        'next_step': ''
    }
    
    # 更新会话监控
    global_session_monitor.track_interaction('user_response', user_input)
    
    # 检查是否为明确的结束意图
    if is_session_end_intent(user_input):
        validation_result.update({
            'action': 'end',
            'reason': '用户明确表达结束意图',
            'next_step': '执行会话结束流程'
        })
        return validation_result
    
    # 检查是否需要强制继续
    if global_session_monitor.should_force_continue():
        validation_result.update({
            'action': 'continue',
            'reason': '会话需要继续进行',
            'next_step': '调用 Interactive Feedback 询问后续需求'
        })
        return validation_result
    
    # 检查输入有效性
    if not user_input.strip():
        validation_result.update({
            'action': 'retry',
            'reason': '用户输入为空',
            'next_step': '重新调用 Interactive Feedback 并提供更多选项'
        })
        return validation_result
    
    return validation_result
```

---

## 🚀 【V7.0实施】快速实施指南

### 立即实施检查清单
- [ ] ✅ 确认所有 Interactive Feedback 调用都使用了V7.0模板
- [ ] ✅ 验证项目路径自动检测机制正常工作
- [ ] ✅ 测试会话结束意图识别算法准确性
- [ ] ✅ 确认强制继续机制在所有场景下都能正常触发
- [ ] ✅ 验证UI显示项目上下文信息正确
- [ ] ✅ 测试跨平台路径处理兼容性

### V7.0升级验证命令
```bash
# 验证项目路径检测
uv run python -c "
from server import _detect_caller_project_context, _get_caller_git_info
context = _detect_caller_project_context()
git_info = _get_caller_git_info(context['cwd'])
print(f'项目上下文: {context}')
print(f'Git信息: {git_info}')
"

# 验证会话结束意图识别
uv run python -c "
# 测试结束意图识别函数
test_inputs = ['好的', '结束对话', '到此为止', '不用继续了', '谢谢']
for inp in test_inputs:
    result = is_session_end_intent(inp)
    print(f'输入: {inp} -> 结束意图: {result}')
"

# 验证UI项目信息显示
uv run python enhanced_feedback_ui.py --prompt "测试项目信息显示" --output-file test.json
```

---

## 🎯 V7.0 执行标准总结

### 强制交互协议（绝不妥协）
1. **每个用户输入** → **必须调用 Interactive Feedback**
2. **每个操作完成** → **必须调用 Interactive Feedback 询问后续**
3. **任何不确定情况** → **必须调用 Interactive Feedback 确认**
4. **只有明确结束指令** → **才允许结束会话**

### 项目上下文集成（自动化）
1. **server.py 自动检测项目路径**
2. **环境变量自动传递上下文**
3. **UI 自动显示项目信息**
4. **跨平台路径处理兼容**

### 会话控制机制（超严格）
1. **结束意图智能识别算法**
2. **强制继续验证机制**
3. **会话状态实时监控**
4. **交互流程自动验证**

---

**📅 最后更新**: 2024年12月  
**📝 版本**: V7.0 - 强制交互版  
**🎯 核心特性**: 超严格会话控制 + 项目路径自动集成  
**👥 适用范围**: Interactive Feedback MCP 全体开发人员  

**🚨 重要提醒**: V7.0版本的核心目标是确保Cursor等AI工具在没有明确结束指令前绝不结束会话，同时自动集成项目上下文信息，提供更智能的交互体验。 