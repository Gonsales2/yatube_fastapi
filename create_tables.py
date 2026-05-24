# create_tables.py
"""
Скрипт создания таблиц через синхронный SQLAlchemy.
Запуск: python create_tables.py
"""

import sys
from pathlib import Path

# Добавляем проект в PATH
sys.path.insert(0, str(Path(__file__).parent))

# === ИМПОРТИРУЕМ ВСЕ МОДЕЛИ ДО Base.metadata.create_all ===
from app.models.user import User  # noqa: F401
from app.models.group import Group  # noqa: F401
from app.models.post import Post  # noqa: F401
from app.models.comment import Comment  # noqa: F401
from app.models.post_image import PostImage  # noqa: F401 ← критично!
from app.models.comment_image import CommentImage  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401

from sqlalchemy import create_engine, text
from app.database.base import Base
from app.config import settings


def main():
    # Конвертируем asyncpg URL в синхронный postgresql+psycopg2
    db_url = str(settings.DATABASE_URL).replace("+asyncpg", "+psycopg2")
    print(f"🔗 Подключение к БД: {db_url}")

    # Создаём СИНХРОННЫЙ engine для создания таблиц
    engine = create_engine(db_url, echo=True, pool_pre_ping=True)

    try:
        print("\n🔄 Создаю таблицы...")
        # create_all создаёт только отсутствующие таблицы (идемпотентно)
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы созданы!\n")

        # Показываем список таблиц
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
                )
            )
            tables = [row[0] for row in result.all()]
            print(f"📋 Таблицы в базе ({len(tables)}):")
            for table in tables:
                print(f"   • {table}")

            # Проверка критичных таблиц
            required = {
                "auth_user",
                "posts_group",
                "posts_post",
                "posts_postimage",
                "posts_comment",
                "posts_commentimage",
                "refresh_tokens",
            }
            missing = required - set(tables)
            if missing:
                print(f"\n❌ Отсутствуют: {missing}")
            else:
                print("\n🎉 Все нужные таблицы на месте!")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\n💡 Проверьте:")
        print("   1. PostgreSQL запущен: docker-compose ps")
        print("   2. DATABASE_URL в .env корректный")
        print(
            "   3. База 'yatube' создана: docker-compose exec db psql -U postgres -c '\\l'"
        )
        raise
    finally:
        engine.dispose()
        print("\n✨ Готово!")


if __name__ == "__main__":
    main()
