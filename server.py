# -*- coding: utf-8 -*-
# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by Pau Oliva (https://x.com/pof) with ideas from https://github.com/ttommyth/interactive-mcp
import os
import sys
import json
import tempfile
import subprocess
import base64
import argparse
from datetime import datetime
from typing import Annotated, Dict, Tuple, List, Optional

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from pydantic import Field

# 解析命令行参数
def parse_command_line_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Interactive Feedback MCP Server')
    parser.add_argument('--caller-source',
                       choices=['cursor', 'augment', 'claude', 'vscode', 'custom'],
                       default=None,
                       help='调用来源标识 (cursor|augment|claude|vscode|custom)')
    parser.add_argument('--debug',
                       action='store_true',
                       help='启用调试模式')
    parser.add_argument('--log-level',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default=None,
                       help='设置日志级别')

    # 只解析已知参数，忽略其他参数（如 FastMCP 的参数）
    args, unknown = parser.parse_known_args()
    return args

# 解析命令行参数
cmd_args = parse_command_line_args()

# 设置全局调用来源（优先级：命令行参数 > 环境变量 > 默认值）
GLOBAL_CALLER_SOURCE = (
    cmd_args.caller_source or
    os.environ.get('MCP_FEEDBACK_CALLER_SOURCE', 'cursor')
)

# 设置调试模式
if cmd_args.debug:
    os.environ['MCP_FEEDBACK_DEBUG'] = 'true'

# 设置日志级别
if cmd_args.log_level:
    os.environ['MCP_FEEDBACK_LOG_LEVEL'] = cmd_args.log_level

# 导入日志系统
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui.utils.logging_system import init_logging, get_logger, log_performance, log_project_context

# 初始化日志系统
logging_manager = init_logging({
    'level': os.environ.get('MCP_FEEDBACK_LOG_LEVEL', 'INFO'),
    'console_enabled': True,
    'console_level': 'WARNING',  # 控制台只显示警告和错误
    'performance_enabled': True,
    'project_context_enabled': True
})

# FastMCP server initialization
mcp = FastMCP("Interactive Feedback MCP")

# 获取主日志记录器
logger = get_logger('mcp_server')

# 记录启动参数
logger.info(f"MCP服务器启动 - 调用来源: {GLOBAL_CALLER_SOURCE}")
if cmd_args.caller_source:
    logger.info(f"通过命令行参数设置调用来源: {cmd_args.caller_source}")
elif os.environ.get('MCP_FEEDBACK_CALLER_SOURCE'):
    logger.info(f"通过环境变量设置调用来源: {os.environ.get('MCP_FEEDBACK_CALLER_SOURCE')}")
else:
    logger.info("使用默认调用来源: cursor")

def _detect_caller_project_context():
    """检测调用方项目上下文信息"""
    with log_performance("detect_caller_project_context", "project_detection"):
        try:        
            # 尝试获取调用方工作目录
            caller_cwd = None
            
            # 方法1: 优先从环境变量获取（通常是最可靠的）
            env_cwd = os.environ.get('PWD')
            if env_cwd and os.path.exists(env_cwd) and _is_project_directory(env_cwd):
                caller_cwd = env_cwd
                logger.info(f"从PWD环境变量检测到项目: {env_cwd}")
            
            # 方法2: 使用当前工作目录
            if not caller_cwd:
                current_cwd = os.getcwd()
                script_dir = os.path.dirname(os.path.abspath(__file__))
                
                # 如果当前目录不是MCP服务器目录，且是有效项目目录
                if current_cwd != script_dir and _is_project_directory(current_cwd):
                    caller_cwd = current_cwd
                    logger.info(f"从当前工作目录检测到项目: {current_cwd}")
                # 即使是同一个目录，如果是有效项目目录也使用
                elif _is_project_directory(current_cwd):
                    caller_cwd = current_cwd
                    logger.info(f"使用当前目录作为项目: {current_cwd}")
            
            # 方法3: 尝试使用psutil从父进程获取
            if not caller_cwd:
                try:
                    import psutil
                    current_process = psutil.Process()
                    parent_process = current_process.parent()
                    if parent_process and hasattr(parent_process, 'cwd'):
                        parent_cwd = parent_process.cwd()
                        if _is_project_directory(parent_cwd):
                            caller_cwd = parent_cwd
                            logger.info(f"从父进程检测到项目: {parent_cwd}")
                except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                    logger.debug(f"父进程检测失败: {e}")
            
            # 方法4: 回退到当前目录
            if not caller_cwd:
                caller_cwd = os.getcwd()
                logger.info(f"使用当前目录作为回退: {caller_cwd}")
            
            # 获取项目基本信息
            project_name = os.path.basename(caller_cwd)
            is_detected = _is_project_directory(caller_cwd)
            
            result = {
                'cwd': caller_cwd,
                'name': project_name,
                'is_detected': is_detected
            }
            
            logger.info(f"项目检测完成: 项目={project_name}, 路径={caller_cwd}, 有效={is_detected}")
            
            # 记录项目上下文
            log_project_context("project_detection", result)
            
            return result
                
        except Exception as e:
            logger.error(f"项目检测异常: {e}")
            fallback_cwd = os.getcwd()
            result = {
                'cwd': fallback_cwd,
                'name': os.path.basename(fallback_cwd),
                'is_detected': False
            }
            
            # 记录错误上下文
            log_project_context("project_detection_error", {
                'error': str(e),
                'fallback': result
            })
            
            return result

def _is_project_directory(path):
    """判断是否为项目目录"""
    if not os.path.exists(path):
        return False
    
    # 检查常见的项目标识文件
    project_indicators = [
        '.git', 'package.json', 'requirements.txt', 'pyproject.toml',
        'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle',
        '.gitignore', 'README.md', 'README.rst', '.cursorrules'
    ]
    
    for indicator in project_indicators:
        if os.path.exists(os.path.join(path, indicator)):
            return True
    
    return False

def _get_caller_git_info(project_dir):
    """获取调用方项目的Git信息"""
    try:
        git_commands = [
            (['git', 'branch', '--show-current'], 'branch'),
            (['git', 'status', '--porcelain'], 'status'),
            (['git', 'log', '-1', '--pretty=format:%s'], 'last_commit'),
            (['git', 'rev-parse', '--is-inside-work-tree'], 'is_git_repo')
        ]
        
        git_info = {}
        for cmd, key in git_commands:
            try:
                result = subprocess.run(cmd, cwd=project_dir,
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    git_info[key] = result.stdout.strip()
                else:
                    git_info[key] = ""
            except:
                git_info[key] = ""
        
        # 处理状态信息
        status_output = git_info.get('status', '')
        modified_files = len(status_output.split('\n')) if status_output.strip() else 0
        
        return {
            'branch': git_info.get('branch', 'unknown') or 'unknown',
            'modified_files': modified_files,
            'last_commit': git_info.get('last_commit', 'No commits') or 'No commits',
            'is_git_repo': git_info.get('is_git_repo') == 'true'
        }
    except:
        return {
            'branch': 'unknown',
            'modified_files': 0,
            'last_commit': 'unknown',
            'is_git_repo': False
        }

def launch_feedback_ui(
    summary: str, 
    predefinedOptions: list[str] | None = None,
    project_path: str | None = None,
    project_name: str | None = None,
    git_branch: str | None = None,
    priority: int = 3,
    category: str = "general",
    context_data: dict | None = None
) -> dict[str, str]:
    with log_performance("launch_feedback_ui", "ui_launch", 
                        summary_length=len(summary), 
                        options_count=len(predefinedOptions) if predefinedOptions else 0):
        
        # 使用全局调用源信息（已在启动时确定优先级）
        caller_source = GLOBAL_CALLER_SOURCE
        logger.info(f"启动反馈UI: 优先级={priority}, 类别={category}, 调用源={caller_source}")
        
        # Create a temporary file for the feedback result
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            output_file = tmp.name

        try:
            # 检测调用方项目上下文
            caller_context = _detect_caller_project_context()
            
            # 使用传入的参数覆盖自动检测的值
            caller_cwd = project_path or caller_context['cwd']
            effective_project_name = project_name or caller_context['name']
            
            logger.info(f"使用项目路径: {caller_cwd}, 项目名称: {effective_project_name}")
            
            # 获取调用方Git信息
            caller_git_info = _get_caller_git_info(caller_cwd)
            effective_git_branch = git_branch or caller_git_info['branch']
            
            # Get the path to enhanced_feedback_ui.py relative to this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            feedback_ui_path = os.path.join(script_dir, "enhanced_feedback_ui.py")

            # 准备环境变量，传递调用方项目上下文
            env = os.environ.copy()
            env['MCP_CALLER_CWD'] = caller_cwd
            env['MCP_CALLER_PROJECT_NAME'] = effective_project_name
            env['MCP_CALLER_IS_DETECTED'] = str(caller_context['is_detected'])
            env['MCP_CALLER_GIT_BRANCH'] = effective_git_branch
            env['MCP_CALLER_GIT_MODIFIED_FILES'] = str(caller_git_info['modified_files'])
            env['MCP_CALLER_GIT_LAST_COMMIT'] = caller_git_info['last_commit']
            env['MCP_CALLER_IS_GIT_REPO'] = str(caller_git_info['is_git_repo'])
            
            # 添加新的扩展参数
            env['MCP_FEEDBACK_PRIORITY'] = str(priority)
            env['MCP_FEEDBACK_CATEGORY'] = category
            env['MCP_FEEDBACK_CALLER_SOURCE'] = caller_source
            
            # 添加额外的上下文数据
            if context_data:
                env['MCP_FEEDBACK_CONTEXT_DATA'] = json.dumps(context_data, ensure_ascii=False)

            # Run feedback_ui.py as a separate process
            # NOTE: There appears to be a bug in uv, so we need
            # to pass a bunch of special flags to make this work
            args = [
                sys.executable,
                "-u",
                feedback_ui_path,
                "--prompt", summary,
                "--output-file", output_file,
                "--predefined-options", "|||".join(predefinedOptions) if predefinedOptions else ""
            ]
            
            logger.info(f"启动UI进程: {' '.join(args[:3])}...")
            
            result = subprocess.run(
                args,
                check=False,
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                close_fds=True,
                env=env  # 传递包含调用方上下文的环境变量
            )
            
            if result.returncode != 0:
                logger.error(f"UI进程异常退出，返回码: {result.returncode}")
                raise Exception(f"Failed to launch feedback UI: {result.returncode}")

            logger.info("UI进程执行完成，读取结果文件")
            
            # Read the result from the temporary file
            with open(output_file, 'r', encoding='utf-8') as f:
                ui_result = json.load(f)
            os.unlink(output_file)
            
            logger.info(f"UI反馈结果: {len(ui_result.get('interactive_feedback', ''))} 字符")
            return ui_result
            
        except Exception as e:
            logger.error(f"UI启动失败: {str(e)}")
            if os.path.exists(output_file):
                os.unlink(output_file)
            raise e

@mcp.tool()
def interactive_feedback(
    message: str = Field(description="The specific question for the user"),
    predefined_options: Optional[list] = Field(default=None, description="Predefined options for the user to choose from (optional)"),
    project_path: Optional[str] = Field(default=None, description="Override project path (optional, auto-detected if not provided)"),
    project_name: Optional[str] = Field(default=None, description="Override project name (optional, auto-detected if not provided)"),
    git_branch: Optional[str] = Field(default=None, description="Override git branch name (optional, auto-detected if not provided)"),
    priority: int = Field(default=3, description="Priority level 1-5 (1=lowest, 5=highest, default=3)"),
    category: str = Field(default="general", description="Category: bug|feature|review|performance|docs|test|deploy|other"),
    context_data: Optional[dict] = Field(default=None, description="Additional context data as key-value pairs"),
) -> str | Tuple[str | Image, ...]:
    """
    Request interactive feedback from the user.
    
    Args:
        message: The specific question for the user
        predefined_options: Predefined options for the user to choose from (optional)
        project_path: Override project path (optional, auto-detected if not provided)
        project_name: Override project name (optional, auto-detected if not provided)  
        git_branch: Override git branch name (optional, auto-detected if not provided)
        priority: Priority level 1-5 (1=lowest, 5=highest, default=3)
        category: Category: bug|feature|review|performance|docs|test|deploy|other
        context_data: Additional context data as key-value pairs
    """
    # 检查关键参数传递情况
    if project_path is None and project_name is None:
        print(f"⚠️ 警告: project_path和project_name都未传递，将使用自动检测")
    
    predefined_options_list = predefined_options if isinstance(predefined_options, list) else None
    result_dict = launch_feedback_ui(
        message, 
        predefined_options_list,
        project_path,
        project_name,
        git_branch,
        priority,
        category,
        context_data
    )

    txt: str = result_dict.get("interactive_feedback", "").strip()
    images_data = result_dict.get("images", [])
    img_b64_list: List[str] = images_data if isinstance(images_data, list) else []

    # 在回复中添加调用来源信息
    caller_source_info = f"\n\n🔗 **调用来源**: {GLOBAL_CALLER_SOURCE.upper()}"

    # 根据调用来源添加不同的标识符
    caller_icons = {
        'cursor': '🖱️',
        'augment': '🚀',
        'claude': '🤖',
        'vscode': '💻',
        'custom': '⚙️'
    }

    caller_icon = caller_icons.get(GLOBAL_CALLER_SOURCE, '❓')
    caller_source_info = f"\n\n{caller_icon} **调用来源**: {GLOBAL_CALLER_SOURCE.upper()}"

    # 添加时间戳
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    caller_source_info += f" | ⏰ {timestamp}"

    # 将调用来源信息添加到回复文本中
    if txt:
        txt += caller_source_info
    else:
        txt = f"✅ 反馈已收到{caller_source_info}"

    # 根据调用来源处理图片
    if GLOBAL_CALLER_SOURCE == "augment" and img_b64_list:
        # Augment 调用：简化处理，只返回文本说明
        txt += f"\n\n📷 检测到 {len(img_b64_list)} 张图片（Augment调用模式）"
        logger.info(f"Augment调用: 检测到 {len(img_b64_list)} 张图片")
        return txt
    else:
        # 其他调用方式（Cursor等）：返回 Image 对象
        images: List[Image] = []
        for b64 in img_b64_list:
            try:
                img_bytes = base64.b64decode(b64)
                images.append(Image(data=img_bytes, format="png"))
            except Exception:
                # 若解码失败，忽略该图片并在文字中提示
                txt += f"\n\n[warning] 有一张图片解码失败。"

        # 根据返回的实际内容组装 tuple
        if txt and images:
            return (txt, *images)
        elif txt:
            return (txt,)
        elif images:
            return (images[0],) if len(images) == 1 else tuple(images)
        else:
            return (caller_source_info,)



if __name__ == "__main__":
    mcp.run(transport="stdio")
