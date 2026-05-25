import pytest
from httpx import AsyncClient
from typing import Dict
from http import HTTPStatus

TEST_GROUP_ID = 1



@pytest.fixture
async def test_post(client: AsyncClient, auth_headers: Dict, test_group: Dict) -> Dict:
    """Создание тестового поста для комментариев"""
    response = await client.post(
        f"/api/group/{test_group['id']}/post/",
        json={"text": "Post for comments"},
        headers=auth_headers,
    )
    assert response.status_code == HTTPStatus.CREATED
    return response.json()


class TestCreateComment:

    @pytest.mark.asyncio
    async def test_create_comment_success(
        self, client: AsyncClient, auth_headers: Dict, test_post: Dict, test_group: Dict
    ):
        """Успешное создание комментария"""
        group_id = test_group["id"]
        response = await client.post(
            f"/api/group/{group_id}/post/{test_post['id']}/comment/",
            json={"text": "Test comment"},
            headers=auth_headers,
        )
        assert (
            response.status_code == HTTPStatus.CREATED
        ), f"Got {response.status_code}: {response.text}"
        data = response.json()
        assert data["text"] == "Test comment"
        assert data["author"] == "testuser"

    @pytest.mark.asyncio
    async def test_create_comment_on_nonexistent_post(
        self, client: AsyncClient, auth_headers: Dict, test_post: Dict, test_group: Dict
    ):
        """Создание комментария к несуществующему посту"""
        group_id = test_group["id"]
        response = await client.post(
            f"/api/group/{group_id}/post/99999/comment/",
            json={"text": "Comment on nothing"},
            headers=auth_headers,
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_empty_comment(
        self, client: AsyncClient, auth_headers: Dict, test_post: Dict, test_group: Dict
    ):
        group_id = test_group["id"]
        """Создание пустого комментария"""
        response = await client.post(
            f"/api/group/{group_id}/post/{test_post['id']}/",
            json={"text": ""},
            headers=auth_headers,
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


class TestReadComments:

    @pytest.mark.asyncio
    async def test_get_comments_list(
        self, client: AsyncClient, auth_headers: Dict, test_post: Dict, test_group: Dict
    ):
        """Получение списка комментариев"""
        group_id = test_group["id"]
        for i in range(3):
            await client.post(
                f"/api/group/{group_id}/post/{test_post['id']}/comment/",
                json={"text": f"Comment {i}"},
                headers=auth_headers,
            )

        response = await client.get(
            f"/api/group/{group_id}/post/{test_post['id']}/comment/",
            headers=auth_headers,
        )
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()) == 3

    @pytest.mark.asyncio
    async def test_get_single_comment(
        self, client: AsyncClient, auth_headers: Dict, test_post: Dict, test_group: Dict
    ):
        """Получение конкретного комментария"""
        group_id = test_group["id"]
        create_resp = await client.post(
            f"/api/{test_post['id']}/comment/",
            json={"text": "Specific comment"},
            headers=auth_headers,
        )
        comment_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/group/{group_id}/post/{test_post['id']}/comment/{comment_id}",
            headers=auth_headers,
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["text"] == "Specific comment"


class TestDeleteComment:

    @pytest.mark.asyncio
    async def test_delete_own_comment(
        self, client: AsyncClient, auth_headers: Dict, test_post: Dict, test_group: Dict
    ):
        """Удаление своего комментария"""
        group_id = test_group["id"]
        create_resp = await client.post(
            f"/api/group/{group_id}/post/{post_id}/comment/",
            json={"text": "Comment to delete"},
            headers=auth_headers,
        )
        comment_id = create_resp.json()["id"]

        response = await client.delete(f"/api/{comment_id}", headers=auth_headers)
        assert response.status_code == HTTPStatus.NO_CONTENT
