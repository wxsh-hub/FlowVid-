"""
配置API接口 - 支持多AI服务配置
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from app.core.database import get_db
from app.models.config import UserConfig

router = APIRouter()


class CreateConfigRequest(BaseModel):
    name: str

    # 文本处理配置
    text_base_url: Optional[str] = "https://api.mimoai.com/v1"
    text_model: Optional[str] = "gpt-3.5-turbo"
    text_api_key: Optional[str] = None
    text_protocol: Optional[str] = "openai"

    # AI生图配置
    image_base_url: Optional[str] = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    image_model: Optional[str] = "doubao-seedream-4-5-251128"
    image_api_key: Optional[str] = None
    image_protocol: Optional[str] = "doubao"

    # TTS配置
    tts_voice: Optional[str] = "zh-CN-YunxiNeural"
    tts_rate: Optional[str] = "+0%"


@router.post("")
async def create_config(request: CreateConfigRequest, db: Session = Depends(get_db)):
    """创建配置方案"""
    config_id = str(uuid.uuid4())
    config = UserConfig(
        id=config_id,
        name=request.name,
        text_base_url=request.text_base_url,
        text_model=request.text_model,
        text_api_key=request.text_api_key,
        text_protocol=request.text_protocol,
        image_base_url=request.image_base_url,
        image_model=request.image_model,
        image_api_key=request.image_api_key,
        image_protocol=request.image_protocol,
        tts_voice=request.tts_voice,
        tts_rate=request.tts_rate,
    )
    db.add(config)
    db.commit()
    return config.to_dict()


@router.get("")
async def list_configs(db: Session = Depends(get_db)):
    """获取配置方案列表"""
    configs = db.query(UserConfig).order_by(UserConfig.created_at.desc()).all()
    return {"configs": [c.to_dict() for c in configs]}


@router.get("/{config_id}")
async def get_config(config_id: str, db: Session = Depends(get_db)):
    """获取配置方案详情（包含完整API Key）"""
    config = db.query(UserConfig).filter(UserConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config.to_full_dict()


@router.put("/{config_id}")
async def update_config(config_id: str, request: CreateConfigRequest, db: Session = Depends(get_db)):
    """更新配置方案"""
    config = db.query(UserConfig).filter(UserConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    config.name = request.name
    config.text_base_url = request.text_base_url
    config.text_model = request.text_model
    config.text_api_key = request.text_api_key
    config.text_protocol = request.text_protocol
    config.image_base_url = request.image_base_url
    config.image_model = request.image_model
    config.image_api_key = request.image_api_key
    config.image_protocol = request.image_protocol
    config.tts_voice = request.tts_voice
    config.tts_rate = request.tts_rate
    db.commit()
    return config.to_dict()


@router.delete("/{config_id}")
async def delete_config(config_id: str, db: Session = Depends(get_db)):
    """删除配置方案"""
    config = db.query(UserConfig).filter(UserConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    db.delete(config)
    db.commit()
    return {"message": "配置已删除"}
