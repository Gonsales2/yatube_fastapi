import pytest

from app.repositories.user_repo import pwd_context


@pytest.mark.asyncio
async def test_password_hashing():
    password = "Test12345"

    hashed = pwd_context.hash(password)

    assert pwd_context.verify(password, hashed)
