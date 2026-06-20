"""
视频下载服务
"""

import re
import subprocess
import uuid
from pathlib import Path


def extract_video_id(url: str) -> str:
    """
    从URL中提取视频ID

    Args:
        url: 视频链接

    Returns:
        视频ID或None
    """
    # 抖音视频ID模式
    patterns = [
        r'modal_id=(\d+)',  # 搜索页面中的modal_id
        r'/video/(\d+)',    # 标准视频链接
        r'/note/(\d+)',     # 图文笔记
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def normalize_douyin_url(url: str) -> str:
    """
    规范化抖音URL

    Args:
        url: 原始URL

    Returns:
        规范化后的URL
    """
    video_id = extract_video_id(url)
    if video_id:
        return f"https://www.douyin.com/video/{video_id}"
    return url


def download_video(url: str, output_path: str, duration: int = 0) -> str:
    """
    下载视频

    Args:
        url: 视频链接
        output_path: 输出路径
        duration: 截取时长（秒），0表示全部

    Returns:
        下载的视频文件路径
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # 规范化URL
    normalized_url = normalize_douyin_url(url)
    if normalized_url != url:
        print(f"[INFO] 规范化URL: {normalized_url}")

    # 使用yt-dlp下载
    cmd = [
        "yt-dlp",
        "--no-check-certificates",
        "-f", "best",
        "-o", str(output),
        normalized_url
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
        video_path = None
        if output.exists():
            video_path = str(output)
        else:
            # yt-dlp可能会添加扩展名
            for f in output.parent.glob(output.stem + ".*"):
                if f.suffix in ['.mp4', '.webm', '.mkv']:
                    video_path = str(f)
                    break

        if not video_path:
            raise Exception("下载的视频文件不存在")

        # 如果需要截取时长
        if duration > 0:
            video_path = trim_video(video_path, duration)

        return video_path

    except subprocess.TimeoutExpired:
        raise Exception("下载超时")
    except FileNotFoundError:
        raise Exception("yt-dlp未安装，请运行: pip install yt-dlp")


def trim_video(video_path: str, duration: int) -> str:
    """
    截取视频指定时长

    Args:
        video_path: 视频文件路径
        duration: 截取时长（秒）

    Returns:
        截取后的视频文件路径
    """
    try:
        from moviepy import VideoFileClip
    except ImportError:
        raise Exception("moviepy未安装，请运行: pip install moviepy")

    # 使用UUID避免并发时文件名冲突
    stem = Path(video_path).stem
    output_path = str(Path(video_path).parent / f"{stem}_trimmed_{uuid.uuid4().hex[:8]}.mp4")

    try:
        print(f"[INFO] 截取视频前 {duration} 秒...")
        video = VideoFileClip(video_path)

        # 如果视频时长小于指定时长，返回原视频
        if video.duration <= duration:
            print(f"[INFO] 视频时长 {video.duration:.1f}s 小于指定时长 {duration}s，使用全部视频")
            video.close()
            return video_path

        # 截取指定时长
        trimmed = video.subclipped(0, duration)
        trimmed.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            preset='medium',
        )

        # 关闭视频
        trimmed.close()
        video.close()

        print(f"[INFO] 视频截取完成: {duration}s")
        return output_path

    except Exception as e:
        print(f"[WARN] 视频截取失败: {e}")
        return video_path
