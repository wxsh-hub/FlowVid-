"""
图片获取服务 - 支持多种AI生图协议，使用线程池并行处理
"""

import os
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_images(keywords_result: list, api_key: str, base_url: str, model: str, protocol: str, output_dir: str) -> list:
    """
    获取图片（搜图 + 生图）- 使用线程池并行处理

    Args:
        keywords_result: 关键词提取结果
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
        protocol: 协议类型 (doubao / dashscope / openai / custom)
        output_dir: 输出目录

    Returns:
        图片路径列表 [{"index": 0, "image_path": "...", "keyword": "..."}]
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # 准备任务列表
    tasks = []
    for i, item in enumerate(keywords_result):
        keyword = item.get("search_keyword", "")
        ai_prompt = item.get("ai_prompt", "")
        output_path = str(output / f"{i:03d}_{keyword}.jpg")
        tasks.append({
            "index": i,
            "keyword": keyword,
            "ai_prompt": ai_prompt,
            "output_path": output_path,
        })

    print(f"[INFO] 开始并行获取 {len(tasks)} 张图片...")

    # 使用线程池并行处理
    result = [None] * len(tasks)
    max_workers = min(4, len(tasks))  # 最多4个线程

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_task = {}
        for task in tasks:
            future = executor.submit(
                _fetch_single_image,
                task["keyword"],
                task["ai_prompt"],
                task["output_path"],
                api_key,
                base_url,
                model,
                protocol,
            )
            future_to_task[future] = task

        # 收集结果
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                image_path = future.result()
                result[task["index"]] = {
                    "index": task["index"],
                    "image_path": image_path,
                    "keyword": task["keyword"],
                }
                print(f"[INFO] 图片 {task['index']+1}/{len(tasks)} 完成: {task['keyword']}")
            except Exception as e:
                print(f"[WARN] 图片 {task['index']+1} 获取失败: {e}")
                result[task["index"]] = {
                    "index": task["index"],
                    "image_path": create_placeholder(task["keyword"], task["output_path"]),
                    "keyword": task["keyword"],
                }

    # 确保所有结果都已填充
    for i in range(len(result)):
        if result[i] is None:
            result[i] = {
                "index": i,
                "image_path": create_placeholder(tasks[i]["keyword"], tasks[i]["output_path"]),
                "keyword": tasks[i]["keyword"],
            }

    print(f"[INFO] 图片获取完成: {len(result)} 张")
    return result


def _fetch_single_image(keyword: str, ai_prompt: str, output_path: str,
                         api_key: str, base_url: str, model: str, protocol: str) -> str:
    """
    获取单张图片（搜图 + 生图）

    Args:
        keyword: 搜索关键词
        ai_prompt: AI生图提示词
        output_path: 输出路径
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
        protocol: 协议类型

    Returns:
        图片路径或None
    """
    image_path = None

    # 尝试Pexels搜图（使用默认API）
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if keyword:
        image_path = search_pexels(keyword, pexels_key, output_path)

    # 如果搜图失败，使用AI生图
    if not image_path and api_key and ai_prompt:
        image_path = generate_image(ai_prompt, api_key, base_url, model, protocol, output_path)

    return image_path


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
                    return output_path

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
    try:
        if protocol == "doubao":
            return generate_image_doubao(prompt, api_key, base_url, model, output_path)
        elif protocol == "dashscope":
            return generate_image_dashscope(prompt, api_key, base_url, model, output_path)
        elif protocol == "openai":
            return generate_image_openai(prompt, api_key, base_url, model, output_path)
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

    print(f"[WARN] 豆包生图失败: {response.status_code}")
    return None


def generate_image_dashscope(prompt: str, api_key: str, base_url: str, model: str, output_path: str) -> str:
    """阿里百炼异步生图"""
    import requests

    # 提交异步任务
    url = base_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-DashScope-Async": "enable"  # 启用异步调用
    }
    payload = {
        "model": model or "wanx-v1",
        "input": {"prompt": prompt},
        "parameters": {
            "size": "1024*1024",
            "n": 1
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        print(f"[WARN] 阿里百炼提交任务失败: {response.status_code}")
        return None

    result = response.json()
    task_id = result.get("output", {}).get("task_id")

    if not task_id:
        print(f"[WARN] 阿里百炼未返回task_id")
        return None

    # 轮询查询任务状态
    query_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    query_headers = {
        "Authorization": f"Bearer {api_key}"
    }

    max_retries = 30  # 最多等待60秒
    for i in range(max_retries):
        time.sleep(2)  # 每2秒查询一次

        query_response = requests.get(query_url, headers=query_headers, timeout=30)
        if query_response.status_code != 200:
            continue

        query_result = query_response.json()
        status = query_result.get("output", {}).get("task_status")

        if status == "SUCCEEDED":
            # 获取图片URL
            results = query_result.get("output", {}).get("results", [])
            if results:
                img_url = results[0].get("url")
                if img_url:
                    return download_image(img_url, output_path)
            return None
        elif status == "FAILED":
            error_msg = query_result.get("output", {}).get("message", "未知错误")
            print(f"[WARN] 阿里百炼任务失败: {error_msg}")
            return None

    print(f"[WARN] 阿里百炼任务超时")
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
        return output_path

    except Exception as e:
        print(f"[WARN] 创建占位图失败: {e}")
        return None
