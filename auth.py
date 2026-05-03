import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import models
from database import get_db
# HTTPBearer — простой способ вытащить токен из заголовка Authorization: Bearer <токен>
security = HTTPBearer()


def create_token() -> str:
    """Генерация случайного токена"""
    return secrets.token_hex(32)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Извлекает пользователя по токену из заголовка"""
    token = credentials.credentials
    user = db.query(models.User).filter(models.User.token == token).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user


def get_current_admin(current_user: models.User = Depends(get_current_user)):
    """Только админы"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user