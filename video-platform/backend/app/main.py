"""
视频生成平台 - FastAPI 后端服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

from app.api import tasks, configs
from app.core.database import init_db


app = FastAPI(
    title="Video Generation Platform",
    description="AI视频生成平台 - 输入视频链接自动生成带字幕的配音视频",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
STORAGE_DIR = Path(__file__).parent.parent.parent / "storage"
STORAGE_DIR.mkdir(exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

# 注册路由
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(configs.router, prefix="/api/configs", tags=["configs"])


@app.on_event("startup")
async def startup():
    """初始化数据库"""
    init_db()
    print("Database initialized")


@app.get("/")
async def root():
    return {"message": "Video Generation Platform API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
