from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
from database import engine, SessionLocal, Base
from models import Scientist, Topic, Paper
import schemas, crud

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Scientific Papers API is running"}

@app.post("/scientists/", response_model=schemas.ScientistResponse)
def create_scientist(scientist: schemas.ScientistCreate, db: Session = Depends(get_db)):
    return crud.create_scientist(db=db, scientist=scientist)


@app.get("/scientists/", response_model=list[schemas.ScientistResponse])
def read_scientists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_scientists(db, skip=skip, limit=limit)


@app.get("/scientists/{scientist_id}", response_model=schemas.ScientistResponse)
def read_scientist(scientist_id: int, db: Session = Depends(get_db)):
    db_scientist = crud.get_scientist(db, scientist_id=scientist_id)
    if db_scientist is None:
        raise HTTPException(status_code=404, detail="Scientist not found")
    return db_scientist


@app.put("/scientists/{scientist_id}", response_model=schemas.ScientistResponse)
def update_scientist(scientist_id: int, scientist: schemas.ScientistCreate, db: Session = Depends(get_db)):
    db_scientist = crud.update_scientist(db, scientist_id=scientist_id, scientist=scientist)
    if db_scientist is None:
        raise HTTPException(status_code=404, detail="Scientist not found")
    return db_scientist


@app.delete("/scientists/{scientist_id}")
def delete_scientist(scientist_id: int, db: Session = Depends(get_db)):
    db_scientist = crud.delete_scientist(db, scientist_id=scientist_id)
    if db_scientist is None:
        raise HTTPException(status_code=404, detail="Scientist not found")
    return {"message": "Scientist deleted"}


@app.post("/topics/", response_model=schemas.TopicResponse)
def create_topic(topic: schemas.TopicCreate, db: Session = Depends(get_db)):
    return crud.create_topic(db=db, topic=topic)


@app.get("/topics/", response_model=list[schemas.TopicResponse])
def read_topics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_topics(db, skip=skip, limit=limit)


@app.get("/topics/{topic_id}", response_model=schemas.TopicResponse)
def read_topic(topic_id: int, db: Session = Depends(get_db)):
    db_topic = crud.get_topic(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return db_topic


@app.delete("/topics/{topic_id}")
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    db_topic = crud.delete_topic(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"message": "Topic deleted"}


# ========== PAPERS ==========

@app.post("/papers/", response_model=schemas.PaperResponse)
def create_paper(paper: schemas.PaperCreate, db: Session = Depends(get_db)):
    return crud.create_paper(db=db, paper=paper)


@app.get("/papers/", response_model=list[schemas.PaperResponse])
def read_papers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_papers(db, skip=skip, limit=limit)


@app.get("/papers/{paper_id}", response_model=schemas.PaperResponse)
def read_paper(paper_id: int, db: Session = Depends(get_db)):
    db_paper = crud.get_paper(db, paper_id=paper_id)
    if db_paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return db_paper


@app.delete("/papers/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    db_paper = crud.delete_paper(db, paper_id=paper_id)
    if db_paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {"message": "Paper deleted"}


# ========== СПЕЦИАЛЬНЫЕ ЗАПРОСЫ (поиск по связям) ==========

@app.get("/papers/by-topic/{topic_id}", response_model=list[schemas.PaperResponse])
def read_papers_by_topic(topic_id: int, db: Session = Depends(get_db)):
    """Все статьи по теме (то, что ты хотел!)"""
    return crud.get_papers_by_topic(db, topic_id=topic_id)


@app.get("/papers/by-scientist/{scientist_id}", response_model=list[schemas.PaperResponse])
def read_papers_by_scientist(scientist_id: int, db: Session = Depends(get_db)):
    """Все статьи учёного"""
    return crud.get_papers_by_scientist(db, scientist_id=scientist_id)