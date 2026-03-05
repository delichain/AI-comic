#!/bin/bash
# 下载 AI-Comic 后端代码

set -e

BACKEND_DIR="/opt/ai-comic/backend"

echo "📦 正在下载后端代码..."

# 创建目录
mkdir -p "$BACKEND_DIR/app/api"
mkdir -p "$BACKEND_DIR/app/core"
mkdir -p "$BACKEND_DIR/app/models"
mkdir -p "$BACKEND_DIR/app/schemas"
mkdir -p "$BACKEND_DIR/app/services"

cd "$BACKEND_DIR"

# 下载文件
echo "下载 requirements.txt..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/requirements.txt" -o requirements.txt

echo "下载 app/main.py..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/main.py" -o app/main.py

echo "下载 app/core/config.py..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/config.py" -o app/core/config.py

echo "下载 app/core/database.py..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/database.py" -o app/core/database.py

echo "下载 app/core/security.py..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/core/security.py" -o app/core/security.py

echo "下载 app/models/models.py..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/models/models.py" -o app/models/models.py

echo "下载 app/schemas/schemas.py..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/schemas/schemas.py" -o app/schemas/schemas.py

echo "下载 app/api/admin.py..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/api/admin.py" -o app/api/admin.py

echo "下载 app/api/user.py..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/api/user.py" -o app/api/user.py

# 创建 __init__.py 文件
touch app/__init__.py
touch app/api/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py

echo "✅ 后端代码下载完成！"
echo ""
echo "重启服务..."
cd /opt/ai-comic
docker compose restart backend

echo "✅ 完成！"
echo "访问 API 文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
