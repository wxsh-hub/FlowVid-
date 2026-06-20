"""
图片获取服务 (Pexels搜图 + Seedream生图)
"""

import os
import json
from pathlib import Path
from openai import OpenAI


def fetch_images(keywords_result: list, pexels_key: str, seedream_key: str, output_dir: str) -> list:
    """
    获取图片（搜图 + 生图）

    Args:
        keywords_result: 关键词提取结果
        pexels_key: Pexels API密钥
        seedream_key: Seedream API密钥
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

        # 尝试Pexels搜图
        if pexels_key and keyword:
            image_path = search_pexels(keyword, pexels_key, str(output / f"{i:03d}_{keyword}.jpg"))

        # 如果搜图失败，使用AI生图
        if not image_path and seedream_key and ai_prompt:
            image_path = generate_image_seedream(ai_prompt, seedream_key, str(output / f"{i:03d}_{keyword}.jpg"))

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


def generate_image_seedream(prompt: str, api_key: str, output_path: str) -> str:
    """
    使用豆包Seedream生成图片

    Args:
        prompt: 生图提示词
        api_key: API密钥 (格式: ark-xxx)
        output_path: 输出路径

    Returns:
        图片路径或None
    """
    import requests

    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "doubao-seedream-4-5-251128",
        "prompt": prompt,
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": "2K",  # 最小尺寸要求
        "stream": False,
        "watermark": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            data = response.json()
            images = data.get("data", [])

            if images:
                img_url = images[0].get("url")
                if img_url:
                    # 下载图片
                    img_response = requests.get(img_url, timeout=60)
                    if img_response.status_code == 200:
                        with open(output_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"[INFO] Seedream生图成功")
                        return output_path

            print(f"[WARN] Seedream返回数据异常: {data}")
            return None
        else:
            print(f"[WARN] Seedream请求失败: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"[WARN] Seedream生图异常: {e}")
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
