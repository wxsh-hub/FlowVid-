"""
TTS语音生成服务 (edge-tts)
"""

import asyncio
from pathlib import Path


def generate_tts(keywords_result: list, voice: str, rate: str, output_dir: str) -> list:
    """
    生成TTS语音

    Args:
        keywords_result: 关键词提取结果
        voice: TTS语音
        rate: 语速
        output_dir: 输出目录

    Returns:
        音频路径列表 [{"index": 0, "audio_path": "...", "duration": 1.5}]
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # 使用同步方式运行异步代码
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(
        _generate_all_tts(keywords_result, voice, rate, str(output))
    )
    loop.close()

    print(f"[INFO] TTS生成完成: {len(result)} 个音频")
    return result


async def _generate_all_tts(keywords_result: list, voice: str, rate: str, output_dir: str) -> list:
    """异步生成所有TTS音频"""
    import edge_tts

    result = []
    output = Path(output_dir)

    for i, item in enumerate(keywords_result):
        text = item.get("text", "")
        if not text:
            continue

        audio_path = str(output / f"{i:03d}.mp3")

        try:
            # 生成TTS
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(audio_path)

            # 获取音频时长
            duration = get_audio_duration(audio_path)

            result.append({
                "index": i,
                "audio_path": audio_path,
                "duration": duration,
            })

            print(f"[INFO] TTS生成成功: 片段{i} ({duration:.2f}s)")

        except Exception as e:
            print(f"[WARN] TTS生成失败: {e}")
            # 创建静音音频
            result.append({
                "index": i,
                "audio_path": None,
                "duration": 3.0,
            })

    return result


def get_audio_duration(audio_path: str) -> float:
    """
    获取音频时长

    Args:
        audio_path: 音频文件路径

    Returns:
        时长（秒）
    """
    try:
        from mutagen.mp3 import MP3
        audio = MP3(audio_path)
        return audio.info.length
    except:
        # 备用方案：估算
        file_size = Path(audio_path).stat().st_size
        return file_size / 16000  # 假设128kbps
