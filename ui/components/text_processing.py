# Text Processing Component for Interactive Feedback MCP
# 文本处理组件

import re
import json

class TextProcessor:
    """文本处理工具类"""
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        预处理文本，处理转义字符问题
        特别处理从Cursor编辑器传入时的转义问题
        """
        # 记录原始文本（用于调试）
        print(f"原始文本: {repr(text)}")

        # 处理字面上的转义序列
        if isinstance(text, str):
            # 尝试多种解码方式来处理不同来源的转义

            # 方式1: 尝试JSON解码（适用于从JSON参数传入的情况）
            try:
                # 如果文本看起来像是被JSON编码过的字符串，尝试解码
                if '\\n' in text or '\\t' in text or '\\r' in text:
                    # 添加引号使其成为有效JSON字符串，然后解码
                    decoded_text = json.loads(f'"{text}"')
                    print(f"JSON解码成功: {repr(decoded_text)}")
                    text = decoded_text
                else:
                    print("不需要JSON解码")
            except (json.JSONDecodeError, ValueError):
                print("JSON解码失败，使用字符串替换方法")
                # 如果JSON解码失败，使用字符串替换方法

                # 先检查是否存在双重转义（如 \\n）
                if '\\\\n' in text:
                    # 处理双重转义的换行符
                    text = text.replace('\\\\n', '\n')
                    text = text.replace('\\\\t', '\t')
                    text = text.replace('\\\\r', '\r')
                    text = text.replace('\\\\\\\\', '\\')  # 四重反斜杠变成单反斜杠
                else:
                    # 1. 处理字面上的转义序列
                    text = text.replace('\\\\', '\\')  # 先处理双反斜杠
                    text = text.replace('\\n', '\n')
                    text = text.replace('\\t', '\t')
                    text = text.replace('\\r', '\r')

            # 2. 规范化换行符
            text = text.replace('\r\n', '\n')
            text = text.replace('\r', '\n')

        # 记录处理后的文本（用于调试）
        print(f"预处理后文本: {repr(text)}")
        return text

    @staticmethod
    def is_markdown(text: str) -> bool:
        """
        检测文本是否可能是Markdown格式
        通过检查常见Markdown语法特征来判断
        """
        # 如果文本为空，不视为Markdown
        if not text or text.strip() == "":
            return False

        # 预处理文本，处理转义字符
        text = TextProcessor.preprocess_text(text)

        # 检查常见的Markdown语法特征
        markdown_patterns = [
            r'^#{1,6}\s+.+',                  # 标题: # 标题文本
            r'\*\*.+?\*\*',                   # 粗体: **文本**
            r'\*.+?\*',                       # 斜体: *文本*
            r'_.+?_',                         # 斜体: _文本_
            r'`[^`]+`',                       # 行内代码: `代码`
            r'^\s*```',                       # 代码块: ```
            r'^\s*>',                         # 引用: > 文本
            r'^\s*[-*+]\s+',                  # 无序列表: - 项目 或 * 项目 或 + 项目
            r'^\s*\d+\.\s+',                  # 有序列表: 1. 项目
            r'\[.+?\]\(.+?\)',                # 链接: [文本](URL)
            r'!\[.+?\]\(.+?\)',               # 图片: ![alt](URL)
            r'\|.+\|.+\|',                    # 表格
            r'^-{3,}$',                       # 水平线: ---
            r'^={3,}$',                       # 水平线: ===
        ]

        # 遍历文本的每一行，检查是否包含Markdown语法特征
        lines = text.split('\n')
        markdown_features_count = 0

        for line in lines:
            for pattern in markdown_patterns:
                if re.search(pattern, line, re.MULTILINE):
                    markdown_features_count += 1
                    # 如果发现明确的Markdown特征，立即返回True
                    if pattern in [r'^#{1,6}\s+.+', r'^\s*```', r'^\s*>', r'^\s*[-*+]\s+', r'^\s*\d+\.\s+', r'\|.+\|.+\|', r'^-{3,}$', r'^={3,}$']:
                        return True

        # 如果文本中包含一定数量的Markdown特征，则视为Markdown
        # 这里根据特征数量和文本长度的比例来判断
        # 如果特征数量超过2个或特征密度较高，则视为Markdown
        return markdown_features_count >= 2 or (markdown_features_count > 0 and markdown_features_count / len(lines) > 0.1)

    @staticmethod
    def convert_text_to_html(text: str, line_height: float = 1.3) -> str:
        """
        将普通文本转换为HTML格式
        保留换行和空格，并进行基本的HTML转义
        """
        # 预处理文本，处理转义字符
        text = TextProcessor.preprocess_text(text)

        # HTML转义
        escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # 保留换行
        html_text = escaped_text.replace("\n", "<br>")

        # 应用样式，去除多余的缩进，添加emoji字体支持
        # 减小行高，并使用更具体的字体列表以保证跨平台一致性
        styled_html = f"""<div style="
            line-height: {line_height};
            color: #ccc;
            font-family: 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', system-ui, -apple-system, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji';
            white-space: pre-wrap;
        ">{html_text}</div>"""

        return styled_html

    @staticmethod
    def convert_markdown_to_html(markdown_text: str, line_height: float = 1.3) -> str:
        """使用markdown库将markdown转换为HTML"""
        try:
            # 预处理文本，处理转义字符
            markdown_text = TextProcessor.preprocess_text(markdown_text)

            import markdown
            from markdown.extensions import codehilite, tables, toc

            # 配置markdown扩展，添加emoji支持
            extensions = ['extra', 'codehilite', 'toc']

            # 尝试添加emoji扩展（如果可用）
            try:
                import pymdownx.emoji
                extensions.append('pymdownx.emoji')
                extension_configs = {
                    'pymdownx.emoji': {
                        'emoji_index': pymdownx.emoji.gemoji,
                        'emoji_generator': pymdownx.emoji.to_svg,
                        'alt': 'short',
                        'options': {
                            'attributes': {
                                'align': 'absmiddle',
                                'height': '20px',
                                'width': '20px'
                            },
                            'image_path': 'https://assets-cdn.github.com/images/icons/emoji/unicode/',
                            'non_standard_image_path': 'https://assets-cdn.github.com/images/icons/emoji/'
                        }
                    }
                }
            except ImportError:
                extension_configs = {}

            # 创建Markdown实例（使用缓存）
            if not hasattr(TextProcessor, '_markdown_instance'):
                TextProcessor._markdown_instance = markdown.Markdown(
                    extensions=extensions,
                    extension_configs=extension_configs
                )

            # 转换markdown到HTML
            html = TextProcessor._markdown_instance.convert(markdown_text)

            # 应用自定义样式，去除多余的缩进，添加emoji支持
            # 统一设置基础样式，减小行高和段落间距
            styled_html = f"""
            <style>
                /* 基础样式 */
                .md-content, .md-content p, .md-content li {{
                    line-height: {line_height} !important; /* 统一并强制行高 */
                    margin-top: 2px !important;
                    margin-bottom: 2px !important;
                }}
                .md-content {{
                    color: #ccc;
                    font-family: 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', system-ui, -apple-system, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji';
                    white-space: pre-wrap;
                }}

                /* 标题样式 */
                h1 {{ color: #FF9800; margin: 12px 0 8px 0; font-size: 1.3em; }}
                h2 {{ color: #2196F3; margin: 10px 0 6px 0; font-size: 1.2em; }}
                h3 {{ color: #4CAF50; margin: 10px 0 6px 0; font-size: 1.1em; }}

                /* 列表样式 */
                ul, ol {{
                    margin: 6px 0;
                    padding-left: 20px;
                }}
                li {{
                    vertical-align: baseline;
                    display: list-item;
                    text-align: left;
                }}

                /* 代码样式 */
                code {{
                    background-color: rgba(255,255,255,0.1);
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 0.9em;
                }}

                pre {{
                    background-color: rgba(255,255,255,0.05);
                    padding: 12px;
                    border-radius: 6px;
                    overflow-x: auto;
                    border-left: 4px solid #2196F3;
                }}

                /* 段落样式 - 已在 .md-content p 中处理 */
                p {{ }}

                /* 强调样式 */
                strong {{ color: #FFD54F; }}
                em {{ color: #81C784; }}

                /* Emoji样式优化 */
                .emoji, img.emoji {{
                    height: 1.2em;
                    width: 1.2em;
                    margin: 0 0.05em 0 0.1em;
                    vertical-align: -0.1em;
                    display: inline-block;
                }}

                /* 表格样式 */
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 10px 0;
                }}
                th, td {{
                    border: 1px solid #444;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: rgba(255,255,255,0.1);
                    font-weight: bold;
                }}
            </style>
            <div class="md-content">{html}</div>
            """

            return styled_html

        except ImportError:
            # Fallback if markdown library is not installed
            # Log that markdown library is not found and basic conversion is used.
            print("Markdown library not found. Using basic HTML escaping for description.")
            return TextProcessor.convert_text_to_html(markdown_text, line_height)
        except Exception as e:
            # Fallback for any other error during markdown conversion
            print(f"Error during markdown conversion: {e}. Using basic HTML escaping.")
            return TextProcessor.convert_text_to_html(markdown_text, line_height) 