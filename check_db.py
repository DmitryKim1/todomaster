# check_db.py — один раз запусти и удали
from models import init_db
init_db()
print("Таблица tasks создана. Файл tasks.db появился в папке.")
