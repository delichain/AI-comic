from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.models import Admin, AdminLoginLog, User, AIModel, APITemplate, ApiLog, UserOperation
from app.schemas.schemas import (
    AdminLoginRequest, AdminLoginResponse, AdminInfo, AdminCreate,
    UserCreate, UserUpdate, UserResponse, UserQuotaUpdate,
    AIModelCreate, AIModelUpdate, AIModelResponse,
    APITemplateCreate, APITemplateUpdate, APITemplateResponse,
    ApiLogResponse, OperationLogResponse,
    MessageResponse, PageResponse
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ========== 依赖 ==========

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

@router.post("/auth/login", response_model=AdminLoginResponse)
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    admin = db.query(Admin).filter(Admin.username == request.username).first()
    
    # 记录登录日志
    login_log = AdminLoginLog(
        admin_id=admin.id if admin else 0,
        success=False
    )
    
    if not admin:
        db.add(login_log)
        db.commit()
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not verify_password(request.password, admin.password_hash):
        db.add(login_log)
        db.commit()
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not admin.is_active:
        db.add(login_log)
        db.commit()
        raise HTTPException(status_code=403, detail="账户已被禁用")
    
    # 更新登录日志为成功
    login_log.success = True
    db.add(login_log)
    db.commit()
    
    # 生成令牌
    access_token = create_access_token(data={"sub": str(admin.id)})
    
    return AdminLoginResponse(
        access_token=access_token,
        admin=AdminInfo.model_validate(admin)
    )


@router.post("/auth/register", response_model=AdminInfo)
def register_admin(request: AdminCreate, db: Session = Depends(get_db)):
    """注册管理员（首个管理员）"""
    # 检查是否已有管理员
    admin_count = db.query(Admin).count()
    if admin_count > 0:
        raise HTTPException(status_code=400, detail="管理员已存在")
    
    admin = Admin(
        username=request.username,
        password_hash=get_password_hash(request.password),
        role=request.role
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return AdminInfo.model_validate(admin)


# ========== 用户管理 ==========

@router.get("/users", response_model=PageResponse)
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """获取用户列表"""
    query = db.query(User)
    
    if status:
        query = query.filter(User.status == status)
    
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return PageResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse.model_validate(user)


@router.post("/users", response_model=UserResponse)
def create_user(request: UserCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """创建用户"""
    # 检查用户名和邮箱是否存在
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    user = User(
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, request: UserUpdate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if request.username and request.username != user.username:
        if db.query(User).filter(User.username == request.username).first():
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = request.username
    
    if request.email and request.email != user.email:
        if db.query(User).filter(User.email == request.email).first():
            raise HTTPException(status_code=400, detail="邮箱已存在")
        user.email = request.email
    
    if request.password:
        user.password_hash = get_password_hash(request.password)
    
    if request.status:
        user.status = request.status
    
    if request.daily_limit is not None:
        user.daily_limit = request.daily_limit
    
    if request.monthly_limit is not None:
        user.monthly_limit = request.monthly_limit
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    
    return MessageResponse(message="用户删除成功")


@router.patch("/users/{user_id}/quota", response_model=UserResponse)
def update_user_quota(user_id: int, request: UserQuotaUpdate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """设置用户配额"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if request.daily_limit is not None:
        user.daily_limit = request.daily_limit
    
    if request.monthly_limit is not None:
        user.monthly_limit = request.monthly_limit
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.patch("/users/{user_id}/disable")
def disable_user(user_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """禁用用户"""
    from app.models.models import UserStatus
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.status = UserStatus.DISABLED
    db.commit()
    
    return MessageResponse(message="用户已禁用")


@router.patch("/users/{user_id}/enable")
def enable_user(user_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """启用用户"""
    from app.models.models import UserStatus
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.status = UserStatus.ACTIVE
    db.commit()
    
    return MessageResponse(message="用户已启用")


# ========== AI 模型管理 ==========

@router.get("/ai-models", response_model=List[AIModelResponse])
def get_ai_models(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取AI模型列表"""
    models = db.query(AIModel).all()
    return [AIModelResponse.model_validate(m) for m in models]


@router.get("/ai-models/{model_id}", response_model=AIModelResponse)
def get_ai_model(model_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取AI模型详情"""
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return AIModelResponse.model_validate(model)


@router.post("/ai-models", response_model=AIModelResponse)
def create_ai_model(request: AIModelCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """创建AI模型配置"""
    model = AIModel(
        name=request.name,
        base_url=request.base_url,
        api_key=request.api_key,
        model_name=request.model_name,
        request_method=request.request_method,
        header_template=request.header_template,
        body_template=request.body_template
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    
    return AIModelResponse.model_validate(model)


@router.put("/ai-models/{model_id}", response_model=AIModelResponse)
def update_ai_model(model_id: int, request: AIModelUpdate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """更新AI模型配置"""
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    if request.name is not None:
        model.name = request.name
    if request.base_url is not None:
        model.base_url = request.base_url
    if request.api_key is not None:
        model.api_key = request.api_key
    if request.model_name is not None:
        model.model_name = request.model_name
    if request.request_method is not None:
        model.request_method = request.request_method
    if request.header_template is not None:
        model.header_template = request.header_template
    if request.body_template is not None:
        model.body_template = request.body_template
    if request.is_active is not None:
        model.is_active = request.is_active
    
    db.commit()
    db.refresh(model)
    
    return AIModelResponse.model_validate(model)


@router.delete("/ai-models/{model_id}")
def delete_ai_model(model_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """删除AI模型"""
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    db.delete(model)
    db.commit()
    
    return MessageResponse(message="模型删除成功")


# ========== API 模板管理 ==========

@router.get("/templates", response_model=List[APITemplateResponse])
def get_templates(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取API模板列表"""
    templates = db.query(APITemplate).all()
    return [APITemplateResponse.model_validate(t) for t in templates]


@router.get("/templates/{template_id}", response_model=APITemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取API模板详情"""
    template = db.query(APITemplate).filter(APITemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return APITemplateResponse.model_validate(template)


@router.post("/templates", response_model=APITemplateResponse)
def create_template(request: APITemplateCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """创建API模板"""
    # 验证模型是否存在
    model = db.query(AIModel).filter(AIModel.id == request.model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="AI模型不存在")
    
    template = APITemplate(
        model_id=request.model_id,
        name=request.name,
        prompt_template=request.prompt_template,
        json_body_template=request.json_body_template,
        timeout=request.timeout,
        max_concurrency=request.max_concurrency
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return APITemplateResponse.model_validate(template)


@router.put("/templates/{template_id}", response_model=APITemplateResponse)
def update_template(template_id: int, request: APITemplateUpdate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """更新API模板"""
    template = db.query(APITemplate).filter(APITemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    if request.name is not None:
        template.name = request.name
    if request.model_id is not None:
        template.model_id = request.model_id
    if request.prompt_template is not None:
        template.prompt_template = request.prompt_template
    if request.json_body_template is not None:
        template.json_body_template = request.json_body_template
    if request.timeout is not None:
        template.timeout = request.timeout
    if request.max_concurrency is not None:
        template.max_concurrency = request.max_concurrency
    if request.is_active is not None:
        template.is_active = request.is_active
    
    db.commit()
    db.refresh(template)
    
    return APITemplateResponse.model_validate(template)


@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """删除API模板"""
    template = db.query(APITemplate).filter(APITemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db.delete(template)
    db.commit()
    
    return MessageResponse(message="模板删除成功")


# ========== 日志管理 ==========

@router.get("/logs/api", response_model=PageResponse)
def get_api_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Query(None),
    template_id: int = Query(None),
    is_error: bool = Query(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """获取API请求日志"""
    query = db.query(ApiLog)
    
    if user_id:
        query = query.filter(ApiLog.user_id == user_id)
    if template_id:
        query = query.filter(ApiLog.template_id == template_id)
    if is_error is not None:
        query = query.filter(ApiLog.is_error == is_error)
    
    total = query.count()
    logs = query.order_by(ApiLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PageResponse(
        items=[ApiLogResponse.model_validate(l) for l in logs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/logs/operations", response_model=PageResponse)
def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Query(None),
    operation_type: str = Query(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """获取用户操作日志"""
    query = db.query(UserOperation)
    
    if user_id:
        query = query.filter(UserOperation.user_id == user_id)
    if operation_type:
        query = query.filter(UserOperation.operation_type == operation_type)
    
    total = query.count()
    logs = query.order_by(UserOperation.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PageResponse(
        items=[OperationLogResponse.model_validate(l) for l in logs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# ========== 统计 ==========

@router.get("/stats/users")
def get_user_stats(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """获取用户统计"""
    from app.models.models import UserStatus
    
    total = db.query(User).count()
    active = db.query(User).filter(User.status == UserStatus.ACTIVE).count()
    disabled = db.query(User).filter(User.status == UserStatus.DISABLED).count()
    
    return {
        "total": total,
        "active": active,
        "disabled": disabled
    }


@router.get("/stats/api")
def get_api_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """获取API调用统计"""
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total_requests = db.query(ApiLog).filter(ApiLog.created_at >= start_date).count()
    error_requests = db.query(ApiLog).filter(ApiLog.created_at >= start_date, ApiLog.is_error == True).count()
    total_tokens = db.query(ApiLog).filter(ApiLog.created_at >= start_date).with_entities(func.sum(ApiLog.tokens_used)).scalar() or 0
    total_cost = db.query(ApiLog).filter(ApiLog.created_at >= start_date).with_entities(func.sum(ApiLog.cost)).scalar() or 0
    
    return {
        "days": days,
        "total_requests": total_requests,
        "error_requests": error_requests,
        "success_rate": round((total_requests - error_requests) / total_requests * 100, 2) if total_requests > 0 else 0,
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 4)
    }
