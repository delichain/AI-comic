#!/bin/bash
# 快速修复 - 删除旧数据重新开始

set -e

echo "==== 快速修复 ===="

cd /opt/ai-comic

# 1. 停止后端
echo "🛑 停止后端..."
docker compose stop backend

# 2. 删除旧数据库卷（会删除所有数据）
echo "🗑️ 删除旧数据库..."
docker volume rm ai-comic_mysql_data 2>/dev/null || true

# 3. 下载最新代码
echo "📥 下载最新代码..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/requirements.txt" -o backend/requirements.txt
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/main.py" -o backend/app/main.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/security.py" -o backend/app/core/security.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/models/models.py" -o backend/app/models/models.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/api/admin.py" -o backend/app/api/admin.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/api/user.py" -o backend/app/api/user.py

# 4. 重新构建
echo "🔨 重新构建后端..."
docker compose build --no-cache backend

# 5. 启动
echo "🚀 启动..."
docker compose up -d

# 6. 等待
echo "⏳ 等待启动 (60秒)..."
sleep 60

# 7. 测试
echo "🧪 测试登录..."
RESULT=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login?username=admin&password=admin123" 2>/dev/null)
echo "$RESULT"

if echo "$RESULT" | grep -q "access_token"; then
    echo ""
    echo "======================================"
    echo "✅ ✅ ✅ 登录成功！ ✅ ✅ ✅"
    echo "======================================"
else
    echo "❌ 登录失败"
fi
