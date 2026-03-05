#!/bin/bash
# AI-Comic 完整部署脚本 (整合版)

set -e

echo "==== AI-Comic 完整部署 ===="

INSTALL_DIR="/opt/ai-comic"

# 1. 清理旧环境
echo "🧹 清理旧环境..."
cd "$INSTALL_DIR"
docker compose down 2>/dev/null || true

# 2. 创建目录
echo "📁 创建目录..."
mkdir -p backend/app/{api,core,models,schemas,services}
mkdir -p frontend/src/{api,router,stores,views,assets}

# 3. 下载后端代码
echo "📦 下载后端代码..."
cd "$INSTALL_DIR/backend"

curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/requirements.txt" -o requirements.txt
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/Dockerfile" -o Dockerfile
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/main.py" -o app/main.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/config.py" -o app/core/config.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/database.py" -o app/core/database.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/security.py" -o app/core/security.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/models/models.py" -o app/models/models.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/schemas/schemas.py" -o app/schemas/schemas.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/api/admin.py" -o app/api/admin.py
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/api/user.py" -o app/api/user.py

# 创建 __init__.py
touch app/__init__.py
touch app/api/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py

# 4. 下载前端代码
echo "📦 下载前端代码..."
cd "$INSTALL_DIR/frontend"

curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/package.json" -o package.json
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/vite.config.js" -o vite.config.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/.env" -o .env
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/index.html" -o index.html
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/main.js" -o src/main.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/App.vue" -o src/App.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/router/index.js" -o src/router/index.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/api/index.js" -o src/api/index.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/stores/user.js" -o src/stores/user.js
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Login.vue" -o src/views/Login.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Register.vue" -o src/views/Register.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Home.vue" -o src/views/Home.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Upload.vue" -o src/views/Upload.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Generate.vue" -o src/views/Generate.vue
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Works.vue" -o src/views/Works.vue

# 5. 下载 docker-compose
echo "📦 下载 docker-compose..."
cd "$INSTALL_DIR"
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/docker-compose.yml" -o docker-compose.yml

# 6. 启动服务
echo "🚀 启动服务..."
docker compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 7. 检查状态
echo "📊 检查服务状态..."
docker ps

echo ""
echo "✅ 部署完成！"
echo "===================="
echo "前端: http://$(hostname -I | awk '{print $1}'):5173"
echo "后端: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "===================="
echo ""
echo "查看日志: docker compose logs -f"
