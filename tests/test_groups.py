import pytest
from httpx import AsyncClient
from typing import Dict
from http import HTTPStatus


class TestReadGroups:

    @pytest.mark.asyncio
    async def test_get_groups_list(
        self, client: AsyncClient, auth_headers: Dict, test_group: Dict
    ):
        """Получение списка групп"""
        response = await client.get("/api/", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        groups = [item for item in data if "slug" in item]
        assert len(groups) >= 1
        assert any(g["slug"] == "test-group" for g in groups)

    @pytest.mark.asyncio
    async def test_get_group_by_id(
        self, client: AsyncClient, auth_headers: Dict, test_group: Dict
    ):
        """Получение группы по ID"""
        response = await client.get(f"/api/{test_group['id']}", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        assert response.json()["title"] == "Test Group"

    @pytest.mark.asyncio
    async def test_get_nonexistent_group(self, client: AsyncClient, auth_headers: Dict):
        """Получение несуществующей группы"""
        response = await client.get("/api/99999", headers=auth_headers)
        assert response.status_code == HTTPStatus.NOT_FOUND
