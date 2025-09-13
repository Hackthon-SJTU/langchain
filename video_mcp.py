from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Dict, List, TypedDict


class VideoResponse(TypedDict):
    status: str
    video_url: str
    last_frame_url: str

import os
from pathlib import Path
from typing import Annotated, List

from fastmcp import FastMCP
from fastmcp.utilities.types import File as MCPFile

mcp = FastMCP("video-stream-mock")


def find_video_directory() -> Path:
    """查找可用的视频目录。

    按优先级查找以下目录：
    1. vedios/
    """
    project_root = Path(__file__).parent.parent
    possible_dirs = ["vedios"]
    
    for dir_name in possible_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            return dir_path
            
    raise FileNotFoundError(f"未找到视频目录，请确保以下任一目录存在：{', '.join(possible_dirs)}")


def get_available_videos(video_dir: Path) -> List[Path]:
    """获取指定目录下的所有 MP4 视频文件。"""
    if not video_dir.exists():
        return []
        
    return sorted(
        [f for f in video_dir.glob("*.mp4") if f.is_file()],
        key=lambda x: int(''.join(filter(str.isdigit, x.stem)))
    )


@mcp.tool
def get_video_stream(
    image_url: Annotated[str, "输入图片的URL或路径"] = "",
    gpt_prompt: Annotated[str, "DeepSeek提炼的核心prompt"] = "",
    is_first_frame: Annotated[bool, "是否作为首帧"] = True,
    duration: Annotated[int, "视频时长(秒)"] = 4,
    turns: Annotated[int, "当前对话轮次，用于选择对应的视频文件"] = 0,
) -> Dict:
    """Mock的视频生成服务，根据轮次返回预设的视频。

    Args:
        image_url: 输入图片的URL或路径（mock服务中未使用）
        gpt_prompt: DeepSeek提炼的核心prompt（mock服务中未使用）
        is_first_frame: 是否作为首帧（mock服务中未使用）
        duration: 视频时长，固定为4秒（mock服务中未使用）
        turns: 当前对话轮次，用于选择对应的视频文件

    Returns:
        Dict: {
            "status": "success",
            "video_url": str,  # 视频文件的路径
            "last_frame_url": str  # 最后一帧图片的路径（mock固定值）
        }

    Raises:
        ValueError: 当 turns 参数为负数时
        FileNotFoundError: 当视频目录或指定轮次的视频文件不存在时
    """
    if turns < 0:
        raise ValueError(f"视频轮次必须为非负数，当前值: {turns}")
        
    try:
        video_dir = find_video_directory()
        available_videos = get_available_videos(video_dir)
        
        if not available_videos:
            raise FileNotFoundError(f"在 {video_dir} 目录下未找到任何 MP4 视频文件")
            
        if turns >= len(available_videos):
            raise ValueError(f"视频轮次 {turns} 超出范围，当前共有 {len(available_videos)} 个视频文件")
            
        video_path = available_videos[turns]
        
        if not os.access(video_path, os.R_OK):
            raise PermissionError(f"无法读取视频文件: {video_path}")
            
        return {
            "status": "success",
            "video_url": str(video_path),
            "last_frame_url": "/outputs/last_frame.png"  # Mock的最后一帧图片路径
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    mcp.run()
