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
from typing import Annotated, Dict, Tuple, List, Optional

from fastmcp import FastMCP, Image
from pydantic import Field

# 导入日志系统
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui.utils.logging_system import init_logging, get_logger, log_performance, log_project_context

# 初始化日志系统
logging_manager = init_logging({
    'level': 'INFO',
    'console_enabled': True,
    'console_level': 'WARNING',  # 控制台只显示警告和错误
    'performance_enabled': True,
    'project_context_enabled': True
})

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

# 获取主日志记录器
logger = get_logger('mcp_server')

def _detect_caller_project_context():
    """检测调用方项目上下文信息"""
    with log_performance("detect_caller_project_context", "project_detection"):
        try:        
            # 尝试获取调用方工作目录
            caller_cwd = None
            
            # 方法1: 深度进程链检测
            try:
                import psutil
                current_process = psutil.Process()
                
                # 遍历进程链，寻找真正的调用方
                process_chain = []
                temp_process = current_process
                
                for i in range(5):  # 最多检查5层父进程
                    try:
                        parent = temp_process.parent()
                        if parent:
                            process_info = {
                                'pid': parent.pid,
                                'name': parent.name(),
                                'cwd': parent.cwd() if hasattr(parent, 'cwd') else None,
                                'cmdline': ' '.join(parent.cmdline()[:3]) if hasattr(parent, 'cmdline') else None
                            }
                            process_chain.append(process_info)
                            
                            # 检查是否是项目目录
                            if process_info['cwd'] and _is_project_directory(process_info['cwd']):
                                # 确保不是我们自己的目录
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                if process_info['cwd'] != script_dir:
                                    caller_cwd = process_info['cwd']
                                    logger.info(f"从进程链检测到项目: {caller_cwd} (进程: {process_info['name']})")
                                    break
                            
                            temp_process = parent
                        else:
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                        break
                
                # 记录完整的进程链用于调试
                logger.info(f"进程链分析: {process_chain}")
                
            except (ImportError, Exception) as e:
                logger.debug(f"进程链检测失败: {e}")
            
            # 方法2: 环境变量全面检测
            if not caller_cwd:
                env_vars_to_check = ['PWD', 'OLDPWD', 'INIT_CWD', 'npm_config_user_config', 'PROJECT_ROOT']
                
                for env_var in env_vars_to_check:
                    env_value = os.environ.get(env_var)
                    if env_value and os.path.exists(env_value) and _is_project_directory(env_value):
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        if env_value != script_dir:
                            caller_cwd = env_value
                            logger.info(f"从环境变量{env_var}检测到项目: {env_value}")
                            break
                
                # 记录所有环境变量用于调试
                relevant_env = {k: v for k, v in os.environ.items() 
                              if any(keyword in k.lower() for keyword in ['pwd', 'cwd', 'dir', 'path', 'project', 'root'])}
                logger.info(f"相关环境变量: {relevant_env}")
            
            # 方法3: 文件系统智能检测
            if not caller_cwd:
                # 检查是否有临时文件或缓存文件指示调用方项目
                temp_dirs = ['/tmp', os.path.expanduser('~/tmp'), os.path.expanduser('~/.cache')]
                
                for temp_dir in temp_dirs:
                    if os.path.exists(temp_dir):
                        try:
                            # 查找最近修改的与项目相关的文件
                            for root, dirs, files in os.walk(temp_dir):
                                for file in files:
                                    if any(keyword in file.lower() for keyword in ['cursor', 'mcp', 'project']):
                                        filepath = os.path.join(root, file)
                                        try:
                                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                                content = f.read(1000)  # 只读前1000字符
                                                # 查找路径模式
                                                import re
                                                path_matches = re.findall(r'/[^/\s]+/[^/\s]+/[^/\s\'"]+', content)
                                                for path in path_matches:
                                                    if os.path.exists(path) and _is_project_directory(path):
                                                        caller_cwd = path
                                                        logger.info(f"从临时文件检测到项目: {path}")
                                                        break
                                        except:
                                            continue
                                        if caller_cwd:
                                            break
                                if caller_cwd:
                                    break
                        except:
                            continue
                        if caller_cwd:
                            break
            
            # 方法4: 当前工作目录检测
            if not caller_cwd:
                current_cwd = os.getcwd()
                script_dir = os.path.dirname(os.path.abspath(__file__))
                
                if current_cwd != script_dir and _is_project_directory(current_cwd):
                    caller_cwd = current_cwd
                    logger.info(f"从当前工作目录检测到项目: {current_cwd}")
                elif _is_project_directory(current_cwd):
                    caller_cwd = current_cwd
                    logger.info(f"使用当前目录作为项目: {current_cwd}")
            
            # 获取项目基本信息
            project_name = os.path.basename(caller_cwd) if caller_cwd else 'unknown'
            is_detected = _is_project_directory(caller_cwd) if caller_cwd else False
            
            result = {
                'cwd': caller_cwd or os.getcwd(),
                'name': project_name,
                'is_detected': is_detected
            }
            
            logger.info(f"项目检测完成: 项目={project_name}, 路径={caller_cwd or os.getcwd()}, 有效={is_detected}")
            
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
        
        logger.info(f"启动反馈UI: 优先级={priority}, 类别={category}")
        
        # Create a temporary file for the feedback result
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            output_file = tmp.name

        try:
            # 检测调用方项目上下文
            caller_context = _detect_caller_project_context()
            
            # 使用传入的参数覆盖自动检测的值
            caller_cwd = project_path or caller_context['cwd']
            effective_project_name = project_name or caller_context['name']
            
            # 设置日志系统的项目上下文
            logging_manager.set_project_context(effective_project_name)
            
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

    # 把 base64 变成 Image 对象
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
        return ("",)

if __name__ == "__main__":
    mcp.run(transport="stdio")
