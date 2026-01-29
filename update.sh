#!/bin/bash
# 大宗商品战情室 - 更新部署脚本

set -e

echo "=========================================="
echo "  大宗商品战情室 - 更新部署"
echo "=========================================="

cd "$(dirname "$0")"

# 检测部署模式
if [ -f "docker-compose.yml" ] && command -v docker-compose &> /dev/null; then
    echo ""
    echo "检测到 Docker 环境，使用 Docker 模式更新..."
    echo ""
    
    # 停止旧容器
    echo "[1/3] 停止旧容器..."
    docker-compose down
    
    # 重新构建
    echo "[2/3] 重新构建镜像..."
    docker-compose build
    
    # 启动新容器
    echo "[3/3] 启动新容器..."
    docker-compose up -d
    
    echo ""
    echo "✅ Docker 部署更新完成！"
    echo ""
    echo "查看日志: docker-compose logs -f"
    echo "前端地址: http://localhost:3000"
    echo "后端地址: http://localhost:8000"
    
else
    echo ""
    echo "使用本地模式更新..."
    echo ""
    
    # 更新后端依赖
    echo "[1/4] 更新后端依赖..."
    cd backend
    pip install -r requirements.txt -q
    cd ..
    
    # 更新前端依赖
    echo "[2/4] 更新前端依赖..."
    cd frontend
    npm install --silent
    cd ..
    
    echo ""
    echo "✅ 依赖更新完成！"
    echo ""
    echo "请手动重启服务："
    echo ""
    echo "  终端1 (后端):"
    echo "    cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    echo "  终端2 (前端):"
    echo "    cd frontend && npm run dev"
    echo ""
fi
