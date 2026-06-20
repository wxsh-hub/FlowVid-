"""
任务API接口
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.task import Task
from app.models.config import UserConfig
from app.services.task_processor import process_video_task, get_config_dict

router = APIRouter()


class CreateTaskRequest(BaseModel):
    video_url: str
    config_id: Optional[str] = None
    duration: Optional[int] = 0  # 截取时长（秒），0表示全部

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """校验URL是否为合法的视频链接"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        if not parsed.netloc:
            return False
        # 禁止内网地址
        import ipaddress
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                return False
        except ValueError:
            # hostname 是域名，检查常见内网域名
            hostname = (parsed.hostname or "").lower()
            if hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
                return False
        return True


@router.post("")
async def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """创建视频生成任务"""
    # 校验URL
    if not CreateTaskRequest._is_valid_url(request.video_url):
        raise HTTPException(status_code=400, detail="无效的视频链接，请提供合法的http/https链接")

    task_id = str(uuid.uuid4())

    # 获取配置
    api_keys = {}
    if request.config_id:
        config = db.query(UserConfig).filter(UserConfig.id == request.config_id).first()
        if config:
            api_keys = get_config_dict(config)
        else:
            raise HTTPException(status_code=404, detail="配置方案不存在")

    # 初始化步骤
    steps = [
        {"name": "下载视频", "status": "pending", "progress": 0},
        {"name": "语音转文字", "status": "pending", "progress": 0},
        {"name": "提取关键词", "status": "pending", "progress": 0},
        {"name": "搜图/生图", "status": "pending", "progress": 0},
        {"name": "生成TTS", "status": "pending", "progress": 0},
        {"name": "合成视频", "status": "pending", "progress": 0},
    ]

    # 创建任务
    task = Task(
        id=task_id,
        video_url=request.video_url,
        duration=request.duration,
        status="pending",
        progress=0,
        current_step="等待开始",
        steps=steps,
        config_id=request.config_id,
    )
    db.add(task)
    db.commit()

    # 启动后台任务
    background_tasks.add_task(process_video_task, task_id, request.video_url, api_keys, request.duration)

    return {"task_id": task_id, "status": "pending", "message": "任务已创建，开始处理"}


@router.get("/{task_id}")
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """获取任务状态"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task.to_dict()


@router.get("")
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    # 先计算总数，再取分页数据，避免重复查询
    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "tasks": [t.to_dict() for t in tasks],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.delete("/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    """删除任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.status == "processing":
        raise HTTPException(status_code=400, detail="不能删除正在处理的任务")
    db.delete(task)
    db.commit()
    return {"message": "任务已删除"}
