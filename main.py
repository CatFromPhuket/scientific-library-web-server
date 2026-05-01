from fastapi import FastAPI
from sqlalchemy.orm import Session


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Scientific Papers API is running"}