"""
视频合成服务 (MoviePy) - 支持中文字幕
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

    # 查找中文字体
    font_path = find_chinese_font()
    print(f"[INFO] 使用字体: {font_path}")

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
            print(f"[WARN] 图片不存在，跳过片段{i}: {img_path}")
            continue

        # 检查音频文件是否有效
        has_audio = False
        if audio_path and Path(audio_path).exists() and Path(audio_path).stat().st_size > 0:
            has_audio = True

        # 创建图片片段
        img_clip = ImageClip(img_path).with_duration(duration)

        # 调整图片尺寸为1920x1080
        img_clip = img_clip.resized((1920, 1080))

        # 添加音频
        if has_audio:
            try:
                audio_clip = AudioFileClip(audio_path)
                img_clip = img_clip.with_audio(audio_clip)
            except Exception as e:
                print(f"[WARN] 音频加载失败: {e}")

        # 添加字幕（使用Pillow渲染中文）
        if text and font_path:
            try:
                # 使用Pillow渲染字幕图片
                subtitle_img_path = render_subtitle_image(text, font_path, i)
                if subtitle_img_path:
                    subtitle_clip = ImageClip(subtitle_img_path).with_duration(duration)
                    subtitle_clip = subtitle_clip.with_position(('center', 850))
                    img_clip = CompositeVideoClip([img_clip, subtitle_clip])
            except Exception as e:
                print(f"[WARN] 字幕渲染失败: {e}")

        clips.append(img_clip)
        print(f"[INFO] 片段{i}: 图片={Path(img_path).name}, 音频={'有' if has_audio else '无'}, 字幕={'有' if text else '无'}")

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


def find_chinese_font():
    """查找中文字体"""
    import os

    # Windows字体路径
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",     # 黑体
        "C:/Windows/Fonts/simsun.ttc",     # 宋体
        "C:/Windows/Fonts/msyhbd.ttc",     # 微软雅黑粗体
    ]

    for path in font_paths:
        if os.path.exists(path):
            return path

    # 如果找不到，返回None
    print("[WARN] 未找到中文字体，字幕可能无法正常显示")
    return None


def render_subtitle_image(text: str, font_path: str, index: int) -> str:
    """
    使用Pillow渲染字幕图片

    Args:
        text: 字幕文本
        font_path: 字体路径
        index: 片段索引

    Returns:
        字幕图片路径
    """
    from PIL import Image, ImageDraw, ImageFont
    import os
    import tempfile

    # 分割长文本
    max_chars = 20
    lines = []
    current_line = ""

    for char in text:
        current_line += char
        if len(current_line) >= max_chars:
            lines.append(current_line)
            current_line = ""
    if current_line:
        lines.append(current_line)

    # 最多显示2行
    lines = lines[:2]
    subtitle_text = "\n".join(lines)

    # 创建字幕图片
    width = 1600
    height = 120

    # 创建透明背景
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 绘制半透明黑色背景
    draw.rectangle([0, 0, width, height], fill=(0, 0, 0, 180))

    # 加载字体
    try:
        font = ImageFont.truetype(font_path, 40)
    except:
        font = ImageFont.load_default()

    # 计算文本位置
    bbox = draw.textbbox((0, 0), subtitle_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # 绘制白色文字
    draw.text((x, y), subtitle_text, fill=(255, 255, 255, 255), font=font)

    # 保存图片
    output_path = os.path.join(tempfile.gettempdir(), f"subtitle_{index}.png")
    img.save(output_path, 'PNG')

    return output_path


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
