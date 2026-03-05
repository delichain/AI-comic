from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ========== 管理员 Schema ==========

class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    """管理员登录响应"""
    access_token: str
    token_type: str = "bearer"
    admin: "AdminInfo"


class AdminInfo(BaseModel):
    """管理员信息"""
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminCreate(BaseModel):
    """创建管理员"""
    username: str
    password: str
    role: str = "admin"


# ========== 用户 Schema ==========

class UserStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class UserCreate(BaseModel):
    """创建用户"""
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """更新用户"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    status: Optional[UserStatus] = None
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    status: str
    daily_limit: int
    monthly_limit: int
    daily_used: int
    monthly_used: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserQuotaUpdate(BaseModel):
    """更新用户配额"""
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None


# ========== AI Model Schema ==========

class AIModelCreate(BaseModel):
    """创建AI模型配置"""
    name: str
    base_url: str
    api_key: str
    model_name: str
    request_method: str = "POST"
    header_template: Dict[str, Any] = {}
    body_template: Optional[str] = None


class AIModelUpdate(BaseModel):
    """更新AI模型配置"""
    name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    request_method: Optional[str] = None
    header_template: Optional[Dict[str, Any]] = None
    body_template: Optional[str] = None
    is_active: Optional[bool] = None


class AIModelResponse(BaseModel):
    """AI模型响应"""
    id: int
    name: str
    base_url: str
    api_key: str  # 实际返回时应该脱敏
    model_name: str
    request_method: str
    header_template: Dict[str, Any]
    body_template: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== API Template Schema ==========

class APITemplateCreate(BaseModel):
    """创建API模板"""
    model_id: int
    name: str
    prompt_template: Optional[str] = None
    json_body_template: Optional[str] = None
    timeout: int = 60
    max_concurrency: int = 5


class APITemplateUpdate(BaseModel):
    """更新API模板"""
    name: Optional[str] = None
    model_id: Optional[int] = None
    prompt_template: Optional[str] = None
    json_body_template: Optional[str] = None
    timeout: Optional[int] = None
    max_concurrency: Optional[int] = None
    is_active: Optional[bool] = None


class APITemplateResponse(BaseModel):
    """API模板响应"""
    id: int
    model_id: int
    name: str
    prompt_template: Optional[str]
    json_body_template: Optional[str]
    timeout: int
    max_concurrency: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 日志 Schema ==========

class ApiLogResponse(BaseModel):
    """API日志响应"""
    id: int
    user_id: Optional[int]
    template_id: Optional[int]
    request_url: Optional[str]
    request_method: Optional[str]
    response_status: Optional[int]
    response_time: Optional[float]
    tokens_used: Optional[int]
    cost: Optional[float]
    is_error: bool
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OperationLogResponse(BaseModel):
    """操作日志响应"""
    id: int
    user_id: Optional[int]
    operation_type: str
    operation_desc: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 通用 Response ==========

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    code: int = 200


class PageResponse(BaseModel):
    """分页响应"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# 更新前向引用
AdminLoginResponse.model_rebuild()
