"""
视频合成服务 (MoviePy) - 使用已验证的字幕渲染方案
"""

from pathlib import Path
from typing import List, Dict


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
        from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
    except ImportError:
        raise Exception("moviepy或Pillow未安装")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # 配置
    VIDEO_WIDTH = 1920
    VIDEO_HEIGHT = 1080
    FPS = 30
    FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
    FONT_SIZE = 44
    SUBTITLE_COLOR = (255, 255, 255)
    MAX_CHARS_PER_LINE = 18

    # 加载字体
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        print(f"[INFO] 使用字体: {FONT_PATH}")
    except Exception as e:
        print(f"[WARN] 加载字体失败: {e}")
        font = ImageFont.load_default()

    # 创建视频片段
    clips = []

    # 对齐三个列表长度
    min_len = min(len(images_result), len(tts_result), len(keywords_result))
    print(f"[INFO] 开始合成视频: {min_len} 个片段")

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
        img_clip = img_clip.resized((VIDEO_WIDTH, VIDEO_HEIGHT))

        # 添加音频
        if has_audio:
            try:
                audio_clip = AudioFileClip(audio_path)
                img_clip = img_clip.with_audio(audio_clip)
            except Exception as e:
                print(f"[WARN] 音频加载失败: {e}")

        # 添加字幕（使用已验证的方案）
        if text:
            try:
                subtitle_img = create_subtitle_image(text, VIDEO_WIDTH, font, MAX_CHARS_PER_LINE, FONT_SIZE, SUBTITLE_COLOR)
                subtitle_clip = ImageClip(subtitle_img, is_mask=False, transparent=True)
                subtitle_clip = subtitle_clip.with_duration(duration)
                subtitle_clip = subtitle_clip.with_position(('center', 880))
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
        fps=FPS,
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


def wrap_text(text: str, max_chars: int) -> List[str]:
    """文本换行"""
    if len(text) <= max_chars:
        return [text]

    lines = []
    current = ""
    for char in text:
        current += char
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines


def create_subtitle_image(text: str, video_width: int, font, max_chars: int, font_size: int, subtitle_color: tuple):
    """
    创建字幕图片（使用已验证的方案）

    Args:
        text: 字幕文本
        video_width: 视频宽度
        font: 字体
        max_chars: 每行最大字符数
        font_size: 字体大小
        subtitle_color: 字幕颜色

    Returns:
        字幕图片数组
    """
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    lines = wrap_text(text, max_chars)

    padding = 15
    line_height = font_size + 8
    total_height = line_height * len(lines) + padding * 2

    temp_img = Image.new("RGBA", (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)

    max_width = 0
    for line in lines:
        bbox = temp_draw.textbbox((0, 0), line, font=font)
        max_width = max(max_width, bbox[2] - bbox[0])

    img_width = min(max_width + padding * 2, video_width - 100)
    img_height = total_height

    img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 半透明黑色背景，圆角矩形
    draw.rounded_rectangle([0, 0, img_width - 1, img_height - 1], radius=10, fill=(0, 0, 0, 180))

    for i, line in enumerate(lines):
        bbox = temp_draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (img_width - line_width) // 2
        y = padding + i * line_height

        # 阴影
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 200))
        # 正文
        draw.text((x, y), line, font=font, fill=subtitle_color)

    return np.array(img)
