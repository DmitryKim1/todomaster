# main.py — FastAPI приложение, 8 эндпоинтов
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import os

from models import Task, get_db, init_db, SessionLocal

# Инициализация БД при старте
init_db()

app = FastAPI(
    title="TodoMaster API",
    description="API для управления задачами",
    version="1.0.0",
)

# Статика (CSS, JS)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def _read_html(filename: str) -> str:
    """Читает HTML из папки templates и возвращает строку (без Jinja2)."""
    path = os.path.join("templates", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return f"<h1>Не найден: {filename}</h1>"


# --- Pydantic схемы ---
class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    done: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool
    created: Optional[str] = None

    class Config:
        from_attributes = True


# --- API эндпоинты ---

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Главная страница — отдаём index.html."""
    return _read_html("index.html")

@app.get("/stats", response_class=HTMLResponse)
def stats_page():
    return _read_html("stats.html")


@app.get("/health", response_class=HTMLResponse)
def health_page():
    return _read_html("health.html")


@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    """Получить все задачи."""
    tasks = db.query(Task).order_by(Task.id).all()
    return [
        TaskResponse(
            id=t.id,
            title=t.title,
            done=t.done,
            created=t.created.strftime("%Y-%m-%d") if t.created else None,
        )
        for t in tasks
    ]


@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Добавить задачу."""
    db_task = Task(title=task.title)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        done=db_task.done,
        created=db_task.created.strftime("%Y-%m-%d") if db_task.created else None,
    )


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Отметить задачу выполненной/невыполненной."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_update.done is not None:
        db_task.done = task_update.done
    db.commit()
    db.refresh(db_task)
    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        done=db_task.done,
        created=db_task.created.strftime("%Y-%m-%d") if db_task.created else None,
    )


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Удалить задачу."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted"}


@app.delete("/tasks/clear")
def clear_tasks(db: Session = Depends(get_db)):
    """Очистить все задачи."""
    db.query(Task).delete()
    db.commit()
    return {"message": "All tasks cleared"}


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Статистика: всего задач, выполнено, процент."""
    total = db.query(Task).count()
    completed = db.query(Task).filter(Task.done == True).count()
    percent = round((completed / total * 100) if total else 0, 1)
    return {"total": total, "completed": completed, "percent": percent}


@app.get("/api/health")
def health():
    """Статус API для мониторинга."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


# Swagger UI доступен по /docs из коробки FastAPI

@app.get("/metrics")
def metrics():
    """Метрики в формате, удобном для мониторинга (можно расширить под Prometheus)."""
    from models import SessionLocal, Task
    db = SessionLocal()
    try:
        total = db.query(Task).count()
        completed = db.query(Task).filter(Task.done == True).count()
        return {"tasks_total": total, "tasks_completed": completed}
    finally:
        db.close()