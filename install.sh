#!/bin/bash
# AI-comic 一键安装脚本 (修复版)
# 运行方式: curl -sL https://raw.githubusercontent.com/delichain/AI-comic/main/install.sh | sudo bash

set -e

echo "==== AI-Comic 一键安装脚本 ===="

# 检测系统
if [ "$(uname)" != "Linux" ]; then
    echo "⚠️ 此脚本仅支持 Linux 系统"
    exit 1
fi

# 检测是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "⚠️ 请使用 sudo 运行: sudo bash -c \"\$(curl -sL https://raw.githubusercontent.com/delichain/AI-comic/main/install.sh)\""
    exit 1
fi

INSTALL_DIR="/opt/ai-comic"
SERVER_IP=$(hostname -I | awk '{print $1}')

# 清理旧的配置
echo "🧹 清理旧配置..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "📦 正在下载 AI-Comic..."

# 下载文件 - 使用 -L 跟随重定向
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/docker-compose.yml" -o docker-compose.yml
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/deploy.sh" -o deploy.sh
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/README.md" -o README.md

# 验证下载
if [ ! -s docker-compose.yml ]; then
    echo "❌ 下载失败，请检查网络"
    exit 1
fi

# 检查并删除 version 属性（已废弃）
sed -i '/^version:/d' docker-compose.yml

chmod +x deploy.sh

# 生成环境变量
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 64 | head -n 1)

cat > .env <<EOF
MYSQL_ROOT_PASSWORD=Root123456!
MYSQL_DATABASE=fastapi_pdf
MYSQL_USER=app
MYSQL_PASSWORD=app123456
SECRET_KEY=$SECRET_KEY
DATABASE_URL=mysql+pymysql://app:app123456@mysql:3306/fastapi_pdf
REDIS_URL=redis://redis:6379/0
EOF

echo "🐳 正在配置 Docker..."
mkdir -p /etc/docker

# 清理旧的 daemon.json（如果有的话）
rm -f /etc/docker/daemon.json

# Docker 已安装?
if ! command -v docker &> /dev/null; then
    echo "📥 正在安装 Docker..."
    apt update
    apt install -y ca-certificates curl gnupg lsb-release
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
fi

# 重置 Docker registry 配置为空（使用默认官方源）
echo '{}' > /etc/docker/daemon.json
systemctl daemon-reload
systemctl restart docker

# 等待 Docker 重启
sleep 2

# 测试 Docker
echo "🔍 测试 Docker..."
docker info >/dev/null 2>&1 || { echo "❌ Docker 启动失败"; exit 1; }

echo "🚀 正在启动服务..."
cd "$INSTALL_DIR"
docker compose up -d

echo ""
echo "✅ 安装完成！"
echo "===================="
echo "Backend API: http://${SERVER_IP}:8000/docs"
echo "Frontend:    http://${SERVER_IP}:5173"
echo ""
echo "查看日志: docker compose logs -f"
echo "停止服务: docker compose down"
echo "===================="
