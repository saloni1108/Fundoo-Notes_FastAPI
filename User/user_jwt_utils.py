import jwt
from Core.setting import settings
from datetime import datetime, timedelta
from jwt import PyJWTError
from fastapi import HTTPException
from enum import Enum

class Audience(Enum):
    register = "register_user"
    login = "login_user"

def encoded_user_jwt(payload: dict):
    if "exp" not in payload:
        payload["exp"] = datetime.utcnow() + timedelta(hours = 1)
    encoded_token = jwt.encode(payload = payload, key = settings.SECRET_KEY, algorithm = settings.ALGORITHM)
    return encoded_token

def decoded_user_jwt(token: str, audience: str)->dict:
    try:
        decoded_token = jwt.decode(token, key = settings.SECRET_KEY, algorithms = [settings.ALGORITHM], audience = audience)
    except PyJWTError:
        raise HTTPException(detail = "Invalid JWT Token", status_code = 401)
    return decoded_token