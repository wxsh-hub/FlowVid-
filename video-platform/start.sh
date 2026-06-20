#!/bin/bash

# 启动脚本

echo "=== AI视频生成平台启动脚本 ==="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js"
    exit 1
fi

# 启动后端
echo "启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 启动前端
echo "启动前端服务..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== 服务已启动 ==="
echo "前端: http://localhost:3000"
echo "后端: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 捕获退出信号
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# 等待
wait
