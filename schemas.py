from pydantic import BaseModel
from typing import Optional

class ScientistBase(BaseModel):
    name: str
    affiliation: Optional[str] = None
    specialization: Optional[str] = None

class ScientistCreate(ScientistBase):
    pass

class ScientistResponse(ScientistBase):
    id: int

    class Config:
        from_attributes = True  # чтобы работало преобразование из ORM-объекта

class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: int

    class Config:
        from_attributes = True

class PaperBase(BaseModel):
    title: str
    year: Optional[int] = None
    doi: Optional[str] = None
    citations: int = 0
    scientist_id: int
    topic_id: int


class PaperCreate(PaperBase):
    pass


class PaperResponse(PaperBase):
    id: int
    scientist: Optional[ScientistResponse] = None
    topic: Optional[TopicResponse] = None

    class Config:
        from_attributes = True

# ========== Auth ==========

class UserCreate(BaseModel):
    """При регистрации"""
    username: str
    password: str


class UserLogin(BaseModel):
    """При входе"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Что возвращаем клиенту (без пароля)"""
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Ответ при успешном входе"""
    access_token: str
    token_type: str = "bearer"


class UserUpdateRole(BaseModel):
    """Для смены роли (только админ)"""
    role: str