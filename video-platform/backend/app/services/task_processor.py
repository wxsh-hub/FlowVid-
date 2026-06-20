"""
任务处理器 - 编排整个视频生成流程
"""

from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.task import Task
from app.models.config import UserConfig
from app.services.downloader import download_video
from app.services.transcriber import transcribe_video
from app.services.extractor import extract_keywords
from app.services.image_fetcher import fetch_images
from app.services.tts_generator import generate_tts
from app.services.video_maker import make_video

# 存储目录
STORAGE_DIR = Path(__file__).parent.parent.parent.parent / "storage"


def update_task_status(task_id: str, step_index: int, step_status: str, progress: int, current_step: str = None):
    """更新任务状态"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        steps = task.steps
        if step_index < len(steps):
            steps[step_index]["status"] = step_status
            steps[step_index]["progress"] = progress
        total_progress = sum(s["progress"] for s in steps) // len(steps)
        task.steps = steps
        task.progress = total_progress
        if current_step:
            task.current_step = current_step
        task.updated_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


def mark_task_failed(task_id: str, error_message: str):
    """标记任务失败"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = error_message
            task.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def mark_task_completed(task_id: str, output_path: str):
    """标记任务完成"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "completed"
            task.progress = 100
            task.output_path = output_path
            task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            for step in task.steps:
                step["status"] = "completed"
                step["progress"] = 100
            db.commit()
    finally:
        db.close()


def get_config_dict(config: UserConfig) -> dict:
    """将配置对象转换为字典"""
    return {
        "text_base_url": config.text_base_url,
        "text_model": config.text_model,
        "text_api_key": config.text_api_key,
        "text_protocol": config.text_protocol,
        "image_base_url": config.image_base_url,
        "image_model": config.image_model,
        "image_api_key": config.image_api_key,
        "image_protocol": config.image_protocol,
        "tts_voice": config.tts_voice,
        "tts_rate": config.tts_rate,
    }


def process_video_task(task_id: str, video_url: str, api_keys: dict):
    """处理视频生成任务"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "processing"
            task.current_step = "开始处理"
            db.commit()
    finally:
        db.close()

    task_dir = STORAGE_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 步骤1: 下载视频
        update_task_status(task_id, 0, "processing", 0, "下载视频中...")
        video_path = download_video(video_url, str(task_dir / "source.mp4"))
        update_task_status(task_id, 0, "completed", 100, "下载完成")

        # 步骤2: 语音转文字
        update_task_status(task_id, 1, "processing", 0, "语音转文字中...")
        transcribe_result = transcribe_video(video_path, str(task_dir / "transcribe.json"))
        update_task_status(task_id, 1, "completed", 100, "转写完成")

        # 步骤3: 提取关键词
        update_task_status(task_id, 2, "processing", 0, "提取关键词中...")
        keywords_result = extract_keywords(
            transcribe_result,
            api_keys.get("text_api_key"),
            api_keys.get("text_base_url"),
            api_keys.get("text_model", "gpt-3.5-turbo"),
            str(task_dir / "keywords.json")
        )
        update_task_status(task_id, 2, "completed", 100, "关键词提取完成")

        # 步骤4: 搜图/生图
        update_task_status(task_id, 3, "processing", 0, "搜图/生图中...")
        images_result = fetch_images(
            keywords_result,
            api_keys.get("image_api_key"),
            api_keys.get("image_base_url"),
            api_keys.get("image_model"),
            api_keys.get("image_protocol", "doubao"),
            str(task_dir / "images")
        )
        update_task_status(task_id, 3, "completed", 100, "图片获取完成")

        # 步骤5: 生成TTS
        update_task_status(task_id, 4, "processing", 0, "生成TTS语音中...")
        tts_result = generate_tts(
            keywords_result,
            api_keys.get("tts_voice", "zh-CN-YunxiNeural"),
            api_keys.get("tts_rate", "+0%"),
            str(task_dir / "audio")
        )
        update_task_status(task_id, 4, "completed", 100, "TTS生成完成")

        # 步骤6: 合成视频
        update_task_status(task_id, 5, "processing", 0, "合成视频中...")
        output_path = make_video(
            images_result,
            tts_result,
            keywords_result,
            str(task_dir / "output.mp4")
        )
        update_task_status(task_id, 5, "completed", 100, "视频合成完成")

        mark_task_completed(task_id, output_path)

    except Exception as e:
        error_msg = f"处理失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        mark_task_failed(task_id, error_msg)
