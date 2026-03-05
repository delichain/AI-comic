#!/bin/bash
# AI-Comic 最终一键修复脚本 - 解决所有问题

set -e

echo "==== AI-Comic 最终修复开始 ===="

cd /opt/ai-comic

# 1. 停止所有容器
echo "🛑 停止所有容器..."
docker compose down

# 2. 删除旧数据库（重新开始）
echo "🗑️ 删除旧数据库..."
docker volume rm ai-comic_mysql_data 2>/dev/null || true

# 3. 下载最新的后端代码
echo "📥 下载后端代码..."
mkdir -p backend/app/{api,core,models}

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

# 4. 下载最新的前端代码
echo "📥 下载前端代码..."
mkdir -p frontend/src/{api,router,stores,views}

curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/package.json" -o frontend/package.json
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/vite.config.js" -o frontend/vite.config.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/index.html" -o frontend/index.html
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/main.js" -o frontend/src/main.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/App.vue" -o frontend/src/App.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/router/index.js" -o frontend/src/router/index.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/api/index.js" -o frontend/src/api/index.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/stores/user.js" -o frontend/src/stores/user.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Login.vue" -o frontend/src/views/Login.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Register.vue" -o frontend/src/views/Register.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Home.vue" -o frontend/src/views/Home.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Upload.vue" -o frontend/src/views/Upload.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Generate.vue" -o frontend/src/views/Generate.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Works.vue" -o frontend/src/views/Works.vue

# 5. 下载 docker-compose
echo "📥 下载 docker-compose..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/docker-compose.yml" -o docker-compose.yml

# 6. 重新构建后端
echo "🔨 重新构建后端..."
docker compose build --no-cache backend

# 7. 启动所有服务
echo "🚀 启动所有服务..."
docker compose up -d

# 8. 等待MySQL就绪
echo "⏳ 等待MySQL就绪..."
for i in {1..30}; do
    if docker exec openclaw-mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo "✅ MySQL 已就绪"
        break
    fi
    sleep 2
done

# 9. 等待后端启动
echo "⏳ 等待后端启动..."
sleep 30

# 10. 测试后端
echo "🧪 测试后端..."
BACKEND_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
echo "后端健康检查: $BACKEND_HEALTH"

# 11. 测试登录
echo "🧪 测试登录..."
LOGIN_RESULT=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login?username=admin&password=admin123" 2>/dev/null || echo '{"error":"failed"}')
echo "登录结果: $LOGIN_RESULT"

# 12. 重启前端
echo "🔄 重启前端..."
docker compose restart frontend
sleep 10

echo ""
echo "======================================"
if echo "$LOGIN_RESULT" | grep -q "access_token"; then
    echo "✅ ✅ ✅ 全部成功！ ✅ ✅ ✅"
    echo "======================================"
    echo ""
    echo "📱 访问地址: http://你的公网IP:5173"
    echo "📚 API文档: http://你的公网IP:8000/docs"
    echo "👤 管理员账号: admin"
    echo "🔑 管理员密码: admin123"
else
    echo "❌ 后端登录测试失败"
    echo "请查看日志: docker logs openclaw-backend"
fi
echo "======================================"
