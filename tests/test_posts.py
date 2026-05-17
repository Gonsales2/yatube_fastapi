import pytest
from httpx import AsyncClient
from typing import Dict
from http import HTTPStatus


class TestCreatePost:
    @pytest.mark.asyncio
    async def test_create_post_success(self, client: AsyncClient, auth_headers: Dict):
        """Успешное создание поста"""
        response = await client.post(
            "/api/", json={"text": "Test post content"}, headers=auth_headers
        )
        assert (
            response.status_code == HTTPStatus.CREATED
        ), f"Got {response.status_code}: {response.text}"
        data = response.json()
        assert data["text"] == "Test post content"
        assert data["author"] == "testuser"
        assert "id" in data
        assert "pub_date" in data

    @pytest.mark.asyncio
    async def test_create_post_unauthorized(self, client: AsyncClient):
        """Создание поста без авторизации"""
        response = await client.post("/api/", json={"text": "Unauthorized post"})
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestReadPosts:
    @pytest.mark.asyncio
    async def test_get_nonexistent_post(self, client: AsyncClient, auth_headers: Dict):
        """Получение несуществующего поста."""
        response = await client.get("/api/99999", headers=auth_headers)
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestUpdateDeletePost:
    @pytest.mark.asyncio
    async def test_update_post(self, client: AsyncClient, auth_headers: Dict):
        """Обновление поста"""
        create_resp = await client.post(
            "/api/", json={"text": "Original text"}, headers=auth_headers
        )
        post_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/{post_id}", json={"text": "Updated text"}, headers=auth_headers
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["text"] == "Updated text"

    @pytest.mark.asyncio
    async def test_delete_post(self, client: AsyncClient, auth_headers: Dict):
        """Удаление поста"""
        create_resp = await client.post(
            "/api/", json={"text": "Post to delete"}, headers=auth_headers
        )
        post_id = create_resp.json()["id"]

        response = await client.delete(f"/api/{post_id}", headers=auth_headers)
        assert response.status_code == HTTPStatus.NO_CONTENT

        get_resp = await client.get(f"/api/{post_id}", headers=auth_headers)
        assert get_resp.status_code == HTTPStatus.NOT_FOUND
