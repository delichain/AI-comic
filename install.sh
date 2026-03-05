#!/bin/bash
# AI-comic 一键安装脚本
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

echo "📦 正在下载 AI-Comic..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 下载文件
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/docker-compose.yml" -o docker-compose.yml
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/deploy.sh" -o deploy.sh
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/README.md" -o README.md

# 设置权限
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

echo "🐳 正在配置 Docker 国内镜像..."
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF

systemctl daemon-reload
systemctl restart docker

echo "🐳 正在启动 Docker 服务..."
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
    
    # 配置国内镜像
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
    systemctl daemon-reload
    systemctl restart docker
fi

# 启动服务
docker compose up -d

echo ""
echo "✅ 安装完成！"
echo "===================="
echo "Backend API: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "Frontend:    http://$(hostname -I | awk '{print $1}'):5173"
echo ""
echo "查看日志: docker compose logs -f"
echo "停止服务: docker compose down"
echo "===================="
