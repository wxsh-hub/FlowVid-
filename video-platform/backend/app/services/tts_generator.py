"""
TTS语音生成服务 (edge-tts) - 支持静音音频生成
"""

import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


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

    # 使用同步方式运行异步代码（在独立线程中运行避免事件循环冲突）
    def _run_async():
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                _generate_all_tts(keywords_result, voice, rate, str(output))
            )
        finally:
            loop.close()

    with ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(_run_async).result()

    print(f"[INFO] TTS生成完成: {len(result)} 个音频")
    return result


async def _generate_all_tts(keywords_result: list, voice: str, rate: str, output_dir: str) -> list:
    """异步并发生成所有TTS音频"""
    import edge_tts

    output = Path(output_dir)
    semaphore = asyncio.Semaphore(4)  # 限制并发数

    async def _generate_one(idx: int, text: str) -> dict:
        """生成单个TTS音频"""
        async with semaphore:
            audio_path = str(output / f"{idx:03d}.mp3")
            try:
                communicate = edge_tts.Communicate(text, voice, rate=rate)
                await communicate.save(audio_path)

                if Path(audio_path).exists() and Path(audio_path).stat().st_size > 0:
                    duration = get_audio_duration(audio_path)
                    print(f"[INFO] TTS生成成功: 片段{idx} ({duration:.2f}s)")
                    return {"index": idx, "audio_path": audio_path, "duration": duration}
                else:
                    print(f"[WARN] TTS生成失败: 片段{idx} 文件为空")
                    silent_path = create_silent_audio(output, idx, 3.0)
                    return {"index": idx, "audio_path": silent_path, "duration": 3.0}
            except Exception as e:
                print(f"[WARN] TTS生成失败: 片段{idx}: {e}")
                silent_path = create_silent_audio(output, idx, 3.0)
                return {"index": idx, "audio_path": silent_path, "duration": 3.0}

    # 收集需要生成的片段并并发执行
    tasks = []
    for i, item in enumerate(keywords_result):
        text = item.get("text", "")
        if not text:
            continue
        tasks.append(_generate_one(i, text))

    results = await asyncio.gather(*tasks)
    return list(results)


def create_silent_audio(output_dir: Path, index: int, duration: float) -> str:
    """
    创建静音音频文件

    Args:
        output_dir: 输出目录
        index: 片段索引
        duration: 时长（秒）

    Returns:
        静音音频文件路径
    """
    try:
        import numpy as np
        from moviepy import AudioArrayClip

        # 创建静音音频
        fps = 44100
        n_samples = int(duration * fps)
        silent_array = np.zeros((n_samples, 2))  # 双声道

        audio_clip = AudioArrayClip(silent_array, fps=fps)
        output_path = str(output_dir / f"{index:03d}_silent.mp3")
        audio_clip.write_audiofile(output_path, fps=fps, nbytes=2, codec='libmp3lame')

        print(f"[INFO] 创建静音音频: {output_path}")
        return output_path

    except Exception as e:
        print(f"[WARN] 创建静音音频失败: {e}")
        return None


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
    except (ImportError, Exception) as e:
        print(f"[WARN] 获取音频时长失败，使用估算: {e}")
        file_size = Path(audio_path).stat().st_size
        return file_size / 16000  # 假设128kbps
