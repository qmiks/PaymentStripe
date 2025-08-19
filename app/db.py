from sqlmodel import SQLModel, create_engine, Session
import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(DB_URL, echo=False, connect_args=connect_args)

def get_session():
    return Session(engine)

def init_db():
    SQLModel.metadata.create_all(engine)
