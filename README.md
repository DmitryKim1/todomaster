# TodoMaster Web-App

Веб-приложение для управления задачами: FastAPI + SQLite + Vue 3 (CDN).

## Запуск локально

1. `python -m venv venv`
2. Активируй venv: `.\venv\Scripts\Activate.ps1` (Windows) или `source venv/bin/activate` (Linux/macOS)
3. `pip install -r requirements.txt`
4. `uvicorn main:app --reload --port 8000`
5. Открой http://localhost:8000

## Запуск в Docker

```bash
docker-compose up --build