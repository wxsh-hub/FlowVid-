"""
视频合成服务 (MoviePy)
"""

from pathlib import Path


def make_video(images_result: list, tts_result: list, keywords_result: list, output_path: str) -> str:
    """
    合成视频

    Args:
        images_result: 图片列表
        tts_result: TTS音频列表
        keywords_result: 关键词结果
        output_path: 输出视频路径

    Returns:
        输出视频路径
    """
    try:
        from moviepy import (
            ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
            concatenate_videoclips
        )
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
    except ImportError:
        raise Exception("moviepy或Pillow未安装")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # 创建视频片段
    clips = []

    # 对齐三个列表长度：以最短的为准，避免IndexError
    min_len = min(len(images_result), len(tts_result), len(keywords_result))
    if min_len < max(len(images_result), len(tts_result), len(keywords_result)):
        print(f"[WARN] 列表长度不一致: images={len(images_result)}, tts={len(tts_result)}, keywords={len(keywords_result)}，截取到 {min_len}")

    for i in range(min_len):
        img_item = images_result[i]
        tts_item = tts_result[i]
        img_path = img_item.get("image_path")
        audio_path = tts_item.get("audio_path")
        duration = tts_item.get("duration", 3.0)
        text = keywords_result[i].get("text", "")

        if not img_path or not Path(img_path).exists():
            continue

        # 创建图片片段
        img_clip = ImageClip(img_path).with_duration(duration)

        # 调整图片尺寸为1920x1080
        img_clip = img_clip.resized((1920, 1080))

        # 添加音频
        if audio_path and Path(audio_path).exists():
            audio_clip = AudioFileClip(audio_path)
            img_clip = img_clip.with_audio(audio_clip)

        # 添加字幕
        if text:
            # 分割长文本
            subtitle_text = split_subtitle(text)
            txt_clip = TextClip(
                text=subtitle_text,
                font_size=36,
                color='white',
                bg_color='black',
                size=(1600, None),
                method='caption',
            ).with_duration(duration)
            txt_clip = txt_clip.with_position(('center', 850))
            img_clip = CompositeVideoClip([img_clip, txt_clip])

        clips.append(img_clip)

    if not clips:
        raise Exception("没有有效的视频片段")

    # 合并所有片段
    final_video = concatenate_videoclips(clips, method="compose")

    # 导出视频
    final_video.write_videofile(
        str(output),
        fps=30,
        codec='libx264',
        audio_codec='aac',
        threads=4,
        preset='medium',
    )

    # 清理
    final_video.close()
    for clip in clips:
        clip.close()

    print(f"[INFO] 视频合成完成: {output_path}")
    return str(output)


def split_subtitle(text: str, max_chars: int = 20) -> str:
    """
    分割字幕文本

    Args:
        text: 原始文本
        max_chars: 每行最大字符数

    Returns:
        分割后的文本
    """
    if len(text) <= max_chars:
        return text

    # 按标点符号分割
    import re
    parts = re.split(r'[，。！？、；]', text)
    parts = [p.strip() for p in parts if p.strip()]

    lines = []
    current_line = ""

    for part in parts:
        if len(current_line) + len(part) <= max_chars:
            current_line += part
        else:
            if current_line:
                lines.append(current_line)
            current_line = part

    if current_line:
        lines.append(current_line)

    return '\n'.join(lines[:2])  # 最多2行
