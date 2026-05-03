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