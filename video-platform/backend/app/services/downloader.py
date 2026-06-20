"""
视频下载服务
"""

import subprocess
from pathlib import Path


def download_video(url: str, output_path: str) -> str:
    """
    下载视频

    Args:
        url: 视频链接
        output_path: 输出路径

    Returns:
        下载的视频文件路径
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # 使用yt-dlp下载
    cmd = [
        "yt-dlp",
        "--no-check-certificates",
        "-f", "best",
        "-o", str(output),
        url
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )

        if result.returncode != 0:
            raise Exception(f"下载失败: {result.stderr}")

        # 检查文件是否存在
        if not output.exists():
            # yt-dlp可能会添加扩展名
            for f in output.parent.glob(output.stem + ".*"):
                if f.suffix in ['.mp4', '.webm', '.mkv']:
                    return str(f)
            raise Exception("下载的视频文件不存在")

        return str(output)

    except subprocess.TimeoutExpired:
        raise Exception("下载超时")
    except FileNotFoundError:
        raise Exception("yt-dlp未安装，请运行: pip install yt-dlp")
