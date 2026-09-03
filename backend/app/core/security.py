# -*- coding: utf-8 -*-
"""
[变更日志]
修改时间: 2026-09-03
AI模型: Gemini 底层
修改内容: [1. 使用原生 bcrypt 代替 passlib，彻底修复 python 3.12 下 bcrypt 72 字节检测异常; 2. 增加安全截断机制]
"""
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import jwt
import bcrypt
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码匹配"""
    try:
        # bcrypt 原生限制密码为 72 字节以内
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """生成密码的 bcrypt 哈希值"""
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(subject: str | Any, user_type: str = "user", expires_delta: Optional[timedelta] = None) -> str:
    """
    生成 JWT Token
    :param subject: 用户/管理员标识 (ID 或 Username)
    :param user_type: 用户类型 ("user" 代表 C端用户, "admin" 代表 B端管理员)
    :param expires_delta: 过期时间差
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": user_type,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str, allow_grace_period: bool = False) -> Optional[Dict[str, Any]]:
    """
    解析并验证 JWT Token
    :param token: 待解析的 JWT Token
    :param allow_grace_period: 是否允许宽限期 (如交卷接口允许 5 分钟缓冲)
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        if allow_grace_period:
            try:
                unverified_payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=[settings.ALGORITHM], 
                    options={"verify_exp": False}
                )
                exp_timestamp = unverified_payload.get("exp")
                if exp_timestamp:
                    exp_time = datetime.utcfromtimestamp(exp_timestamp)
                    if datetime.utcnow() <= exp_time + timedelta(minutes=settings.GRACE_PERIOD_MINUTES):
                        return unverified_payload
            except Exception:
                return None
        return None
    except jwt.PyJWTError:
        return None

