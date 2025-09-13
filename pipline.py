# pipeline.py
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.chains import SequentialChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek 

import subprocess
import requests
import os
from pathlib import Path
from gradio_client import Client, handle_file

TMP = Path("./tmp")
TMP.mkdir(exist_ok=True)

# ---- Tool 1: text -> image ----
@tool
def text_to_image(prompt: str, out_name: str = "img.png") -> str:
    """
    使用阿里云 DashScope API 将文本转换为图像。
    Args:
        prompt: 图像描述文本
        out_name: 输出图像文件名
    Returns:
        生成的图像本地路径
    """
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量")

    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "qwen-image",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        },
        "parameters": {
            "negative_prompt": "",
            "prompt_extend": True,
            "watermark": True,
            "size": "1328*1328"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # 从响应中获取图像 URL 并下载
        if 'output' in result and 'results' in result['output']:
            image_url = result['output']['results'][0].get('url')
            if image_url:
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                
                out_path = TMP / out_name
                with open(out_path, "wb") as f:
                    f.write(image_response.content)
                return str(out_path)
            
        raise Exception("未能从 API 响应中获取图像 URL")
    except Exception as e:
        raise Exception(f"调用 DashScope API 失败: {str(e)}")

# ---- Tool 2: image -> video ----
@tool
def image_to_video(image_path: str, prompt: str = "", duration_s: int = 8, out_name: str = "out.mp4") -> str:
    """
    输入图片路径，调用 image->video 服务，返回视频本地路径
    TODO: 用 Runway/Gen-2 等 API 替换伪代码
    """
    out_path = TMP / out_name
    # 伪代码：调用 Runway 的 image->video 接口并将返回二进制写入 out_path
    # e.g. requests.post("https://api.runwayml.com/v1/generate_video", files=..., data=...)
    open(out_path, "wb").write(b"MP4-DUMMY")
    return str(out_path)

# ---- Tool 3: video -> music ----
@tool
def video_to_music(video_path: str, mood: str = "epic", length_s: int = 8, out_name: str = "music.mp3") -> str:
    """
    使用 HuggingFace 的 image-to-music 模型，从视频的第一帧生成音乐
    Args:
        video_path: 输入视频路径
        mood: 音乐情绪（暂未使用）
        length_s: 期望的音乐长度（秒）
        out_name: 输出音频文件名
    Returns:
        生成的音频文件路径
    """
    # 确保输出目录存在
    out_path = TMP / out_name
    
    try:
        # 创建 HuggingFace 客户端
        client = Client("fffiloni/image-to-music-v2")
        
        # 从视频提取第一帧作为参考图像
        frame_path = TMP / "reference_frame.jpg"
        extract_cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vframes", "1",
            "-f", "image2",
            str(frame_path)
        ]
        subprocess.run(extract_cmd, check=True)
        
        # 调用 image-to-music API
        # 使用 ACE Step 模型，它通常产生较好的结果
        prompt, audio_path = client.predict(
            image_in=handle_file(str(frame_path)),
            chosen_model="ACE Step",
            api_name="/infer"
        )
        
        # 将生成的音频移动到指定位置
        import shutil
        shutil.copy(audio_path, out_path)
        
        # 清理临时文件
        frame_path.unlink(missing_ok=True)
        Path(audio_path).unlink(missing_ok=True)
        
        return str(out_path)
        
    except Exception as e:
        raise Exception(f"生成音乐失败: {str(e)}")
        
    return str(out_path)

# ---- Tool 4: merge audio + video using ffmpeg ----
@tool
def merge_audio_video(video_path: str, audio_path: str, out_name: str = "final.mp4") -> str:
    """
    使用 ffmpeg 把音频铺到视频上，返回合成后视频路径
    """
    out_path = TMP / out_name
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)
    return str(out_path)

# ---- Orchestration: 顺序执行（SequentialChain 风格，或者直接调用）----
def run_pipeline(user_prompt: str):
    img = text_to_image(prompt=user_prompt, out_name="frame.png")
    vid = image_to_video(image_path=img, prompt=user_prompt, duration_s=10, out_name="anim.mp4")
    music = video_to_music(video_path=vid, mood="ambient", length_s=10, out_name="bgm.mp3")
    final = merge_audio_video(video_path=vid, audio_path=music, out_name="final_with_music.mp4")
    return final

if __name__ == "__main__":
    res = run_pipeline("赛博朋克城市夜景，霓虹，雨中慢镜头")
    print("输出文件：", res)
