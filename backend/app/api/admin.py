from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.models import Admin, User, AIModel, APITemplate, ApiLog, UserOperation

router = APIRouter()


# ========== 依赖 ==========

def get_current_admin(token: str, db: Session = Depends(get_db)):
    """获取当前管理员"""
    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的令牌")
    
    admin_id = payload.get("sub")
    if admin_id is None:
        raise HTTPException(status_code=401, detail="无效的令牌")
    
    admin = db.query(Admin).filter(Admin.id == int(admin_id)).first()
    if admin is None:
        raise HTTPException(status_code=401, detail="管理员不存在")
    
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")
    
    return admin


# ========== 认证路由 ==========

@router.post("/auth/login")
def admin_login(username: str, password: str, db: Session = Depends(get_db)):
    """管理员登录"""
    admin = db.query(Admin).filter(Admin.username == username).first()
    
    if not admin:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not verify_password(password, admin.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")
    
    # 生成令牌
    access_token = create_access_token(data={"sub": str(admin.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "role": admin.role,
            "is_active": admin.is_active
        }
    }


@router.post("/auth/register")
def register_admin(username: str, password: str, role: str = "admin", db: Session = Depends(get_db)):
    """注册管理员"""
    admin_count = db.query(Admin).count()
    if admin_count > 0:
        raise HTTPException(status_code=400, detail="管理员已存在")
    
    admin = Admin(
        username=username,
        password_hash=get_password_hash(password),
        role=role,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return {"id": admin.id, "username": admin.username}


# ========== 用户管理 ==========

@router.get("/users")
def get_users(page: int = 1, page_size: int = 20, status: str = None, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取用户列表"""
    query = db.query(User)
    if status:
        query = query.filter(User.status == status)
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": users, "total": total, "page": page, "page_size": page_size}


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/users")
def create_user(username: str, email: str, password: str, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """创建用户"""
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    user = User(username=username, email=email, password_hash=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/quota")
def update_user_quota(user_id: int, daily_limit: int = None, monthly_limit: int = None, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """设置用户配额"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if daily_limit is not None:
        user.daily_limit = daily_limit
    if monthly_limit is not None:
        user.monthly_limit = monthly_limit
    
    db.commit()
    return user


@router.patch("/users/{user_id}/disable")
def disable_user(user_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """禁用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.status = "disabled"
    db.commit()
    return {"message": "用户已禁用"}


# ========== AI 模型管理 ==========

@router.get("/ai-models")
def get_ai_models(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取AI模型列表"""
    models = db.query(AIModel).all()
    return models


@router.post("/ai-models")
def create_ai_model(name: str, base_url: str, api_key: str, model_name: str, request_method: str = "POST", 
                   header_template: str = "{}", body_template: str = None, db: Session = Depends(get_db), 
                   current_admin: Admin = Depends(get_current_admin)):
    """创建AI模型配置"""
    import json
    model = AIModel(
        name=name, base_url=base_url, api_key=api_key, model_name=model_name,
        request_method=request_method, header_template=json.loads(header_template), body_template=body_template
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


# ========== API 模板管理 ==========

@router.get("/templates")
def get_templates(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取API模板列表"""
    templates = db.query(APITemplate).all()
    return templates


@router.post("/templates")
def create_template(model_id: int, name: str, prompt_template: str = None, json_body_template: str = None,
                   timeout: int = 60, max_concurrency: int = 5, db: Session = Depends(get_db), 
                   current_admin: Admin = Depends(get_current_admin)):
    """创建API模板"""
    template = APITemplate(model_id=model_id, name=name, prompt_template=prompt_template, 
                          json_body_template=json_body_template, timeout=timeout, max_concurrency=max_concurrency)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


# ========== 日志管理 ==========

@router.get("/logs/api")
def get_api_logs(page: int = 1, page_size: int = 20, user_id: int = None, is_error: bool = None,
                db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取API请求日志"""
    query = db.query(ApiLog)
    if user_id:
        query = query.filter(ApiLog.user_id == user_id)
    if is_error is not None:
        query = query.filter(ApiLog.is_error == is_error)
    total = query.count()
    logs = query.order_by(ApiLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": logs, "total": total, "page": page, "page_size": page_size}


# ========== 统计 ==========

@router.get("/stats/users")
def get_user_stats(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取用户统计"""
    total = db.query(User).count()
    active = db.query(User).filter(User.status == "active").count()
    return {"total": total, "active": active}
