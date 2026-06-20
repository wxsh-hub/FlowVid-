"""
配置模型 - 支持多AI服务配置
"""

from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from app.core.database import Base


class UserConfig(Base):
    __tablename__ = "configs"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    # 文本处理配置（关键词提取）
    text_base_url = Column(Text, default="https://api.mimoai.com/v1")
    text_model = Column(String(100), default="gpt-3.5-turbo")
    text_api_key = Column(Text, nullable=True)
    text_protocol = Column(String(20), default="openai")

    # AI生图配置
    image_base_url = Column(Text, default="https://ark.cn-beijing.volces.com/api/v3/images/generations")
    image_model = Column(String(100), default="doubao-seedream-4-5-251128")
    image_api_key = Column(Text, nullable=True)
    image_protocol = Column(String(20), default="doubao")

    # TTS配置
    tts_voice = Column(String(50), default="zh-CN-YunxiNeural")
    tts_rate = Column(String(10), default="+0%")

    # 时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "text_base_url": self.text_base_url,
            "text_model": self.text_model,
            "text_api_key": self.text_api_key[:10] + "***" if self.text_api_key else None,
            "text_protocol": self.text_protocol,
            "image_base_url": self.image_base_url,
            "image_model": self.image_model,
            "image_api_key": self.image_api_key[:10] + "***" if self.image_api_key else None,
            "image_protocol": self.image_protocol,
            "tts_voice": self.tts_voice,
            "tts_rate": self.tts_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_full_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "text_base_url": self.text_base_url,
            "text_model": self.text_model,
            "text_api_key": self.text_api_key,
            "text_protocol": self.text_protocol,
            "image_base_url": self.image_base_url,
            "image_model": self.image_model,
            "image_api_key": self.image_api_key,
            "image_protocol": self.image_protocol,
            "tts_voice": self.tts_voice,
            "tts_rate": self.tts_rate,
        }
