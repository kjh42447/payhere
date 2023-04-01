from typing import Optional
from fastapi import FastAPI
from dotenv import load_dotenv
import os

from pydantic import BaseModel
from database import engineconn
from models import User, Expenses

load_dotenv()

engine = engineconn()
session = engine.sessionmaker()

app = FastAPI()

@app.get("/")
def index():
    return {"fastapi": "framework"}