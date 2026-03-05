#!/bin/bash
# 完全修复并重启 - 一键运行

set -e

echo "==== 完全修复 AI-Comic ===="

cd /opt/ai-comic

# 1. 停止所有容器
echo "🛑 停止所有容器..."
docker compose down 2>/dev/null || true

# 2. 下载后端代码
echo "📥 下载后端代码..."
mkdir -p backend/app/{api,core,models,schemas}

curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/requirements.txt" -o backend/requirements.txt
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/main.py" -o backend/app/main.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/config.py" -o backend/app/core/config.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/database.py" -o backend/app/core/database.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/security.py" -o backend/app/core/security.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/models/models.py" -o backend/app/models/models.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/api/admin.py" -o backend/app/api/admin.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/api/user.py" -o backend/app/api/user.py

# 创建 __init__.py
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py

# 3. 下载前端代码
echo "📥 下载前端代码..."
mkdir -p frontend/src/{api,router,stores,views}

curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/package.json" -o frontend/package.json
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/vite.config.js" -o frontend/vite.config.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/.env" -o frontend/.env
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/index.html" -o frontend/index.html
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/main.js" -o frontend/src/main.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/App.vue" -o frontend/src/App.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/router/index.js" -o frontend/src/router/index.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/api/index.js" -o frontend/src/api/index.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/stores/user.js" -o frontend/src/stores/user.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Login.vue" -o frontend/src/views/Login.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Register.vue" -o frontend/src/views/Register.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Home.vue" -o frontend/src/views/Home.vue

# 4. 下载 docker-compose
echo "📥 下载 docker-compose..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/docker-compose.yml" -o docker-compose.yml

# 5. 删除旧的镜像，重新构建
echo "🔨 重新构建后端..."
docker rmi openclaw-backend 2>/dev/null || true
docker compose build --no-cache backend

# 6. 启动所有服务
echo "🚀 启动所有服务..."
docker compose up -d

# 7. 等待启动
echo "⏳ 等待服务启动 (60秒)..."
sleep 60

# 8. 检查后端状态
echo "📊 检查后端..."
docker logs --tail 10 openclaw-backend 2>&1 || true

# 9. 测试登录
echo "🧪 测试登录..."
sleep 5

RESULT=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login?username=admin&password=admin123" 2>/dev/null || echo '{"error":"failed"}')
echo "登录结果: $RESULT"

if echo "$RESULT" | grep -q "access_token"; then
    echo ""
    echo "======================================"
    echo "✅ ✅ ✅ 登录成功！ ✅ ✅ ✅"
    echo "======================================"
    echo "前端: http://你的公网IP:5173"
    echo "后端: http://你的公网IP:8000/docs"
    echo "账号: admin"
    echo "密码: admin123"
else
    echo "❌ 登录可能失败，请查看日志"
fi
