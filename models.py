# models.py — модель задачи и настройка SQLite
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Создаёт таблицы в БД при первом запуске."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Генератор сессии БД для FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()