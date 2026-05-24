import asyncio
import pytest
from http import HTTPStatus
from typing import AsyncGenerator, Dict
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import NullPool

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.models.user import User
from app.models.post import Post
from app.models.group import Group
from app.models.comment import Comment

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:15432/yatube_test"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Переопределение зависимости БД для тестов"""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="session")
async def setup_test_db():
    """Создание тестовой БД и таблиц"""
    default_url = TEST_DATABASE_URL.replace("/yatube_test", "/postgres")
    default_engine = create_async_engine(
        default_url, isolation_level="AUTOCOMMIT", poolclass=NullPool
    )

    async with default_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'yatube_test'")
        )
        if not result.scalar():
            await conn.execute(text("CREATE DATABASE yatube_test"))

    await default_engine.dispose()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    default_engine = create_async_engine(
        default_url, isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    async with default_engine.connect() as conn:
        await conn.execute(text("""SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'yatube_test'
            AND pid <> pg_backend_pid();"""))
        await conn.execute(text("DROP DATABASE IF EXISTS yatube_test"))

    await default_engine.dispose()
    await engine.dispose()


@pytest.fixture(autouse=True)
async def clean_tables(setup_test_db):
    """Очистка таблиц перед каждым тестом"""
    async with engine.connect() as conn:
        await conn.execute(
            text(
                "LOCK TABLE posts_comment, posts_post, posts_group, auth_user IN ACCESS EXCLUSIVE MODE"
            )
        )
        await conn.execute(text("DELETE FROM posts_comment"))
        await conn.execute(text("DELETE FROM posts_post"))
        await conn.execute(text("DELETE FROM posts_group"))
        await conn.execute(text("DELETE FROM auth_user"))
        await conn.commit()

    yield


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный клиент для тестирования API"""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(client: AsyncClient) -> Dict:
    user_data = {
        "username": "testuser",
        "password": "TestPass123",
        "email": "testuser@example.com",
    }
    response = await client.post("/api/register/", json=user_data)
    if response.status_code not in [HTTPStatus.CREATED, HTTPStatus.CONFLICT]:
        pytest.fail(f"Не удалось подготовить пользователя: {response.status_code} {response.text}")
    
    return user_data


@pytest.fixture
async def auth_token(client: AsyncClient, test_user: Dict) -> str:
    """Получение токена авторизации"""
    response = await client.post(
        "/api/api-token-auth/",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    assert response.status_code == HTTPStatus.OK
    return response.json()["access_token"]


@pytest.fixture
async def auth_headers(auth_token: str) -> Dict[str, str]:
    """Заголовки с авторизацией"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def test_group(auth_headers: Dict) -> Dict:
    """Создание тестовой группы напрямую в БД"""
    async with TestSessionLocal() as session:
        async with session.begin():
            group = Group(
                title="Test Group",
                slug="test-group",
                description="Test group description",
            )
            session.add(group)
            await session.flush()
            await session.refresh(group)
            return {
                "id": group.id,
                "title": group.title,
                "slug": group.slug,
                "description": group.description,
            }

