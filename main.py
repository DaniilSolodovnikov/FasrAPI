from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uvicorn import *
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


app = FastAPI()

users = {}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SQLALCHEMY_DATABASE_URL = "postgresql:///./users.db"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(BaseModel):
    id: int
    created_ad: datetime
    email: str  # В тз это поле называлось как "login - почтовый адрес", я решил назвать его как "email"
    password: str
    project_id: int
    env: str
    domain: str
    locktime: datetime


@app.post("/create_user/")
def create_user(user: User):
    user_id = len(users) + 1
    new_user = dict(user)
    new_user["id"] = user_id
    users[user_id] = new_user
    return new_user


@app.get("/users/", response_model=list[User])
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users


@app.post("/acquire_lock/{user_id}")
def acquire_lock(user_id: int):
    if user_id in users and users[user_id].get('locktime'):
        return {"message": f"Пользователь {user_id} уже заблокирован"}

    users[user_id] = {'locktime': 1}  # Set locktime to 1 or any other value to indicate lock
    return {"message": f"Блокировка совершена для пользователя {user_id}"}


@app.post("/release_lock/{user_id}")
def release_lock(user_id: int):
    if user_id in users and users[user_id].get('locktime'):
        users[user_id]['locktime'] = None
        return {"message": f"Блокировка для пользователя {user_id} была снята"}
    else:
        return {"message": f"Пользователь {user_id} не был заблокирован"}
