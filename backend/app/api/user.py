from datetime import datetime
from typing import Optional
import json
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User, AIModel, APITemplate, ApiLog, UserOperation, UserStatus
from app.schemas.schemas import MessageResponse
from app.api.admin import get_current_admin, oauth2_scheme, Admin

router = APIRouter()


# ========== 用户 API ==========

@router.post("/ai/generate")
def generate_image(
    template_id: int,
    variables: dict,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """AI 生成图片（用户调用）"""
    # 解析 token 获取用户
    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的令牌")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="无效的令牌")
    
    # 查找用户
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户状态
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="用户已被禁用")
    
    # 检查配额
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if user.last_reset_date != today:
        # 重置每日配额
        user.daily_used = 0
        user.last_reset_date = today
        db.commit()
    
    if user.daily_used >= user.daily_limit:
        raise HTTPException(status_code=403, detail="已达到每日限额")
    
    # 获取模板
    template = db.query(APITemplate).filter(APITemplate.id == template_id, APITemplate.is_active == True).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 获取模型
    model = db.query(AIModel).filter(AIModel.id == template.model_id, AIModel.is_active == True).first()
    if not model:
        raise HTTPException(status_code=404, detail="AI模型不可用")
    
    # 替换变量
    prompt = template.prompt_template or ""
    body_template = template.json_body_template or "{}"
    
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        prompt = prompt.replace(placeholder, str(value))
        body_template = body_template.replace(placeholder, str(value))
    
    # 构造请求
    url = f"{model.base_url}/{model.model_name}"
    headers = model.header_template.copy()
    headers["Authorization"] = f"Bearer {model.api_key}"
    
    try:
        body = json.loads(body_template)
        if prompt:
            body["prompt"] = prompt
    except json.JSONDecodeError:
        body = {"prompt": prompt}
    
    # 记录请求日志
    log = ApiLog(
        user_id=user.id,
        template_id=template.id,
        request_url=url,
        request_method=model.request_method,
        request_headers=headers,
        request_body=json.dumps(body)
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    # 发送请求
    start_time = datetime.utcnow()
    try:
        with httpx.Client(timeout=template.timeout) as client:
            response = client.request(
                method=model.request_method,
                url=url,
                headers=headers,
                json=body if model.request_method == "POST" else None
            )
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # 更新日志
        log.response_status = response.status_code
        log.response_headers = dict(response.headers)
        log.response_body = response.text
        log.response_time = response_time
        
        if response.status_code >= 400:
            log.is_error = True
            log.error_message = response.text
        else:
            # 解析响应（这里需要根据实际 API 调整）
            try:
                resp_data = response.json()
                # 假设返回包含 usage 信息
                log.tokens_used = resp_data.get("usage", {}).get("total_tokens", 0)
                # 假设返回包含 cost 信息
                log.cost = resp_data.get("cost", 0.001)
            except:
                pass
            
            # 更新用户配额
            user.daily_used += 1
            user.monthly_used += 1
        
        db.commit()
        
        if log.is_error:
            raise HTTPException(status_code=500, detail=f"AI API 请求失败: {log.error_message}")
        
        return {
            "success": True,
            "data": resp_data if 'resp_data' in dir() else {"message": "生成成功"},
            "log_id": log.id
        }
        
    except httpx.TimeoutException:
        log.is_error = True
        log.error_message = "请求超时"
        log.response_time = template.timeout * 1000
        db.commit()
        raise HTTPException(status_code=500, detail="请求超时")
    except Exception as e:
        log.is_error = True
        log.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/profile")
def get_user_profile(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取当前用户信息"""
    from app.core.security import decode_access_token
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的令牌")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "daily_limit": user.daily_limit,
        "monthly_limit": user.monthly_limit,
        "daily_used": user.daily_used,
        "monthly_used": user.monthly_used,
        "status": user.status.value
    }


@router.get("/templates/available")
def get_available_templates(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取可用模板列表（用户可见）"""
    templates = db.query(APITemplate).filter(APITemplate.is_active == True).all()
    
    result = []
    for t in templates:
        model = db.query(AIModel).filter(AIModel.id == t.model_id, AIModel.is_active == True).first()
        if model:
            result.append({
                "id": t.id,
                "name": t.name,
                "model_name": model.name,
                "timeout": t.timeout,
                "variables": extract_variables(t.prompt_template, t.json_body_template)
            })
    
    return result


def extract_variables(prompt_template: str, json_body_template: str) -> list:
    """提取模板中的变量"""
    import re
    variables = set()
    
    if prompt_template:
        variables.update(re.findall(r'\{\{(\w+)\}\}', prompt_template))
    if json_body_template:
        variables.update(re.findall(r'\{\{(\w+)\}\}', json_body_template))
    
    return list(variables)
