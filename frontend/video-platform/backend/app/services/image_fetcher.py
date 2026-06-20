"""
图片获取服务 - 支持多种AI生图协议
"""

import os
import json
from pathlib import Path


def fetch_images(keywords_result: list, api_key: str, base_url: str, model: str, protocol: str, output_dir: str) -> list:
    """
    获取图片（搜图 + 生图）

    Args:
        keywords_result: 关键词提取结果
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
        protocol: 协议类型 (doubao / openai / dashscope / custom)
        output_dir: 输出目录

    Returns:
        图片路径列表 [{"index": 0, "image_path": "...", "keyword": "..."}]
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    result = []

    for i, item in enumerate(keywords_result):
        keyword = item.get("search_keyword", "")
        ai_prompt = item.get("ai_prompt", "")

        image_path = None

        # 尝试Pexels搜图（使用默认API）
        pexels_key = os.environ.get("PEXELS_API_KEY", "")
        if keyword:
            image_path = search_pexels(keyword, pexels_key, str(output / f"{i:03d}_{keyword}.jpg"))

        # 如果搜图失败，使用AI生图
        if not image_path and api_key and ai_prompt:
            image_path = generate_image(ai_prompt, api_key, base_url, model, protocol, str(output / f"{i:03d}_{keyword}.jpg"))

        # 如果还是失败，使用占位图
        if not image_path:
            image_path = create_placeholder(keyword, str(output / f"{i:03d}_{keyword}.jpg"))

        result.append({
            "index": i,
            "image_path": image_path,
            "keyword": keyword,
        })

    print(f"[INFO] 图片获取完成: {len(result)} 张")
    return result


def search_pexels(keyword: str, api_key: str, output_path: str) -> str:
    """
    从Pexels搜索图片

    Args:
        keyword: 搜索关键词
        api_key: Pexels API密钥
        output_path: 输出路径

    Returns:
        图片路径或None
    """
    import requests

    if not api_key:
        print(f"[WARN] Pexels API密钥未配置，跳过搜图")
        return None

    headers = {"Authorization": api_key}
    params = {"query": keyword, "per_page": 1, "orientation": "landscape"}

    try:
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            photos = data.get("photos", [])

            if photos:
                # 下载图片
                img_url = photos[0]["src"]["large"]
                img_response = requests.get(img_url, timeout=30)

                if img_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"[INFO] Pexels搜图成功: {keyword}")
                    return output_path

        print(f"[WARN] Pexels搜图失败: {keyword}")
        return None

    except Exception as e:
        print(f"[WARN] Pexels搜图异常: {e}")
        return None


def generate_image(prompt: str, api_key: str, base_url: str, model: str, protocol: str, output_path: str) -> str:
    """
    使用AI生成图片（支持多种协议）

    Args:
        prompt: 生图提示词
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
        protocol: 协议类型
        output_path: 输出路径

    Returns:
        图片路径或None
    """
    import requests

    try:
        if protocol == "doubao":
            return generate_image_doubao(prompt, api_key, base_url, model, output_path)
        elif protocol == "openai":
            return generate_image_openai(prompt, api_key, base_url, model, output_path)
        elif protocol == "dashscope":
            return generate_image_dashscope(prompt, api_key, base_url, model, output_path)
        else:
            return generate_image_custom(prompt, api_key, base_url, model, output_path)
    except Exception as e:
        print(f"[WARN] AI生图失败: {e}")
        return None


def generate_image_doubao(prompt: str, api_key: str, base_url: str, model: str, output_path: str) -> str:
    """豆包协议生图"""
    import requests

    url = base_url or "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model or "doubao-seedream-4-5-251128",
        "prompt": prompt,
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": "2K",
        "stream": False,
        "watermark": False
    }

    response = requests.post(url, headers=headers, json=payload, timeout=120)

    if response.status_code == 200:
        data = response.json()
        images = data.get("data", [])
        if images:
            img_url = images[0].get("url")
            if img_url:
                return download_image(img_url, output_path)

    print(f"[WARN] 豆包生图失败: {response.status_code} - {response.text[:200]}")
    return None


def generate_image_openai(prompt: str, api_key: str, base_url: str, model: str, output_path: str) -> str:
    """OpenAI协议生图"""
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.images.generate(
        model=model or "dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )

    if response.data:
        img_url = response.data[0].url
        if img_url:
            return download_image(img_url, output_path)

    return None


def generate_image_dashscope(prompt: str, api_key: str, base_url: str, model: str, output_path: str) -> str:
    """通义万相协议生图"""
    import requests

    url = base_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model or "wanx-v1",
        "input": {"prompt": prompt},
        "parameters": {
            "size": "1024*1024",
            "n": 1
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=120)

    if response.status_code == 200:
        data = response.json()
        output = data.get("output", {})
        results = output.get("results", [])
        if results:
            img_url = results[0].get("url")
            if img_url:
                return download_image(img_url, output_path)

    print(f"[WARN] 通义万相生图失败: {response.status_code}")
    return None


def generate_image_custom(prompt: str, api_key: str, base_url: str, model: str, output_path: str) -> str:
    """自定义协议生图（通用OpenAI兼容格式）"""
    import requests

    url = base_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "response_format": "url",
        "size": "1024x1024",
        "n": 1
    }

    response = requests.post(url, headers=headers, json=payload, timeout=120)

    if response.status_code == 200:
        data = response.json()
        images = data.get("data", [])
        if images:
            img_url = images[0].get("url")
            if img_url:
                return download_image(img_url, output_path)

    print(f"[WARN] 自定义协议生图失败: {response.status_code}")
    return None


def download_image(img_url: str, output_path: str) -> str:
    """下载图片"""
    import requests

    try:
        img_response = requests.get(img_url, timeout=60)
        if img_response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            print(f"[INFO] 图片下载成功")
            return output_path
    except Exception as e:
        print(f"[WARN] 图片下载失败: {e}")

    return None


def create_placeholder(keyword: str, output_path: str) -> str:
    """
    创建占位图

    Args:
        keyword: 关键词
        output_path: 输出路径

    Returns:
        图片路径
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        # 创建纯色背景
        img = Image.new('RGB', (1920, 1080), color=(50, 50, 80))
        draw = ImageDraw.Draw(img)

        # 添加文字
        try:
            font = ImageFont.truetype("msyh.ttc", 60)
        except:
            font = ImageFont.load_default()

        # 绘制文字
        text = keyword or "图片"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (1920 - text_width) // 2
        y = (1080 - text_height) // 2
        draw.text((x, y), text, fill=(200, 200, 200), font=font)

        img.save(output_path, 'JPEG')
        print(f"[INFO] 创建占位图: {keyword}")
        return output_path

    except Exception as e:
        print(f"[WARN] 创建占位图失败: {e}")
        return None
