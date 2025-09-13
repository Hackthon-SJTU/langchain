import subprocess
import os
from pathlib import Path

def get_video_duration(video_path):
    """获取视频时长（秒）"""
    cmd = [
        'ffprobe', 
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    output = subprocess.check_output(cmd).decode().strip()
    return float(output)

def trim_video(input_path, output_path, seconds_to_trim=10):
    """
    从视频末尾切除指定秒数
    :param input_path: 输入视频路径
    :param output_path: 输出视频路径
    :param seconds_to_trim: 要从末尾切除的秒数（默认10秒）
    """
    try:
        # 获取视频总时长
        duration = get_video_duration(input_path)
        
        # 计算新的结束时间
        new_duration = duration - seconds_to_trim
        
        if new_duration <= 0:
            print(f"错误: 视频 {input_path} 长度小于 {seconds_to_trim} 秒")
            return False
            
        # 使用ffmpeg切除最后10秒
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-t', str(new_duration),
            '-c', 'copy',  # 复制编解码器，不重新编码
            '-y',  # 覆盖输出文件（如果存在）
            output_path
        ]
        
        subprocess.run(cmd, check=True)
        print(f"成功处理视频: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"处理视频时出错: {e}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False

if __name__ == "__main__":
    # 获取当前目录下所有mp4文件
    video_files = list(Path('.').glob('*.mp4'))
    
    if not video_files:
        print("当前目录下没有找到MP4文件")
        exit(1)
        
    # 创建输出目录
    output_dir = Path('trimmed_videos')
    output_dir.mkdir(exist_ok=True)
    
    # 处理每个视频文件
    for video_file in video_files:
        output_path = output_dir / f"trimmed_{video_file.name}"
        print(f"\n处理视频: {video_file}")
        trim_video(str(video_file), str(output_path))
