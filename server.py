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
from typing import Annotated, Dict, Tuple, List

from fastmcp import FastMCP, Image
from pydantic import Field

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

def _detect_caller_project_context():
    """检测调用方项目上下文信息"""
    try:
        import psutil
        current_process = psutil.Process()
        
        # 尝试获取调用方工作目录
        caller_cwd = None
        
        # 方法1: 从父进程获取工作目录
        try:
            parent_process = current_process.parent()
            if parent_process and hasattr(parent_process, 'cwd'):
                parent_cwd = parent_process.cwd()
                # 检查是否为有效的项目目录
                if _is_project_directory(parent_cwd):
                    caller_cwd = parent_cwd
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # 方法2: 从环境变量获取（如果调用方已设置）
        if not caller_cwd:
            env_cwd = os.environ.get('PWD') or os.environ.get('OLDPWD')
            if env_cwd and _is_project_directory(env_cwd):
                caller_cwd = env_cwd
        
        # 方法3: 使用当前工作目录作为回退
        if not caller_cwd:
            current_cwd = os.getcwd()
            # 如果当前目录不是MCP服务器目录，则可能是调用方目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if current_cwd != script_dir and _is_project_directory(current_cwd):
                caller_cwd = current_cwd
        
        # 获取项目基本信息
        if caller_cwd:
            project_name = os.path.basename(caller_cwd)
            return {
                'cwd': caller_cwd,
                'name': project_name,
                'is_detected': True
            }
        else:
            return {
                'cwd': os.getcwd(),
                'name': 'unknown',
                'is_detected': False
            }
            
    except ImportError:
        # 如果psutil不可用，使用基本方法
        return {
            'cwd': os.getcwd(),
            'name': os.path.basename(os.getcwd()),
            'is_detected': False
        }
    except Exception:
        return {
            'cwd': os.getcwd(),
            'name': 'unknown',
            'is_detected': False
        }

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
    # Create a temporary file for the feedback result
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        # 检测调用方项目上下文
        caller_context = _detect_caller_project_context()
        
        # 使用传入的参数覆盖自动检测的值
        caller_cwd = project_path or caller_context['cwd']
        effective_project_name = project_name or caller_context['name']
        
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
            import json
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
            raise Exception(f"Failed to launch feedback UI: {result.returncode}")

        # Read the result from the temporary file
        with open(output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        os.unlink(output_file)
        return result
    except Exception as e:
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

@mcp.tool()
def interactive_feedback(
    message: str = Field(description="The specific question for the user"),
    predefined_options: list = Field(default=None, description="Predefined options for the user to choose from (optional)"),
    project_path: str = Field(default=None, description="Override project path (optional, auto-detected if not provided)"),
    project_name: str = Field(default=None, description="Override project name (optional, auto-detected if not provided)"),
    git_branch: str = Field(default=None, description="Override git branch name (optional, auto-detected if not provided)"),
    priority: int = Field(default=3, description="Priority level 1-5 (1=lowest, 5=highest, default=3)"),
    category: str = Field(default="general", description="Category: bug|feature|review|performance|docs|test|deploy|other"),
    context_data: dict = Field(default=None, description="Additional context data as key-value pairs"),
) -> Tuple[str | Image, ...]:
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
    img_b64_list: List[str] = result_dict.get("images", [])

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
        return txt
    elif images:
        return (images[0],) if len(images) == 1 else tuple(images)
    else:
        return ("",)

if __name__ == "__main__":
    mcp.run(transport="stdio")
