#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import json
import argparse

def get_video_duration(video_path):
    """
    获取视频的总时长（秒）
    
    Args:
        video_path: 视频文件路径
    Returns:
        float: 视频时长（秒）
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        str(video_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
    except subprocess.CalledProcessError as e:
        raise Exception(f"获取视频时长失败: {str(e)}")
    except (KeyError, json.JSONDecodeError) as e:
        raise Exception(f"解析视频信息失败: {str(e)}")

def extract_last_frame(video_path, output_path=None):
    """
    提取视频的最后一帧
    
    Args:
        video_path: 视频文件路径
        output_path: 输出图片路径，如果不指定则在同目录下创建
    Returns:
        str: 输出图片的路径
    """
    video_path = Path(video_path)
    
    # 如果没有指定输出路径，则使用默认路径
    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_last_frame.jpg"
    else:
        output_path = Path(output_path)
    
    try:
        # 获取视频时长
        duration = get_video_duration(video_path)
        
        # 构建 ffmpeg 命令
        cmd = [
            'ffmpeg',
            '-y',  # 覆盖已存在的文件
            '-ss', str(duration - 0.1),  # 定位到最后 0.1 秒
            '-i', str(video_path),
            '-vframes', '1',  # 只提取一帧
            '-q:v', '2',  # 设置质量（2 是较高质量）
            str(output_path)
        ]
        
        # 执行命令
        subprocess.run(cmd, check=True, capture_output=True)
        
        print(f"✓ 成功提取最后一帧:")
        print(f"  - 输入视频: {video_path}")
        print(f"  - 视频时长: {duration:.2f} 秒")
        print(f"  - 输出图片: {output_path}")
        
        return str(output_path)
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"提取帧失败: {e.stderr.decode()}")
    except Exception as e:
        raise Exception(f"处理过程出错: {str(e)}")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='提取视频最后一帧')
    parser.add_argument('video_path', help='输入视频的路径')
    parser.add_argument('-o', '--output', help='输出图片的路径（可选）')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    try:
        # 确认输入视频存在
        if not Path(args.video_path).exists():
            raise FileNotFoundError(f"找不到视频文件: {args.video_path}")
            
        # 提取最后一帧
        extract_last_frame(args.video_path, args.output)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
