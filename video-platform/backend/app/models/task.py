"""
任务模型
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from datetime import datetime
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, index=True)
    video_url = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending/processing/completed/failed
    progress = Column(Integer, default=0)
    current_step = Column(String(100), default="")
    steps = Column(JSON, default=[])
    config_id = Column(String(36), nullable=True)
    output_path = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "video_url": self.video_url,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "steps": self.steps,
            "config_id": self.config_id,
            "output_path": self.output_path,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
