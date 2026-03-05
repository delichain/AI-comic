from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Admin(Base):
    """管理员表"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(20), default="active")
    
    # 配额管理
    daily_limit = Column(Integer, default=100)
    monthly_limit = Column(Integer, default=1000)
    daily_used = Column(Integer, default=0)
    monthly_used = Column(Integer, default=0)
    last_reset_date = Column(String(10))
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    api_logs = relationship("ApiLog", back_populates="user")
    operations = relationship("UserOperation", back_populates="user")


class AIModel(Base):
    """AI模型配置表"""
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    base_url = Column(String(255), nullable=False)
    api_key = Column(String(255), nullable=False)
    model_name = Column(String(100), nullable=False)
    request_method = Column(String(10), default="POST")
    header_template = Column(JSON, default=dict)
    body_template = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    templates = relationship("APITemplate", back_populates="model")


class APITemplate(Base):
    """API模板表"""
    __tablename__ = "api_templates"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"))
    name = Column(String(100), nullable=False)
    prompt_template = Column(Text)
    json_body_template = Column(Text)
    timeout = Column(Integer, default=60)
    max_concurrency = Column(Integer, default=5)
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
    
    request_url = Column(String(500))
    request_method = Column(String(10))
    request_headers = Column(JSON)
    request_body = Column(Text)
    
    response_status = Column(Integer)
    response_headers = Column(JSON)
    response_body = Column(Text)
    response_time = Column(Float)
    
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0)
    
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
    operation_type = Column(String(50))
    operation_desc = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="operations")
