from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Scientist(Base):
    """Таблица учёных"""
    __tablename__ = "scientists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)              # имя
    affiliation = Column(String(200), nullable=True)        # университет / институт
    specialization = Column(String(200), nullable=True)     # научная специализация

    # Связь: у одного учёного может быть много статей
    # back_populates говорит SQLAlchemy, что с другой стороны связь называется "scientist"
    papers = relationship("Paper", back_populates="scientist")

class Topic(Base):
    """Таблица тем (Теория струн, Квантовая физика...)"""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)     # название темы
    description = Column(Text, nullable=True)                   # краткое описание

    # Связь: у одной темы может быть много статей
    papers = relationship("Paper", back_populates="topic")

class Paper(Base):
    """Таблица статей — центральная, связывает учёных и темы"""
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)              # название статьи
    year = Column(Integer, nullable=True)                    # год публикации
    doi = Column(String(100), unique=True, nullable=True)    # цифровой идентификатор
    citations = Column(Integer, default=0)                   # число цитирований

    # Внешние ключи — ссылаются на id в других таблицах
    scientist_id = Column(Integer, ForeignKey("scientists.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    # Связи: статья "знает" своего автора и свою тему
    scientist = relationship("Scientist", back_populates="papers")
    topic = relationship("Topic", back_populates="papers")
