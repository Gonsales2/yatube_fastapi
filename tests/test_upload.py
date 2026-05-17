import pytest
from httpx import AsyncClient
from typing import Dict
from pathlib import Path
from io import BytesIO
from PIL import Image
from app.config import settings
from http import HTTPStatus


def create_test_image(filename: str = "test_image.jpg") -> BytesIO:
    """Создание тестового изображения в памяти"""
    img = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    return img_byte_arr


class TestUploadImage:

    @pytest.mark.asyncio
    async def test_upload_image_success(self, client: AsyncClient, auth_headers: Dict):
        """Успешная загрузка изображения."""
        test_image = create_test_image()
        response = await client.post(
            "/api/upload/",
            files={"file": ("test.jpg", test_image, "image/jpeg")},
            headers=auth_headers,
        )
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert "filename" in data
        assert "path" in data
        assert "url" in data
        assert data["filename"] == "test.jpg"

    @pytest.mark.asyncio
    async def test_upload_invalid_format(self, client: AsyncClient, auth_headers: Dict):
        """Загрузка файла недопустимого формата"""
        response = await client.post(
            "/api/upload/",
            files={"file": ("test.txt", b"text content", "text/plain")},
            headers=auth_headers,
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "недопустимый формат" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_unauthorized(self, client: AsyncClient):
        """Загрузка без авторизации"""
        test_image = create_test_image()
        response = await client.post(
            "/api/upload/", files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
