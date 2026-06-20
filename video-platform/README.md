# FlowVid - AI视频生成平台

> 🎬 输入视频链接，自动生成带字幕的配音视频

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 项目亮点

### 🎯 核心特性

- **多模型支持**：文本处理支持OpenAI、Anthropic等协议，图片生成支持豆包Seedream、DALL-E、通义万相
- **配置方案管理**：保存多个AI模型配置方案，一键切换
- **精准字幕同步**：使用Whisper large-v3语音识别，字幕与语音高度匹配
- **智能图片匹配**：AI提取关键词 → 搜图保底 → AI生图兜底
- **分段生成策略**：6秒分段避免TTS语速累积误差

### 🔧 技术亮点

| 技术 | 应用 |
|------|------|
| **Whisper large-v3** | 高精度中文语音识别 |
| **edge-tts** | 微软免费高质量TTS |
| **MoviePy 2.x** | 视频合成与字幕渲染 |
| **FastAPI** | 高性能异步后端 |
| **Vue 3 + Element Plus** | 现代化前端界面 |

---

## 📋 完整流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户输入                                  │
│                     视频链接 + 选择配置方案                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤1: 下载视频 (yt-dlp)                                        │
│  ─────────────────────────────────────────────────────────────── │
│  • 支持抖音、B站、YouTube等主流平台                               │
│  • 自动选择最佳画质                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤2: 语音转文字 (Whisper large-v3)                            │
│  ─────────────────────────────────────────────────────────────── │
│  • 高精度中文语音识别                                            │
│  • 输出带时间戳的文本片段                                        │
│  • VAD语音活动检测，过滤静音                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤3: 提取关键词 (AI文本模型)                                   │
│  ─────────────────────────────────────────────────────────────── │
│  • 合并短文本片段（<3秒）                                        │
│  • AI提取搜索关键词（中文）                                      │
│  • AI生成生图提示词（英文）                                      │
│  • 支持OpenAI/Anthropic/自定义协议                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤4: 获取图片 (搜图 + AI生图)                                  │
│  ─────────────────────────────────────────────────────────────── │
│  • 优先Pexels搜图（免费图库）                                    │
│  • 搜图失败则AI生图兜底                                          │
│  • 支持豆包Seedream/OpenAI DALL-E/通义万相                       │
│  • 输出1920x1080高清图片                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤5: 生成TTS语音 (edge-tts)                                   │
│  ─────────────────────────────────────────────────────────────── │
│  • 微软免费高质量中文TTS                                         │
│  • 多种语音可选（云希/晓晓/云扬/晓涵）                            │
│  • 可调节语速                                                    │
│  • 精确获取音频时长                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤6: 合成视频 (MoviePy)                                       │
│  ─────────────────────────────────────────────────────────────── │
│  • 图片 + 音频 + 字幕合成                                        │
│  • 1920x1080高清输出                                            │
│  • 30fps流畅播放                                                │
│  • 字幕自动换行，防止溢出                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        输出结果                                  │
│              带精准字幕的配音视频 (MP4)                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- FFmpeg（视频处理）

### 1. 克隆项目

```bash
git clone https://github.com/wxsh-hub/FlowVid-.git
cd FlowVid-
```

### 2. 启动后端

```bash
cd video-platform/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

后端API文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动服务
npm run dev
```

前端界面：http://localhost:3000

### 4. 配置AI模型

1. 访问 http://localhost:3000/configs
2. 点击"新建配置方案"
3. 填写文本模型配置（用于关键词提取）
4. 填写图片模型配置（用于AI生图）
5. 保存配置

### 5. 生成视频

1. 访问 http://localhost:3000/create
2. 输入视频链接
3. 选择配置方案
4. 点击"开始生成"
5. 等待处理完成，下载视频

---

## 📁 项目结构

```
FlowVid-/
├── frontend/                      # Vue3前端
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue          # 首页（任务列表）
│   │   │   ├── Create.vue        # 创建任务
│   │   │   ├── TaskDetail.vue    # 任务详情
│   │   │   └── Configs.vue       # 配置管理
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
│
├── video-platform/                # 主项目目录
│   ├── backend/                   # FastAPI后端
│   │   ├── app/
│   │   │   ├── api/              # API接口
│   │   │   │   ├── tasks.py      # 任务管理
│   │   │   │   └── configs.py    # 配置管理
│   │   │   ├── services/         # 业务服务
│   │   │   │   ├── downloader.py # 视频下载
│   │   │   │   ├── transcriber.py# 语音识别
│   │   │   │   ├── extractor.py  # 关键词提取
│   │   │   │   ├── image_fetcher.py # 搜图/生图
│   │   │   │   ├── tts_generator.py # TTS语音
│   │   │   │   └── video_maker.py   # 视频合成
│   │   │   ├── models/           # 数据模型
│   │   │   └── core/             # 核心配置
│   │   └── requirements.txt
│   │
│   ├── frontend/                  # 前端副本
│   ├── storage/                   # 文件存储
│   │   ├── uploads/              # 原始视频
│   │   ├── transcribes/          # 转写文本
│   │   ├── images/               # 搜图/生图
│   │   ├── audio/                # TTS音频
│   │   └── outputs/              # 最终视频
│   │
│   ├── docker-compose.yml
│   └── README.md
│
├── .gitignore
└── README.md                      # 本文件
```

---

## 🔌 API接口

### 任务管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/tasks` | 创建视频生成任务 |
| GET | `/api/tasks` | 获取任务列表 |
| GET | `/api/tasks/{id}` | 获取任务详情 |
| DELETE | `/api/tasks/{id}` | 删除任务 |

### 配置管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/configs` | 创建配置方案 |
| GET | `/api/configs` | 获取配置列表 |
| GET | `/api/configs/{id}` | 获取配置详情 |
| PUT | `/api/configs/{id}` | 更新配置方案 |
| DELETE | `/api/configs/{id}` | 删除配置方案 |

---

## 🤖 支持的AI模型

### 文本处理（关键词提取）

| 协议 | 模型示例 | 说明 |
|------|----------|------|
| OpenAI兼容 | gpt-4o, gpt-3.5-turbo | 支持所有OpenAI兼容API |
| Anthropic | claude-3-5-sonnet | Anthropic Claude系列 |
| 自定义 | 任意模型 | 支持自定义API地址 |

### 图片生成（AI生图）

| 协议 | 模型 | 说明 |
|------|------|------|
| 豆包Seedream | doubao-seedream-4-5-251128 | 字节跳动豆包模型 |
| OpenAI DALL-E | dall-e-3 | OpenAI图片生成 |
| 通义万相 | wanx-v1 | 阿里通义万相 |
| 自定义 | 任意模型 | 支持自定义API地址 |

---

## 🐳 Docker部署

```bash
cd video-platform

# 启动所有服务
docker-compose up -d

# 访问前端
open http://localhost:3000
```

---

## 💡 使用技巧

### 1. 字幕同步优化

- 分段时长设为6秒，避免TTS语速累积误差
- Whisper识别后按字数比例分配时间戳
- 省略时长<1秒的最后字幕，防止重叠

### 2. 图片质量提升

- 优先使用Pexels搜图（免费高质量图库）
- 搜图失败自动切换AI生图
- 支持多种AI生图协议，可灵活切换

### 3. 配置方案管理

- 可保存多个配置方案（如：GPT-4方案、Claude方案）
- 编辑时API Key密文显示，保护隐私
- 一键切换不同AI模型组合

---

## 📝 更新日志

### v1.0.0 (2024-06-20)

- ✨ 初始版本发布
- ✨ 支持多AI模型配置
- ✨ 支持抖音/B站/YouTube视频下载
- ✨ Whisper large-v3语音识别
- ✨ edge-tts语音合成
- ✨ 搜图+AI生图双保险
- ✨ 1920x1080高清视频输出

---

## 📄 License

MIT License

---

## 🙏 致谢

- [Whisper](https://github.com/openai/whisper) - 语音识别
- [edge-tts](https://github.com/rany2/edge-tts) - 语音合成
- [MoviePy](https://github.com/Zulko/moviepy) - 视频处理
- [FastAPI](https://github.com/tiangolo/fastapi) - Web框架
- [Vue.js](https://vuejs.org/) - 前端框架
- [Element Plus](https://element-plus.org/) - UI组件库
- [Pexels](https://www.pexels.com/) - 免费图库
