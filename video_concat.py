import os
import subprocess

def concat_videos(input_dir='.', output_file='output.mp4', pattern='*.mp4'):
    """
    将指定目录下的所有MP4视频按文件名顺序拼接成一个视频
    
    Args:
        input_dir (str): 输入视频文件所在目录
        output_file (str): 输出视频文件名
        pattern (str): 文件匹配模式
    """
    # 获取所有mp4文件并排序
    video_files = [f for f in os.listdir(input_dir) if f.endswith('.mp4')]
    video_files.sort()  # 按文件名排序
    
    if not video_files:
        print("没有找到MP4文件")
        return
    
    # 创建一个临时文件列表
    with open('temp_file_list.txt', 'w', encoding='utf-8') as f:
        for video in video_files:
            # 使用完整路径
            full_path = os.path.join(input_dir, video)
            f.write(f"file '{full_path}'\n")
    
    try:
        # 使用ffmpeg的concat demuxer进行视频拼接
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', 'temp_file_list.txt',
            '-c', 'copy',  # 直接复制流，不重新编码
            output_file
        ]
        
        subprocess.run(cmd, check=True)
        print(f"视频拼接完成，输出文件: {output_file}")
    
    except subprocess.CalledProcessError as e:
        print(f"视频拼接失败: {e}")
    
    finally:
        # 清理临时文件
        if os.path.exists('temp_file_list.txt'):
            os.remove('temp_file_list.txt')

if __name__ == '__main__':
    # 可以直接运行脚本，使用默认参数
    concat_videos(output_file='combined_video.mp4')
