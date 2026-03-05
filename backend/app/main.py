from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.models.models import Admin, UserRole
from app.core.security import get_password_hash
from app.api import admin, user

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Comic Backend",
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

# 注册路由 (必须在导入之后)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX, tags=["管理后台"])
app.include_router(user.router, prefix=settings.API_V1_PREFIX, tags=["用户接口"])


@app.get("/")
def root():
    return {
        "name": "AI Comic Backend",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# 启动时创建默认管理员
@app.on_event("startup")
async def startup_event():
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        admin_count = db.query(Admin).count()
        if admin_count == 0:
            default_admin = Admin(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(default_admin)
            db.commit()
            print("✅ 默认管理员已创建: admin / admin123")
        else:
            print(f"管理员已存在 ({admin_count}个)")
    except Exception as e:
        print(f"❌ 启动错误: {e}")
    finally:
        db.close()
