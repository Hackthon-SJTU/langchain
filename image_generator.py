import json
import os
import dashscope
import requests
from dashscope import MultiModalConversation

messages = [
    {
        "role": "user",
        "content": [
            {"text":  "宁静的森林景观，郁郁葱葱的绿色植物，参天大树和茂密的树叶，斑驳的阳光透过树冠，一条温柔的溪流蜿蜒穿过场景，河岸两旁生机勃勃的野花和蕨类植物，宁静而未受破坏的荒野，比较高视角"}
        ]
    }
]

# 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
api_key = 'sk-60b22327f9a7438b99245a48ac098f1b'

response = MultiModalConversation.call(
    api_key=api_key,
    model="qwen-image",
    messages=messages,
    result_format='message',
    stream=False,
    watermark=True,
    prompt_extend=True,
    negative_prompt='',
    size='1328*1328'
)

if response.status_code == 200:
    print(json.dumps(response, ensure_ascii=False))
    # 提取图片URL
    image_url = response['output']['choices'][0]['message']['content'][0]['image']
    # 下载图片
    response = requests.get(image_url)
    if response.status_code == 200:
        os.makedirs('./temp', exist_ok=True)
        image_path = './temp/downloaded_image.png'
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"图片已下载到: {image_path}")
    else:
        print(f"图片下载失败，HTTP返回码: {response.status_code}")
else:
    print(f"HTTP返回码：{response.status_code}")
    print(f"错误码：{response.code}")
    print(f"错误信息：{response.message}")
    print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")