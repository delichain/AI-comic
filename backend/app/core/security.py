from datetime import datetime, timedelta
from typing import Optional
import hashlib
import hmac
import base64
import json
from app.core.config import settings

def simple_hash(password: str) -> str:
    """简单哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return simple_hash(plain_password) == hashed_password

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return simple_hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    import jwt
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """解码访问令牌"""
    import jwt
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        return None
