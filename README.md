# OpenClaw Full Deployment (Phase 1-3)

一键部署完整系统：
- MySQL
- Redis
- FastAPI Backend
- Celery Worker
- Frontend (Node/Vite)
- Docker Compose

适用于 **Linux Server (Debian / Ubuntu)**。

## 项目结构

部署后的推荐仓库结构：

```
openclaw-deployment
│
├── backend/
│   └── FastAPI 项目代码
│
├── frontend/
│   └── 前端项目代码
│
├── deploy.sh
├── docker-compose.yml
└── README.md
```

## 1. 克隆仓库

在你的 Linux 服务器执行：

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

## 2. 运行部署脚本

给脚本执行权限：

```bash
chmod +x deploy.sh
```

运行部署：

```bash
sudo ./deploy.sh
```

脚本会自动：
- 安装 Docker
- 安装 Docker Compose
- 创建 `.env`
- 启动 MySQL
- 启动 Redis
- 启动 FastAPI
- 启动 Celery Worker
- 启动 Frontend

## 3. 访问服务

部署成功后：

### Backend API
http://SERVER_IP:8000/docs

FastAPI 自动生成接口文档。

### Frontend
http://SERVER_IP:5173

## 4. 环境变量

部署脚本会自动生成 `.env`：

```
MYSQL_ROOT_PASSWORD=Root123456!
MYSQL_DATABASE=fastapi_pdf
MYSQL_USER=app
MYSQL_PASSWORD=app123456
SECRET_KEY=auto_generated_key
DATABASE_URL=mysql+pymysql://app:app123456@mysql:3306/fastapi_pdf
REDIS_URL=redis://redis:6379/0
```

## 5. Docker 服务

系统会启动以下容器：

| Service   | 说明             |
|-----------|------------------|
| mysql     | MySQL 8 数据库   |
| redis     | Redis 缓存       |
| backend   | FastAPI API      |
| worker    | Celery Worker    |
| frontend  | Node 前端        |

查看容器：

```bash
docker ps
```

## 6. 常用命令

停止服务
```bash
docker compose down
```

重启服务
```bash
docker compose restart
```

查看日志
```bash
docker compose logs -f
```

## 7. 服务器要求

| 资源   | 推荐        |
|--------|-------------|
| CPU    | 2 Core      |
| RAM    | 4GB         |
| Disk   | 20GB        |

系统：Debian 11+
