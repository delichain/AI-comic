#!/bin/bash
# 下载 AI-Comic 前端代码

set -e

FRONTEND_DIR="/opt/ai-comic/frontend"

echo "📦 正在下载前端代码..."

# 创建目录
mkdir -p "$FRONTEND_DIR/src/{api,components,router,stores,views,assets}"

cd "$FRONTEND_DIR"

# 下载文件
echo "下载 package.json..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/package.json" -o package.json

echo "下载 vite.config.js..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/vite.config.js" -o vite.config.js

echo "下载 index.html..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/index.html" -o index.html

echo "下载 src/main.js..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/main.js" -o src/main.js

echo "下载 src/App.vue..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/App.vue" -o src/App.vue

echo "下载 src/router/index.js..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/router/index.js" -o src/router/index.js

echo "下载 src/api/index.js..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/api/index.js" -o src/api/index.js

echo "下载 src/stores/user.js..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/stores/user.js" -o src/stores/user.js

echo "下载 src/views/Login.vue..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Login.vue" -o src/views/Login.vue

echo "下载 src/views/Register.vue..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Register.vue" -o src/views/Register.vue

echo "下载 src/views/Home.vue..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Home.vue" -o src/views/Home.vue

echo "下载 src/views/Upload.vue..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Upload.vue" -o src/views/Upload.vue

echo "下载 src/views/Generate.vue..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Generate.vue" -o src/views/Generate.vue

echo "下载 src/views/Works.vue..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/frontend/src/views/Works.vue" -o src/views/Works.vue

echo "✅ 前端代码下载完成！"
echo ""
echo "安装依赖并启动..."
cd "$FRONTEND_DIR"
npm config set registry https://registry.npmmirror.com
npm install

echo "重启服务..."
cd /opt/ai-comic
docker compose restart frontend

echo "✅ 完成！"
echo "访问前端: http://$(hostname -I | awk '{print $1}'):5173"
