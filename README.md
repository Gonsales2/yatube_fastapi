1. git clone
2. python -m venv venv
3. source venv/Scripts/activate
4. pip install -r requirements.txt
5. pip install sqlalchemy alembic aiosqlite fastapi uvicorn
6. alembic revision --autogenerate -m "1_ready"
7. alembic upgrade head
8. uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
