import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

# Импорт всех моделей для autogenerate
from app.database.base import Base
from app.models.user import User      # noqa: F401
from app.models.group import Group    # noqa: F401
from app.models.post import Post      # noqa: F401
from app.models.comment import Comment  # noqa: F401

# Получаем конфигурацию Alembic
config = context.config

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем метаданные моделей
target_metadata = Base.metadata


def get_database_url() -> str:
    """
    Получает URL базы данных для миграций.
    Для локального запуска заменяет db на localhost.
    """
    # Получаем URL из переменных окружения
    database_url = os.getenv(
        'DATABASE_URL', 
        'postgresql+asyncpg://postgres:postgres@localhost:15432/yatube'
    )
    
    # Заменяем @db: на @localhost: для локального доступа
    database_url = database_url.replace('@db:', '@localhost:')
    
    # Конвертируем асинхронный URL в синхронный для Alembic
    database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    database_url = database_url.replace('postgresql+psycopg://', 'postgresql://')
    
    return database_url


def run_migrations_offline() -> None:
    """Запуск миграций в оффлайн-режиме."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме."""
    url = get_database_url()
    print(f"Connecting to database: {url}")
    
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if PostgreSQL is running: docker ps")
        print("2. Check logs: docker compose logs db")
        print("3. Try connecting manually:")
        print("   docker compose exec db psql -U postgres -d yatube")
        print("   (default password is: postgres)")
        raise
    finally:
        connectable.dispose()


# Определяем режим запуска
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()