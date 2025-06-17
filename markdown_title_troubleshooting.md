# 📋 Markdown标题乱码字符排查指南

## 🔍 问题现象
在Interactive Feedback MCP的右侧项目信息面板中，markdown标题显示时出现乱码字符（如 `�`、菱形问号等）。

## 🎯 常见原因分析

### 1. 编码问题
**症状**: 中文字符显示为 `???` 或 `�` 
**原因**: 文件编码不一致或字符串处理时编码丢失

### 2. 字体渲染问题
**症状**: 特定Unicode字符显示为方框或乱码
**原因**: 字体不支持某些Unicode字符集

### 3. Qt/PySide6渲染问题
**症状**: 在QTextBrowser中特定字符无法正确显示
**原因**: Qt的HTML渲染引擎字符支持限制

### 4. markdown解析问题
**症状**: markdown语法解析后产生异常字符
**原因**: python-markdown库对特殊字符的处理

## 🔧 排查步骤

### 步骤1: 检查输入源编码
```python
# 检查原始文本编码
def check_text_encoding(text):
    print(f"文本类型: {type(text)}")
    if isinstance(text, str):
        print(f"字符串长度: {len(text)}")
        # 检查是否包含替换字符
        if '�' in text or '\ufffd' in text:
            print("⚠️ 发现替换字符，原始数据可能有编码问题")
        
        # 检查编码有效性
        try:
            encoded = text.encode('utf-8')
            decoded = encoded.decode('utf-8')
            if decoded == text:
                print("✅ UTF-8编码正常")
            else:
                print("❌ UTF-8编码不一致")
        except Exception as e:
            print(f"❌ 编码检查失败: {e}")
```

### 步骤2: 验证markdown渲染器
```python
# 测试渲染器
def test_markdown_renderer():
    from ui.components.enhanced_markdown_renderer import EnhancedMarkdownRenderer
    
    renderer = EnhancedMarkdownRenderer()
    
    # 测试用例
    test_cases = [
        "# 普通英文标题",
        "## 中文标题测试",
        "### 🎯 带emoji的标题",
        "#### 混合Содержание标题",
        "##### 特殊字符 ♦️⚡️🔥",
    ]
    
    for test_text in test_cases:
        print(f"\n输入: {test_text}")
        rendered = renderer.render(test_text)
        print(f"输出包含乱码: {'�' in rendered or '\ufffd' in rendered}")
```

### 步骤3: 检查字体支持
```python
# 检查字体字符支持
def check_font_support():
    from PySide6.QtGui import QFont, QFontMetrics
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    # 测试中文字体
    fonts = ['PingFang SC', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    test_chars = ['中', '文', '🎯', '⚡', '▲', '●']
    
    for font_name in fonts:
        font = QFont(font_name, 14)
        metrics = QFontMetrics(font)
        
        print(f"\n字体: {font_name}")
        for char in test_chars:
            if metrics.inFontUcs4(ord(char)):
                print(f"  ✅ 支持: {char}")
            else:
                print(f"  ❌ 不支持: {char}")
```

### 步骤4: 检查系统环境
```bash
# 检查系统编码环境
python3 -c "
import locale, sys
print(f'系统默认编码: {locale.getpreferredencoding()}')
print(f'文件系统编码: {sys.getfilesystemencoding()}')
print(f'标准输出编码: {sys.stdout.encoding}')
print(f'当前locale: {locale.getlocale()}')
"
```

## 🛠️ 解决方案

### 方案1: 强化编码处理
```python
# 在enhanced_markdown_renderer.py中加强编码处理
def _robust_encode_decode(self, text: str) -> str:
    """强化编码解码处理"""
    if isinstance(text, bytes):
        # 尝试多种编码解码
        for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']:
            try:
                text = text.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            # 如果都失败，使用errors='replace'
            text = text.decode('utf-8', errors='replace')
    
    # 确保是字符串
    if not isinstance(text, str):
        text = str(text)
    
    # 移除NULL字符和控制字符
    text = text.replace('\x00', '').replace('\ufffd', '')
    
    # 重新编码为UTF-8确保一致性
    return text.encode('utf-8', errors='replace').decode('utf-8')
```

### 方案2: 字符白名单清理
```python
def _clean_title_with_whitelist(self, title_content: str) -> str:
    """使用白名单方式清理标题"""
    import re
    
    # 允许的字符类别
    allowed_patterns = [
        r'\u4e00-\u9fff',      # 中文字符
        r'\u3000-\u303f',      # CJK符号和标点
        r'\uff00-\uffef',      # 全角字符
        r'a-zA-Z0-9',          # 英文和数字
        r'\s',                 # 空白字符
        r'\U0001f300-\U0001f9ff',  # emoji
        r'\u2600-\u26ff',      # 杂项符号
        r'!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>?/~`',  # ASCII符号
        r'（）【】《》""''：；，。？！—…·',  # 中文标点
    ]
    
    # 构建完整的允许字符正则
    allowed_pattern = '[' + ''.join(allowed_patterns) + ']'
    
    # 只保留允许的字符
    cleaned = re.sub(f'[^{allowed_pattern}]', '', title_content)
    
    # 规范化空格
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned
```

### 方案3: 字体回退机制
```python
def _setup_font_fallback(self):
    """设置字体回退机制"""
    fallback_css = """
    body, h1, h2, h3, h4, h5, h6 {
        font-family: 
            'PingFang SC',           /* macOS中文 */
            'Hiragino Sans GB',      /* macOS中文备选 */
            'Microsoft YaHei',       /* Windows中文 */
            'SimHei',                /* Windows中文备选 */
            'Noto Sans CJK SC',      /* Linux中文 */
            'Source Han Sans CN',    /* 思源黑体 */
            'Arial Unicode MS',      /* Unicode字体 */
            -apple-system,           /* macOS系统字体 */
            BlinkMacSystemFont,      /* macOS WebKit */
            'Segoe UI',              /* Windows */
            Roboto,                  /* Android */
            'Helvetica Neue',        /* macOS备选 */
            Arial,                   /* 通用 */
            sans-serif;              /* 系统默认 */
    }
    """
    return fallback_css
```

### 方案4: 运行时检测和修复
```python
def _detect_and_fix_garbled_chars(self, html_content: str) -> str:
    """检测并修复乱码字符"""
    import re
    
    # 检测常见乱码模式
    garbled_patterns = [
        (r'�+', ''),                    # 替换字符
        (r'\ufffd+', ''),              # Unicode替换字符
        (r'[^\x09\x0A\x0D\x20-\x7E\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\U0001f300-\U0001f9ff\u2600-\u26ff]+', ''),  # 非预期字符
    ]
    
    for pattern, replacement in garbled_patterns:
        html_content = re.sub(pattern, replacement, html_content)
    
    # 验证修复效果
    remaining_garbled = len(re.findall(r'[�\ufffd]', html_content))
    if remaining_garbled > 0:
        print(f"⚠️ 仍有 {remaining_garbled} 个乱码字符未修复")
    
    return html_content
```

## 🚨 临时解决方案

如果问题紧急，可以使用以下临时方案：

### 1. 禁用问题字符
```python
# 在_clean_title_characters方法中添加
def _emergency_clean(self, text: str) -> str:
    """紧急清理方案"""
    # 移除所有可能的问题字符
    text = re.sub(r'[^\u4e00-\u9fffa-zA-Z0-9\s\-_.]', '', text)
    return text
```

### 2. 强制ASCII模式
```python
# 临时使用ASCII安全模式
def _ascii_safe_mode(self, text: str) -> str:
    """ASCII安全模式"""
    return text.encode('ascii', errors='ignore').decode('ascii')
```

## 🔍 调试工具

### 调试脚本
```python
#!/usr/bin/env python3
# debug_markdown_rendering.py

def debug_markdown_issue():
    """调试markdown渲染问题"""
    
    # 测试输入
    test_input = "## 🎯 测试标题 with 特殊字符"
    
    print("=== 调试信息 ===")
    print(f"原始输入: {repr(test_input)}")
    print(f"UTF-8字节: {test_input.encode('utf-8')}")
    
    # 逐步处理
    from ui.components.enhanced_markdown_renderer import EnhancedMarkdownRenderer
    renderer = EnhancedMarkdownRenderer()
    
    # 步骤1: 清理乱码
    cleaned = renderer._clean_garbled_text(test_input)
    print(f"清理乱码后: {repr(cleaned)}")
    
    # 步骤2: 清理标题
    title_cleaned = renderer._clean_title_characters(cleaned)
    print(f"清理标题后: {repr(title_cleaned)}")
    
    # 步骤3: 渲染
    final_html = renderer.render(title_cleaned)
    print(f"最终HTML包含乱码: {'�' in final_html}")
    
    return final_html

if __name__ == "__main__":
    debug_markdown_issue()
```

## 📋 检查清单

- [ ] 确认输入文本编码为UTF-8
- [ ] 验证字体支持所需字符集
- [ ] 检查系统环境编码设置
- [ ] 测试markdown渲染器各阶段输出
- [ ] 验证Qt/PySide6版本兼容性
- [ ] 检查HTML meta charset设置
- [ ] 测试不同操作系统的兼容性

## 🎯 最佳实践

1. **始终使用UTF-8编码**
2. **提供字体回退机制**
3. **在每个处理阶段验证编码**
4. **使用白名单而非黑名单过滤字符**
5. **保留调试信息便于排查**
6. **提供降级渲染方案**

---

**💡 提示**: 如果问题持续存在，建议开启debug模式并收集详细的错误日志进行进一步分析。 