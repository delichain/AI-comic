from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色"""
    ADMIN = "admin"      # 超级管理员
    MANAGER = "manager"  # 管理员
    USER = "user"        # 普通用户


class UserStatus(str, enum.Enum):
    """用户状态"""
    ACTIVE = "active"
    DISABLED = "disabled"


class Admin(Base):
    """管理员表"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ADMIN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    login_logs = relationship("AdminLoginLog", back_populates="admin")


class AdminLoginLog(Base):
    """管理员登录日志"""
    __tablename__ = "admin_login_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    login_time = Column(DateTime, server_default=func.now())
    success = Column(Boolean, default=True)

    admin = relationship("Admin", back_populates="login_logs")


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    
    # 配额管理
    daily_limit = Column(Integer, default=100)      # 每日限制
    monthly_limit = Column(Integer, default=1000)   # 每月限制
    daily_used = Column(Integer, default=0)        # 今日已用
    monthly_used = Column(Integer, default=0)      # 本月已用
    last_reset_date = Column(String(10))           # 上次重置日期 YYYY-MM-DD
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    api_logs = relationship("ApiLog", back_populates="user")
    operations = relationship("UserOperation", back_populates="user")


class AIModel(Base):
    """AI模型配置表"""
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)           # 模型名称 如 OpenAI
    base_url = Column(String(255), nullable=False)       # Base URL
    api_key = Column(String(255), nullable=False)        # API Key (加密存储)
    model_name = Column(String(100), nullable=False)     # 模型名称 如 gpt-4o
    request_method = Column(String(10), default="POST")  # 请求方式
    header_template = Column(JSON, default=dict)         # Header 模板
    body_template = Column(Text)                          # Body 模板
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    templates = relationship("APITemplate", back_populates="model")


class APITemplate(Base):
    """API模板表"""
    __tablename__ = "api_templates"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"))
    name = Column(String(100), nullable=False)           # 模板名称
    prompt_template = Column(Text)                       # Prompt 模板
    json_body_template = Column(Text)                   # JSON Body 模板
    timeout = Column(Integer, default=60)               # 超时时间(秒)
    max_concurrency = Column(Integer, default=5)        # 最大并发
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    model = relationship("AIModel", back_populates="templates")
    logs = relationship("ApiLog", back_populates="template")


class ApiLog(Base):
    """API请求日志"""
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    template_id = Column(Integer, ForeignKey("api_templates.id"))
    
    # 请求信息
    request_url = Column(String(500))
    request_method = Column(String(10))
    request_headers = Column(JSON)
    request_body = Column(Text)
    
    # 响应信息
    response_status = Column(Integer)
    response_headers = Column(JSON)
    response_body = Column(Text)
    response_time = Column(Float)  # 毫秒
    
    # 费用
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0)
    
    # 状态
    is_error = Column(Boolean, default=False)
    error_message = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="api_logs")
    template = relationship("APITemplate", back_populates="logs")


class UserOperation(Base):
    """用户操作日志"""
    __tablename__ = "user_operations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    operation_type = Column(String(50))  # 操作类型
    operation_desc = Column(Text)        # 操作描述
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="operations")
