from sqlalchemy.orm import Session
import models, schemas

def get_scientists(db: Session, skip: int = 0, limit: int = 100):
    """Вернуть список учёных с пагинацией"""
    return db.query(models.Scientist).offset(skip).limit(limit).all()

def get_scientist(db: Session, scientist_id: int):
    """Вернуть одного учёного по id"""
    return db.query(models.Scientist).filter(models.Scientist.id == scientist_id).first()

def create_scientist(db: Session, scientist: schemas.ScientistCreate):
    """Создать учёного"""
    db_scientist = models.Scientist(**scientist.model_dump())
    db.add(db_scientist)
    db.commit()
    db.refresh(db_scientist)  # получаем id, который выдала БД
    return db_scientist

def update_scientist(db: Session, scientist_id: int, scientist: schemas.ScientistCreate):
    """Обновить данные учёного"""
    db_scientist = get_scientist(db, scientist_id)
    if db_scientist:
        for key, value in scientist.model_dump().items():
            setattr(db_scientist, key, value)
        db.commit()
        db.refresh(db_scientist)
    return db_scientist

def delete_scientist(db: Session, scientist_id: int):
    """Удалить учёного"""
    db_scientist = get_scientist(db, scientist_id)
    if db_scientist:
        db.delete(db_scientist)
        db.commit()
    return db_scientist

# ========== Topic ==========

def get_topics(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Topic).offset(skip).limit(limit).all()


def get_topic(db: Session, topic_id: int):
    return db.query(models.Topic).filter(models.Topic.id == topic_id).first()


def create_topic(db: Session, topic: schemas.TopicCreate):
    db_topic = models.Topic(**topic.model_dump())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


def delete_topic(db: Session, topic_id: int):
    db_topic = get_topic(db, topic_id)
    if db_topic:
        db.delete(db_topic)
        db.commit()
    return db_topic


# ========== Paper ==========

def get_papers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Paper).offset(skip).limit(limit).all()


def get_paper(db: Session, paper_id: int):
    return db.query(models.Paper).filter(models.Paper.id == paper_id).first()


def create_paper(db: Session, paper: schemas.PaperCreate):
    db_paper = models.Paper(**paper.model_dump())
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper


def delete_paper(db: Session, paper_id: int):
    db_paper = get_paper(db, paper_id)
    if db_paper:
        db.delete(db_paper)
        db.commit()
    return db_paper


# ========== Специальные запросы ==========

def get_papers_by_topic(db: Session, topic_id: int):
    """Все статьи по конкретной теме"""
    return db.query(models.Paper).filter(models.Paper.topic_id == topic_id).all()


def get_papers_by_scientist(db: Session, scientist_id: int):
    """Все статьи конкретного учёного"""
    return db.query(models.Paper).filter(models.Paper.scientist_id == scientist_id).all()