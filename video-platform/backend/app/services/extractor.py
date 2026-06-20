"""
关键词提取服务 - 支持多种AI协议
"""

import json
from pathlib import Path
from openai import OpenAI


def extract_keywords(transcribe_result: list, api_key: str, base_url: str, model: str, output_path: str) -> list:
    """
    使用AI提取关键词和生成提示词

    Args:
        transcribe_result: Whisper转写结果
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
        output_path: 输出JSON路径

    Returns:
        提取结果列表 [{"text": "...", "search_keyword": "...", "ai_prompt": "..."}]
    """
    if not api_key:
        raise Exception("API密钥未配置")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # 合并短文本
    merged_texts = merge_short_texts(transcribe_result)

    # 提取关键词
    client = OpenAI(api_key=api_key, base_url=base_url)
    result = []

    for item in merged_texts:
        text = item["text"]

        # 调用AI提取关键词
        prompt = f"""请为以下文本提取：
1. 搜索关键词（用于在图库搜索相关图片，用中文，2-4个字）
2. AI生图提示词（用英文描述，用于AI生成图片）

文本：{text}

请用JSON格式回复：
{{"search_keyword": "关键词", "ai_prompt": "English prompt for AI image generation"}}"""

        try:
            response = client.chat.completions.create(
                model=model or "gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = response.choices[0].message.content
            # 解析JSON
            parsed = json.loads(content)
            result.append({
                "text": text,
                "search_keyword": parsed.get("search_keyword", ""),
                "ai_prompt": parsed.get("ai_prompt", ""),
                "start": item.get("start"),
                "end": item.get("end"),
            })
        except Exception as e:
            print(f"[WARN] AI提取失败: {e}")
            result.append({
                "text": text,
                "search_keyword": text[:4],
                "ai_prompt": text,
                "start": item.get("start"),
                "end": item.get("end"),
            })

    print(f"[INFO] 关键词提取完成: {len(result)} 个片段")

    # 保存结果
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def merge_short_texts(transcribe_result: list, min_duration: float = 3.0) -> list:
    """
    合并过短的文本片段

    Args:
        transcribe_result: Whisper转写结果
        min_duration: 最小时长（秒）

    Returns:
        合并后的文本列表
    """
    if not transcribe_result:
        return []

    merged = []
    current = {
        "text": transcribe_result[0]["text"],
        "start": transcribe_result[0]["start"],
        "end": transcribe_result[0]["end"],
    }

    for item in transcribe_result[1:]:
        duration = current["end"] - current["start"]

        if duration < min_duration:
            # 合并
            current["text"] += item["text"]
            current["end"] = item["end"]
        else:
            merged.append(current)
            current = {
                "text": item["text"],
                "start": item["start"],
                "end": item["end"],
            }

    merged.append(current)
    return merged
