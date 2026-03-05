from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

# 导入所有模型，确保表能创建
from app.models import models

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Comic Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(admin.router, prefix=settings.API_V1_PREFIX, tags=["管理后台"])
app.include_router(user.router, prefix=settings.API_V1_PREFIX, tags=["用户接口"])


@app.get("/")
def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


#启动 时创建默认管理员
@app.on_event("startup")
async def startup_event():
    from app.core.database import SessionLocal
    from app.models.models import Admin
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    try:
        # 检查是否已有管理员
        admin_count = db.query(Admin).count()
        if admin_count == 0:
            # 创建默认管理员
            default_admin = Admin(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role="admin"
            )
            db.add(default_admin)
            db.commit()
            print("✅ 默认管理员已创建: admin / admin123")
    finally:
        db.close()
