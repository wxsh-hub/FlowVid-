"""
语音转文字服务 (Whisper)
"""

import json
from pathlib import Path

# 模型缓存，避免每次任务都重新加载（数GB模型）
_whisper_model = None


def _get_whisper_model():
    """获取Whisper模型单例"""
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise Exception("faster-whisper未安装，请运行: pip install faster-whisper")
        print("[INFO] 首次加载Whisper large-v3模型...")
        _whisper_model = WhisperModel("large-v3", device="cpu", compute_type="int8")
        print("[INFO] Whisper模型加载完成")
    return _whisper_model


def transcribe_video(video_path: str, output_path: str) -> list:
    """
    使用Whisper转写视频语音

    Args:
        video_path: 视频文件路径
        output_path: 输出JSON路径

    Returns:
        转写结果列表 [{"start": 0.0, "end": 1.0, "text": "..."}]
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # 使用缓存的模型
    model = _get_whisper_model()

    # 转写
    print(f"[INFO] 开始转写: {video_path}")
    segments, info = model.transcribe(
        video_path,
        language="zh",
        beam_size=5,
        vad_filter=True,
    )

    # 收集结果
    result = []
    for segment in segments:
        result.append({
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": segment.text.strip()
        })

    print(f"[INFO] 转写完成: {len(result)} 个片段")

    # 保存结果
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result
