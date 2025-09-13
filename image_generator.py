import os
import requests
from pathlib import Path

# 创建临时目录用于存储生成的图片
TMP = Path("./tmp")
TMP.mkdir(exist_ok=True)

def text_to_image(prompt: str, out_name: str = "img.png") -> str:
    """
    使用阿里云 DashScope API 将文本转换为图像。
    Args:
        prompt: 图像描述文本
        out_name: 输出图像文件名
    Returns:
        生成的图像本地路径
    """
    api_key = 'sk-60b22327f9a7438b99245a48ac098f1b'
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
