from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User, UserStatus, AIModel, APITemplate
import json

router = APIRouter()


# ========== 用户 API ==========

@router.post("/ai/generate")
def generate_image(template_id: int, variables: str, db: Session = Depends(get_db), token: str = None):
    """AI 生成图片（用户调用）"""
    from app.core.security import decode_access_token
    
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    
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
    from datetime import datetime
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if user.last_reset_date != today:
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
    import re
    vars_dict = json.loads(variables) if isinstance(variables, str) else variables
    prompt = template.prompt_template or ""
    body_template = template.json_body_template or "{}"
    
    for key, value in vars_dict.items():
        placeholder = f"{{{{{key}}}}}"
        prompt = prompt.replace(placeholder, str(value))
        body_template = body_template.replace(placeholder, str(value))
    
    # TODO: 实际调用 AI API
    return {"success": True, "message": "生成成功", "data": {"image_url": "https://example.com/image.jpg"}}


@router.get("/user/profile")
def get_user_profile(db: Session = Depends(get_db), token: str = None):
    """获取当前用户信息"""
    from app.core.security import decode_access_token
    
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    
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
        "status": user.status.value if hasattr(user.status, 'value') else user.status
    }


@router.get("/templates/available")
def get_available_templates(db: Session = Depends(get_db)):
    """获取可用模板列表"""
    templates = db.query(APITemplate).filter(APITemplate.is_active == True).all()
    result = []
    import re
    for t in templates:
        model = db.query(AIModel).filter(AIModel.id == t.model_id, AIModel.is_active == True).first()
        if model:
            variables = set()
            if t.prompt_template:
                variables.update(re.findall(r'\{\{(\w+)\}\}', t.prompt_template))
            if t.json_body_template:
                variables.update(re.findall(r'\{\{(\w+)\}\}', t.json_body_template))
            result.append({
                "id": t.id, "name": t.name, "model_name": model.name,
                "timeout": t.timeout, "variables": list(variables)
            })
    return result
