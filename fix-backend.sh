#!/bin/bash
# 修复并重启后端 - 确保成功

set -e

echo "==== 修复 AI-Comic 后端 ===="

cd /opt/ai-comic

# 1. 下载最新代码
echo "📥 下载最新代码..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/requirements.txt" -o backend/requirements.txt
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/main.py" -o backend/app/main.py

# 2. 删除旧容器和镜像，重新构建
echo "🔨 重新构建后端..."
docker compose down backend 2>/dev/null || true
docker rmi openclaw-backend 2>/dev/null || true
docker compose build --no-cache backend

# 3. 启动后端
echo "🔄 启动后端..."
docker compose up -d backend

# 4. 等待启动（较长时间）
echo "⏳ 等待后端启动 (60秒)..."
sleep 60

# 5. 检查日志
echo "📋 后端日志:"
docker logs --tail 20 openclaw-backend

# 6. 测试
echo ""
echo "🧪 测试..."
sleep 5

HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
echo "健康检查: $HEALTH"

if echo "$HEALTH" | grep -q "healthy"; then
    echo ""
    echo "==== ✅ 后端启动成功！===="
    echo "请访问: http://你的IP:5173"
    echo "账号: admin"
    echo "密码: admin123"
else
    echo "❌ 后端启动可能失败，请查看上方日志"
fi
