import os
import time
from pathlib import Path
from image_generator import text_to_image
def test_text_to_image():
    """
    测试 text_to_image 函数的各种场景
    """
    # 测试用的提示词列表
    test_prompts = [
        
        "一位英俊的骑手独自骑马，荒凉的草原，末日后的废土，衰败景象，电影级构图，戏剧性光线，低角度拍摄，风尘仆仆的帅气男子穿着磨损的皮夹克，风吹拂的头发，金色时刻光照。"
    ]

    print("\n=== 开始测试文本生成图像功能 ===\n")
    print(f"将生成 {len(test_prompts)} 张测试图片...")
    
    successful_tests = 0
    failed_tests = 0
    
    # 创建保存结果的目录
    output_dir = Path("./test_results")
    output_dir.mkdir(exist_ok=True)
    
    for i, prompt in enumerate(test_prompts, 1):
        try:
            # 为每个提示词生成不同的输出文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"test_image_{i}_{timestamp}.png"
            
            print(f"\n测试 {i}/{len(test_prompts)}:")
            print(f"提示词: {prompt[:100]}...")
            print("生成图像中...")
            
            # 记录开始时间
            start_time = time.time()
            
            # 调用函数生成图像
            result_path = text_to_image(prompt, str(output_file))
            
            # 计算耗时
            generation_time = time.time() - start_time
            
            # 验证文件是否生成
            if Path(result_path).exists():
                file_size = Path(result_path).stat().st_size
                print(f"✓ 成功生成图像:")
                print(f"  - 保存路径: {result_path}")
                print(f"  - 文件大小: {file_size/1024:.2f}KB")
                print(f"  - 生成耗时: {generation_time:.2f}秒")
                successful_tests += 1
            else:
                print(f"✗ 错误: 文件未生成: {result_path}")
                failed_tests += 1
                
        except Exception as e:
            print(f"✗ 错误: {str(e)}")
            failed_tests += 1
        
        # 测试间隔，避免请求过快
        if i < len(test_prompts):
            print("\n等待 3 秒后继续下一个测试...")
            time.sleep(3)
    
    # 打印测试总结
    print("\n=== 测试结果总结 ===")
    print(f"总计测试: {len(test_prompts)} 个场景")
    print(f"成功: {successful_tests} 个")
    print(f"失败: {failed_tests} 个")
    print(f"成功率: {(successful_tests/len(test_prompts))*100:.1f}%")
    print(f"\n生成的图片保存在: {output_dir}")

def main():
    """
    主函数，检查环境变量并运行测试
    """
    # 确保环境变量已设置
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("错误: 请先设置 DASHSCOPE_API_KEY 环境变量")
        print("使用方式: export DASHSCOPE_API_KEY='你的API密钥'")
        exit(1)
    
    print(f"使用 API Key: {api_key[:8]}...{api_key[-4:]}")
    test_text_to_image()

if __name__ == "__main__":
    main()
