#!/bin/bash

# Boss直聘爬虫系统启动脚本

echo "启动Boss直聘爬虫系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python"
    exit 1
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt"
    exit 1
fi

echo "检查Python依赖..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "安装Python依赖..."
    pip3 install -r requirements.txt
}

# 创建必要的目录
mkdir -p backend/static/wordclouds

# 启动后端服务
echo "启动后端服务 (http://localhost:8000)..."
cd backend
python3 main.py &
BACKEND_PID=$!

# 等待服务启动
sleep 3

# 启动前端服务（可选）
echo "前端页面: 打开 frontend/index.html 或使用 http://localhost:8080"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待中断信号
trap "kill $BACKEND_PID; exit" INT TERM
wait $BACKEND_PID

