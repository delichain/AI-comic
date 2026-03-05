#!/bin/bash
# 修复并重启后端

set -e

echo "==== 修复 AI-Comic 后端 ===="

cd /opt/ai-comic

# 1. 下载最新的 main.py
echo "📥 下载修复后的代码..."
curl -sL "https://raw.githubusercontent.com/delichain/AI-comic/main/backend/app/main.py" -o backend/app/main.py

# 2. 重新构建后端
echo "🔨 重新构建后端..."
docker compose build backend

# 3. 重启后端
echo "🔄 重启后端..."
docker compose up -d backend

# 4. 等待启动
echo "⏳ 等待后端启动 (30秒)..."
sleep 30

# 5. 测试健康检查
echo "🧪 测试后端..."
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "failed")
echo "健康检查: $HEALTH"

# 6. 尝试创建管理员
echo "👤 创建默认管理员..."
curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","role":"admin"}' 2>/dev/null || echo "管理员可能已存在"

# 7. 测试登录
echo "🔐 测试登录..."
LOGIN_RESULT=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' 2>/dev/null)

if echo "$LOGIN_RESULT" | grep -q "access_token"; then
  echo "✅ 登录成功！"
else
  echo "❌ 登录失败: $LOGIN_RESULT"
fi

echo ""
echo "==== 完成 ===="
echo "前端: http://你的IP:5173"
echo "后端: http://你的IP:8000/docs"
echo "账号: admin"
echo "密码: admin123"
