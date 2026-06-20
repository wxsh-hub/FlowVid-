# AI视频生成平台

输入视频链接，自动生成带字幕的配音视频。

## 功能特性

- 🎬 **视频下载**: 支持抖音、B站、YouTube等主流平台
- 🎤 **语音识别**: 使用Whisper large-v3进行高精度语音转文字
- 🔍 **关键词提取**: 使用MiMo AI提取关键词和生图提示词
- 🖼️ **图片获取**: Pexels搜图 + Seedream AI生图双重保障
- 🔊 **语音合成**: 使用edge-tts生成高质量中文语音
- 📝 **字幕生成**: 自动同步字幕，精准匹配语音
- 🎥 **视频合成**: 1920x1080高清输出，30fps

## 技术栈

### 后端
- **FastAPI**: Web框架
- **SQLAlchemy**: 数据库ORM
- **Whisper**: 语音识别
- **MoviePy**: 视频处理
- **edge-tts**: 语音合成

### 前端
- **Vue 3**: 前端框架
- **Element Plus**: UI组件库
- **Vite**: 构建工具

## 快速开始

### 方式一：本地运行

#### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

#### 4. 启动前端服务

```bash
cd frontend
npm run dev
```

#### 5. 访问应用

打开浏览器访问 http://localhost:3000

### 方式二：Docker运行

```bash
docker-compose up -d
```

## API密钥配置

使用前需要配置以下API密钥：

| API | 用途 | 获取地址 |
|-----|------|----------|
| **MiMo API** | 关键词提取 | https://mimoai.com |
| **Pexels API** | 图片搜索 | https://www.pexels.com/api/ |
| **Seedream API** | AI生图 | https://seedream.ai |

## 使用流程

1. **配置API**: 在"配置管理"页面添加API密钥
2. **创建任务**: 输入视频链接，选择配置方案
3. **等待处理**: 系统自动完成下载、转写、搜图、生图、合成
4. **下载结果**: 处理完成后预览并下载视频

## 目录结构

```
video-platform/
├── backend/                # 后端代码
│   ├── app/
│   │   ├── api/           # API接口
│   │   ├── services/      # 业务服务
│   │   ├── models/        # 数据模型
│   │   └── core/          # 核心配置
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 公共组件
│   │   └── api/           # API封装
│   ├── package.json
│   └── Dockerfile
├── storage/                # 文件存储
│   ├── uploads/           # 原始视频
│   ├── transcribes/       # 转写文本
│   ├── images/            # 搜图/生图
│   ├── audio/             # TTS音频
│   └── outputs/           # 最终视频
├── docker-compose.yml
└── README.md
```

## 开发说明

### 添加新的视频源

在 `backend/app/services/downloader.py` 中添加新的下载逻辑。

### 添加新的AI服务

在 `backend/app/services/` 中创建新的服务模块，并在 `task_processor.py` 中调用。

### 自定义字幕样式

修改 `backend/app/services/video_maker.py` 中的字幕配置。

## 常见问题

### Q: Whisper模型下载慢？

使用HuggingFace镜像：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q: edge-tts报错？

检查网络连接，或更换语音：
```python
voice = "zh-CN-YunxiNeural"  # 男声
voice = "zh-CN-XiaoxiaoNeural"  # 女声
```

### Q: MoviePy导出失败？

确保安装了ffmpeg：
```bash
# Windows
choco install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## License

MIT
