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

def launch_feedback_ui(summary: str, predefinedOptions: list[str] | None = None) -> dict[str, str]:
    # Create a temporary file for the feedback result
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        # Get the path to enhanced_feedback_ui.py relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        feedback_ui_path = os.path.join(script_dir, "enhanced_feedback_ui.py")

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
            close_fds=True
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
) -> Tuple[str | Image, ...]:
    """
    Request interactive feedback from the user.
    """
    predefined_options_list = predefined_options if isinstance(predefined_options, list) else None
    result_dict = launch_feedback_ui(message, predefined_options_list)

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
