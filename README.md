Yatube on FastAPI

1. git clone
2. python -m venv venv
3. source venv/Scripts/activate
4. pip install -r requirements.txt
5. pip install sqlalchemy alembic aiosqlite fastapi uvicorn
6. docker compose up -d
7. alembic revision --autogenerate -m "1_ready"
8. alembic upgrade head
9. uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Если не работает авторизация
pip install --upgrade "passlib[bcrypt]"
pip install bcrypt==3.2.2