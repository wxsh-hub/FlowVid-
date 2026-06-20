@echo off
chcp 65001 >nul

echo === AI视频生成平台启动脚本 ===

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    pause
    exit /b 1
)

REM 检查Node.js环境
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js
    pause
    exit /b 1
)

REM 启动后端
echo 启动后端服务...
cd backend
if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt -q
start "Backend" cmd /c "uvicorn app.main:app --reload --port 8000"
cd ..

REM 启动前端
echo 启动前端服务...
cd frontend
if not exist "node_modules" (
    echo 安装前端依赖...
    call npm install
)
start "Frontend" cmd /c "npm run dev"
cd ..

echo.
echo === 服务已启动 ===
echo 前端: http://localhost:3000
echo 后端: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 按任意键停止服务
pause >nul

REM 停止服务
taskkill /FI "WindowTitle eq Backend*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend*" /F >nul 2>&1
