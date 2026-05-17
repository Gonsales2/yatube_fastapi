import pytest
from httpx import AsyncClient
from http import HTTPStatus


class TestAuthRegistration:

    @pytest.mark.asyncio
    async def test_register_user_success(self, client: AsyncClient):
        """Успешная регистрация нового пользователя"""
        response = await client.post(
            "/api/register/",
            json={
                "username": "newuser",
                "password": "SecurePass1",
                "email": "newuser@example.com",
            },
        )
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Регистрация с уже существующим username"""
        response = await client.post(
            "/api/register/",
            json={
                "username": "testuser",
                "password": "AnotherPass1",
                "email": "another@example.com",
            },
        )
        assert response.status_code == HTTPStatus.CONFLICT
        assert "уже существует" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Регистрация со слабым паролем"""
        response = await client.post(
            "/api/register/",
            json={
                "username": "weakuser",
                "password": "123",
                "email": "weak@example.com",
            },
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


class TestAuthLogin:
    """Тесты получения токена."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Успешный вход в систему"""
        response = await client.post(
            "/api/api-token-auth/",
            data={"username": "testuser", "password": "TestPass123"},
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user):
        """Вход с неверным паролем"""
        response = await client.post(
            "/api/api-token-auth/",
            data={"username": "testuser", "password": "WrongPass123"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert "неверные" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Вход несуществующего пользователя"""
        response = await client.post(
            "/api/api-token-auth/",
            data={"username": "nonexistent", "password": "SomePass123"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
