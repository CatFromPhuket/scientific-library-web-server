from fastapi import FastAPI
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
from models import Scientist, Topic, Paper

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